"""0.4.0 portal-parity Block Storage, Object Storage and CDN."""

from __future__ import annotations

import asyncio
import json
import time

import httpx
import pytest

import ibee.operations as operations_module
from _compute_fixtures import ACCEPTED, OP, VM, VM2, WS, Router, async_client, async_transport, sync_client, vm
from ibee import AsyncIbee, CdnPurgeFailedError, Ibee, IbeeValidationError
from ibee.errors import (
    BillingDeniedError,
    ConflictError,
    ForbiddenError,
    OperationFailedError,
    OperationTimeoutError,
    UnprocessableEntityError,
)
from ibee.validation import (
    build_bucket_create_body,
    build_cdn_purge_body,
    build_s3_credential_body,
    normalize_cdn_domain,
    resolve_object_storage_region,
    validate_block_volume_name,
    validate_cdn_index_document,
)

VOL = "64b0000000000000000000b1"
SKU = {"sku_id": 12, "sku_code": "blocksto-std", "product_code": "block_storage"}
ELIGIBLE = {
    "organization_id": "o",
    "allowed": True,
    "reason": "eligible",
    "billing_mode": "PREPAID",
    "billing_state": "CURRENT",
    "evaluated_at": "2026-09-01T00:00:00Z",
}
DENIED = {**ELIGIBLE, "allowed": False, "reason": "insufficient_balance", "sku_code": "OBJECTST-STD"}


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    original = asyncio.sleep

    async def fast(seconds: float, *args: object) -> None:
        await original(0)

    monkeypatch.setattr(asyncio, "sleep", fast)


def volume(**overrides: object) -> dict:
    record = {
        "id": VOL,
        "name": "data",
        "size_gb": 20,
        "state": "ready",
        "vm_type": "cloud",
        "site_id": "site-1",
        "site_name": "Chennai",
        "attachments": [],
        "metadata": {"billing_catalog": SKU},
    }
    record.update(overrides)
    return record


def op(status: str, **extra: object) -> dict:
    return {
        "operation_id": OP,
        "vm_id": VM,
        "action": "attach_volume",
        "status": status,
        "submitted_at": "2026-09-01T10:00:00Z",
        "updated_at": "2026-09-01T10:00:02Z",
        **extra,
    }


def base_client(router: Router, base_url: str) -> Ibee:
    return Ibee(token="t", base_url=base_url, httpx_client=httpx.Client(transport=httpx.MockTransport(router)), max_retries=0)


# ---------------------------------------------------------------------------
# Block Storage validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "message"),
    [("ab", "at least 3 characters"), ("My Data", "try 'my-data'"), ("data_1", "Lowercase letters"), ("  ", "Enter a volume name"), ("a" * 256, "at most 255")],
)
def test_volume_name_rule(name: str, message: str) -> None:
    with pytest.raises(IbeeValidationError, match=message):
        validate_block_volume_name(name)
    assert validate_block_volume_name("  db-01 ") == "db-01"


def test_create_volume_validates_before_any_request() -> None:
    router = Router()
    block = sync_client(router).block_storage
    bad = [
        dict(name="data", size_gb=9, site_id="s"),
        dict(name="data", size_gb=10001, site_id="s"),
        dict(name="data", size_gb=True, site_id="s"),
        dict(name="data", size_gb=10.5, site_id="s"),
        dict(name="data", size_gb=10, site_id="  "),
        dict(name="data", size_gb=10, site_id="s", sku_code="rootdisk-1"),
        dict(name="data", size_gb=10, site_id="s", sku_code=" "),
        dict(name="data", size_gb=10, site_id="s", volume_class="fast"),
        dict(name="data", size_gb=10, site_id="s", replica_count=6),
        dict(name="data", size_gb=10, site_id="s", vm_type="bare"),
        dict(name="data", size_gb=10, site_id="s", delete_on_termination="yes"),
    ]
    for kwargs in bad:
        with pytest.raises(IbeeValidationError):
            block.create_block_volume(workspace_id=WS, **kwargs)
    assert router.requests == []


def test_create_volume_resolves_site_name_and_sends_key_in_body_and_header() -> None:
    router = Router()
    router.add("GET", "compute/sites", (200, {"sites": [{"site_id": "site-1", "name": "Chennai"}], "count": 1}))
    router.add("POST", "block-storage/volumes", (201, {"volume": volume(), "operation": {"status": "succeeded"}}))
    result = sync_client(router).block_storage.create_block_volume(
        workspace_id=WS, name=" data ", size_gb=20, site_id=" site-1 ", sku_code=" blocksto-std ", vm_type="gpu",
        delete_on_termination=True,
    )
    assert result["volume"]["id"] == VOL
    body = router.body("POST", "block-storage/volumes")
    key = body.pop("idempotency_key")
    assert key.startswith("block-volume-create-data-")
    assert router.last("POST", "block-storage/volumes").headers["x-idempotency-key"] == key
    assert body == {
        "name": "data",
        "size_gb": 20,
        "site_id": "site-1",
        "site_name": "Chennai",
        "sku_code": "BLOCKSTO-STD",
        "volume_class": "balanced",
        "replica_count": 2,
        "backup_enabled": True,
        "vm_type": "gpu",
        "delete_on_termination": True,
    }
    assert "billing_catalog" not in body and "volume_kind" not in body


