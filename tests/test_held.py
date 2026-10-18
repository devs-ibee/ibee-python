"""ibee.held: the temporary behaviours send the same requests as 0.4.2 (bodies captured from 0.4.2)."""

import asyncio
import json
import typing

import httpx
import pytest
from mockapi import ACCEPTED, VM, WS, async_client, client

OPTIONS = [
    {"billing_interval": "HOURLY", "unit_price_minor": 100, "price_unit": "hour"},
    {"billing_interval": "MONTHLY", "unit_price_minor": 7000.0, "committed": 1, "commitment_months": 1.0, "discount_percent": 5},
]
VOLUME = "fedcba9876543210fedcba98"
HOURLY = {
    "attached_skus": {}, "billing_interval": "HOURLY", "commitment_period": "HOURLY", "committed": False,
    "price_unit": "hour", "sku_code": "VM-2C", "sku_id": 11, "unit_price_minor": 100,
}
MONTHLY = {
    "attached_skus": {}, "billing_interval": "MONTHLY", "commitment_months": 1, "commitment_period": "MONTHLY",
    "committed": True, "discount_percent": 5, "sku_code": "VM-2C", "sku_id": 11, "unit_price_minor": 7000,
}
LICENSE = {"sku_id": 51, "sku_code": "WIN-LIC", "billing_options": OPTIONS}


def _plan(plan_id: str, vm_type: str, **extra: typing.Any) -> dict:
    plan = {
        "plan_id": plan_id, "vm_type": vm_type, "name": "n", "code": "c", "cpu": 2, "ram_mb": 2048, "disk_gb": 40,
        "gpu_count": 0, "selectable": False, "pricing_status": "unpriced", "currency": "INR", "billing_interval": "HOURLY",
        "billing_catalog": {"sku_id": 11, "sku_code": "VM-2C", "billing_options": OPTIONS},
    }
    return {**plan, **extra}


def _image(template_id: str, os_type: str, vm_types: list) -> dict:
    return {
        "template_id": template_id, "name": template_id, "os_distro": os_type == "windows" and "windows" or "ubuntu",
        "os_type": os_type, "architecture": "x86_64", "size_bytes": 1, "gpu_compatible": True,
        "compatible_vm_types": vm_types, "site_ids": ["s1"],
    }


