"""0.4.0 portal-parity VM lifecycle: create, delete, power, access, resize, metrics, console."""

from __future__ import annotations

import asyncio

import pytest

from _compute_fixtures import (
    ACCEPTED,
    OP,
    VM,
    WS,
    Router,
    async_client,
    async_transport,
    image,
    plan,
    sync_client,
    vm,
)
from ibee import IbeeValidationError
from ibee.errors import BillingDeniedError, ConflictError, ResizeBlockedError, ServiceUnavailableError


def _catalog_router(vm_type: str = "cloud", plans=None, images=None, create=(202, ACCEPTED)) -> Router:
    router = Router()
    router.add("GET", "compute/plans", (200, {"plans": plans if plans is not None else [plan(vm_type=vm_type)]}))
    router.add("GET", "compute/images", (200, {"images": images if images is not None else [image(vm_type=vm_type)]}))
    router.add("POST", f"compute/{vm_type}-vms", create)
    return router


def _create(client, **overrides):
    kwargs = dict(workspace_id=WS, name=" web-1 ", site_id="site-1", plan_id="plan-1", template_id="tmpl-ubuntu")
    kwargs.update(overrides)
    return client.cloud_vms.create_cloud_vm(**kwargs)


# create ---------------------------------------------------------------------------


def test_create_resolves_plan_and_image_and_builds_hourly_billing_catalog() -> None:
    router = _catalog_router()
    result = _create(sync_client(router), ssh_keys=["ssh-ed25519 AAAAC3Nza user@host", "ssh-ed25519 AAAAC3Nza user@host"])
    assert result.operation_id == OP
    assert router.calls() == [("GET", "compute/plans"), ("GET", "compute/images"), ("POST", "compute/cloud-vms")]
    assert dict(router.requests[0].url.params) == {"workspace_id": WS, "vm_type": "cloud", "site_id": "site-1"}
    body = router.body("POST", "compute/cloud-vms")
    assert body["name"] == "web-1"
    assert (body["cpu"], body["ram_mb"], body["disk_gb"]) == (2, 4096, 50)
    assert (body["os_type"], body["os_distro"], body["template_id"], body["plan_id"]) == ("linux", "ubuntu", "tmpl-ubuntu", "plan-1")
    catalog = body["billing_catalog"]
    assert catalog["sku_code"] == "VM-STD-2-4"
    assert catalog["billing_interval"] == "HOURLY" and catalog["unit_price_minor"] == 250 and catalog["committed"] is False
    assert "billing_options" not in catalog
    assert catalog["attached_skus"] == {"bandwidth": {"sku_id": 9, "sku_code": "BW-1TB"}}
    assert body["ssh_keys"] == ["ssh-ed25519 AAAAC3Nza user@host"]
    for forbidden in ("created_by", "created_by_name", "created_by_email", "organization_id", "workspace_id"):
        assert forbidden not in body
    assert router.last("POST", "compute/cloud-vms").headers["x-idempotency-key"].startswith("cloud-vm-create-web-1-")


def test_create_monthly_term_applies_the_plan_option() -> None:
    router = _catalog_router()
    _create(sync_client(router), billing_term="monthly")
    catalog = router.body("POST", "compute/cloud-vms")["billing_catalog"]
    assert catalog["billing_interval"] == "MONTHLY"
    assert catalog["committed"] is True and catalog["commitment_period"] == "MONTHLY"
    assert (catalog["commitment_months"], catalog["committed_hours"], catalog["discount_percent"]) == (1, 730, 10)
    assert catalog["unit_price_minor"] == 150000 and catalog["price_unit"] == "MONTH"


def test_create_rejects_unsupported_term_before_posting() -> None:
    router = _catalog_router()
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(router), billing_term="YEARLY")
    assert str(info.value) == "Selected plan does not support yearly billing"
    assert ("POST", "compute/cloud-vms") not in router.calls()


def test_create_rejects_bad_local_input_without_any_request() -> None:
    router = _catalog_router()
    client = sync_client(router)
    cases = [
        dict(name="web_1"),
        dict(name="   "),
        dict(site_id=None),
        dict(billing_term="WEEKLY"),
        dict(ssh_keys=["-----BEGIN OPENSSH PRIVATE KEY-----"]),
        dict(ssh_keys=["ssh-dss AAAA"]),
        dict(ssh_keys=["ssh-rsa AAAA\nssh-rsa BBBB"]),
        dict(firewall_group_ids=["fw-1", "fw-2"]),
        dict(network_connectivity="nat"),
        dict(vpc_id="vpc-1"),
        dict(reserved_public_ip_id="rip-1"),
        dict(vpc_id="vpc-1", subnet_id="s-1", network_connectivity="private", reserved_public_ip_id="rip-1"),
    ]
    for overrides in cases:
        with pytest.raises(IbeeValidationError):
            _create(client, **overrides)
    assert router.requests == []


