"""ibee.transport and ibee.core.api_error: workspace default, idempotency keys, safe retries, errors."""

import asyncio
import uuid

import httpx
import pytest
from mockapi import ACCEPTED, VM, WS, Recorder, async_client, client

from ibee.core.api_error import ApiError
from ibee.errors import (
    ConflictError,
    ForbiddenError,
    LockedError,
    PaymentRequiredError,
    ServiceUnavailableError,
)

EDGE_402 = {
    "error": "billing_denied",
    "required_scope": None,
    "billing_reason": "resource_limit_reached",
    "billing_sku_code": "VM-2C",
    "billing_evaluated_at": "2026-10-19T10:00:00Z",
    "admission_context_id": "adm-1",
}


# workspace_id -------------------------------------------------------------------


def test_default_workspace_is_sent_and_a_call_value_wins() -> None:
    rec = Recorder((200, []))
    api = client(rec, workspace_id=WS)
    api.reserved_ips.list_reserved_ips()
    api.reserved_ips.list_reserved_ips(workspace_id="42")
    assert [r.url.params["workspace_id"] for r in rec.requests] == [WS, "42"]


def test_workspace_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IBEE_WORKSPACE_ID", "77")
    rec = Recorder((200, []))
    client(rec).reserved_ips.list_reserved_ips()
    assert rec.requests[0].url.params["workspace_id"] == "77"


def test_no_workspace_is_left_to_the_server() -> None:
    rec = Recorder((400, {"error": "workspace_id_required"}))
    with pytest.raises(ApiError) as info:
        client(rec).reserved_ips.list_reserved_ips()
    assert "workspace_id" not in rec.requests[0].url.params
    assert info.value.code == "workspace_id_required"


# idempotency keys ---------------------------------------------------------------


def test_key_is_generated_where_the_contract_has_the_header() -> None:
    rec = Recorder((202, ACCEPTED))
    client(rec, workspace_id=WS).cloud_vms.start_cloud_vm(VM)
    uuid.UUID(rec.requests[0].headers["x-idempotency-key"])


def test_caller_key_is_sent_unchanged() -> None:
    rec = Recorder((202, ACCEPTED))
    api = client(rec, workspace_id=WS)
    api.cloud_vms.reboot_cloud_vm(VM, idempotency_key="my-key-1")
    api.cloud_vms.stop_cloud_vm(VM, request_options={"additional_headers": {"X-Idempotency-Key": "opt-key"}})
    assert [r.headers["x-idempotency-key"] for r in rec.requests] == ["my-key-1", "opt-key"]


def test_routes_without_the_header_get_no_key() -> None:
    rec = Recorder((201, {}))
    try:
        client(rec, workspace_id=WS).vpcs.create_vpc(name="v", site_id="s")
    except Exception:
        pass  # the mock body does not parse as a VPC; only the request matters
    assert "x-idempotency-key" not in rec.requests[0].headers


# retries ------------------------------------------------------------------------


@pytest.mark.parametrize("status", [429, 502, 503, 504])
def test_reads_are_retried(status: int) -> None:
    rec = Recorder((status, {"detail": "busy"}), (200, []))
    assert client(rec, workspace_id=WS).reserved_ips.list_reserved_ips() == []
    assert len(rec.requests) == 2


def test_reads_give_up_after_max_retries() -> None:
    rec = Recorder((502, {"detail": "bad"}))
    with pytest.raises(ApiError) as info:
        client(rec, workspace_id=WS).reserved_ips.list_reserved_ips()
    assert info.value.status_code == 502
    assert len(rec.requests) == 3


@pytest.mark.parametrize("status", [400, 408, 409, 500])
def test_other_statuses_are_not_retried(status: int) -> None:
    rec = Recorder((status, {"detail": "x"}))
    with pytest.raises(ApiError):
        client(rec, workspace_id=WS).cloud_vms.get_cloud_vm(VM)
    assert len(rec.requests) == 1


@pytest.mark.parametrize("status", [429, 503])
def test_keyed_write_is_retried_with_the_same_key(status: int) -> None:
    rec = Recorder((status, {"detail": "busy"}), (202, ACCEPTED))
    client(rec, workspace_id=WS).cloud_vms.start_cloud_vm(VM)
    keys = [r.headers["x-idempotency-key"] for r in rec.requests]
    assert len(keys) == 2 and keys[0] == keys[1]


@pytest.mark.parametrize("family", ["cloud", "gpu"])
@pytest.mark.parametrize("failure", [(503, {"detail": "busy"}), (429, {}), httpx.ConnectError("refused")])
def test_vm_create_is_never_retried(family: str, failure: object) -> None:
    rec = Recorder(failure, (202, ACCEPTED))
    vms = getattr(client(rec, workspace_id=WS), f"{family}_vms")
    shape = dict(cpu=2, ram_mb=2048, disk_gb=40, os_type="linux", os_distro="ubuntu", billing_catalog={"sku_id": 1, "sku_code": "VM"})
    if family == "gpu":
        shape.update(gpu_count=1, gpu_model="L4")
    with pytest.raises((ApiError, httpx.ConnectError)):
        getattr(vms, f"create_{family}_vm")(name="a", plan_id="p", template_id="t", site_id="s1", **shape)
    assert len(rec.requests) == 1
    assert rec.requests[0].headers["x-idempotency-key"]