def test_create_volume_site_lookup_is_best_effort_but_rejects_unknown_sites() -> None:
    router = Router().add("GET", "compute/sites", (403, {"error": "insufficient_scope", "required_scope": "vm.read"}))
    router.add("POST", "block-storage/volumes", (201, {"volume": volume()}))
    sync_client(router).block_storage.create_block_volume(workspace_id=WS, name="data", size_gb=10, site_id="site-1")
    assert "site_name" not in router.body("POST", "block-storage/volumes")

    unknown = Router().add("GET", "compute/sites", (200, {"sites": [{"site_id": "other", "name": "X"}], "count": 1}))
    with pytest.raises(IbeeValidationError, match="Unknown site_id"):
        sync_client(unknown).block_storage.create_block_volume(workspace_id=WS, name="data", size_gb=10, site_id="site-1")
    assert unknown.calls() == [("GET", "compute/sites")]


def test_create_volume_billing_denial_is_typed() -> None:
    router = Router().add(
        "POST",
        "block-storage/volumes",
        (402, {"error": "billing_denied", "billing_reason": "insufficient_balance", "billing_sku_code": "BLOCKSTO-STD"}),
    )
    with pytest.raises(BillingDeniedError) as info:
        sync_client(router).block_storage.create_block_volume(
            workspace_id=WS, name="data", size_gb=10, site_id="s", resolve_site_name=False
        )
    assert info.value.reason == "insufficient_balance"
    assert info.value.billing_sku_code == "BLOCKSTO-STD"


def test_volume_ids_and_list_filters_are_validated() -> None:
    router = Router().add("GET", "block-storage/volumes", (200, []))
    block = sync_client(router).block_storage
    for call in (
        lambda: block.get_block_volume("vol-1", workspace_id=WS),
        lambda: block.list_block_volume_operations(VOL, workspace_id=WS, limit=201),
        lambda: block.list_block_volumes(workspace_id=WS, limit=1001),
        lambda: block.list_block_volumes(workspace_id=WS, offset=-1),
        lambda: block.list_block_volumes(workspace_id=WS, vm_type="bare"),
        lambda: block.list_block_volumes(workspace_id=WS, site_id=" "),
    ):
        with pytest.raises(IbeeValidationError):
            call()
    assert router.requests == []
    block.list_block_volumes(workspace_id=WS, site_id="site-1", vm_type="gpu", limit=50, offset=100)
    params = router.requests[-1].url.params
    assert (params["site_id"], params["vm_type"], params["limit"], params["offset"]) == ("site-1", "gpu", "50", "100")


def test_iter_block_volumes_pages_until_a_short_page() -> None:
    pages = [[volume(id=f"{i:024x}") for i in range(2)], [volume(id=f"{9:024x}")]]
    router = Router().add("GET", "block-storage/volumes", *[(200, page) for page in pages])
    items = sync_client(router).block_storage.list_all_block_volumes(workspace_id=WS, page_size=2)
    assert [item["id"] for item in items] == [f"{0:024x}", f"{1:024x}", f"{9:024x}"]
    assert [r.url.params["offset"] for r in router.requests] == ["0", "2"]


def test_list_operations_limit() -> None:
    router = Router().add("GET", f"block-storage/volumes/{VOL}/operations", (200, []))
    sync_client(router).block_storage.list_block_volume_operations(VOL, workspace_id=WS, limit=200)
    assert router.requests[-1].url.params["limit"] == "200"


def test_delete_volume_guards_like_the_portal() -> None:
    attached = Router().add("GET", f"block-storage/volumes/{VOL}", (200, volume(attachments=[{"vm_id": VM, "vm_name": "web-1", "node_name": "n1"}])))
    with pytest.raises(IbeeValidationError, match="Detach this volume from all servers before deleting") as info:
        sync_client(attached).block_storage.delete_block_volume(VOL, workspace_id=WS)
    assert info.value.details["servers"] == ["web-1"]
    busy = Router().add("GET", f"block-storage/volumes/{VOL}", (200, volume(state="resizing")))
    with pytest.raises(IbeeValidationError, match="Retry delete once workflow completes"):
        sync_client(busy).block_storage.delete_block_volume(VOL, workspace_id=WS)

    ok = Router().add("GET", f"block-storage/volumes/{VOL}", (200, volume()))
    ok.add("DELETE", f"block-storage/volumes/{VOL}", (200, {"status": "deleted", "id": VOL, "operation_id": "o"}))
    sync_client(ok).block_storage.delete_block_volume(VOL, workspace_id=WS)
    params = ok.last("DELETE", f"block-storage/volumes/{VOL}").url.params
    assert params["force"] == "false" and params["idempotency_key"].startswith("block-volume-delete-")

    forced = Router().add("DELETE", f"block-storage/volumes/{VOL}", (200, {"status": "deleted"}))
    sync_client(forced).block_storage.delete_block_volume(VOL, workspace_id=WS, force=True)
    assert forced.calls() == [("DELETE", f"block-storage/volumes/{VOL}")]

    no_read = Router().add("GET", f"block-storage/volumes/{VOL}", (403, {"error": "insufficient_scope"}))
    no_read.add("DELETE", f"block-storage/volumes/{VOL}", (200, {"status": "deleted"}))
    sync_client(no_read).block_storage.delete_block_volume(VOL, workspace_id=WS)
    assert no_read.calls()[-1] == ("DELETE", f"block-storage/volumes/{VOL}")

    conflict = Router().add("DELETE", f"block-storage/volumes/{VOL}", (409, {"detail": {"message": "Volume is attached.", "debug_reason": "x"}}))
    with pytest.raises(ConflictError) as err:
        sync_client(conflict).block_storage.delete_block_volume(VOL, workspace_id=WS, check_state=False)
    assert err.value.message == "Volume is attached."