def test_create_checks_plan_and_shape() -> None:
    client = sync_client(_catalog_router(plans=[plan(selectable=False)]))
    with pytest.raises(IbeeValidationError) as info:
        _create(client)
    assert info.value.code == "plan_not_selectable"
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(_catalog_router(plans=[plan(pricing_status="unpriced")])))
    assert info.value.code == "plan_not_selectable"
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(_catalog_router()), cpu=4)
    assert info.value.code == "shape_mismatch" and info.value.field == "cpu"
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(_catalog_router()), plan_id="missing")
    assert info.value.code == "plan_not_found"
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(_catalog_router(images=[image(site_ids=["site-2"])])))
    assert info.value.code == "image_not_compatible"
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(_catalog_router(plans=[plan(billing_catalog={"sku_id": 1, "sku_code": "ROOTDISK-50"})])))
    assert "root disk" in str(info.value)


def test_windows_create_requires_and_prices_the_licence() -> None:
    windows = [image(os_type="windows", os_distro="windows")]
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(_catalog_router(images=windows)))
    assert info.value.code == "windows_license_required"

    licence = {
        "sku_id": 77,
        "sku_code": "win-lic",
        "billing_options": [
            {"billing_interval": "HOURLY", "unit_price_minor": 10},
            {"billing_interval": "MONTHLY", "unit_price_minor": 5000, "committed": True},
        ],
    }
    router = _catalog_router(images=windows)
    _create(sync_client(router), windows_license=licence, billing_term="MONTHLY")
    attached = router.body("POST", "compute/cloud-vms")["billing_catalog"]["attached_skus"]["windows_license"]
    assert attached["sku_code"] == "WIN-LIC" and attached["billing_interval"] == "MONTHLY"
    assert (attached["quantity_basis"], attached["quantity"], attached["component_key"]) == ("VCPU", 2, "windows_license")
    assert attached["os_type"] == attached["os_family"] == "windows"

    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(_catalog_router()), windows_license=licence)
    assert info.value.code == "windows_license_not_allowed"
    with pytest.raises(IbeeValidationError):
        _create(sync_client(_catalog_router(images=windows)), windows_license=licence, billing_term="YEARLY")


def test_vpc_placement_rules_and_reserved_ip_sku() -> None:
    def router_for(vpc: dict, reserved: dict | None = None) -> Router:
        router = _catalog_router()
        router.add("GET", "networking/vpcs/vpc-1", (200, vpc))
        router.add("GET", "networking/vpcs/vpc-1/subnets/sub-1", (200, {"subnet_id": "sub-1", "vpc_id": "vpc-1"}))
        if reserved is not None:
            router.add("GET", "networking/reserved-ips/rip-1", (200, reserved))
        return router

    network = dict(vpc_id="vpc-1", subnet_id="sub-1")
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(router_for({"site_id": "site-1", "connectivity_type": "public"})), **network, network_connectivity="nat")
    assert str(info.value) == "Select a NAT Gateway VPC for managed outbound internet"
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(router_for({"site_id": "site-2", "connectivity_type": "nat"})), **network, network_connectivity="nat")
    assert info.value.code == "vpc_site_mismatch"
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(router_for({"site_id": "site-1", "connectivity_type": "private"})), **network, network_connectivity="public_ip")
    assert info.value.code == "reserved_ip_required"
    with pytest.raises(IbeeValidationError) as info:
        _create(
            sync_client(router_for({"connectivity_type": "private"}, {"site_id": "site-1", "vm_id": VM, "billing_catalog": {"sku_id": 1, "sku_code": "RIP"}})),
            **network,
            network_connectivity="public_ip",
            reserved_public_ip_id="rip-1",
        )
    assert info.value.code == "reserved_ip_attached"

    router = router_for({"connectivity_type": "private"}, {"site_id": "site-1", "billing_catalog": {"sku_id": 3, "sku_code": "rip-std"}})
    _create(sync_client(router), **network, network_connectivity="public_ip", reserved_public_ip_id="rip-1", firewall_group_ids=["fw-1"])
    body = router.body("POST", "compute/cloud-vms")
    assert body["vpc_attachment_mode"] == "primary"
    assert (body["vpc_id"], body["subnet_id"], body["network_connectivity"], body["reserved_public_ip_id"]) == (
        "vpc-1",
        "sub-1",
        "public_ip",
        "rip-1",
    )
    assert body["firewall_group_id"] == "fw-1" and body["firewall_group_ids"] == ["fw-1"]
    assert body["billing_catalog"]["attached_skus"]["reserved_ip"] == {"sku_id": 3, "sku_code": "RIP-STD"}


