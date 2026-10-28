"""Contract 0.6.2: every method is the generated call; the request goes out as given and the answer comes back unchanged."""

import asyncio
import json
import typing

import pytest
from mockapi import ACCEPTED, VM, WS, Recorder, async_client, client

from ibee import Ibee
from ibee.core.parse_error import ParsingError
from ibee.errors import BadRequestError, ServiceUnavailableError

PLAN_CATALOG = {
    "source": "billing_v2", "product_code": "vm_shared", "sku_id": "019f25b7", "sku_code": "PERFORMA-1-2-50",
    "plan_id": "plan_default", "plan_version": 117, "price_currency": "INR",
    "billing_options": [
        {"billing_interval": "HOURLY", "committed": False, "commitment_period": "HOURLY", "unit_price_minor": 82},
        {"billing_interval": "MONTHLY", "committed": True, "commitment_period": "MONTHLY", "commitment_months": 1,
         "committed_hours": 731, "unit_price_minor": 66, "price_unit": "HOUR", "discount_percent": 19.51},
    ],
    "attached_skus": {"bandwidth": {"sku_id": "019f25b8", "sku_code": "BW-V-PF-1-2-50"}},
}
PLAN = {
    "plan_id": "019f25b7", "vm_type": "cloud", "name": "perf.1.c1.m2", "code": "PERFORMA-1-2-50", "cpu": 1, "ram_mb": 2048,
    "disk_gb": 50, "gpu_count": 0, "selectable": True, "pricing_status": "priced", "currency": "INR",
    "billing_interval": "MONTHLY", "billing_catalog": PLAN_CATALOG,
}


def billing_selection(plan: typing.Any, interval: str = "HOURLY") -> dict:
    """The README recipe: the plan's billing_catalog with the chosen billing_options entry merged in."""
    catalog = dict(plan.billing_catalog)
    option = next(o for o in catalog["billing_options"] if o["billing_interval"] == interval)
    return {**catalog, **option}


def _calls(rec: Recorder) -> typing.List[typing.Tuple[str, str]]:
    return [(r.method, r.url.path.replace("/v1/", "", 1)) for r in rec.requests]


# compute ------------------------------------------------------------------------


@pytest.mark.parametrize("interval", ["HOURLY", "MONTHLY"])
def test_vm_create_sends_the_billing_selection_built_from_the_plan(interval: str) -> None:
    rec = Recorder((200, {"plans": [PLAN], "count": 1, "vm_type": "cloud", "currency": "INR", "billing_interval": "MONTHLY"}),
                   (202, ACCEPTED))
    ibee = client(rec, workspace_id=WS)
    plan = ibee.compute_catalog.list_compute_plans(vm_type="cloud", site_id="s1").plans[0]
    selection = billing_selection(plan, interval)
    ibee.cloud_vms.create_cloud_vm(
        name="web-1", site_id="s1", plan_id=plan.plan_id, template_id="t-ubuntu", os_type="linux", os_distro="ubuntu",
        cpu=plan.cpu, ram_mb=plan.ram_mb, disk_gb=plan.disk_gb, billing_catalog=selection,
    )
    assert _calls(rec) == [("GET", "compute/plans"), ("POST", "compute/cloud-vms")]
    assert rec.requests[0].url.params["vm_type"] == "cloud"
    sent = rec.body()["billing_catalog"]
    option = next(o for o in PLAN_CATALOG["billing_options"] if o["billing_interval"] == interval)
    assert sent == {**PLAN_CATALOG, **option}
    assert sent["price_currency"] == "INR" and isinstance(sent["unit_price_minor"], int)
    assert rec.requests[1].headers["x-idempotency-key"]


def test_vm_create_makes_no_lookups_and_sends_what_it_is_given() -> None:
    rec = Recorder((400, {"error": "compute_billing_term_required", "admission_context_id": "adm-1"}))
    with pytest.raises(BadRequestError) as info:
        client(rec, workspace_id=WS).gpu_vms.create_gpu_vm(
            name="g", site_id="s1", plan_id="g1", template_id="t", os_type="linux", os_distro="ubuntu", cpu=8,
            ram_mb=32768, gpu_count=1, gpu_model="rtx5000", billing_catalog={"sku_id": "x", "sku_code": "GPU"},
        )
    assert _calls(rec) == [("POST", "compute/gpu-vms")]
    assert rec.body()["billing_catalog"] == {"sku_id": "x", "sku_code": "GPU"}
    assert info.value.code == "compute_billing_term_required"