def test_resize_rules() -> None:
    block_path = f"block-storage/volumes/{VOL}"
    shrink = Router().add("GET", block_path, (200, volume(size_gb=50)))
    with pytest.raises(IbeeValidationError, match="increase-only"):
        sync_client(shrink).block_storage.resize_block_volume(VOL, workspace_id=WS, new_size_gb=40)
    attached = Router().add("GET", block_path, (200, volume(attachments=[{"vm_id": VM, "node_name": "n"}])))
    with pytest.raises(IbeeValidationError, match="allow_online"):
        sync_client(attached).block_storage.resize_block_volume(VOL, workspace_id=WS, new_size_gb=40, vm_state="running")
    with pytest.raises(IbeeValidationError):
        sync_client(Router()).block_storage.resize_block_volume(VOL, workspace_id=WS, new_size_gb=0)
    with pytest.raises(IbeeValidationError):
        sync_client(Router()).block_storage.resize_block_volume(VOL, workspace_id=WS, new_size_gb=30, vm_state="paused")

    ok = Router().add("GET", block_path, (200, volume(attachments=[{"vm_id": VM, "node_name": "n"}])))
    ok.add("POST", f"{block_path}/resize", (200, {"volume": volume(size_gb=40)}))
    sync_client(ok).block_storage.resize_block_volume(VOL, workspace_id=WS, new_size_gb=40, vm_state="stopped")
    body = ok.body("POST", f"{block_path}/resize")
    assert body["new_size_gb"] == 40 and body["vm_state"] == "stopped" and body["allow_online"] is False
    assert "billing_catalog" not in body


def test_node_level_attach_and_detach() -> None:
    path = f"block-storage/volumes/{VOL}"
    block = sync_client(Router()).block_storage
    with pytest.raises(IbeeValidationError, match="Safe detach"):
        block.detach_block_volume(VOL, workspace_id=WS, node_name="n1")
    with pytest.raises(IbeeValidationError):
        block.attach_block_volume(VOL, workspace_id=WS, node_name=" ")
    with pytest.raises(IbeeValidationError):
        block.attach_block_volume(VOL, workspace_id=WS, node_name="n", mode="shared")

    router = Router().add("GET", path, (200, volume(vm_type="gpu", attachments=[{"node_name": "n1", "vm_id": VM}])))
    router.add("POST", f"{path}/detach", (200, {"volume": volume()}))
    sync_client(router).block_storage.detach_block_volume(VOL, workspace_id=WS, vm_state="stopped")
    body = router.body("POST", f"{path}/detach")
    assert (body["node_name"], body["vm_type"], body["vm_state"]) == ("n1", "gpu", "stopped")

    several = Router().add("GET", path, (200, volume(attachments=[{"node_name": "a"}, {"node_name": "b"}])))
    with pytest.raises(IbeeValidationError, match="several"):
        sync_client(several).block_storage.detach_block_volume(VOL, workspace_id=WS, force=True)

    site = Router().add("GET", path, (200, volume(site_id="site-1")))
    with pytest.raises(IbeeValidationError, match="Select a server in Chennai"):
        sync_client(site).block_storage.attach_block_volume(VOL, workspace_id=WS, node_name="n", vm_site_id="site-2")


# ---------------------------------------------------------------------------
# VM attach / detach (portal flow)
# ---------------------------------------------------------------------------


def test_attach_to_vm_reads_volume_picks_endpoint_and_waits() -> None:
    path = f"block-storage/volumes/{VOL}"
    router = Router().add("GET", path, (200, volume(vm_type="gpu")), (200, volume(vm_type="gpu", state="in-use")))
    router.add("GET", f"compute/gpu-vms/{VM}", (200, vm()))
    router.add("POST", f"compute/gpu-vms/{VM}/actions/attach-volume", (202, ACCEPTED))
    router.add("GET", f"compute/operations/{OP}", (200, op("running")), (200, op("succeeded")))
    result = sync_client(router).block_storage.attach_block_volume_to_vm(VOL, VM, workspace_id=WS, wait=True)
    assert result["operation"].status == "succeeded"
    assert result["volume"]["state"] == "in-use"
    body = router.body("POST", f"compute/gpu-vms/{VM}/actions/attach-volume")
    assert body == {
        "volume_id": VOL,
        "mode": "single-writer",
        "billing_catalog": {**SKU, "sku_code": "BLOCKSTO-STD", "attached_skus": {}},
    }
    headers = router.last("POST", f"compute/gpu-vms/{VM}/actions/attach-volume").headers
    assert headers["x-idempotency-key"].startswith("gpu-vm-attach-volume-")
    assert [c for c in router.calls() if c[0] == "GET" and c[1] == path].__len__() == 2