def test_gpu_create_takes_gpu_fields_from_plan_and_keeps_catalog_unmodified() -> None:
    router = _catalog_router("gpu")
    sync_client(router).gpu_vms.create_gpu_vm(
        workspace_id=WS, name="trainer", site_id="site-1", plan_id="plan-1", template_id="tmpl-ubuntu"
    )
    body = router.body("POST", "compute/gpu-vms")
    assert (body["gpu_count"], body["gpu_model"], body["cpu"]) == (1, "L40S", 2)
    assert "billing_interval" not in body["billing_catalog"]  # portal GPU deploy sends the plan SKU as-is
    with pytest.raises(IbeeValidationError) as info:
        sync_client(_catalog_router("gpu")).gpu_vms.create_gpu_vm(
            workspace_id=WS, name="trainer", site_id="site-1", plan_id="plan-1", template_id="tmpl-ubuntu", gpu_model="H100"
        )
    assert info.value.field == "gpu_model"
    with pytest.raises(IbeeValidationError) as info:
        sync_client(_catalog_router("gpu", images=[image(vm_type="gpu", os_type="windows")])).gpu_vms.create_gpu_vm(
            workspace_id=WS, name="trainer", site_id="site-1", plan_id="plan-1", template_id="tmpl-ubuntu"
        )
    assert info.value.field == "os_type"


def test_create_preflight_billing_denied_stops_before_create() -> None:
    router = _catalog_router()
    router.add(
        "POST",
        "billing/resource-eligibility",
        (200, {"organization_id": "org", "allowed": False, "reason": "insufficient_balance", "sku_code": "VM-STD-2-4"}),
    )
    with pytest.raises(BillingDeniedError) as info:
        _create(sync_client(router), preflight_billing=True)
    assert info.value.topup_allowed is True
    assert ("POST", "compute/cloud-vms") not in router.calls()
    eligibility = router.body("POST", "billing/resource-eligibility")
    assert eligibility == {}


@pytest.mark.parametrize("family", ["cloud", "gpu"])
@pytest.mark.parametrize("term", ["HOURLY", "MONTHLY"])
@pytest.mark.parametrize("asynchronous", [False, True])
def test_vm_preflight_leaves_selected_term_affordability_to_upstream(family, term, asynchronous):
    router = _catalog_router(family)
    router.add("POST", "billing/resource-eligibility", (200, {
        "organization_id": "org", "allowed": True, "reason": "status_only",
        "effective_balance_minor": 3500,
    }))
    def create(client):
        resource = getattr(client, f"{family}_vms")
        method = getattr(resource, f"create_{family}_vm")
        return method(workspace_id=WS, name="test", site_id="site-1", plan_id="plan-1",
                      template_id="tmpl-ubuntu", billing_term=term, preflight_billing=True)
    if asynchronous:
        async def run():
            async with async_transport(router) as transport:
                return await create(async_client(router, transport))
        result = asyncio.run(run())
    else:
        result = create(sync_client(router))
    assert result.operation_id == OP
    assert router.body("POST", "billing/resource-eligibility") == {}
    assert router.body("POST", f"compute/{family}-vms")["billing_catalog"]["billing_interval"] == term


def test_account_preflight_does_not_override_upstream_create_denial():
    router = _catalog_router(create=(402, {
        "error": "billing_denied", "billing_reason": "insufficient_balance",
        "billing_sku_code": "VM-STD-2-4", "admission_context_id": "adm_upstream",
    }))
    router.add("POST", "billing/resource-eligibility", (200, {
        "organization_id": "org", "allowed": True, "reason": "status_only",
    }))
    with pytest.raises(BillingDeniedError) as info:
        _create(sync_client(router), preflight_billing=True)
    assert info.value.admission_context_id == "adm_upstream"
    assert router.calls().count(("POST", "compute/cloud-vms")) == 1


