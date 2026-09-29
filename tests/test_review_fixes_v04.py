"""0.4.0 review fixes: scope-tolerant pre-steps, TypeScript parity and portal rules."""

from __future__ import annotations

import asyncio

import pytest

from _compute_fixtures import ACCEPTED, VM, WS, Router, async_client, async_transport, sync_client
from ibee import IbeeBillingWarning, IbeeValidationError
from ibee.errors import BadRequestError, ForbiddenError, NotFoundError, ReservedIpTargetUnsupportedError
from ibee.validation import (
    build_firewall_rule_body,
    build_nat_delete_body,
    build_node_attach_body,
    default_nat_delete_ip_action,
    validate_target_volume_names,
    validate_vpc_connectivity_type,
)
from test_network_services_v04 import FW, RIP, group, rip, summary
from test_networking_v04 import V, gateway, node, rule, subnet, vip, vpc_record

FORBIDDEN = (403, {"error": "insufficient_scope", "required_scope": "network.read"})
VOL = "64b0000000000000000000b1"
BLOCK_SKU = {"sku_id": 12, "sku_code": "BLOCKSTO-STD", "product_code": "block_storage"}


# ---------------------------------------------------------------------------
# Compute
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("family", ["cloud", "gpu"])
def test_backup_policy_get_and_disable_validate_vm_id(family: str) -> None:
    router = Router()
    vms = getattr(sync_client(router), f"{family}_vms")
    for call in (
        lambda: getattr(vms, f"get_{family}_vm_backup_policy")("all", workspace_id=WS),
        lambda: getattr(vms, f"disable_{family}_vm_backups")("all", workspace_id=WS),
        lambda: getattr(vms, f"disable_{family}_vm_backups")(VM, workspace_id=WS, requested_by=" "),
    ):
        with pytest.raises(IbeeValidationError):
            call()
    assert router.requests == []


def test_detach_volume_state_check_tolerates_a_missing_block_storage_read() -> None:
    router = Router().add("GET", f"block-storage/volumes/{VOL}", (403, {"error": "insufficient_scope"}))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/detach-volume", (202, ACCEPTED))
    sync_client(router).cloud_vms.detach_cloud_vm_volume(
        VM, workspace_id=WS, volume_id=VOL, confirm_unmounted=True, check_state=True
    )
    assert router.calls()[-1] == ("POST", f"compute/cloud-vms/{VM}/actions/detach-volume")


def test_list_all_backup_runs_defaults_to_succeeded() -> None:
    router = Router().add("GET", "compute/cloud-vm-backups/runs", (200, {"runs": [], "total": 0}))
    client = sync_client(router)
    client.cloud_vms.list_all_cloud_vm_backup_runs(workspace_id=WS)
    assert router.requests[-1].url.params.get_list("status") == ["succeeded"]
    client.cloud_vms.list_all_cloud_vm_backup_runs(workspace_id=WS, status="all")
    assert router.requests[-1].url.params.get_list("status") == []
    client.cloud_vms.list_all_cloud_vm_backup_runs(workspace_id=WS, status=["failed", "running"])
    assert router.requests[-1].url.params.get_list("status") == ["failed", "running"]


def test_console_session_is_labelled_api_by_default() -> None:
    session = {
        "session_id": "s", "vm_id": VM, "vm_type": "cloud", "console_type": "novnc", "connect_url": "https://c/x",
        "expires_at": "2026-09-01T10:05:00Z", "status": "active", "created_at": "2026-09-01T10:00:00Z",
        "token_expires_in_seconds": 60, "idle_timeout_seconds": 600, "max_duration_seconds": 3600, "state": "active",
    }
    router = Router().add("POST", "compute/console/sessions", (200, session))
    client = sync_client(router)
    client.vm_console.create_vm_console_session(workspace_id=WS, vm_id=VM, vm_type="cloud")
    assert router.body("POST", "compute/console/sessions")["requested_by"] == "api"
    client.vm_console.create_vm_console_session(workspace_id=WS, vm_id=VM, vm_type="cloud", requested_by="ops")
    assert router.body("POST", "compute/console/sessions")["requested_by"] == "ops"