def test_attach_to_vm_guards() -> None:
    path = f"block-storage/volumes/{VOL}"
    cases = [
        (volume(attachments=[{"vm_id": VM2}]), {}, "already attached"),
        (volume(vm_type="cloud"), {"vm_type": "gpu"}, "created for cloud VMs"),
        (volume(site_id="site-9", site_name="Mumbai"), {}, "Select a server in Mumbai"),
        (volume(metadata={}), {}, "billing catalog"),
    ]
    for record, kwargs, message in cases:
        router = Router().add("GET", path, (200, record)).add("GET", f"compute/cloud-vms/{VM}", (200, vm()))
        with pytest.raises(IbeeValidationError, match=message):
            sync_client(router).block_storage.attach_block_volume_to_vm(VOL, VM, workspace_id=WS, **kwargs)
        assert not any(c[0] == "POST" for c in router.calls())


def test_attach_without_block_storage_read_needs_catalog() -> None:
    path = f"block-storage/volumes/{VOL}"
    router = Router().add("GET", path, (403, {"error": "insufficient_scope", "required_scope": "block-storage.read"}))
    with pytest.raises(IbeeValidationError, match="block-storage.read"):
        sync_client(router).block_storage.attach_block_volume_to_vm(VOL, VM, workspace_id=WS)
    with pytest.raises(IbeeValidationError, match="billing_catalog is required"):
        sync_client(router).cloud_vms.attach_cloud_vm_volume(VM, workspace_id=WS, volume_id=VOL)

    router.add("GET", f"compute/cloud-vms/{VM}", (403, {"error": "insufficient_scope"}))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/attach-volume", (202, ACCEPTED))
    sync_client(router).block_storage.attach_block_volume_to_vm(
        VOL, VM, workspace_id=WS, vm_type="cloud", billing_catalog=SKU
    )
    assert router.body("POST", f"compute/cloud-vms/{VM}/actions/attach-volume")["billing_catalog"]["sku_code"] == "BLOCKSTO-STD"
    assert router.calls().count(("GET", path)) == 3


def test_vm_attach_checks_vm_type_on_existing_method() -> None:
    router = Router().add("GET", f"block-storage/volumes/{VOL}", (200, volume(vm_type="cloud")))
    router.add("GET", f"compute/gpu-vms/{VM}", (200, vm()))
    with pytest.raises(IbeeValidationError, match="cannot attach to a gpu VM"):
        sync_client(router).gpu_vms.attach_gpu_vm_volume(VM, workspace_id=WS, volume_id=VOL)
    with pytest.raises(IbeeValidationError, match="24 hexadecimal"):
        sync_client(router).gpu_vms.attach_gpu_vm_volume(VM, workspace_id=WS, volume_id="vol-1")


def test_wait_failure_and_timeout_messages(monkeypatch: pytest.MonkeyPatch) -> None:
    path = f"block-storage/volumes/{VOL}"
    router = Router().add("GET", path, (200, volume()))
    router.add("GET", f"compute/cloud-vms/{VM}", (200, vm()))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/attach-volume", (202, ACCEPTED))
    router.add("GET", f"compute/operations/{OP}", (200, op("failed")))
    with pytest.raises(OperationFailedError, match="Volume operation failed"):
        sync_client(router).block_storage.attach_block_volume_to_vm(VOL, VM, workspace_id=WS, wait=True)

    ticks = iter(range(0, 1000, 50))
    monkeypatch.setattr(operations_module, "_clock", lambda: next(ticks))
    slow = Router().add("GET", f"compute/operations/{OP}", (200, op("running")))
    with pytest.raises(OperationTimeoutError, match="Please refresh to check the latest state"):
        sync_client(slow).block_storage.wait_for_volume_operation(OP, workspace_id=WS)


def test_detach_from_vm_finds_the_vm_and_requires_confirmation() -> None:
    path = f"block-storage/volumes/{VOL}"
    with pytest.raises(IbeeValidationError, match="confirm_unmounted=True"):
        sync_client(Router()).block_storage.detach_block_volume_from_vm(VOL, workspace_id=WS)
    with pytest.raises(IbeeValidationError, match="confirm_unmounted=True"):
        sync_client(Router()).cloud_vms.detach_cloud_vm_volume(VM, workspace_id=WS, volume_id=VOL)

    router = Router().add("GET", path, (200, volume(vm_type="gpu", attachments=[{"vm_id": VM, "node_name": "n"}])))
    router.add("POST", f"compute/gpu-vms/{VM}/actions/detach-volume", (202, ACCEPTED))
    sync_client(router).block_storage.detach_block_volume_from_vm(VOL, workspace_id=WS, confirm_unmounted=True)
    assert router.body("POST", f"compute/gpu-vms/{VM}/actions/detach-volume") == {"volume_id": VOL, "confirm_unmounted": True, "force": False}

    for record, message in (
        (volume(), "not attached to any server"),
        (volume(attachments=[{"vm_id": VM}, {"vm_id": VM2}]), "several VMs"),
        (volume(attachments=[{"node_name": "n"}]), "no VM ID"),
    ):
        bad = Router().add("GET", path, (200, record))
        with pytest.raises(IbeeValidationError, match=message):
            sync_client(bad).block_storage.detach_block_volume_from_vm(VOL, workspace_id=WS, force=True)