def test_create_is_not_retried_and_explicit_mode_is_one_request() -> None:
    router = Router().add("POST", "compute/cloud-vms", (503, {"detail": "workflow engine unavailable"}))
    client = sync_client(router)
    client._client_wrapper.httpx_client.base_max_retries = 3
    with pytest.raises(ServiceUnavailableError):
        _create(
            client,
            cpu=2,
            ram_mb=4096,
            disk_gb=50,
            os_type="linux",
            os_distro="ubuntu",
            billing_catalog={"sku_id": 1, "sku_code": "VM-1"},
        )
    assert router.calls() == [("POST", "compute/cloud-vms")]


# list / get ------------------------------------------------------------------------


def test_list_all_pages_and_maps_mongo_ids() -> None:
    first = [{"_id": f"{i:024x}", "name": f"vm-{i}"} for i in range(2)]
    router = Router().add("GET", "compute/cloud-vms", (200, first), (200, []))
    vms = sync_client(router).cloud_vms.list_all_cloud_vms(workspace_id=WS, page_size=2, sort_by="name")
    assert [item.id for item in vms] == [f"{0:024x}", f"{1:024x}"]
    assert dict(router.requests[1].url.params) == {"workspace_id": WS, "limit": "2", "offset": "2", "sort_by": "name"}


def test_vm_ids_are_checked_before_any_request() -> None:
    router = Router()
    client = sync_client(router)
    for call in (
        lambda: client.gpu_vms.get_gpu_vm("all", workspace_id=WS),
        lambda: client.cloud_vms.start_cloud_vm("vm-1", workspace_id=WS),
        lambda: client.cloud_vms.get_cloud_vm_metrics("../x", workspace_id=WS),
        lambda: client.cloud_vms.get_compute_operation("op-1", workspace_id=WS),
        lambda: client.vm_console.create_vm_console_session(workspace_id=WS, vm_id="x"),
    ):
        with pytest.raises(IbeeValidationError):
            call()
    assert router.requests == []


# delete ----------------------------------------------------------------------------


def test_delete_defaults_to_releasing_an_auto_assigned_public_ip() -> None:
    router = Router().add("GET", f"compute/cloud-vms/{VM}", (200, vm(public_ip="203.0.113.5")))
    router.add("DELETE", f"compute/cloud-vms/{VM}", (202, ACCEPTED))
    sync_client(router).cloud_vms.delete_cloud_vm(VM, workspace_id=WS)
    assert router.body("DELETE", f"compute/cloud-vms/{VM}") == {"public_ip_action": "release"}


def test_delete_reserve_needs_sku_and_defaults_label() -> None:
    def router() -> Router:
        r = Router().add("GET", f"compute/cloud-vms/{VM}", (200, vm(public_ip="203.0.113.5")))
        return r.add("DELETE", f"compute/cloud-vms/{VM}", (202, ACCEPTED))

    with pytest.raises(IbeeValidationError) as info:
        sync_client(router()).cloud_vms.delete_cloud_vm(VM, workspace_id=WS, public_ip_action="reserve")
    assert info.value.code == "reserved_ip_billing_catalog_required"
    r = router()
    sync_client(r).cloud_vms.delete_cloud_vm(
        VM, workspace_id=WS, public_ip_action="reserve", reserved_ip_billing_catalog={"sku_id": 4, "sku_code": "rip"}
    )
    assert r.body("DELETE", f"compute/cloud-vms/{VM}") == {
        "public_ip_action": "reserve",
        "reserved_ip_billing_catalog": {"sku_id": 4, "sku_code": "RIP"},
        "reserved_ip_label": "web-1",
    }


def test_delete_without_auto_ip_sends_no_body_and_checks_state() -> None:
    router = Router().add("GET", f"compute/gpu-vms/{VM}", (200, vm(public_ip="1.2.3.4", reserved_public_ip_id="rip-1")))
    router.add("DELETE", f"compute/gpu-vms/{VM}", (202, ACCEPTED))
    sync_client(router).gpu_vms.delete_gpu_vm(VM, workspace_id=WS)
    assert router.last("DELETE", f"compute/gpu-vms/{VM}").content == b""
    with pytest.raises(IbeeValidationError):
        sync_client(router).gpu_vms.delete_gpu_vm(VM, workspace_id=WS, public_ip_action="reserve")
    busy = Router().add("GET", f"compute/cloud-vms/{VM}", (200, vm(status="deleting")))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(busy).cloud_vms.delete_cloud_vm(VM, workspace_id=WS)
    assert info.value.code == "invalid_vm_state"


# power / access ---------------------------------------------------------------------


