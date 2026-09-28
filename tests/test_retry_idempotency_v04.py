"""0.4.0 key-aware retries and automatic idempotency keys."""

from __future__ import annotations

import asyncio
import json
import typing

import httpx
import pytest

import ibee.core.http_client as http_client_module
from ibee import AsyncIbee, Ibee, IbeeValidationError
from ibee.errors import ConflictError, InternalServerError, ServiceUnavailableError
from ibee.retry import is_retry_safe, parse_retry_after, retry_delay, should_retry_status

BASE = "https://api.example.test/v1"
WS = "710995"
ACCEPTED = {"operation_id": "op_0123456789abcdef01234567", "vm_id": "0123456789abcdef01234567", "status": "accepted", "submitted_at": "2026-08-04T10:00:00Z"}


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> list:
    delays: list = []

    def fake_delay(attempt: int, headers: typing.Any = None) -> float:
        delays.append(retry_delay(attempt, headers))
        return 0.0

    monkeypatch.setattr(http_client_module, "retry_delay", fake_delay)
    return delays


def _client(handler, **kwargs) -> Ibee:
    return Ibee(token="t", base_url=BASE, httpx_client=httpx.Client(transport=httpx.MockTransport(handler)), **kwargs)


def _sequence(*responses):
    observed: list[httpx.Request] = []
    queue = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, Exception):
            raise item
        status, body = item
        return httpx.Response(status, json=body, request=request)

    return handler, observed


# policy helpers ----------------------------------------------------------------


def test_retry_policy_helpers() -> None:
    assert is_retry_safe("GET", "compute/cloud-vms")
    assert not is_retry_safe("POST", "compute/cloud-vms")
    # VM creates are never retried: a replay answers 409 "name already exists".
    assert not is_retry_safe("POST", "compute/cloud-vms", {"x-idempotency-key": "k"})
    assert is_retry_safe("DELETE", "compute/cloud-vms/0123456789abcdef01234567", {"x-idempotency-key": "k"})
    assert is_retry_safe("PATCH", "/v1/compute/gpu-vms/0123456789abcdef01234567/actions/access", {"X-Idempotency-Key": "k"})
    assert not is_retry_safe("POST", "compute/cloud-vms/0123456789abcdef01234567/snapshots", {"X-Idempotency-Key": "k"})
    assert not is_retry_safe("POST", "networking/vpcs", {"X-Idempotency-Key": "k"})
    assert is_retry_safe("POST", "block-storage/volumes", json_body={"idempotency_key": "k"})
    assert is_retry_safe("POST", "block-storage/volumes/v-1/resize", json_body={"idempotency_key": "k"})
    assert not is_retry_safe("POST", "block-storage/volumes", json_body={"idempotency_key": "  "})
    assert is_retry_safe("DELETE", "block-storage/volumes/v-1", params={"idempotency_key": "k"})
    assert [s for s in (408, 409, 429, 500, 502, 503, 504) if should_retry_status(s)] == [429, 502, 503, 504]


def test_retry_delay_honours_and_clamps_retry_after() -> None:
    assert retry_delay(0, {"Retry-After": "3"}) == 3.0
    assert retry_delay(0, {"retry-after": "600"}) == 30.0
    assert retry_delay(0, {"retry-after-ms": "1500"}) == 1.5
    assert parse_retry_after({"Retry-After": "Wed, 21 Oct 2015 07:28:00 GMT"}) == 0.0
    assert 0.9 <= retry_delay(0) <= 1.1
    assert 3.6 <= retry_delay(2) <= 4.4
    assert retry_delay(10) <= 30.0


# transport behaviour -----------------------------------------------------------


def test_get_is_retried_on_503_then_succeeds(_no_sleep: list) -> None:
    handler, observed = _sequence((503, {"detail": "busy"}), (200, []))
    assert _client(handler).cloud_vms.list_cloud_vms(workspace_id=WS, limit=10) == []
    assert len(observed) == 2