def test_async_block_storage_parity() -> None:
    path = f"block-storage/volumes/{VOL}"
    router = Router().add("GET", path, (200, volume()), (200, volume(attachments=[{"vm_id": VM}])))
    router.add("GET", f"compute/cloud-vms/{VM}", (200, vm()))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/attach-volume", (202, ACCEPTED))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/detach-volume", (202, ACCEPTED))
    router.add("GET", f"compute/operations/{OP}", (200, op("succeeded")))
    router.add("GET", "block-storage/volumes", (200, [volume()]))

    async def run() -> None:
        async with async_transport(router) as http_client:
            block = async_client(router, http_client).block_storage
            done = await block.attach_block_volume_to_vm(VOL, VM, workspace_id=WS, wait=True)
            assert done["operation"].status == "succeeded"
            await block.detach_block_volume_from_vm(VOL, VM, workspace_id=WS, confirm_unmounted=True)
            items = [item async for item in block.iter_block_volumes(workspace_id=WS)]
            assert len(items) == 1
            with pytest.raises(IbeeValidationError):
                await block.create_block_volume(workspace_id=WS, name="x", size_gb=10, site_id="s")

    asyncio.run(run())
    assert router.body("POST", f"compute/cloud-vms/{VM}/actions/attach-volume")["billing_catalog"]["sku_code"] == "BLOCKSTO-STD"


# ---------------------------------------------------------------------------
# Object Storage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "message"),
    [("ab", "at least 3"), ("a" * 64, "less than 63"), ("Assets", "start and end"), ("-assets", "start and end"), ("as_ets", "start and end")],
)
def test_bucket_name_rule(name: str, message: str) -> None:
    router = Router()
    with pytest.raises(IbeeValidationError, match=message):
        sync_client(router).object_storage.create_bucket(workspace_id=WS, name=name, region="in-south-1")
    assert router.requests == []


def test_bucket_region_defaults_from_the_api_host() -> None:
    assert resolve_object_storage_region(None, "https://api.ibee.ai/v1") == "in-south-1"
    assert resolve_object_storage_region(None, "https://api.ibee.co.in/v1") == "in-south-2"
    assert resolve_object_storage_region(" eu-1 ", "https://x.test") == "eu-1"
    with pytest.raises(IbeeValidationError, match="region is required"):
        resolve_object_storage_region(None, "https://api.example.test/v1")

    router = Router().add("POST", "object-storage/buckets", (201, {"name": "assets", "is_public": False, "bucket_lock_enabled": False}))
    base_client(router, "https://api.ibee.co.in/v1").object_storage.create_bucket(workspace_id=WS, name="assets")
    assert router.body("POST", "object-storage/buckets") == {"name": "assets", "region": "in-south-2"}


def test_bucket_retention_rules() -> None:
    body = build_bucket_create_body(name="assets", region="r", default_retention={"mode": "GOVERNANCE", "days": 30})
    assert body["object_lock_enabled"] is True and body["default_retention"] == {"mode": "GOVERNANCE", "days": 30}
    for retention in (
        {"mode": "NONE", "days": 1},
        {"mode": "COMPLIANCE"},
        {"mode": "COMPLIANCE", "days": 1, "years": 1},
        {"mode": "COMPLIANCE", "days": 0},
        {"mode": "COMPLIANCE", "years": 101},
        {"mode": "COMPLIANCE", "days": True},
    ):
        with pytest.raises(IbeeValidationError):
            build_bucket_create_body(name="assets", region="r", default_retention=retention)
    with pytest.raises(IbeeValidationError, match="object_lock_enabled must be true"):
        build_bucket_create_body(name="assets", region="r", object_lock_enabled=False, default_retention={"mode": "COMPLIANCE", "years": 1})


def test_bucket_create_preflight_and_409_is_not_retried() -> None:
    router = Router().add("POST", "billing/resource-eligibility", (200, DENIED))
    with pytest.raises(BillingDeniedError):
        sync_client(router).object_storage.create_bucket(workspace_id=WS, name="assets", region="r", preflight_billing=True)
    assert router.calls() == [("POST", "billing/resource-eligibility")]
    assert router.body("POST", "billing/resource-eligibility")["sku_code"] == "OBJECTST-STD"

    conflict = Router().add("POST", "object-storage/buckets", (409, {"detail": "Bucket already exists"}))
    client = Ibee(token="t", base_url="https://api.example.test/v1", httpx_client=httpx.Client(transport=httpx.MockTransport(conflict)))
    with pytest.raises(ConflictError):
        client.object_storage.create_bucket(workspace_id=WS, name="assets", region="r")
    assert len(conflict.requests) == 1