def test_power_actions_check_state_when_asked() -> None:
    router = Router().add("GET", f"compute/cloud-vms/{VM}", (200, vm(status="running")))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/stop", (202, ACCEPTED))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.start_cloud_vm(VM, workspace_id=WS, check_state=True)
    client.cloud_vms.stop_cloud_vm(VM, workspace_id=WS, check_state=True)
    assert router.calls()[-1] == ("POST", f"compute/cloud-vms/{VM}/actions/stop")


def test_access_update_rules() -> None:
    def router(record: dict) -> Router:
        r = Router().add("GET", f"compute/cloud-vms/{VM}", (200, record))
        return r.add("PATCH", f"compute/cloud-vms/{VM}/actions/access", (202, ACCEPTED))

    client = sync_client(router(vm()))
    for kwargs in (
        {},
        {"ssh_keys": ["ssh-ed25519 AAAA"]},
        {"ssh_key_mode": "add"},
        {"new_password": " short  "},
        {"new_password": "long-enough\npassword"},
    ):
        with pytest.raises(IbeeValidationError):
            client.cloud_vms.update_cloud_vm_access(VM, workspace_id=WS, **kwargs)
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router(vm(os_type="windows"))).cloud_vms.update_cloud_vm_access(VM, workspace_id=WS, new_password="Password-1")
    assert info.value.code == "vm_not_linux"
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router(vm(status="stopped"))).cloud_vms.update_cloud_vm_access(VM, workspace_id=WS, new_password="Password-1")
    assert info.value.code == "invalid_vm_state"
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router(vm())).cloud_vms.update_cloud_vm_access(VM, workspace_id=WS, password_auth_enabled=False)
    assert info.value.code == "ssh_key_required"
    keyed = vm(ssh_keys=["ssh-ed25519 AAAA a"], ssh_password_auth_enabled=False)
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router(keyed)).cloud_vms.update_cloud_vm_access(
            VM, workspace_id=WS, ssh_key_mode="remove", ssh_keys=["ssh-ed25519 AAAA a"]
        )
    assert info.value.code == "confirmation_required"

    r = router(vm())
    sync_client(r).cloud_vms.update_cloud_vm_access(VM, workspace_id=WS, new_password="Password-1")
    assert r.body("PATCH", f"compute/cloud-vms/{VM}/actions/access") == {"admin_username": "ubuntu", "new_password": "Password-1"}


# resize -----------------------------------------------------------------------------


def _resize_router(decision: str = "in_place", record: dict | None = None, vm_type: str = "cloud") -> Router:
    router = Router().add("GET", f"compute/{vm_type}-vms/{VM}", (200, record or vm()))
    router.add("GET", "compute/plans", (200, {"plans": [plan("plan-2", vm_type=vm_type, cpu=4, ram_mb=8192, disk_gb=80)]}))
    router.add("POST", f"compute/{vm_type}-vms/{VM}/actions/resize/precheck", (200, {"decision": decision, "reasons": ["disk shrink"]}))
    router.add("POST", f"compute/{vm_type}-vms/{VM}/actions/resize", (202, ACCEPTED))
    return router


def test_resize_to_plan_prechecks_and_sends_the_new_sku() -> None:
    router = _resize_router()
    sync_client(router).cloud_vms.resize_cloud_vm(VM, workspace_id=WS, plan_id="plan-2", billing_term="MONTHLY")
    assert [call[1].rsplit("/", 1)[-1] for call in router.calls()] == [VM, "plans", "precheck", "resize"]
    assert router.body("POST", f"compute/cloud-vms/{VM}/actions/resize/precheck") == {"cpu": 4, "ram_mb": 8192, "disk_gb": 80}
    body = router.body("POST", f"compute/cloud-vms/{VM}/actions/resize")
    assert (body["cpu"], body["ram_mb"], body["disk_gb"]) == (4, 8192, 80)
    assert body["billing_catalog"]["billing_interval"] == "MONTHLY"


def test_resize_stops_when_precheck_is_not_in_place() -> None:
    router = _resize_router("migration_required")
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).cloud_vms.resize_cloud_vm(VM, workspace_id=WS, plan_id="plan-2")
    assert str(info.value) == "This downgrade requires migration. In-place disk shrink is blocked."
    assert info.value.details["decision"] == "migration_required"
    assert ("POST", f"compute/cloud-vms/{VM}/actions/resize") not in router.calls()
    with pytest.raises(IbeeValidationError):
        sync_client(_resize_router()).cloud_vms.resize_cloud_vm(VM, workspace_id=WS, plan_id="plan-2", cpu=4)
    with pytest.raises(IbeeValidationError):
        sync_client(_resize_router()).cloud_vms.resize_cloud_vm(VM, workspace_id=WS)