@pytest.mark.parametrize("status", [502, 504])
def test_keyed_write_is_not_retried_on_502_or_504(status: int) -> None:
    rec = Recorder((status, {"detail": "upstream"}), (202, ACCEPTED))
    with pytest.raises(ApiError) as info:
        client(rec, workspace_id=WS).cloud_vms.start_cloud_vm(VM)
    assert len(rec.requests) == 1
    assert info.value.idempotency_key == rec.requests[0].headers["x-idempotency-key"]


def test_unkeyed_write_is_not_retried() -> None:
    rec = Recorder((503, {"detail": "busy"}))
    with pytest.raises(ServiceUnavailableError) as info:
        client(rec, workspace_id=WS).vpcs.create_vpc(name="v", site_id="s")
    assert len(rec.requests) == 1
    assert info.value.idempotency_key is None


@pytest.mark.parametrize(
    "body",
    [
        {"error": "billing_admission_unavailable", "billing_reason": None, "admission_context_id": None},
        {"error": "compute_catalog_unavailable"},
        {"error": "unsupported_product_quote"},
        {"error": "workspace_verification_unavailable", "admission_context_id": "adm-1"},
    ],
)
def test_billing_and_admission_answers_are_never_retried(body: dict) -> None:
    rec = Recorder((503, body), (202, ACCEPTED))
    with pytest.raises(ServiceUnavailableError):
        client(rec, workspace_id=WS).cloud_vms.start_cloud_vm(VM)
    assert len(rec.requests) == 1


def test_gateway_503_without_a_billing_code_is_retried_for_a_keyed_write() -> None:
    rec = Recorder((503, {"error": "workspace_verification_unavailable"}), (202, ACCEPTED))
    client(rec, workspace_id=WS).cloud_vms.start_cloud_vm(VM)
    assert len(rec.requests) == 2


def test_block_storage_body_key_makes_a_write_retryable() -> None:
    volume = {"operation_id": "o", "status": "accepted"}
    rec = Recorder((503, {"detail": "busy"}), (200, volume))
    try:
        client(rec, workspace_id=WS).block_storage.create_block_volume(name="d", size_gb=10, site_id="s", idempotency_key="k-1")
    except Exception:
        pass
    assert len(rec.requests) == 2
    assert rec.requests[0].content == rec.requests[1].content


def test_402_is_never_retried() -> None:
    rec = Recorder((402, EDGE_402))
    with pytest.raises(PaymentRequiredError):
        client(rec, workspace_id=WS).cloud_vms.start_cloud_vm(VM)
    assert len(rec.requests) == 1


def test_connect_error_is_retried_for_any_request() -> None:
    rec = Recorder(httpx.ConnectError("refused"), (201, {}))
    try:
        client(rec, workspace_id=WS).vpcs.create_vpc(name="v", site_id="s")
    except Exception:
        pass
    assert len(rec.requests) == 2


def test_read_timeout_is_retried_only_for_keyed_writes() -> None:
    rec = Recorder(httpx.ReadTimeout("slow"), (201, {}))
    with pytest.raises(httpx.ReadTimeout):
        client(rec, workspace_id=WS).vpcs.create_vpc(name="v", site_id="s")
    assert len(rec.requests) == 1

    rec = Recorder(httpx.ReadTimeout("slow"), (202, ACCEPTED))
    client(rec, workspace_id=WS).cloud_vms.start_cloud_vm(VM)
    assert len(rec.requests) == 2


def test_transport_error_carries_the_key() -> None:
    rec = Recorder(httpx.ReadTimeout("slow"))
    with pytest.raises(httpx.ReadTimeout) as info:
        client(rec, workspace_id=WS, max_retries=0).cloud_vms.start_cloud_vm(VM, idempotency_key="k-1")
    assert getattr(info.value, "idempotency_key") == "k-1"


IDENTITY = {"id": "id-1", "organization_id": "o", "workspace_id": WS, "name": "app", "auth_method": "approle",
            "status": "active", "token_policy_mode": "read_only", "created_at": "2026-10-19T00:00:00Z", "updated_at": "2026-10-19T00:00:00Z"}


@pytest.mark.parametrize("failure", [(429, {"detail": "slow down"}), (503, {"detail": "busy"}), httpx.ConnectError("refused")])
def test_identity_access_read_is_never_retried(failure: object) -> None:
    # Each GET of an identity's access mints a new AppRole credential.
    rec = Recorder(failure, (200, {"identity_id": "id-1", "auth_method": "approle", "role_id": "r", "secret_id": "s"}))
    with pytest.raises((ApiError, httpx.ConnectError)):
        client(rec, workspace_id=WS).secret_store.get_secret_identity_access("id-1")
    assert len(rec.requests) == 1
    assert rec.requests[0].url.path.endswith("/secret-store/identities/id-1/access")