def test_bucket_delete_preflight() -> None:
    path = "object-storage/buckets/assets"
    locked = Router().add("GET", path, (200, {"name": "assets", "is_public": False, "bucket_lock_enabled": True, "object_count": 0}))
    with pytest.raises(IbeeValidationError, match="Object Lock"):
        sync_client(locked).object_storage.delete_bucket("assets", workspace_id=WS, skip_preflight=True)
    full = Router().add("GET", path, (200, {"name": "assets", "is_public": False, "bucket_lock_enabled": False, "object_count": 3}))
    with pytest.raises(IbeeValidationError, match=r"not empty \(3 objects\)"):
        sync_client(full).object_storage.delete_bucket("assets", workspace_id=WS)
    full.add("DELETE", path, (200, {"detail": "Bucket deleted"}))
    assert sync_client(full).object_storage.delete_bucket("assets", workspace_id=WS, skip_preflight=True).detail == "Bucket deleted"
    with pytest.raises(IbeeValidationError):
        sync_client(Router()).object_storage.update_bucket("assets", workspace_id=WS, is_public="no")  # type: ignore[arg-type]


def test_list_buckets_iterates_continuation_tokens() -> None:
    bucket = {"name": "a", "is_public": False, "bucket_lock_enabled": False}
    router = Router().add(
        "GET",
        "object-storage/buckets",
        (200, {"buckets": [bucket], "is_truncated": True, "next_continuation_token": "t2"}),
        (200, {"buckets": [{**bucket, "name": "b"}], "is_truncated": False}),
    )
    names = [b.name for b in sync_client(router).object_storage.list_all_buckets(workspace_id=WS, page_size=1)]
    assert names == ["a", "b"]
    assert router.requests[1].url.params["continuation_token"] == "t2"
    with pytest.raises(IbeeValidationError):
        sync_client(Router()).object_storage.list_buckets(workspace_id=WS, limit=0)


def test_s3_credential_rules() -> None:
    assert build_s3_credential_body() == {"name": "Default Key", "permission_type": "admin_rw", "bucket_scope": "all", "allowed_buckets": []}
    assert build_s3_credential_body(name=" ci ", permission_type="object_ro", bucket_scope="specific", allowed_buckets=[" a ", "a", "", "b"]) == {
        "name": "ci", "permission_type": "object_ro", "bucket_scope": "specific", "allowed_buckets": ["a", "b"],
    }
    for kwargs, message in (
        ({"name": " "}, "enter a credential name"),
        ({"name": "x" * 101}, "at most 100"),
        ({"permission_type": "owner"}, "permission_type"),
        ({"permission_type": "admin_ro", "bucket_scope": "specific"}, "only to object_rw"),
        ({"permission_type": "object_rw", "bucket_scope": "specific", "allowed_buckets": [" "]}, "at least one bucket"),
        ({"permission_type": "object_rw", "allowed_buckets": ["a"]}, "must be empty"),
    ):
        with pytest.raises(IbeeValidationError, match=message):
            build_s3_credential_body(**kwargs)


def test_s3_credential_create_defaults_and_is_never_retried() -> None:
    router = Router().add("POST", "object-storage/credentials", (503, {"detail": "unavailable"}))
    client = Ibee(token="t", base_url="https://api.example.test/v1", httpx_client=httpx.Client(transport=httpx.MockTransport(router)))
    with pytest.raises(Exception):
        client.object_storage.create_s3credential(workspace_id=WS)
    assert len(router.requests) == 1
    assert router.body("POST", "object-storage/credentials") == {
        "name": "Default Key", "permission_type": "admin_rw", "bucket_scope": "all", "allowed_buckets": [],
    }
    with pytest.raises(IbeeValidationError, match="object_rw"):
        client.object_storage.create_s3credential(workspace_id=WS, bucket_scope="specific", allowed_buckets=["a"])


def test_s3_credential_delete_alias_and_extra_fields() -> None:
    router = Router().add("DELETE", "object-storage/credentials/AK1", (200, {"success": True, "message": "has been deleted"}))
    router.add("GET", "object-storage/credentials/AK1", (200, {
        "access_key_id": "AK1", "name": "ci", "status": "active", "created_at": "2026-09-01T00:00:00Z",
        "organization_id": "7", "workspace_id": WS, "permission_type": "object_ro", "bucket_scope": "specific",
        "allowed_buckets": ["a"], "created_by_user_id": "u1",
    }))
    client = sync_client(router)
    assert client.object_storage.delete_s3credential("AK1", workspace_id=WS).success is True
    assert client.object_storage.revoke_s3credential("AK1", workspace_id=WS).success is True
    credential = client.object_storage.get_s3credential("AK1", workspace_id=WS)
    assert credential.permission_type == "object_ro" and credential.allowed_buckets == ["a"]
    with pytest.raises(IbeeValidationError):
        client.object_storage.get_s3credential(" ", workspace_id=WS)


def test_async_object_storage_parity() -> None:
    bucket = {"name": "a", "is_public": False, "bucket_lock_enabled": False, "object_count": 0}
    router = Router().add("GET", "object-storage/buckets/a", (200, bucket)).add("DELETE", "object-storage/buckets/a", (200, {"detail": "Bucket deleted"}))
    router.add("GET", "object-storage/buckets", (200, {"buckets": [bucket], "is_truncated": False}))
    router.add("POST", "object-storage/credentials", (201, {
        "access_key_id": "AK", "secret_access_key": "s", "name": "Default Key", "status": "active", "created_at": "2026-09-01T00:00:00Z",
    }))
    router.add("DELETE", "object-storage/credentials/AK", (200, {"success": True, "message": "deleted"}))

    async def run() -> None:
        async with async_transport(router) as http_client:
            storage = async_client(router, http_client).object_storage
            await storage.delete_bucket("a", workspace_id=WS)
            assert [b.name async for b in storage.iter_buckets(workspace_id=WS)] == ["a"]
            assert (await storage.list_all_buckets(workspace_id=WS))[0].name == "a"
            assert (await storage.create_s3credential(workspace_id=WS)).secret_access_key == "s"
            assert (await storage.delete_s3credential("AK", workspace_id=WS)).success is True
            with pytest.raises(IbeeValidationError):
                await storage.create_bucket(workspace_id=WS, name="a")

    asyncio.run(run())
    assert router.body("POST", "object-storage/credentials")["permission_type"] == "admin_rw"