def test_windows_resize_carries_the_licence() -> None:
    record = vm(os_type="windows", billing_catalog={"sku_id": 1, "sku_code": "OLD", "attached_skus": {"windows_license": {"sku_id": 8, "sku_code": "WIN"}}})
    router = _resize_router(record=record)
    sync_client(router).cloud_vms.resize_cloud_vm(VM, workspace_id=WS, plan_id="plan-2")
    licence = router.body("POST", f"compute/cloud-vms/{VM}/actions/resize")["billing_catalog"]["attached_skus"]["windows_license"]
    assert (licence["sku_code"], licence["quantity"], licence["quantity_basis"]) == ("WIN", 4, "VCPU")
    bare = _resize_router(record=vm(os_type="windows"))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(bare).cloud_vms.resize_cloud_vm(VM, workspace_id=WS, plan_id="plan-2")
    assert info.value.code == "windows_license_required"


def test_resize_plan_and_root_disk_rules() -> None:
    def router(action: str, record: dict) -> Router:
        r = Router().add("GET", f"compute/gpu-vms/{VM}", (200, record))
        return r.add("PATCH", f"compute/gpu-vms/{VM}/actions/{action}", (202, ACCEPTED))

    client = sync_client(router("resize-plan", vm(cpu=4, ram_mb=8192)))
    with pytest.raises(IbeeValidationError) as info:
        client.gpu_vms.resize_gpu_vm_plan(VM, workspace_id=WS, cpu=2, ram_mb=8192)
    assert info.value.field == "confirm_downgrade"
    with pytest.raises(IbeeValidationError) as info:
        client.gpu_vms.resize_gpu_vm_plan(VM, workspace_id=WS, cpu=4, ram_mb=8192)
    assert info.value.code == "no_changes"
    client.gpu_vms.resize_gpu_vm_plan(VM, workspace_id=WS, cpu=2, ram_mb=8192, confirm_downgrade=True)
    with pytest.raises(IbeeValidationError):
        client.gpu_vms.resize_gpu_vm_plan(VM, workspace_id=WS, cpu=512, ram_mb=8192, check_state=False)

    disk = sync_client(router("resize-root-disk", vm(disk_gb=80)))
    with pytest.raises(IbeeValidationError) as info:
        disk.gpu_vms.resize_gpu_vm_root_disk(VM, workspace_id=WS, new_size_gb=80)
    assert info.value.code == "root_disk_grow_only"
    disk.gpu_vms.resize_gpu_vm_root_disk(VM, workspace_id=WS, new_size_gb=100)


def test_resize_409_with_decision_is_typed() -> None:
    router = Router().add(
        "POST",
        f"compute/cloud-vms/{VM}/actions/resize/precheck",
        (409, {"detail": {"decision": "blocked", "reasons": ["gpu busy"], "warnings": ["w"]}}),
    )
    with pytest.raises(ResizeBlockedError) as info:
        sync_client(router).cloud_vms.precheck_cloud_vm_resize(VM, workspace_id=WS, cpu=4)
    assert isinstance(info.value, ConflictError)
    assert (info.value.decision, info.value.reasons, info.value.warnings) == ("blocked", ["gpu busy"], ["w"])


# metrics / console --------------------------------------------------------------------


def test_metrics_parameters_are_checked_and_bandwidth_defaults_to_this_month() -> None:
    router = Router().add(
        "GET", f"compute/cloud-vms/{VM}/metrics/bandwidth", (200, {"vm_id": VM, "month": "2026-09", "rx_bytes": 0, "tx_bytes": 0})
    )
    client = sync_client(router)
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.get_cloud_vm_metrics_timeseries(VM, workspace_id=WS, range="2h")
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.get_cloud_vm_bandwidth(VM, workspace_id=WS, month="2026-13")
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.list_cloud_vm_events(VM, workspace_id=WS, limit=501)
    client.cloud_vms.get_cloud_vm_bandwidth(VM, workspace_id=WS)
    month = router.requests[-1].url.params["month"]
    assert len(month) == 7 and month[4] == "-"


def test_console_is_cloud_only() -> None:
    router = Router().add("POST", "compute/console/sessions", (200, {"session_id": "s"}))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError) as info:
        client.vm_console.create_vm_console_session(workspace_id=WS, vm_id=VM, vm_type="gpu")
    assert info.value.code == "console_not_supported"
    assert router.requests == []