def test_target_volume_names_must_name_every_captured_data_volume() -> None:
    manifest = [
        {"source_volume_id": "root-1", "role": "root"},
        {"source_volume_id": "data-1", "role": "data"},
        {"source_volume_id": "data-2", "role": "data"},
    ]
    with pytest.raises(IbeeValidationError, match="missing a name for: data-2"):
        validate_target_volume_names(manifest, {"data-1": "logs"})
    assert validate_target_volume_names(manifest, {"data-1": " logs ", "data-2": "db"}) == {"data-1": "logs", "data-2": "db"}


# ---------------------------------------------------------------------------
# Networking: pre-step reads without the read scope
# ---------------------------------------------------------------------------


def _forbidden_prestep_cases():
    return [
        (
            "create_nat_gateway",
            lambda r: r.add("GET", V, FORBIDDEN).add("POST", f"{V}/nat-gateways", (201, gateway())),
            lambda c: c.vpcs.create_nat_gateway("vpc-1", workspace_id=WS, billing_catalog={"sku_id": 7, "sku_code": "NAT-GATEWAY"}),
            ("POST", f"{V}/nat-gateways"),
        ),
        (
            "create_vpc_subnet",
            lambda r: r.add("GET", V, FORBIDDEN).add("POST", f"{V}/subnets", (201, subnet(subnet_id="sub-2", cidr="10.20.0.128/25"))),
            lambda c: c.vpcs.create_vpc_subnet("vpc-1", workspace_id=WS, name="apps", cidr="10.20.0.128/25"),
            ("POST", f"{V}/subnets"),
        ),
        (
            "delete_vpc",
            lambda r: r.add("GET", V, FORBIDDEN).add("GET", f"{V}/virtual-ips", FORBIDDEN).add("DELETE", V, (204, None)),
            lambda c: c.vpcs.delete_vpc("vpc-1", workspace_id=WS),
            ("DELETE", V),
        ),
        (
            "release_reserved_ip",
            lambda r: r.add("GET", RIP, FORBIDDEN).add("DELETE", RIP, (204, None)),
            lambda c: c.reserved_ips.release_reserved_ip("rip-1", workspace_id=WS),
            ("DELETE", RIP),
        ),
        (
            "detach_reserved_ip",
            lambda r: r.add("GET", RIP, FORBIDDEN).add("POST", f"{RIP}/detach", (200, rip())),
            lambda c: c.reserved_ips.detach_reserved_ip("rip-1", workspace_id=WS),
            ("POST", f"{RIP}/detach"),
        ),
        (
            "create_firewall_group",
            lambda r: r.add("GET", FW, FORBIDDEN).add("POST", FW, (201, group(name="api"))),
            lambda c: c.firewalls.create_firewall_group(workspace_id=WS, name="api"),
            ("POST", FW),
        ),
        (
            "delete_firewall_rule",
            lambda r: r.add("GET", f"{FW}/fw-1", FORBIDDEN).add("DELETE", f"{FW}/fw-1/rules/r-1", (200, group())),
            lambda c: c.firewalls.delete_firewall_rule("fw-1", "r-1", workspace_id=WS),
            ("DELETE", f"{FW}/fw-1/rules/r-1"),
        ),
        (
            "create_nat_port_forwarding_rule",
            lambda r: r.add("GET", f"{V}/nat-gateways", FORBIDDEN)
            .add("GET", f"{V}/nat-gateways/nat-1/port-forwarding-rules", FORBIDDEN)
            .add("GET", f"{V}/nodes", FORBIDDEN)
            .add("POST", f"{V}/nat-gateways/nat-1/port-forwarding-rules", (201, rule())),
            lambda c: c.vpcs.create_nat_port_forwarding_rule(
                "vpc-1", "nat-1", workspace_id=WS, name="ssh", external_port=2222, internal_ip="10.20.0.10", internal_port=22
            ),
            ("POST", f"{V}/nat-gateways/nat-1/port-forwarding-rules"),
        ),
    ]


@pytest.mark.parametrize("case", _forbidden_prestep_cases(), ids=lambda case: case[0])
def test_networking_prestep_reads_are_skipped_without_the_read_scope(case) -> None:
    _, build, call, main = case
    router = build(Router())
    call(sync_client(router))
    assert router.calls()[-1] == main
    # check_state=True keeps the read mandatory.
    strict = build(Router())
    with pytest.raises(ForbiddenError):
        call(_StrictClient(sync_client(strict)))
    assert main not in strict.calls()