def test_vm_list_is_one_request() -> None:
    rec = Recorder((200, [{"id": VM, "name": "web-1", "status": "running"}]))
    vms = client(rec, workspace_id=WS).cloud_vms.list_cloud_vms(limit=10, offset=20)
    assert len(rec.requests) == 1
    assert (rec.requests[0].url.params["limit"], rec.requests[0].url.params["offset"]) == ("10", "20")
    assert vms[0].id == VM


def test_vm_delete_sends_no_public_ip_action_of_its_own() -> None:
    rec = Recorder((202, ACCEPTED))
    client(rec, workspace_id=WS).cloud_vms.delete_cloud_vm(VM, public_ip_action="reserve")
    assert _calls(rec) == [("DELETE", f"compute/cloud-vms/{VM}")]
    assert rec.body() == {"public_ip_action": "reserve"}


def test_resize_sends_the_shape_only() -> None:
    rec = Recorder((202, ACCEPTED))
    client(rec, workspace_id=WS).cloud_vms.resize_cloud_vm(VM, cpu=2, ram_mb=4096)
    assert _calls(rec) == [("POST", f"compute/cloud-vms/{VM}/actions/resize")]
    assert rec.body() == {"cpu": 2, "ram_mb": 4096}
    assert rec.requests[0].headers["x-idempotency-key"]


@pytest.mark.parametrize("family", ["cloud", "gpu"])
def test_backups_disable_sends_an_empty_object(family: str) -> None:
    rec = Recorder((200, {}))
    try:
        getattr(getattr(client(rec, workspace_id=WS), f"{family}_vms"), f"disable_{family}_vm_backups")(VM, request={})
    except ParsingError:
        pass  # the mock answer is not a BackupPolicy; only the request matters
    assert _calls(rec) == [("POST", f"compute/{family}-vms/{VM}/backups/disable")]
    assert rec.requests[0].content == b"{}"


def test_recovery_storage_plans() -> None:
    plans = {"items": [], "source": "billing_v2", "product_code": "snapshot_storage", "plan_id": "plan_default",
             "plan_version": 1, "billing_interval": "MONTHLY", "currency": "INR"}
    rec = Recorder((200, plans), (200, {**plans, "product_code": "backup_storage"}))
    catalog = client(rec, workspace_id=WS).compute_catalog
    catalog.list_snapshot_storage_plans(site_id="s1")
    catalog.list_backup_storage_plans(site_id="s1")
    assert _calls(rec) == [("GET", "compute/plans/snapshot-storage"), ("GET", "compute/plans/backup-storage")]


# object storage -----------------------------------------------------------------


def test_s3_credential_revoke_and_delete() -> None:
    rec = Recorder((200, {"success": True, "message": "revoked"}), (200, {"success": True, "message": "deleted"}))
    storage = client(rec, workspace_id=WS).object_storage
    storage.revoke_s3credential("AK1")
    storage.delete_s3credential("AK1")
    assert _calls(rec) == [("POST", "object-storage/credentials/AK1/revoke"), ("DELETE", "object-storage/credentials/AK1")]


def test_bucket_cors_write_is_snake_case_and_an_s3_cased_read_is_not_rewritten() -> None:
    s3_cased = {"rules": [{"AllowedOrigins": ["*"], "AllowedMethods": ["GET"]}]}
    rec = Recorder((200, {"detail": "ok"}), (200, s3_cased))
    storage = client(rec, workspace_id=WS).object_storage
    storage.set_bucket_cors("b1", rules=[{"allowed_origins": ["*"], "allowed_methods": ["GET"], "max_age_seconds": 60}])
    assert json.loads(rec.requests[0].content) == {"rules": [{"allowed_origins": ["*"], "allowed_methods": ["GET"], "max_age_seconds": 60}]}
    with pytest.raises(ParsingError) as info:
        storage.get_bucket_cors("b1")
    assert (info.value.status_code, info.value.body) == (200, s3_cased)
    assert _calls(rec) == [("PUT", "object-storage/buckets/b1/cors"), ("GET", "object-storage/buckets/b1/cors")]