# async parity -------------------------------------------------------------------------


def test_async_create_delete_resize_parity() -> None:
    router = _catalog_router()
    router.add("GET", f"compute/cloud-vms/{VM}", (200, vm(public_ip="203.0.113.5")))
    router.add("DELETE", f"compute/cloud-vms/{VM}", (202, ACCEPTED))
    router.add("GET", "compute/plans", (200, {"plans": [plan(), plan("plan-2", cpu=4, ram_mb=8192, disk_gb=80)]}))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/resize/precheck", (200, {"decision": "in_place"}))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/resize", (202, ACCEPTED))

    async def run() -> None:
        async with async_transport(router) as http_client:
            client = async_client(router, http_client)
            await client.cloud_vms.create_cloud_vm(
                workspace_id=WS, name="web-1", site_id="site-1", plan_id="plan-1", template_id="tmpl-ubuntu"
            )
            await client.cloud_vms.delete_cloud_vm(VM, workspace_id=WS)
            await client.cloud_vms.resize_cloud_vm(VM, workspace_id=WS, plan_id="plan-2")
            with pytest.raises(IbeeValidationError):
                await client.cloud_vms.update_cloud_vm_access(VM, workspace_id=WS)
            listed = await client.cloud_vms.list_all_cloud_vms(workspace_id=WS)
            assert listed == []

    router.add("GET", "compute/cloud-vms", (200, []))
    asyncio.run(run())
    assert router.body("POST", "compute/cloud-vms")["billing_catalog"]["billing_interval"] == "HOURLY"
    assert router.body("DELETE", f"compute/cloud-vms/{VM}") == {"public_ip_action": "release"}
    assert router.body("POST", f"compute/cloud-vms/{VM}/actions/resize")["cpu"] == 4


# review fixes ------------------------------------------------------------------------

_CALLER_CATALOG = {
    "sku_id": 101,
    "sku_code": "VM-STD-2-4",
    "billing_options": [
        {"billing_interval": "HOURLY", "unit_price_minor": 250, "committed": False},
        {"billing_interval": "MONTHLY", "unit_price_minor": 150000, "committed": True, "commitment_period": "MONTHLY"},
    ],
}


def test_billing_term_is_applied_to_an_explicit_billing_catalog() -> None:
    single = Router().add("POST", "compute/cloud-vms", (202, ACCEPTED))
    _create(
        sync_client(single),
        billing_catalog=_CALLER_CATALOG,
        billing_term="MONTHLY",
        cpu=2,
        ram_mb=4096,
        disk_gb=50,
        os_type="linux",
        os_distro="ubuntu",
    )
    assert single.calls() == [("POST", "compute/cloud-vms")]
    catalog = single.body("POST", "compute/cloud-vms")["billing_catalog"]
    assert catalog["billing_interval"] == "MONTHLY" and catalog["unit_price_minor"] == 150000
    assert "billing_options" not in catalog

    lookup = _catalog_router()
    _create(sync_client(lookup), billing_catalog=_CALLER_CATALOG, billing_term="MONTHLY")
    assert lookup.body("POST", "compute/cloud-vms")["billing_catalog"]["billing_interval"] == "MONTHLY"

    for router, kwargs in (
        (Router().add("POST", "compute/cloud-vms", (202, ACCEPTED)), dict(cpu=2, ram_mb=4096, disk_gb=50, os_type="linux", os_distro="ubuntu")),
        (_catalog_router(), {}),
    ):
        with pytest.raises(IbeeValidationError) as info:
            _create(sync_client(router), billing_catalog=_CALLER_CATALOG, billing_term="YEARLY", **kwargs)
        assert info.value.code == "unsupported_billing_term"
        assert ("POST", "compute/cloud-vms") not in router.calls()

    fixed = {"sku_id": 1, "sku_code": "X", "billing_interval": "HOURLY"}
    with pytest.raises(IbeeValidationError) as info:
        _create(sync_client(_catalog_router()), billing_catalog=fixed, billing_term="MONTHLY")
    assert info.value.code == "unsupported_billing_term"