class _StrictClient:
    """Proxy that adds ``check_state=True`` to every networking call."""

    def __init__(self, client) -> None:
        self._client = client

    def __getattr__(self, name):
        resource = getattr(self._client, name)

        class _Resource:
            def __getattr__(self, method):
                target = getattr(resource, method)
                return lambda *args, **kwargs: target(*args, check_state=True, **kwargs)

        return _Resource()


def test_async_networking_prestep_reads_are_skipped_without_the_read_scope() -> None:
    async def main() -> None:
        router = Router().add("GET", RIP, FORBIDDEN).add("DELETE", RIP, (204, None))
        router.add("GET", V, FORBIDDEN).add("POST", f"{V}/nat-gateways", (201, gateway()))
        async with async_transport(router) as http:
            client = async_client(router, http)
            await client.reserved_ips.release_reserved_ip("rip-1", workspace_id=WS)
            await client.vpcs.create_nat_gateway("vpc-1", workspace_id=WS, billing_catalog={"sku_id": 7, "sku_code": "NAT-GATEWAY"})
        assert ("DELETE", RIP) in router.calls() and ("POST", f"{V}/nat-gateways") in router.calls()

    asyncio.run(main())


def test_required_networking_reads_explain_the_missing_scope() -> None:
    router = Router().add("GET", RIP, FORBIDDEN)
    with pytest.raises(ForbiddenError) as info:
        sync_client(router).reserved_ips.attach_reserved_ip(
            "rip-1", workspace_id=WS, vm_id="vm-1", vpc_id="vpc-1", subnet_id="sub-1", detach_from_service=True
        )
    assert "detach from a NAT gateway/VIP first" in info.value.message


def test_pf_vip_target_without_readable_virtual_ips_needs_target_vm_ids() -> None:
    router = Router().add("GET", f"{V}/nat-gateways", (200, [gateway()]))
    router.add("GET", f"{V}/nat-gateways/nat-1/port-forwarding-rules", (200, []))
    router.add("GET", f"{V}/virtual-ips", FORBIDDEN)
    with pytest.raises(IbeeValidationError, match="grant network.read"):
        sync_client(router).vpcs.create_nat_port_forwarding_rule(
            "vpc-1", "nat-1", workspace_id=WS, name="web", external_port=80, internal_ip="10.20.0.50",
            internal_port=8080, target_type="vip",
        )


# ---------------------------------------------------------------------------
# Networking: port-forwarding update target checks
# ---------------------------------------------------------------------------

PF = f"{V}/nat-gateways/nat-1/port-forwarding-rules"


def test_pf_update_to_vip_fills_announcers_from_the_virtual_ip() -> None:
    router = Router().add("GET", PF, (200, [rule()]))
    router.add("GET", f"{V}/virtual-ips", (200, [vip()]))
    router.add("PATCH", f"{PF}/natpf-1", (200, rule(target_type="vip")))
    sync_client(router).vpcs.update_nat_port_forwarding_rule(
        "vpc-1", "nat-1", "natpf-1", workspace_id=WS, target_type="vip", internal_ip="10.20.0.50"
    )
    assert router.body("PATCH", f"{PF}/natpf-1") == {
        "internal_ip": "10.20.0.50",
        "target_type": "vip",
        "target_vm_ids": ["vm-1", "vm-2"],
    }


def test_pf_update_checks_the_new_target() -> None:
    router = Router().add("GET", PF, (200, [rule()]))
    router.add("GET", f"{V}/nodes", (200, [node(ip="10.20.0.10")]))
    with pytest.raises(IbeeValidationError, match="NAT-connected node"):
        sync_client(router).vpcs.update_nat_port_forwarding_rule(
            "vpc-1", "nat-1", "natpf-1", workspace_id=WS, internal_ip="10.20.0.99"
        )
    vip_router = Router().add("GET", PF, (200, [rule(target_type="vip", internal_ip="10.20.0.50", target_vm_ids=["vm-1", "vm-2"])]))
    vip_router.add("GET", f"{V}/virtual-ips", (200, [vip(), vip(virtual_ip_id="pvip-2", private_ip="10.20.0.60", announcer_vm_ids=["vm-3"])]))
    with pytest.raises(IbeeValidationError, match="announcer VMs"):
        sync_client(vip_router).vpcs.update_nat_port_forwarding_rule(
            "vpc-1", "nat-1", "natpf-1", workspace_id=WS, internal_ip="10.20.0.60"
        )