def test_get_gives_up_after_max_retries() -> None:
    handler, observed = _sequence((502, {"detail": "bad"}))
    with pytest.raises(Exception) as info:
        _client(handler).cloud_vms.list_cloud_vms(workspace_id=WS, limit=10)
    assert info.value.status_code == 502  # type: ignore[attr-defined]
    assert len(observed) == 3


@pytest.mark.parametrize("status", [408, 409, 500])
def test_non_retryable_statuses_are_not_retried(status: int) -> None:
    handler, observed = _sequence((status, {"detail": "x"}))
    with pytest.raises(Exception):
        _client(handler).cloud_vms.get_cloud_vm("0123456789abcdef01234567", workspace_id=WS)
    assert len(observed) == 1


def test_unkeyed_write_is_not_retried_on_503() -> None:
    handler, observed = _sequence((503, {"detail": "busy"}), (201, {}))
    with pytest.raises(ServiceUnavailableError) as info:
        _client(handler).vpcs.create_vpc(workspace_id=WS, name="v", cidr="10.0.0.0/24", site_id="s")
    assert len(observed) == 1
    assert info.value.idempotency_key is None


def test_keyed_vm_write_is_retried_with_the_same_generated_key() -> None:
    handler, observed = _sequence((503, {"detail": "busy"}), (202, ACCEPTED))
    result = _client(handler).cloud_vms.start_cloud_vm("0123456789abcdef01234567", workspace_id=WS)
    assert result.operation_id == "op_0123456789abcdef01234567"
    keys = [request.headers["x-idempotency-key"] for request in observed]
    assert len(keys) == 2 and keys[0] == keys[1]
    assert keys[0].startswith("cloud-vm-start-0123456789abcdef01234567-")


def test_generated_create_key_uses_vm_name_and_conflict_is_not_retried() -> None:
    observed: list[httpx.Request] = []
    plan = {
        "plan_id": "p", "vm_type": "gpu", "name": "L40S", "code": "GPU-L40S", "cpu": 2, "ram_mb": 4096, "disk_gb": 100,
        "gpu_count": 1, "gpu_model": "L40S", "selectable": True, "pricing_status": "priced",
        "billing_catalog": {"sku_id": 7, "sku_code": "GPU-L40S"},
    }
    image = {"template_id": "t", "os_type": "linux", "os_distro": "ubuntu", "compatible_vm_types": ["gpu"], "site_ids": []}

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        if request.url.path.endswith("/compute/plans"):
            return httpx.Response(200, json={"plans": [plan]}, request=request)
        if request.url.path.endswith("/compute/images"):
            return httpx.Response(200, json={"images": [image]}, request=request)
        return httpx.Response(409, json={"detail": "A VM named web-1 already exists"}, request=request)

    with pytest.raises(ConflictError) as info:
        _client(handler).gpu_vms.create_gpu_vm(
            workspace_id=WS,
            name="web-1",
            site_id="site-1",
            os_distro="ubuntu",
            os_type="linux",
            template_id="t",
            cpu=2,
            ram_mb=4096,
            plan_id="p",
            gpu_count=1,
            gpu_model="L40S",
        )
    creates = [request for request in observed if request.method == "POST"]
    assert len(creates) == 1
    key = creates[0].headers["x-idempotency-key"]
    assert key.startswith("gpu-vm-create-web-1-")
    assert info.value.idempotency_key == key


def test_caller_key_is_validated_and_sent_unchanged() -> None:
    handler, observed = _sequence((202, ACCEPTED))
    client = _client(handler)
    client.cloud_vms.reboot_cloud_vm("0123456789abcdef01234567", workspace_id=WS, idempotency_key="my-key-1")
    assert observed[0].headers["x-idempotency-key"] == "my-key-1"
    with pytest.raises(IbeeValidationError) as info:
        client.cloud_vms.reboot_cloud_vm("0123456789abcdef01234567", workspace_id=WS, idempotency_key="bad key")
    assert info.value.code == "invalid_idempotency_key"
    assert len(observed) == 1