def test_resize_applies_billing_term_to_an_explicit_catalog() -> None:
    router = Router()
    router.add("POST", f"compute/cloud-vms/{VM}/actions/resize/precheck", (200, {"decision": "in_place"}))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/resize", (202, ACCEPTED))
    sync_client(router).cloud_vms.resize_cloud_vm(
        VM, workspace_id=WS, cpu=4, ram_mb=8192, disk_gb=80, billing_catalog=_CALLER_CATALOG, billing_term="MONTHLY"
    )
    assert router.body("POST", f"compute/cloud-vms/{VM}/actions/resize")["billing_catalog"]["billing_interval"] == "MONTHLY"
    plan_router = Router().add("GET", f"compute/gpu-vms/{VM}", (200, vm()))
    plan_router.add("PATCH", f"compute/gpu-vms/{VM}/actions/resize-plan", (202, ACCEPTED))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(plan_router).gpu_vms.resize_gpu_vm_plan(
            VM, workspace_id=WS, cpu=4, ram_mb=8192, billing_catalog=_CALLER_CATALOG, billing_term="YEARLY"
        )
    assert info.value.code == "unsupported_billing_term"
    assert ("PATCH", f"compute/gpu-vms/{VM}/actions/resize-plan") not in plan_router.calls()


def test_vm_state_matrix_is_opt_in() -> None:
    # resize with an explicit shape: the VM is not read unless check_state=True
    router = Router()
    router.add("POST", f"compute/cloud-vms/{VM}/actions/resize/precheck", (200, {"decision": "in_place"}))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/resize", (202, ACCEPTED))
    sync_client(router).cloud_vms.resize_cloud_vm(VM, workspace_id=WS, cpu=4, ram_mb=8192, disk_gb=80)
    assert ("GET", f"compute/cloud-vms/{VM}") not in router.calls()
    sync_client(_resize_router(record=vm(status="provisioning"))).cloud_vms.resize_cloud_vm(VM, workspace_id=WS, plan_id="plan-2")
    with pytest.raises(IbeeValidationError) as info:
        sync_client(_resize_router(record=vm(status="provisioning"))).cloud_vms.resize_cloud_vm(
            VM, workspace_id=WS, plan_id="plan-2", check_state=True
        )
    assert info.value.code == "invalid_vm_state"

    # resize-plan / root disk still read the VM (required checks) but gate state only on request
    def patch_router(action: str) -> Router:
        r = Router().add("GET", f"compute/cloud-vms/{VM}", (200, vm(status="provisioning", disk_gb=50)))
        return r.add("PATCH", f"compute/cloud-vms/{VM}/actions/{action}", (202, ACCEPTED))

    client = sync_client(patch_router("resize-plan"))
    client.cloud_vms.resize_cloud_vm_plan(VM, workspace_id=WS, cpu=4, ram_mb=8192)
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.resize_cloud_vm_plan(VM, workspace_id=WS, cpu=4, ram_mb=8192, check_state=True)
    disk = sync_client(patch_router("resize-root-disk"))
    disk.cloud_vms.resize_cloud_vm_root_disk(VM, workspace_id=WS, new_size_gb=100)
    with pytest.raises(IbeeValidationError):
        disk.cloud_vms.resize_cloud_vm_root_disk(VM, workspace_id=WS, new_size_gb=100, check_state=True)


def test_delete_state_gate_matches_the_portal() -> None:
    router = Router().add("GET", f"compute/cloud-vms/{VM}", (200, vm(status="resizing")))
    router.add("DELETE", f"compute/cloud-vms/{VM}", (202, ACCEPTED))
    sync_client(router).cloud_vms.delete_cloud_vm(VM, workspace_id=WS)
    assert router.calls()[-1] == ("DELETE", f"compute/cloud-vms/{VM}")
    release = Router().add("DELETE", f"compute/cloud-vms/{VM}", (202, ACCEPTED))
    sync_client(release).cloud_vms.delete_cloud_vm(VM, workspace_id=WS, public_ip_action="release")
    assert release.calls() == [("DELETE", f"compute/cloud-vms/{VM}")]


def test_async_state_matrix_opt_in_parity() -> None:
    async def main() -> None:
        router = Router()
        router.add("POST", f"compute/cloud-vms/{VM}/actions/resize/precheck", (200, {"decision": "in_place"}))
        router.add("POST", f"compute/cloud-vms/{VM}/actions/resize", (202, ACCEPTED))
        async with async_transport(router) as http:
            await async_client(router, http).cloud_vms.resize_cloud_vm(
                VM, workspace_id=WS, cpu=4, ram_mb=8192, disk_gb=80, billing_catalog=_CALLER_CATALOG, billing_term="MONTHLY"
            )
        assert ("GET", f"compute/cloud-vms/{VM}") not in router.calls()
        assert router.body("POST", f"compute/cloud-vms/{VM}/actions/resize")["billing_catalog"]["billing_interval"] == "MONTHLY"

    asyncio.run(main())