def test_pf_update_to_vip_without_checks_needs_target_vm_ids() -> None:
    router = Router()
    with pytest.raises(IbeeValidationError, match="target_vm_ids is required"):
        sync_client(router).vpcs.update_nat_port_forwarding_rule(
            "vpc-1", "nat-1", "natpf-1", workspace_id=WS, target_type="vip", check_state=False
        )
    assert router.requests == []


# ---------------------------------------------------------------------------
# Networking: other portal / TypeScript parity
# ---------------------------------------------------------------------------


def test_legacy_nat_gateway_backed_by_a_reserved_ip_can_be_reserved_without_catalog() -> None:
    legacy = gateway(public_ip_source=None, public_ip_id="rip-1")
    router = Router().add("GET", f"{V}/nat-gateways", (200, [legacy]))
    router.add("GET", RIP, (200, rip(attached_resource_type="nat_gateway", attached_resource_id="nat-1", status="attached")))
    router.add("DELETE", f"{V}/nat-gateways/nat-1", (204, None))
    sync_client(router).vpcs.delete_nat_gateway("vpc-1", "nat-1", workspace_id=WS, public_ip_action="reserve")
    assert router.body("DELETE", f"{V}/nat-gateways/nat-1") == {"public_ip_action": "reserve"}
    platform = Router().add("GET", f"{V}/nat-gateways", (200, [legacy]))
    platform.add("GET", RIP, (200, rip()))
    with pytest.raises(IbeeValidationError, match="RESERVED-IP billing_catalog"):
        sync_client(platform).vpcs.delete_nat_gateway("vpc-1", "nat-1", workspace_id=WS, public_ip_action="reserve")
    assert default_nat_delete_ip_action(legacy, uses_reserved_ip=True) == "reserve"
    assert build_nat_delete_body(public_ip_action="reserve", gateway=legacy, uses_reserved_ip=True) == {"public_ip_action": "reserve"}


def test_delete_vpc_refuses_while_virtual_ips_exist() -> None:
    router = Router().add("GET", V, (200, vpc_record()))
    router.add("GET", f"{V}/virtual-ips", (200, [vip()]))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).vpcs.delete_vpc("vpc-1", workspace_id=WS)
    assert info.value.code == "vpc_has_virtual_ips"
    assert ("DELETE", V) not in router.calls()


def test_delete_virtual_ip_refuses_while_a_rule_targets_it() -> None:
    router = Router().add("GET", f"{V}/virtual-ips", (200, [vip()]))
    router.add("GET", f"{V}/nat-gateways", (200, [gateway()]))
    router.add("GET", PF, (200, [rule(internal_ip="10.20.0.50", target_type="vip")]))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).vpcs.delete_vpc_virtual_ip("vpc-1", "pvip-1", workspace_id=WS)
    assert info.value.code == "virtual_ip_has_rules"
    assert ("DELETE", f"{V}/virtual-ips/pvip-1") not in router.calls()


def test_firewall_attach_to_an_ineligible_vm_is_a_validation_error() -> None:
    router = Router().add(
        "POST", f"{FW}/fw-1/attachments", (400, {"detail": "Only OVS/OVN-backed VM networks can attach firewall groups"})
    )
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).firewalls.attach_firewall_group("fw-1", workspace_id=WS, vm_id="vm-1")
    assert info.value.code == "firewall_attach_unsupported" and info.value.field == "vm_id"
    assert isinstance(info.value.__cause__, BadRequestError)


def test_enum_inputs_are_trimmed_and_case_insensitive() -> None:
    assert validate_vpc_connectivity_type(" NAT_GATEWAY ") == "nat_gateway"
    assert build_node_attach_body(vm_id="vm-1", subnet_id="sub-1", connectivity="NAT")["connectivity"] == "nat"
    body = build_firewall_rule_body(protocol="TCP", port_start=443, direction="Ingress", action="ALLOW")
    assert (body["protocol"], body["direction"], body["action"]) == ("tcp", "ingress", "allow")
    assert "description" not in build_firewall_rule_body(update=True, description="  ", enabled=True)