@pytest.mark.parametrize(
    ("call", "scope"),
    [
        (lambda c: c.cloud_vms.delete_cloud_vm("0123456789abcdef01234567", workspace_id=WS, public_ip_action="release", check_state=False), "cloud-vm-delete-0123456789abcdef01234567-"),
        (lambda c: c.cloud_vms.stop_cloud_vm("0123456789abcdef01234567", workspace_id=WS), "cloud-vm-stop-0123456789abcdef01234567-"),
        (lambda c: c.gpu_vms.update_gpu_vm_access("0123456789abcdef01234567", workspace_id=WS, new_password="Pw-123456789!", check_state=False), "gpu-vm-access-0123456789abcdef01234567-"),
        (lambda c: c.cloud_vms.resize_cloud_vm_root_disk("0123456789abcdef01234567", workspace_id=WS, new_size_gb=100, check_state=False), "cloud-vm-resize-root-disk-0123456789abcdef01234567-"),
        (lambda c: c.gpu_vms.detach_gpu_vm_volume("0123456789abcdef01234567", workspace_id=WS, volume_id="64b0000000000000000000b1", confirm_unmounted=True), "gpu-vm-detach-volume-0123456789abcdef01234567-"),
    ],
)
def test_every_keyed_vm_route_gets_a_key(call, scope: str) -> None:
    handler, observed = _sequence((202, ACCEPTED))
    call(_client(handler))
    assert observed[0].headers["x-idempotency-key"].startswith(scope)


def test_unkeyed_routes_get_no_key() -> None:
    handler, observed = _sequence((200, {"items": [], "total": 0}))
    client = _client(handler)
    client._client_wrapper.httpx_client.request(
        "compute/cloud-vms/0123456789abcdef01234567/snapshots", method="POST", params={"workspace_id": WS}, json={}
    )
    assert "x-idempotency-key" not in observed[0].headers


def test_connect_error_is_retried_even_for_unkeyed_post() -> None:
    handler, observed = _sequence(httpx.ConnectError("refused"), (201, {"id": "v"}))
    client = _client(handler)
    client._client_wrapper.httpx_client.request(
        "networking/vpcs", method="POST", params={"workspace_id": WS}, json={"name": "v"}
    )
    assert len(observed) == 2


def test_read_timeout_is_not_retried_for_unkeyed_post_but_is_for_keyed() -> None:
    handler, observed = _sequence(httpx.ReadTimeout("slow"), (201, {}))
    client = _client(handler)
    with pytest.raises(httpx.ReadTimeout):
        client._client_wrapper.httpx_client.request(
            "networking/vpcs", method="POST", params={"workspace_id": WS}, json={"name": "v"}
        )
    assert len(observed) == 1

    handler, observed = _sequence(httpx.ReadTimeout("slow"), (202, ACCEPTED))
    _client(handler).cloud_vms.start_cloud_vm("0123456789abcdef01234567", workspace_id=WS)
    assert len(observed) == 2


def test_transport_error_carries_idempotency_key() -> None:
    handler, _ = _sequence(httpx.ReadTimeout("slow"))
    with pytest.raises(httpx.ReadTimeout) as info:
        _client(handler, max_retries=0).cloud_vms.start_cloud_vm("0123456789abcdef01234567", workspace_id=WS, idempotency_key="k-1")
    assert getattr(info.value, "idempotency_key") == "k-1"


def test_max_retries_zero_disables_retries() -> None:
    handler, observed = _sequence((503, {}), (200, []))
    with pytest.raises(ServiceUnavailableError):
        _client(handler).cloud_vms.list_cloud_vms(
            workspace_id=WS, limit=5, request_options={"max_retries": 0}
        )
    assert len(observed) == 1