class FakeApi:
    """Answers the lookups the held code makes and records every other request."""

    def __init__(self, vm: typing.Optional[dict] = None, vm_count: int = 0) -> None:
        self.vm = vm or {"id": VM, "name": "web-1", "status": "running", "cpu": 2, "os_type": "linux", "os_distro": "ubuntu",
                         "site_id": "s1", "public_ip": "203.0.113.5"}
        self.vm_count = vm_count
        self.sent: typing.List[dict] = []
        self.reads: typing.List[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        path, query = request.url.path.replace("/v1/", "", 1), dict(request.url.params)
        if request.method == "GET":
            self.reads.append(path)
            return httpx.Response(200, json=self.read(path, query))
        self.sent.append({"method": request.method, "path": path, "body": json.loads(request.content) if request.content else None})
        if "nat-gateways" in path:
            return httpx.Response(201, json={"nat_gateway_id": "n", "vpc_id": "v", "site_id": "s1", "name": "n",
                                             "public_ip_id": "p", "public_ip": "203.0.113.7", "status": "creating"})
        return httpx.Response(202, json=ACCEPTED)

    def read(self, path: str, query: dict) -> typing.Any:
        if path == "compute/plans":
            plans = [_plan("p1", "cloud"), _plan("p2", "cloud", cpu=4, ram_mb=8192, disk_gb=80)]
            if query["vm_type"] == "gpu":
                plans = [_plan("g1", "gpu", gpu_count=1, gpu_model="L4", billing_catalog={"sku_id": 21, "sku_code": "GPU-L4", "billing_options": OPTIONS})]
            return {"plans": plans, "count": len(plans), "vm_type": query["vm_type"], "currency": "INR", "billing_interval": "HOURLY"}
        if path == "compute/images":
            images = [_image("t-ubuntu", "linux", ["cloud", "gpu"]), _image("t-win", "windows", ["cloud"])]
            return {"images": images, "count": 2, "vm_type": query["vm_type"]}
        if path.endswith(VM):
            return self.vm
        if path == f"block-storage/volumes/{VOLUME}":
            return {"id": VOLUME, "name": "d", "size_gb": 20, "state": "available", "volume_class": "standard", "replica_count": 1,
                    "attachments": [], "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
                    "billing_catalog": {"sku_id": 31, "sku_code": "BLOCK-STD"}}
        if path.startswith("networking/reserved-ips/"):
            return {"public_ip_id": "rip-1", "address": "203.0.113.9", "site_id": "s1", "status": "reserved",
                    "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
                    "billing_catalog": {"sku_id": 41, "sku_code": "RESERVED-IP"}}
        if path in ("compute/cloud-vms", "networking/firewall-groups"):
            offset, limit = int(query.get("offset", 0)), int(query.get("limit", 10))
            return [{"id": f"vm{i}", "firewall_group_id": f"fw{i}", "organization_id": "o", "workspace_id": WS, "name": "x",
                     "is_default": False, "status": "active", "rules": [], "created_at": "2026-01-01T00:00:00Z",
                     "updated_at": "2026-01-01T00:00:00Z"} for i in range(offset, min(offset + limit, self.vm_count))]
        raise AssertionError(f"unexpected read {path}")

    @property
    def body(self) -> typing.Any:
        assert len(self.sent) == 1
        return self.sent[0]["body"]


# 1. VM create -------------------------------------------------------------------


def test_create_fills_the_shape_and_merges_the_default_hourly_term() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.create_cloud_vm(name="a", plan_id="p1", template_id="t-ubuntu", site_id="s1")
    assert api.body == {
        "billing_catalog": HOURLY, "cpu": 2, "disk_gb": 40, "name": "a", "os_distro": "ubuntu", "os_type": "linux",
        "plan_id": "p1", "ram_mb": 2048, "site_id": "s1", "template_id": "t-ubuntu",
    }


def test_create_with_a_term_and_a_plan_that_is_not_selectable_is_sent() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.create_cloud_vm(
        name="a", plan_id="p2", template_id="t-ubuntu", site_id="s1", billing_term="monthly", tags=["x"]
    )
    assert api.body["billing_catalog"] == MONTHLY
    assert (api.body["cpu"], api.body["ram_mb"], api.body["disk_gb"], api.body["tags"]) == (4, 8192, 80, ["x"])


def test_create_windows_adds_the_licence_per_vcpu() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.create_cloud_vm(
        name="w", plan_id="p1", template_id="t-win", site_id="s1", windows_license=LICENSE, billing_term="MONTHLY"
    )
    licence = {k: v for k, v in MONTHLY.items() if k != "attached_skus"}
    licence.update(sku_id=51, sku_code="WIN-LIC", component_key="windows_license", os_type="windows", os_family="windows",
                   quantity_basis="VCPU", quantity=2)
    assert api.body["billing_catalog"] == {**MONTHLY, "attached_skus": {"windows_license": licence}}
    assert (api.body["os_type"], api.body["os_distro"]) == ("windows", "windows")


def test_gpu_create_keeps_the_plan_catalog_without_a_term() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).gpu_vms.create_gpu_vm(name="g", plan_id="g1", template_id="t-ubuntu", site_id="s1")
    assert api.body["billing_catalog"] == {"attached_skus": {}, "sku_code": "GPU-L4", "sku_id": 21}
    assert (api.body["gpu_count"], api.body["gpu_model"]) == (1, "L4")


def test_explicit_create_makes_no_lookups() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.create_cloud_vm(
        name="e", plan_id="p1", template_id="t-ubuntu", cpu=2, ram_mb=2048, disk_gb=40, os_type="linux", os_distro="ubuntu",
        billing_catalog={"sku_id": 11, "sku_code": "VM-2C", "billing_options": OPTIONS}, billing_term="HOURLY",
    )
    assert api.reads == []
    assert api.body["billing_catalog"] == HOURLY


def test_reserved_ip_without_a_vpc_is_sent_with_its_sku() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.create_cloud_vm(
        name="r", plan_id="p1", template_id="t-ubuntu", site_id="s1", network_connectivity="public_ip", reserved_public_ip_id="rip-1"
    )
    assert api.body["billing_catalog"]["attached_skus"] == {"reserved_ip": {"sku_id": 41, "sku_code": "RESERVED-IP"}}
    assert "vpc_id" not in api.body


def test_unknown_plan_is_left_to_the_server() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.create_cloud_vm(name="a", plan_id="nope", template_id="t-ubuntu")
    assert api.body["plan_id"] == "nope" and api.body["cpu"] is None and api.body["billing_catalog"] is None


# 2. VM delete -------------------------------------------------------------------


def test_delete_releases_an_auto_assigned_public_ip_by_default() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.delete_cloud_vm(VM)
    assert api.body == {"public_ip_action": "release"}


def test_delete_without_a_public_ip_sends_no_choice() -> None:
    api = FakeApi(vm={"id": VM, "name": "web-1", "public_ip": None})
    client(api, workspace_id=WS).cloud_vms.delete_cloud_vm(VM)
    assert "public_ip_action" not in (api.body or {})