def test_iter_firewall_group_summaries_pages_through_everything() -> None:
    router = Router().add("GET", FW, [(200, [summary(i) for i in range(2)]), (200, [summary(2)])])
    items = list(sync_client(router).firewalls.iter_firewall_group_summaries(workspace_id=WS, page_size=2))
    assert [item.firewall_group_id for item in items] == ["fw-0", "fw-1", "fw-2"]

    async def main() -> None:
        arouter = Router().add("GET", FW, (200, [summary(1)]))
        async with async_transport(arouter) as http:
            client = async_client(arouter, http)
            got = [item async for item in client.firewalls.iter_firewall_group_summaries(workspace_id=WS)]
        assert len(got) == 1

    asyncio.run(main())


def test_reserved_ip_target_error_is_also_a_validation_error() -> None:
    error = ReservedIpTargetUnsupportedError(body={"detail": "Reserved IP attach targets require a VPC network allocation"})
    assert isinstance(error, NotFoundError) and isinstance(error, IbeeValidationError)
    assert (error.status_code, error.code, error.field) == (404, "reserved_ip_target_unsupported", "vm_id")


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


def test_delete_bucket_skips_the_checks_without_object_storage_read() -> None:
    path = "object-storage/buckets/logs"
    router = Router().add("GET", path, (403, {"error": "insufficient_scope", "required_scope": "object-storage.read"}))
    router.add("DELETE", path, (200, {"message": "deleted"}))
    sync_client(router).object_storage.delete_bucket("logs", workspace_id=WS)
    assert router.calls() == [("GET", path), ("DELETE", path)]


def test_attach_to_vm_checks_an_explicit_catalog_before_any_request() -> None:
    router = Router()
    for catalog in ({"sku_id": 1, "sku_code": "ROOTDISK-X"}, {"sku_code": "BLOCKSTO-STD"}):
        with pytest.raises(IbeeValidationError):
            sync_client(router).block_storage.attach_block_volume_to_vm(VOL, VM, workspace_id=WS, billing_catalog=catalog)
    assert router.requests == []


def test_attach_to_vm_without_volume_read_needs_only_the_catalog() -> None:
    router = Router().add("GET", f"block-storage/volumes/{VOL}", (403, {"error": "insufficient_scope"}))
    router.add("GET", f"compute/cloud-vms/{VM}", (403, {"error": "insufficient_scope"}))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/attach-volume", (202, ACCEPTED))
    sync_client(router).block_storage.attach_block_volume_to_vm(VOL, VM, workspace_id=WS, billing_catalog=BLOCK_SKU)
    assert router.calls()[-1] == ("POST", f"compute/cloud-vms/{VM}/actions/attach-volume")
    header = router.last("POST", f"compute/cloud-vms/{VM}/actions/attach-volume").headers["x-idempotency-key"]
    assert header.startswith(f"cloud-vm-attach-volume-{VOL}-")


# ---------------------------------------------------------------------------
# Secret Store
# ---------------------------------------------------------------------------


def test_list_all_secret_stores_treats_none_as_include_archived() -> None:
    router = Router().add("GET", "secret-store/stores", (200, {"stores": [], "total": 0, "page": 1, "limit": 200}))
    client = sync_client(router)
    client.secret_store.list_all_secret_stores(workspace_id=WS, include_archived=None)
    assert router.requests[-1].url.params["include_archived"] == "true"
    client.secret_store.list_all_secret_stores(workspace_id=WS, include_archived=False)
    assert router.requests[-1].url.params["include_archived"] == "false"


def test_secret_store_billing_preflight_alias() -> None:
    router = Router().add("POST", "billing/resource-eligibility", (403, {"error": "insufficient_scope", "required_scope": "billing.read"}))
    router.add("POST", "secret-store/stores", (201, {"id": "st-1", "name": "app", "store_key": "app"}))
    client = sync_client(router)
    client.secret_store.create_secret_store(workspace_id=WS, name="app", billing_preflight=True)
    assert router.calls() == [("POST", "secret-store/stores")]