def test_500_is_raised_as_internal_server_error_without_retry() -> None:
    handler, observed = _sequence((500, {"detail": "boom"}))
    with pytest.raises(InternalServerError):
        _client(handler).cloud_vms.get_cloud_vm("0123456789abcdef01234567", workspace_id=WS)
    assert len(observed) == 1


def test_async_keyed_retry_parity(monkeypatch: pytest.MonkeyPatch) -> None:
    handler, observed = _sequence((504, {}), (202, ACCEPTED))

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            client = AsyncIbee(token="t", base_url=BASE, httpx_client=http_client)
            await client.gpu_vms.reboot_gpu_vm("0123456789abcdef01234567", workspace_id=WS)
            with pytest.raises(ConflictError):
                handler_409, _ = _sequence((409, {"detail": "x"}))
                async with httpx.AsyncClient(transport=httpx.MockTransport(handler_409)) as other:
                    await AsyncIbee(token="t", base_url=BASE, httpx_client=other).vpcs.create_vpc(
                        workspace_id=WS, name="v", cidr="10.0.0.0/24", site_id="s"
                    )

    asyncio.run(run())
    assert len(observed) == 2
    assert observed[0].headers["x-idempotency-key"] == observed[1].headers["x-idempotency-key"]


# block storage keys ------------------------------------------------------------


def test_block_storage_writes_carry_keys() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json={}, request=request)

    block = _client(handler).block_storage
    block.create_block_volume(workspace_id=WS, name="data", size_gb=10, site_id="s", site_name="S", idempotency_key="given-1")
    block.attach_block_volume("64b0000000000000000000b1", workspace_id=WS, node_name="n")
    block.detach_block_volume("64b0000000000000000000b1", workspace_id=WS, node_name="n", confirm_unmounted=True)
    block.resize_block_volume("64b0000000000000000000b1", workspace_id=WS, new_size_gb=20, check_state=False)
    block.delete_block_volume("64b0000000000000000000b1", workspace_id=WS, check_state=False)

    assert json.loads(observed[0].content)["idempotency_key"] == "given-1"
    assert observed[0].headers["x-idempotency-key"] == "given-1"
    assert json.loads(observed[1].content)["idempotency_key"].startswith("block-volume-attach-64b0000000000000000000b1-")
    assert json.loads(observed[2].content)["idempotency_key"].startswith("block-volume-detach-64b0000000000000000000b1-")
    assert json.loads(observed[3].content)["idempotency_key"].startswith("block-volume-resize-64b0000000000000000000b1-")
    assert observed[4].method == "DELETE"
    assert observed[4].url.params["idempotency_key"].startswith("block-volume-delete-64b0000000000000000000b1-")
    with pytest.raises(IbeeValidationError):
        block.create_block_volume(workspace_id=WS, name="data", size_gb=10, site_id="s", idempotency_key="a b")


def test_async_block_storage_writes_carry_keys() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json={}, request=request)

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            block = AsyncIbee(token="t", base_url=BASE, httpx_client=http_client).block_storage
            await block.create_block_volume(workspace_id=WS, name="data", size_gb=10, site_id="s", resolve_site_name=False)
            await block.resize_block_volume("64b0000000000000000000b1", workspace_id=WS, new_size_gb=20, check_state=False)
            await block.delete_block_volume("64b0000000000000000000b1", workspace_id=WS, idempotency_key="del-1", check_state=False)

    asyncio.run(run())
    assert json.loads(observed[0].content)["idempotency_key"].startswith("block-volume-create-data-")
    assert json.loads(observed[1].content)["idempotency_key"].startswith("block-volume-resize-64b0000000000000000000b1-")
    assert observed[2].url.params["idempotency_key"] == "del-1"


def test_keyed_block_volume_create_is_retried_with_same_body(_no_sleep: list) -> None:
    handler, observed = _sequence((502, {}), (200, {"id": "vol-1"}))
    _client(handler).block_storage.create_block_volume(workspace_id=WS, name="data", size_gb=10, site_id="s", site_name="S")
    assert len(observed) == 2
    assert observed[0].content == observed[1].content