# ---------------------------------------------------------------------------
# CDN
# ---------------------------------------------------------------------------


def test_cdn_distribution_validation_and_origin_check() -> None:
    cdn = sync_client(Router()).cdn
    for kwargs in (
        dict(name=" ", origin_id="assets"),
        dict(name="x" * 129, origin_id="assets"),
        dict(name="site", origin_id=" "),
        dict(name="site", origin_id="assets", cache_policy="public-development"),
        dict(name="site", origin_id="assets", origin_type="s3"),
    ):
        with pytest.raises(IbeeValidationError):
            cdn.create_cdn_distribution(workspace_id=WS, **kwargs)
    with pytest.raises(IbeeValidationError, match="at least one"):
        cdn.update_cdn_distribution("d1", workspace_id=WS)

    private = Router().add("GET", "object-storage/buckets/assets", (200, {"name": "assets", "is_public": False, "bucket_lock_enabled": False}))
    with pytest.raises(IbeeValidationError, match="Only public buckets"):
        sync_client(private).cdn.create_cdn_distribution(workspace_id=WS, name="site", origin_id="assets", check_origin_public=True)

    by_id = Router().add("GET", "object-storage/buckets/b-123", (404, {"detail": "Bucket not found"}))
    by_id.add("POST", "billing/resource-eligibility", (200, ELIGIBLE))
    by_id.add("POST", "cdn/distributions", (201, {"id": "d1"}))
    sync_client(by_id).cdn.create_cdn_distribution(
        workspace_id=WS, name=" site ", origin_id="b-123", check_origin_public=True, preflight_billing=True
    )
    assert by_id.body("POST", "cdn/distributions") == {"name": "site", "origin_type": "bucket", "origin_id": "b-123", "cache_policy": "static-assets"}
    assert "sku_code" not in by_id.body("POST", "billing/resource-eligibility")


def test_cdn_index_document_and_domain_rules() -> None:
    assert validate_cdn_index_document(None) == "index.html"
    assert validate_cdn_index_document(" app/index.html ") == "app/index.html"
    for bad in ("/index.html", "a\\b", "a//b", "../x", "café.html", "x" * 1025, " "):
        with pytest.raises(IbeeValidationError):
            validate_cdn_index_document(bad)
    assert normalize_cdn_domain(" CDN.Example.com ", for_create=True) == "cdn.example.com"
    for bad in ("localhost", "a.", "-a.com", "a" * 254, "x_y.com"):
        with pytest.raises(IbeeValidationError):
            normalize_cdn_domain(bad, for_create=True)
    with pytest.raises(IbeeValidationError, match="subdomain"):
        normalize_cdn_domain("example", for_create=True)


def test_cdn_custom_domain_preflight_and_normalised_paths() -> None:
    router = Router().add("POST", "billing/resource-eligibility", (200, {**ELIGIBLE, "sku_code": "CUSTOMDO-STD"}))
    router.add("POST", "cdn/distributions/d1/custom-domains", (201, {"domain": "cdn.example.com", "status": "pending_validation"}))
    router.add("GET", "cdn/distributions/d1/custom-domains/cdn.example.com", (200, {"domain": "cdn.example.com"}))
    client = sync_client(router)
    client.cdn.create_cdn_custom_domain("d1", workspace_id=WS, domain="CDN.example.com", preflight_billing=True)
    assert router.body("POST", "billing/resource-eligibility") == {"sku_code": "CUSTOMDO-STD", "estimated_cost_minor": 19900}
    assert router.body("POST", "cdn/distributions/d1/custom-domains") == {"domain": "cdn.example.com"}
    client.cdn.get_cdn_custom_domain("d1", " CDN.EXAMPLE.COM ", workspace_id=WS)


def test_wait_for_cdn_custom_domain(monkeypatch: pytest.MonkeyPatch) -> None:
    verify = "cdn/distributions/d1/custom-domains/cdn.example.com/verify"
    router = Router().add("POST", verify, (200, {"status": "pending_tls"}), (200, {"status": "active"}))
    assert sync_client(router).cdn.wait_for_cdn_custom_domain("d1", "cdn.example.com", workspace_id=WS)["status"] == "active"
    ticks = iter(range(0, 10000, 300))
    monkeypatch.setattr(operations_module, "_clock", lambda: next(ticks))
    pending = Router().add("POST", verify, (200, {"status": "pending_validation", "message": "DNS not found"}))
    with pytest.raises(OperationTimeoutError, match="still pending_validation"):
        sync_client(pending).cdn.wait_for_cdn_custom_domain("d1", "cdn.example.com", workspace_id=WS)