def test_custom_domain_refusal_is_relayed_unchanged() -> None:
    body = {"detail": "CNAME for files.example.com does not point to b1.cdn.ibee.ai"}
    rec = Recorder((400, body, {"x-request-id": "req-7"}))
    with pytest.raises(BadRequestError) as info:
        client(rec, workspace_id=WS).object_storage.add_bucket_custom_domain("b1", domain="files.example.com")
    assert (info.value.body, info.value.request_id) == (body, "req-7")
    assert rec.body() == {"domain": "files.example.com"}


# networking ---------------------------------------------------------------------


def test_nat_gateway_public_ip_and_delete() -> None:
    nat = {"nat_gateway_id": "n1", "vpc_id": "v1", "site_id": "s1", "name": "n", "public_ip_id": "p2",
           "public_ip": "203.0.113.7", "status": "active"}
    rec = Recorder((200, nat), (204, ""))
    vpcs = client(rec, workspace_id=WS).vpcs
    vpcs.update_nat_gateway_public_ip("v1", "n1", reserved_public_ip_id="p2")
    vpcs.delete_nat_gateway("v1", "n1", public_ip_action="release")
    assert _calls(rec) == [("PUT", "networking/vpcs/v1/nat-gateways/n1/public-ip"), ("DELETE", "networking/vpcs/v1/nat-gateways/n1")]
    assert [rec.body(0), rec.body(1)] == [{"reserved_public_ip_id": "p2"}, {"public_ip_action": "release"}]


def test_reserved_ip_convert_and_attach_direct() -> None:
    rec = Recorder((200, {}))
    ips = client(rec, workspace_id=WS).reserved_ips
    for call in (lambda: ips.convert_reserved_ip(vm_id=VM, site_id="s1"), lambda: ips.attach_reserved_ip_direct("r1", vm_id=VM)):
        try:
            call()
        except ParsingError:
            pass
    assert _calls(rec) == [("POST", "networking/reserved-ips/convert"), ("POST", "networking/reserved-ips/r1/attach-direct")]


# removed in 0.6.2 ---------------------------------------------------------------

REMOVED = {
    "cloud_vms": ["resize_cloud_vm_plan", "resize_cloud_vm_root_disk", "create_cloud_vm_backup_run",
                  "reschedule_cloud_vm_backup", "acknowledge_cloud_vm_mount_guidance"],
    "gpu_vms": ["resize_gpu_vm_plan", "resize_gpu_vm_root_disk", "create_gpu_vm_backup_run",
                "reschedule_gpu_vm_backup", "acknowledge_gpu_vm_mount_guidance"],
    "block_storage": ["attach_block_volume", "detach_block_volume"],
    "cdn": ["generate_cdn_url"],
    "vpcs": ["update_vpc_subnet"],
    "secret_store": ["patch_secret_value", "update_secret_identity", "update_secret_identity_scope", "update_secret_store"],
    "container_registry": ["empty_container_registry"],
}


def test_removed_operations_are_gone() -> None:
    ibee = Ibee(token="t", base_url="https://api.example.test/v1")
    for namespace, methods in REMOVED.items():
        for method in methods:
            assert not hasattr(getattr(ibee, namespace), method), f"{namespace}.{method}"
    assert not hasattr(ibee, "billing") and not hasattr(ibee, "vm_console")


def test_async_create_is_sent_once_with_a_key() -> None:
    rec = Recorder((503, {"detail": "busy"}), (202, ACCEPTED))

    async def run() -> None:
        with pytest.raises(ServiceUnavailableError):
            await async_client(rec, workspace_id=WS).cloud_vms.create_cloud_vm(
                name="a", site_id="s1", plan_id="p", template_id="t", os_type="linux", os_distro="ubuntu", cpu=1,
                ram_mb=2048, billing_catalog={**PLAN_CATALOG, **PLAN_CATALOG["billing_options"][0]},
            )

    asyncio.run(run())
    assert len(rec.requests) == 1 and rec.requests[0].headers["x-idempotency-key"]