def test_delete_reserve_labels_the_address_with_the_vm_name() -> None:
    api = FakeApi()
    sku = {"sku_id": 41, "sku_code": "RESERVED-IP"}
    client(api, workspace_id=WS).gpu_vms.delete_gpu_vm(VM, public_ip_action="reserve", reserved_ip_billing_catalog=sku)
    assert api.body == {"public_ip_action": "reserve", "reserved_ip_billing_catalog": sku, "reserved_ip_label": "web-1"}


def test_delete_with_an_explicit_release_makes_no_lookup() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.delete_cloud_vm(VM, public_ip_action="release")
    assert api.reads == [] and api.body == {"public_ip_action": "release"}


# 3. billing_catalog on attach, resize and NAT ------------------------------------


def test_attach_reads_the_sku_from_the_volume() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.attach_cloud_vm_volume(VM, volume_id=VOLUME)
    assert api.body == {"volume_id": VOLUME, "billing_catalog": {"sku_id": 31, "sku_code": "BLOCK-STD"}}


def test_resize_with_a_plan_sends_its_shape_and_sku() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.resize_cloud_vm(VM, plan_id="p2")
    assert api.body == {"billing_catalog": HOURLY, "cpu": 4, "disk_gb": 80, "ram_mb": 8192}
    assert "resize/precheck" not in " ".join(api.reads)


def test_resize_plan_with_a_term() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.resize_cloud_vm_plan(VM, plan_id="p2", billing_term="MONTHLY")
    assert api.body == {"billing_catalog": MONTHLY, "cpu": 4, "ram_mb": 8192}


def test_plain_resize_is_sent_as_given() -> None:
    api = FakeApi()
    client(api, workspace_id=WS).cloud_vms.resize_cloud_vm(VM, cpu=4)
    assert api.reads == [] and api.body == {"cpu": 4}


def test_root_disk_and_backup_policy_catalogs_are_passed_through() -> None:
    api = FakeApi()
    sku = {"sku_id": 71, "sku_code": "BACKUP-STD"}
    vms = client(api, workspace_id=WS).cloud_vms
    vms.resize_cloud_vm_root_disk(VM, new_size_gb=100, billing_catalog=sku)
    try:
        vms.update_cloud_vm_backup_policy(VM, retention_days=7, billing_catalog=sku)
    except Exception:
        pass  # the mock answer does not parse as a policy; only the request matters
    assert api.sent[0]["body"] == {"new_size_gb": 100, "billing_catalog": sku}
    assert api.sent[1]["body"] == {"retention_days": 7, "billing_catalog": sku}


def test_nat_catalogs_are_passed_through() -> None:
    api = FakeApi()
    sku = {"sku_id": 61, "sku_code": "NAT-GATEWAY"}
    vpcs = client(api, workspace_id=WS).vpcs
    vpcs.create_nat_gateway("vpc-1", name="n", billing_catalog=sku)
    vpcs.delete_nat_gateway("vpc-1", "nat-1", public_ip_action="reserve", billing_catalog=sku)
    assert api.sent[0]["body"] == {"name": "n", "billing_catalog": sku}
    assert api.sent[1]["body"] == {"public_ip_action": "reserve", "billing_catalog": sku}


# 4. all pages -------------------------------------------------------------------


def test_lists_return_every_page_unless_limit_or_offset_is_given() -> None:
    api = FakeApi(vm_count=150)
    ibee = client(api, workspace_id=WS)
    assert len(ibee.cloud_vms.list_cloud_vms()) == 150
    assert len(ibee.firewalls.list_firewall_groups()) == 150
    assert len(ibee.cloud_vms.list_cloud_vms(limit=10)) == 10


# async --------------------------------------------------------------------------


@pytest.mark.parametrize("family", ["cloud", "gpu"])
def test_async_create_delete_and_list(family: str) -> None:
    api = FakeApi(vm_count=120)

    async def run() -> int:
        vms = getattr(async_client(api, workspace_id=WS), f"{family}_vms")
        plan = "p1" if family == "cloud" else "g1"
        await getattr(vms, f"create_{family}_vm")(name="a", plan_id=plan, template_id="t-ubuntu", site_id="s1")
        await getattr(vms, f"delete_{family}_vm")(VM)
        await getattr(vms, f"attach_{family}_vm_volume")(VM, volume_id=VOLUME)
        return len(await vms.list_cloud_vms()) if family == "cloud" else 120

    assert asyncio.run(run()) == 120
    assert api.sent[0]["body"]["billing_catalog"]["sku_code"] in ("VM-2C", "GPU-L4")
    assert api.sent[1]["body"] == {"public_ip_action": "release"}
    assert api.sent[2]["body"]["billing_catalog"] == {"sku_id": 31, "sku_code": "BLOCK-STD"}