def test_cdn_purge_builder() -> None:
    assert build_cdn_purge_body("url", paths=["a.png", " /b ", "https://cdn.example.com/c"]) == {
        "mode": "url", "paths": ["/a.png", "/b", "https://cdn.example.com/c"],
    }
    assert build_cdn_purge_body("hostname", hostnames=["CDN.Example.com"]) == {"mode": "hostname", "hostnames": ["cdn.example.com"]}
    assert build_cdn_purge_body("all") == {"mode": "all"}
    for mode, kwargs in (
        ("all", {"paths": ["/a"]}),
        ("url", {}),
        ("url", {"paths": [f"/{i}" for i in range(31)]}),
        ("url", {"paths": ["http://cdn.example.com/a"]}),
        ("url", {"paths": ["https://u:p@cdn.example.com/a"]}),
        ("url", {"paths": ["https://cdn.example.com/a#x"]}),
        ("prefix", {"prefixes": ["/a?x=1"]}),
        ("tag", {"tags": [" "]}),
        ("everything", {}),
    ):
        with pytest.raises(IbeeValidationError):
            build_cdn_purge_body(mode, **kwargs)


def test_cdn_purge_failure_is_raised() -> None:
    router = Router().add("POST", "cdn/distributions/d1/purge", (200, {"success": False, "mode": "prefix", "message": "Cache purge failed"}))
    with pytest.raises(CdnPurgeFailedError) as info:
        sync_client(router).cdn.purge_cdn_cache("d1", workspace_id=WS, mode="prefix", prefixes=["/img/"])
    assert info.value.mode == "prefix" and info.value.status_code == 200
    raw = sync_client(router).cdn.purge_cdn_cache("d1", workspace_id=WS, mode="prefix", prefixes=["/img/"], raise_on_failure=False)
    assert raw["success"] is False


def test_cdn_new_uncontracted_reads_and_generate_url() -> None:
    router = Router().add("GET", "cdn/distributions/cache-policies", (200, {"policies": []}))
    router.add("GET", "cdn/distributions/d1/metrics", (200, {"points": []}))
    router.add("POST", "cdn/generate-url", (200, {"cdn_url": "https://x"}))
    cdn = sync_client(router).cdn
    cdn.list_cdn_cache_policies(workspace_id=WS)
    cdn.get_cdn_distribution_metrics("d1", workspace_id=WS)
    assert router.last("GET", "cdn/distributions/d1/metrics").url.params["range"] == "24h"
    cdn.get_cdn_distribution_metrics("d1", workspace_id=WS, range="30d")
    with pytest.raises(IbeeValidationError):
        cdn.get_cdn_distribution_metrics("d1", workspace_id=WS, range="1y")
    for kwargs in ({"expires_in": 0}, {"disposition": "download"}, {"object_key": " "}):
        with pytest.raises(IbeeValidationError):
            cdn.generate_cdn_url(workspace_id=WS, bucket_name="b", **{"object_key": "k", **kwargs})
    cdn.generate_cdn_url(workspace_id=WS, bucket_name=" b ", object_key="a b.png", disposition="inline")
    assert router.body("POST", "cdn/generate-url") == {"bucket_name": "b", "object_key": "a b.png", "disposition": "inline"}


def test_cdn_errors_are_typed() -> None:
    router = Router().add("POST", "cdn/distributions", (422, {"detail": [{"loc": ["body", "name"], "msg": "too long"}]}))
    router.add("GET", "cdn/distributions/d1", (403, {"detail": "Storage namespace changes are restricted"}))
    with pytest.raises(UnprocessableEntityError):
        sync_client(router).cdn.create_cdn_distribution(workspace_id=WS, name="n", origin_id="a")
    with pytest.raises(ForbiddenError):
        sync_client(router).cdn.get_cdn_distribution("d1", workspace_id=WS)


def test_async_cdn_parity() -> None:
    router = Router().add("POST", "cdn/distributions/d1/purge", (200, {"success": False, "mode": "tag"}))
    router.add("PUT", "cdn/distributions/d1/website-config", (200, {"enabled": True}))

    async def run() -> None:
        async with async_transport(router) as http_client:
            cdn = async_client(router, http_client).cdn
            with pytest.raises(CdnPurgeFailedError):
                await cdn.purge_cdn_cache("d1", workspace_id=WS, mode="tag", tags=["t"])
            await cdn.update_cdn_website_config("d1", workspace_id=WS)
            with pytest.raises(IbeeValidationError):
                await cdn.update_cdn_website_config("d1", workspace_id=WS, index_document="/x")

    asyncio.run(run())
    assert router.body("PUT", "cdn/distributions/d1/website-config") == {"index_document": "index.html"}


def test_public_surface_is_in_parity() -> None:
    sync = Ibee(token="t", base_url="https://api.example.test/v1")
    asy = AsyncIbee(token="t", base_url="https://api.example.test/v1")
    for name in ("block_storage", "object_storage", "cdn"):
        left = {m for m in dir(getattr(sync, name)) if not m.startswith("_")}
        right = {m for m in dir(getattr(asy, name)) if not m.startswith("_")}
        assert left == right, name
    assert json.dumps(sorted({"attach_block_volume_to_vm", "detach_block_volume_from_vm"} - set(dir(sync.block_storage)))) == "[]"