def test_other_identity_reads_are_still_retried() -> None:
    rec = Recorder((503, {"detail": "busy"}), (200, IDENTITY))
    try:
        client(rec, workspace_id=WS).secret_store.get_secret_identity("id-1")
    except Exception:
        pass  # only the request count matters
    assert len(rec.requests) == 2


@pytest.mark.parametrize(
    ("method", "path", "never"),
    [
        ("GET", "secret-store/identities/id-1/access", True),
        ("GET", "/v1/secret-store/identities/id-1/access", True),
        ("GET", "v2/secret-store/identities/id-1/access/", True),
        ("HEAD", "secret-store/identities/id-1/access", True),
        ("GET", "secret-store/identities/id-1", False),
        ("GET", "secret-store/identities/id-1/access/other", False),
        ("POST", "compute/cloud-vms", True),
        ("POST", "compute/cloud-vms/vm-1/actions/start", False),
    ],
)
def test_never_retried_routes(method: str, path: str, never: bool) -> None:
    from ibee.transport import _never_retried

    assert _never_retried(method, path) is never


def test_max_retries_zero_disables_retries() -> None:
    rec = Recorder((503, {}), (200, []))
    with pytest.raises(ServiceUnavailableError):
        client(rec, workspace_id=WS).reserved_ips.list_reserved_ips(request_options={"max_retries": 0})
    assert len(rec.requests) == 1


# errors -------------------------------------------------------------------------


def test_edge_denial_is_relayed_unchanged() -> None:
    rec = Recorder((402, EDGE_402, {"x-request-id": "req-1"}))
    with pytest.raises(PaymentRequiredError) as info:
        client(rec, workspace_id=WS).cloud_vms.start_cloud_vm(VM)
    error = info.value
    assert error.status_code == 402
    assert error.body == EDGE_402 and error.raw_body == EDGE_402
    assert (error.code, error.billing_reason, error.admission_context_id) == ("billing_denied", "resource_limit_reached", "adm-1")
    assert error.message is None
    assert error.request_id == "req-1"
    assert "billing_denied" in str(error) and "req-1" in str(error)


def test_product_service_detail_is_relayed_unchanged() -> None:
    detail = {"code": "RESOURCE_LIMIT_REACHED", "message": "Your plan allows 2 volumes.", "limit": 2, "usage": 2}
    rec = Recorder((409, {"detail": detail}))
    with pytest.raises(ConflictError) as info:
        client(rec, workspace_id=WS).cloud_vms.start_cloud_vm(VM)
    assert info.value.code == "RESOURCE_LIMIT_REACHED"
    assert info.value.message == "Your plan allows 2 volumes."
    assert info.value.body == {"detail": detail}


@pytest.mark.parametrize(
    ("status", "cls"),
    [(403, ForbiddenError), (423, LockedError), (429, ApiError), (502, ApiError), (504, ApiError)],
)
def test_status_named_classes(status: int, cls: type) -> None:
    # Contract 0.6.2 declares no 429, 502 or 504 answer, so those raise ApiError itself.
    rec = Recorder((status, {"error": "organization_restricted"}, {"x-request-id": "req-1"}))
    with pytest.raises(ApiError) as info:
        client(rec, workspace_id=WS, max_retries=0).cloud_vms.get_cloud_vm(VM)
    assert type(info.value) is cls
    assert (info.value.status_code, info.value.code, info.value.request_id) == (status, "organization_restricted", "req-1")


def test_other_statuses_and_text_bodies() -> None:
    rec = Recorder((418, "teapot"))
    with pytest.raises(ApiError) as info:
        client(rec, workspace_id=WS).cloud_vms.get_cloud_vm(VM)
    assert type(info.value) is ApiError
    assert (info.value.status_code, info.value.body, info.value.message) == (418, "teapot", "teapot")
    rec = Recorder((404, {"detail": "VM not found"}))
    with pytest.raises(ApiError) as info:
        client(rec, workspace_id=WS).cloud_vms.get_cloud_vm(VM)
    assert (info.value.code, info.value.message) == (None, "VM not found")


# async parity -------------------------------------------------------------------


def test_async_retries_keys_and_errors() -> None:
    rec = Recorder((503, {"detail": "busy"}), (202, ACCEPTED), (402, EDGE_402, {"x-request-id": "req-2"}))

    async def run() -> None:
        api = async_client(rec, workspace_id=WS)
        await api.gpu_vms.reboot_gpu_vm(VM)
        with pytest.raises(PaymentRequiredError) as info:
            await api.gpu_vms.reboot_gpu_vm(VM)
        assert info.value.request_id == "req-2"

    asyncio.run(run())
    assert len(rec.requests) == 3
    assert rec.requests[0].headers["x-idempotency-key"] == rec.requests[1].headers["x-idempotency-key"]
    assert rec.requests[0].url.params["workspace_id"] == WS
