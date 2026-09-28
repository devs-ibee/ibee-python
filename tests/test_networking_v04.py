"""0.4.0 portal-parity networking: VPCs, subnets, nodes, NAT gateways, port forwarding and virtual IPs."""

from __future__ import annotations

import asyncio
import json
import warnings

import pytest

from _compute_fixtures import WS, Router, async_client, async_transport, sync_client
from ibee import IbeeBillingWarning, IbeeValidationError
from ibee.errors import BillingDeniedError, ForbiddenError, IbeeError, NotFoundError
from ibee.validation import (
    default_nat_delete_ip_action,
    network_billing_catalog,
    parse_ipv4,
    resolve_node_connectivity,
    validate_host_in_subnet,
    validate_port,
    validate_subnet_cidr,
    validate_vpc_cidr,
)

TS = "2026-09-01T10:00:00Z"
NAT_CATALOG = {"sku_id": 7, "sku_code": "NAT-GATEWAY", "unit_price_minor": 500}


def vpc_record(**overrides):
    record = {
        "vpc_id": "vpc-1",
        "organization_id": "org",
        "workspace_id": WS,
        "site_id": "site-1",
        "name": "net",
        "cidr": "10.20.0.0/24",
        "status": "available",
        "connectivity_type": "nat_gateway",
        "created_at": TS,
        "updated_at": TS,
        "node_count": 0,
        "subnets": [],
        "nat_gateways": [],
        "attached_nodes": [],
    }
    record.update(overrides)
    return record


def gateway(**overrides):
    record = {
        "nat_gateway_id": "nat-1",
        "vpc_id": "vpc-1",
        "site_id": "site-1",
        "name": "NAT Gateway",
        "public_ip_id": "pip-1",
        "public_ip": "203.0.113.5",
        "status": "available",
        "public_ip_source": "automatic",
    }
    record.update(overrides)
    return record


def subnet(**overrides):
    record = {
        "subnet_id": "sub-1",
        "vpc_id": "vpc-1",
        "site_id": "site-1",
        "name": "default",
        "cidr": "10.20.0.0/24",
        "gateway": "10.20.0.1",
        "dns": ["1.1.1.1"],
        "status": "available",
        "created_at": TS,
        "updated_at": TS,
    }
    record.update(overrides)
    return record


def node(vm_id="vm-1", ip="10.20.0.10", **overrides):
    record = {
        "allocation_id": f"alloc-{vm_id}",
        "vpc_id": "vpc-1",
        "subnet_id": "sub-1",
        "vm_id": vm_id,
        "connectivity": "nat",
        "private_ip": ip,
        "prefix_length": 24,
        "subnet_mask": "255.255.255.0",
        "gateway": "10.20.0.1",
        "dns": [],
        "nat_gateway_id": "nat-1",
        "status": "active",
    }
    record.update(overrides)
    return record


def rule(**overrides):
    record = {
        "port_forward_rule_id": "natpf-1",
        "vpc_id": "vpc-1",
        "nat_gateway_id": "nat-1",
        "name": "ssh",
        "protocol": "tcp",
        "external_port": 2222,
        "internal_ip": "10.20.0.10",
        "internal_port": 22,
        "status": "available",
        "created_at": TS,
        "updated_at": TS,
    }
    record.update(overrides)
    return record


def vip(**overrides):
    record = {
        "virtual_ip_id": "pvip-1",
        "vpc_id": "vpc-1",
        "subnet_id": "sub-1",
        "private_ip": "10.20.0.50",
        "purpose": "metallb",
        "announcer_vm_ids": ["vm-1", "vm-2"],
        "status": "available",
    }
    record.update(overrides)
    return record


V = "networking/vpcs/vpc-1"


# validation helpers -----------------------------------------------------------------


def test_vpc_cidr_rules_match_the_portal() -> None:
    assert validate_vpc_cidr(" 10.20.0.0/24 ") == "10.20.0.0/24"
    with pytest.raises(IbeeValidationError, match="Did you mean 10.20.0.0/22") as info:
        validate_vpc_cidr("10.20.1.0/22")
    assert info.value.details == {"suggestion": "10.20.0.0/22"}
    with pytest.raises(IbeeValidationError, match="RFC1918"):
        validate_vpc_cidr("8.8.8.0/24")
    with pytest.raises(IbeeValidationError, match="RFC1918"):
        validate_vpc_cidr("172.32.0.0/24")
    for bad in ("10.0.0.0/16", "10.0.0.0/29", "10.0.0/24", "10.0.0.256/24", "10.0.0.0"):
        with pytest.raises(IbeeValidationError):
            validate_vpc_cidr(bad)


def test_subnet_cidr_containment_and_overlap() -> None:
    assert validate_subnet_cidr("10.20.0.128/25", vpc_cidr="10.20.0.0/24") == "10.20.0.128/25"
    with pytest.raises(IbeeValidationError, match="sub-range of 10.20.0.0/24"):
        validate_subnet_cidr("10.20.1.0/25", vpc_cidr="10.20.0.0/24")
    with pytest.raises(IbeeValidationError, match="overlaps"):
        validate_subnet_cidr("10.20.0.0/25", vpc_cidr="10.20.0.0/24", existing_cidrs=["10.20.0.0/26"])
    with pytest.raises(IbeeValidationError, match="/29"):
        validate_subnet_cidr("10.20.0.0/30")


def test_host_in_subnet_messages_match_the_portal() -> None:
    assert validate_host_in_subnet(" 10.20.0.10 ", "10.20.0.0/24", "10.20.0.1") == "10.20.0.10"
    with pytest.raises(IbeeValidationError, match=r"Address must be inside 10.20.0.0/24\."):
        validate_host_in_subnet("10.20.1.10", "10.20.0.0/24")
    with pytest.raises(IbeeValidationError, match="network or broadcast"):
        validate_host_in_subnet("10.20.0.255", "10.20.0.0/24")
    with pytest.raises(IbeeValidationError, match="network or broadcast"):
        validate_host_in_subnet("10.20.0.0", "10.20.0.0/24")
    with pytest.raises(IbeeValidationError, match="subnet gateway"):
        validate_host_in_subnet("10.20.0.1", "10.20.0.0/24", "10.20.0.1")
    with pytest.raises(IbeeValidationError):
        parse_ipv4("10.20.0.1000")


def test_port_and_small_helpers() -> None:
    assert validate_port(22) == 22
    for bad in (0, 65536, True, 22.0, "22"):
        with pytest.raises(IbeeValidationError, match="whole numbers"):
            validate_port(bad)
    assert resolve_node_connectivity("nat_gateway", True) == "nat"
    assert resolve_node_connectivity("nat_gateway", True, has_primary_network=True, use_vpc_for_internet=False) == "private"
    assert resolve_node_connectivity("private", True) == "private"
    assert default_nat_delete_ip_action({"public_ip_source": "reserved"}) == "reserve"
    assert default_nat_delete_ip_action({"public_ip_source": "automatic"}, True) == "reserve"
    assert default_nat_delete_ip_action({"public_ip_source": "automatic"}) == "release"
    assert network_billing_catalog(None) == {}
    assert network_billing_catalog({"skuId": 3, "skuCode": "RESERVED-IP", "unitPriceMinor": 10, "junk": 1}) == {
        "sku_id": 3,
        "sku_code": "RESERVED-IP",
        "unit_price_minor": 10,
    }


# VPCs -------------------------------------------------------------------------------


def test_create_vpc_sends_the_portal_body() -> None:
    router = Router().add("POST", "networking/vpcs", (201, vpc_record(connectivity_type="private")))
    result = sync_client(router).vpcs.create_vpc(
        workspace_id=WS, name="  net ", site_id=" site-1 ", description="   ", cidr="10.20.0.0/24", connectivity_type="private"
    )
    assert result.connectivity_type == "private"
    assert router.body("POST", "networking/vpcs") == {
        "name": "net",
        "site_id": "site-1",
        "connectivity_type": "private",
        "cidr": "10.20.0.0/24",
        "auto_cidr": False,
    }


def test_create_vpc_rules() -> None:
    client = sync_client(Router())
    with pytest.raises(IbeeValidationError, match="cidr requires auto_cidr=false"):
        client.vpcs.create_vpc(workspace_id=WS, name="n", site_id="s", cidr="10.0.0.0/24", auto_cidr=True)
    with pytest.raises(IbeeValidationError, match="cidr is required"):
        client.vpcs.create_vpc(workspace_id=WS, name="n", site_id="s", auto_cidr=False)
    with pytest.raises(IbeeValidationError, match="Name and location are required"):
        client.vpcs.create_vpc(workspace_id=WS, name="  ", site_id="s")
    with pytest.raises(IbeeValidationError, match="1-80"):
        client.vpcs.create_vpc(workspace_id=WS, name="x" * 81, site_id="s")
    with pytest.raises(IbeeValidationError, match="nat_billing_catalog is only allowed"):
        client.vpcs.create_vpc(workspace_id=WS, name="n", site_id="s", connectivity_type="private", nat_billing_catalog=NAT_CATALOG)
    with pytest.raises(IbeeValidationError, match="sub-range"):
        client.vpcs.create_vpc(workspace_id=WS, name="n", site_id="s", cidr="10.0.0.0/24", default_subnet_cidr="10.0.4.0/24")
    with pytest.raises(IbeeValidationError, match="connectivity_type"):
        client.vpcs.create_vpc(workspace_id=WS, name="n", site_id="s", connectivity_type="nat")
    assert client._client_wrapper.httpx_client is not None  # no request was sent


def test_create_vpc_warns_for_nat_without_catalog_and_for_public() -> None:
    router = Router().add("POST", "networking/vpcs", (201, vpc_record()))
    client = sync_client(router)
    with pytest.warns(IbeeBillingWarning):
        client.vpcs.create_vpc(workspace_id=WS, name="n", site_id="s", connectivity_type="nat_gateway")
    with pytest.warns(DeprecationWarning):
        client.vpcs.create_vpc(workspace_id=WS, name="n", site_id="s", connectivity_type="public")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        client.vpcs.create_vpc(
            workspace_id=WS, name="n", site_id="s", connectivity_type="nat_gateway", nat_billing_catalog=NAT_CATALOG
        )
    assert router.body("POST", "networking/vpcs")["nat_billing_catalog"]["sku_code"] == "NAT-GATEWAY"


def test_create_vpc_check_site() -> None:
    router = Router().add("GET", "networking/sites", (200, [{"site_id": "s", "site_name": "S", "available": False, "message": "VPC is not enabled here"}]))
    with pytest.raises(IbeeValidationError, match="VPC is not enabled here"):
        sync_client(router).vpcs.create_vpc(workspace_id=WS, name="n", site_id="s", check_site=True)
    assert router.calls() == [("GET", "networking/sites")]


def test_list_sites_available_only_and_list_vpcs_site_filter() -> None:
    router = Router()
    router.add("GET", "networking/sites", (200, [{"site_id": "a", "site_name": "A", "available": True}, {"site_id": "b", "site_name": "B", "available": False}]))
    router.add("GET", "networking/vpcs", (200, [vpc_record(connectivity_type="private")]))
    client = sync_client(router)
    assert [s.site_id for s in client.vpcs.list_networking_sites(workspace_id=WS, available_only=True)] == ["a"]
    assert len(client.vpcs.list_networking_sites(workspace_id=WS)) == 2
    assert client.vpcs.list_vpcs(workspace_id=WS, site_id=" site-1 ")[0].connectivity_type == "private"
    assert router.last("GET", "networking/vpcs").url.params["site_id"] == "site-1"
    with pytest.raises(IbeeValidationError):
        client.vpcs.list_vpcs(workspace_id=WS, site_id="  ")


def test_update_vpc_requires_a_field() -> None:
    router = Router().add("PATCH", V, (200, vpc_record()))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError, match="At least one VPC field"):
        client.vpcs.update_vpc("vpc-1", workspace_id=WS)
    client.vpcs.update_vpc("vpc-1", workspace_id=WS, name=" new ", description=" d ")
    assert router.body("PATCH", V) == {"name": "new", "description": "d"}


def test_delete_vpc_refuses_with_nodes_or_nat() -> None:
    router = Router().add("GET", V, (200, vpc_record(node_count=2)))
    with pytest.raises(IbeeValidationError, match="Detach 2 attached node"):
        sync_client(router).vpcs.delete_vpc("vpc-1", workspace_id=WS)
    router = Router().add("GET", V, (200, vpc_record(nat_gateways=[gateway()])))
    with pytest.raises(IbeeValidationError, match="Delete the NAT gateway first"):
        sync_client(router).vpcs.delete_vpc("vpc-1", workspace_id=WS)
    assert ("DELETE", V) not in router.calls()


def test_delete_vpc_deletes_nat_gateway_first_and_waits() -> None:
    router = Router()
    router.add("GET", V, [(200, vpc_record(nat_gateways=[gateway()])), (200, vpc_record(nat_gateways=[gateway(status="deleting")])), (200, vpc_record())])
    router.add("GET", f"{V}/virtual-ips", (200, []))
    router.add("DELETE", f"{V}/nat-gateways/nat-1", (204, None))
    router.add("DELETE", V, (204, None))
    assert sync_client(router).vpcs.delete_vpc("vpc-1", workspace_id=WS, delete_nat_gateway=True, wait_interval=0) is None
    assert router.calls() == [
        ("GET", V),
        ("GET", f"{V}/virtual-ips"),
        ("DELETE", f"{V}/nat-gateways/nat-1"),
        ("GET", V),
        ("GET", V),
        ("DELETE", V),
    ]
    assert router.last("DELETE", f"{V}/nat-gateways/nat-1").content == b""


def test_delete_vpc_stops_when_nat_gateway_keeps_reconciling() -> None:
    router = Router().add("GET", V, (200, vpc_record(nat_gateways=[gateway()])))
    router.add("GET", f"{V}/virtual-ips", (200, []))
    router.add("DELETE", f"{V}/nat-gateways/nat-1", (204, None))
    with pytest.raises(IbeeError, match="still reconciling") as info:
        sync_client(router).vpcs.delete_vpc("vpc-1", workspace_id=WS, delete_nat_gateway=True, wait_attempts=2, wait_interval=0)
    # Server state, not an input error: same class and code as the TypeScript SDK.
    assert type(info.value) is IbeeError and not isinstance(info.value, IbeeValidationError)
    assert info.value.code == "nat_gateway_deleting"
    assert ("DELETE", V) not in router.calls()


def test_delete_vpc_without_check_is_one_request() -> None:
    router = Router().add("DELETE", V, (204, None))
    sync_client(router).vpcs.delete_vpc("vpc-1", workspace_id=WS, check_state=False)
    assert router.calls() == [("DELETE", V)]


# subnets and nodes ------------------------------------------------------------------------


def test_create_subnet_checks_against_the_vpc() -> None:
    existing = [subnet(cidr="10.20.0.0/25")]
    router = Router().add("GET", V, (200, vpc_record(subnets=existing))).add("POST", f"{V}/subnets", (201, subnet(cidr="10.20.0.128/25")))
    client = sync_client(router)
    client.vpcs.create_vpc_subnet("vpc-1", workspace_id=WS, name=" apps ", cidr="10.20.0.128/25")
    assert router.body("POST", f"{V}/subnets") == {"name": "apps", "cidr": "10.20.0.128/25", "auto_cidr": False}
    with pytest.raises(IbeeValidationError, match="overlaps"):
        client.vpcs.create_vpc_subnet("vpc-1", workspace_id=WS, name="x", cidr="10.20.0.64/26")
    with pytest.raises(IbeeValidationError, match="only valid with automatic"):
        client.vpcs.create_vpc_subnet("vpc-1", workspace_id=WS, name="x", cidr="10.20.0.128/25", prefix_length=26)
    with pytest.raises(IbeeValidationError, match="prefix_length must be /24 or smaller"):
        client.vpcs.create_vpc_subnet("vpc-1", workspace_id=WS, name="x", prefix_length=22)
    full = Router().add("GET", V, (200, vpc_record(subnets=[subnet(subnet_id=str(i)) for i in range(10)])))
    with pytest.raises(IbeeValidationError, match="limit is 10"):
        sync_client(full).vpcs.create_vpc_subnet("vpc-1", workspace_id=WS, name="x")


def test_subnet_dns_and_update() -> None:
    router = Router().add("PATCH", f"{V}/subnets/sub-1", (200, subnet()))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError, match="At least one subnet field"):
        client.vpcs.update_vpc_subnet("vpc-1", "sub-1", workspace_id=WS)
    with pytest.raises(IbeeValidationError):
        client.vpcs.update_vpc_subnet("vpc-1", "sub-1", workspace_id=WS, dns=["dns.google"])
    client.vpcs.update_vpc_subnet("vpc-1", "sub-1", workspace_id=WS, dns=[" 9.9.9.9 "])
    assert router.body("PATCH", f"{V}/subnets/sub-1") == {"dns": ["9.9.9.9"]}


def test_attach_node_with_requested_private_ip_reads_the_subnet() -> None:
    router = Router().add("GET", f"{V}/subnets/sub-1", (200, subnet())).add("POST", f"{V}/nodes", (201, node()))
    client = sync_client(router)
    client.vpcs.attach_vpc_node("vpc-1", workspace_id=WS, vm_id="vm-1", subnet_id="sub-1", requested_private_ip=" 10.20.0.10 ")
    assert router.body("POST", f"{V}/nodes") == {"vm_id": "vm-1", "subnet_id": "sub-1", "requested_private_ip": "10.20.0.10"}
    with pytest.raises(IbeeValidationError, match="reserved for the subnet gateway"):
        client.vpcs.attach_vpc_node("vpc-1", workspace_id=WS, vm_id="vm-1", subnet_id="sub-1", requested_private_ip="10.20.0.1")
    with pytest.raises(IbeeValidationError, match="only valid with connectivity='public_ip'"):
        client.vpcs.attach_vpc_node("vpc-1", workspace_id=WS, vm_id="vm-1", subnet_id="sub-1", reserved_public_ip_id="r")


def test_attach_node_blank_requested_ip_is_omitted_and_connectivity_checked() -> None:
    router = Router().add("POST", f"{V}/nodes", (201, node())).add("GET", V, (200, vpc_record()))
    client = sync_client(router)
    client.vpcs.attach_vpc_node("vpc-1", workspace_id=WS, vm_id="vm-1", subnet_id="sub-1", requested_private_ip="  ")
    assert router.calls() == [("POST", f"{V}/nodes")]
    with pytest.raises(IbeeValidationError, match="not available for nat_gateway"):
        client.vpcs.attach_vpc_node("vpc-1", workspace_id=WS, vm_id="vm-1", subnet_id="sub-1", connectivity="public_ip", check_state=True)
    with pytest.raises(IbeeValidationError, match="available NAT gateway"):
        client.vpcs.attach_vpc_node("vpc-1", workspace_id=WS, vm_id="vm-1", subnet_id="sub-1", connectivity="nat", check_state=True)


# NAT gateways -------------------------------------------------------------------------------


def test_create_nat_gateway_only_in_nat_vpcs() -> None:
    router = Router().add("GET", V, (200, vpc_record(connectivity_type="private")))
    with pytest.raises(IbeeValidationError, match="only be created for nat_gateway VPCs"):
        sync_client(router).vpcs.create_nat_gateway("vpc-1", workspace_id=WS, billing_catalog=NAT_CATALOG)


def test_create_nat_gateway_with_reserved_ip_catalog_and_preflight() -> None:
    router = Router()
    router.add("GET", V, (200, vpc_record()))
    router.add("GET", "networking/reserved-ips/rip-1", (200, {"public_ip_id": "rip-1", "site_id": "site-1", "status": "reserved", "reservation_type": "user_reserved"}))
    router.add("POST", "billing/resource-eligibility", (200, {"allowed": True, "organization_id": "o", "reason": "ok", "sku_code": "NAT-GATEWAY"}))
    router.add("POST", f"{V}/nat-gateways", (201, gateway(public_ip_source="reserved")))
    result = sync_client(router).vpcs.create_nat_gateway(
        "vpc-1", workspace_id=WS, reserved_public_ip_id="rip-1", billing_catalog=NAT_CATALOG, preflight_billing=True
    )
    assert result.public_ip_source == "reserved"
    assert router.body("POST", f"{V}/nat-gateways") == {"reserved_public_ip_id": "rip-1", "billing_catalog": NAT_CATALOG}
    assert router.body("POST", "billing/resource-eligibility")["sku_code"] == "NAT-GATEWAY"


def test_create_nat_gateway_rejects_attached_reserved_ip_and_warns_without_catalog() -> None:
    router = Router().add("GET", V, (200, vpc_record()))
    router.add("GET", "networking/reserved-ips/rip-1", (200, {"public_ip_id": "rip-1", "site_id": "site-1", "status": "attached", "attached_resource_id": "vm-9"}))
    with pytest.raises(IbeeValidationError, match="already attached"):
        sync_client(router).vpcs.create_nat_gateway("vpc-1", workspace_id=WS, reserved_public_ip_id="rip-1", billing_catalog=NAT_CATALOG)
    router = Router().add("POST", f"{V}/nat-gateways", (201, gateway()))
    with pytest.warns(IbeeBillingWarning):
        sync_client(router).vpcs.create_nat_gateway("vpc-1", workspace_id=WS, check_state=False)


def test_nat_gateway_edge_billing_denial_is_typed() -> None:
    router = Router().add("POST", f"{V}/nat-gateways", (402, {"error": "billing_denied", "billing_reason": "insufficient_balance", "billing_sku_code": "NAT-GATEWAY"}))
    with pytest.raises(BillingDeniedError) as info:
        sync_client(router).vpcs.create_nat_gateway("vpc-1", workspace_id=WS, check_state=False, billing_catalog=NAT_CATALOG)
    assert "NAT gateway" in info.value.message


def test_preflight_forbidden_explains_billing_scope() -> None:
    router = Router().add("GET", V, (200, vpc_record()))
    router.add("POST", "billing/resource-eligibility", (403, {"detail": "Missing scope"}))
    with pytest.raises(ForbiddenError) as info:
        sync_client(router).vpcs.create_nat_gateway("vpc-1", workspace_id=WS, billing_catalog=NAT_CATALOG, preflight_billing=True)
    assert "billing.read" in info.value.message


def test_delete_nat_gateway_bodies() -> None:
    path = f"{V}/nat-gateways/nat-1"
    router = Router().add("DELETE", path, (204, None)).add("GET", f"{V}/nat-gateways", (200, [gateway()]))
    client = sync_client(router)
    assert client.vpcs.delete_nat_gateway("vpc-1", "nat-1", workspace_id=WS) is None
    assert router.last("DELETE", path).content == b""
    client.vpcs.delete_nat_gateway("vpc-1", "nat-1", workspace_id=WS, public_ip_action="release")
    assert json.loads(router.last("DELETE", path).content) == {"public_ip_action": "release"}
    with pytest.raises(IbeeValidationError, match="requires the RESERVED-IP billing_catalog"):
        client.vpcs.delete_nat_gateway("vpc-1", "nat-1", workspace_id=WS, public_ip_action="reserve")
    catalog = {"sku_id": 3, "sku_code": "RESERVED-IP"}
    client.vpcs.delete_nat_gateway("vpc-1", "nat-1", workspace_id=WS, public_ip_action="reserve", billing_catalog=catalog)
    assert json.loads(router.last("DELETE", path).content) == {"public_ip_action": "reserve", "billing_catalog": catalog}
    with pytest.raises(IbeeValidationError, match="only allowed with public_ip_action='reserve'"):
        client.vpcs.delete_nat_gateway("vpc-1", "nat-1", workspace_id=WS, public_ip_action="release", billing_catalog=catalog)
    with pytest.raises(IbeeValidationError, match="'reserve' or 'release'"):
        client.vpcs.delete_nat_gateway("vpc-1", "nat-1", workspace_id=WS, public_ip_action="keep")


def test_delete_nat_gateway_reserve_of_reserved_ip_needs_no_catalog_and_waits() -> None:
    path = f"{V}/nat-gateways/nat-1"
    router = Router().add("GET", f"{V}/nat-gateways", (200, [gateway(public_ip_source="reserved")]))
    router.add("DELETE", path, (204, None)).add("GET", V, (404, {"detail": "gone"}))
    assert sync_client(router).vpcs.delete_nat_gateway("vpc-1", "nat-1", workspace_id=WS, public_ip_action="reserve", wait=True) is True
    assert json.loads(router.last("DELETE", path).content) == {"public_ip_action": "reserve"}


def test_delete_nat_gateway_check_state_refuses_vips_with_public_ips() -> None:
    router = Router().add("GET", f"{V}/nat-gateways", (200, [gateway()])).add("GET", f"{V}/virtual-ips", (200, [vip(public_ip_id="rip-9")]))
    with pytest.raises(IbeeValidationError, match="Detach virtual-IP Reserved Public IPs"):
        sync_client(router).vpcs.delete_nat_gateway("vpc-1", "nat-1", workspace_id=WS, check_state=True)


def test_replace_nat_gateway_public_ip() -> None:
    path = f"{V}/nat-gateways/nat-1/public-ip"
    router = Router().add("PUT", path, (200, gateway(public_ip_source="reserved")))
    router.add("GET", V, (200, vpc_record(nat_gateways=[gateway()])))
    router.add("GET", "networking/reserved-ips/rip-1", (200, {"public_ip_id": "rip-1", "site_id": "site-2", "status": "reserved"}))
    client = sync_client(router)
    assert client.vpcs.replace_nat_gateway_public_ip("vpc-1", "nat-1", workspace_id=WS, reserved_public_ip_id=" rip-1 ").public_ip_source == "reserved"
    assert router.body("PUT", path) == {"reserved_public_ip_id": "rip-1"}
    with pytest.raises(IbeeValidationError, match="same site"):
        client.vpcs.replace_nat_gateway_public_ip("vpc-1", "nat-1", workspace_id=WS, reserved_public_ip_id="rip-1", check_state=True)
    with pytest.raises(IbeeValidationError):
        client.vpcs.replace_nat_gateway_public_ip("vpc-1", "nat-1", workspace_id=WS, reserved_public_ip_id=" ")


# port forwarding -------------------------------------------------------------------------------

PF = f"{V}/nat-gateways/nat-1/port-forwarding-rules"


def _pf_router(rules=None, nodes=None, vips=None) -> Router:
    router = Router()
    router.add("GET", f"{V}/nat-gateways", (200, [gateway()]))
    router.add("GET", PF, (200, rules if rules is not None else [rule()]))
    router.add("GET", f"{V}/nodes", (200, nodes if nodes is not None else [node()]))
    router.add("GET", f"{V}/virtual-ips", (200, vips if vips is not None else [vip()]))
    router.add("POST", PF, (201, rule(external_port=8080)))
    router.add("PATCH", f"{PF}/natpf-1", (200, rule()))
    return router


def test_create_pf_rule_vm_target_sends_portal_body() -> None:
    router = _pf_router()
    result = sync_client(router).vpcs.create_nat_port_forwarding_rule(
        "vpc-1", "nat-1", workspace_id=WS, name=" web ", external_port=8080, internal_ip="10.20.0.10", internal_port=80, protocol="TCP"
    )
    assert result.external_port == 8080
    assert router.body("POST", PF) == {
        "name": "web",
        "protocol": "tcp",
        "external_port": 8080,
        "internal_ip": "10.20.0.10",
        "internal_port": 80,
        "target_type": "vm",
        "target_vm_ids": [],
        "note": "",
        "enabled": True,
    }


def test_create_pf_rule_portal_checks() -> None:
    client = sync_client(_pf_router())
    kwargs = dict(workspace_id=WS, name="r", internal_ip="10.20.0.10", internal_port=22)
    with pytest.raises(IbeeValidationError, match="TCP external port 2222 already exists"):
        client.vpcs.create_nat_port_forwarding_rule("vpc-1", "nat-1", external_port=2222, **kwargs)
    with pytest.raises(IbeeValidationError, match="NAT-connected node"):
        client.vpcs.create_nat_port_forwarding_rule("vpc-1", "nat-1", external_port=80, **{**kwargs, "internal_ip": "10.20.0.99"})
    with pytest.raises(IbeeValidationError, match="whole numbers"):
        client.vpcs.create_nat_port_forwarding_rule("vpc-1", "nat-1", external_port=70000, **kwargs)
    with pytest.raises(IbeeValidationError, match="private IPv4"):
        client.vpcs.create_nat_port_forwarding_rule("vpc-1", "nat-1", external_port=80, **{**kwargs, "internal_ip": "8.8.8.8"})
    with pytest.raises(IbeeValidationError, match="only supported for VIP targets"):
        client.vpcs.create_nat_port_forwarding_rule("vpc-1", "nat-1", external_port=80, target_vm_ids=["vm-1"], **kwargs)
    unavailable = _pf_router()
    unavailable.routes[("GET", f"{V}/nat-gateways")] = [(200, [gateway(status="provisioning")])]
    with pytest.raises(IbeeValidationError, match="An active NAT gateway is required"):
        sync_client(unavailable).vpcs.create_nat_port_forwarding_rule("vpc-1", "nat-1", external_port=80, **kwargs)


def test_create_pf_rule_vip_target_fills_announcers() -> None:
    router = _pf_router()
    sync_client(router).vpcs.create_nat_port_forwarding_rule(
        "vpc-1", "nat-1", workspace_id=WS, name="lb", external_port=443, internal_ip="10.20.0.50", internal_port=443, target_type="vip"
    )
    body = router.body("POST", PF)
    assert body["target_type"] == "vip" and body["target_vm_ids"] == ["vm-1", "vm-2"]
    with pytest.raises(IbeeValidationError, match="announcer VMs"):
        sync_client(_pf_router()).vpcs.create_nat_port_forwarding_rule(
            "vpc-1", "nat-1", workspace_id=WS, name="lb", external_port=443, internal_ip="10.20.0.50", internal_port=443, target_type="vip", target_vm_ids=["vm-1"]
        )


def test_update_pf_rule() -> None:
    router = _pf_router(rules=[rule(), rule(port_forward_rule_id="natpf-2", external_port=8080)])
    client = sync_client(router)
    with pytest.raises(IbeeValidationError, match="At least one port forwarding field"):
        client.vpcs.update_nat_port_forwarding_rule("vpc-1", "nat-1", "natpf-1", workspace_id=WS)
    with pytest.raises(IbeeValidationError, match="8080 already exists"):
        client.vpcs.update_nat_port_forwarding_rule("vpc-1", "nat-1", "natpf-1", workspace_id=WS, external_port=8080)
    client.vpcs.update_nat_port_forwarding_rule("vpc-1", "nat-1", "natpf-1", workspace_id=WS, external_port=2222)
    with pytest.raises(IbeeValidationError, match="requires target_type"):
        client.vpcs.update_nat_port_forwarding_rule("vpc-1", "nat-1", "natpf-1", workspace_id=WS, target_vm_ids=["vm-1"])
    client.vpcs.update_nat_port_forwarding_rule("vpc-1", "nat-1", "natpf-1", workspace_id=WS, target_type="vm")
    assert router.body("PATCH", f"{PF}/natpf-1") == {"target_type": "vm", "target_vm_ids": []}
    client.vpcs.update_nat_port_forwarding_rule("vpc-1", "nat-1", "natpf-1", workspace_id=WS, enabled=False)
    assert router.body("PATCH", f"{PF}/natpf-1") == {"enabled": False}


# virtual IPs -------------------------------------------------------------------------------


def test_virtual_ip_list_get_and_missing() -> None:
    router = Router().add("GET", f"{V}/virtual-ips", (200, [vip()]))
    client = sync_client(router)
    assert client.vpcs.list_vpc_virtual_ips("vpc-1", workspace_id=WS)[0].announcer_vm_ids == ["vm-1", "vm-2"]
    assert client.vpcs.get_vpc_virtual_ip("vpc-1", "pvip-1", workspace_id=WS).private_ip == "10.20.0.50"
    with pytest.raises(NotFoundError) as info:
        client.vpcs.get_vpc_virtual_ip("vpc-1", "pvip-9", workspace_id=WS)
    assert "Virtual IP pvip-9 was not found" in info.value.message


def test_create_virtual_ip_checks_subnet_and_announcers() -> None:
    router = Router().add("GET", f"{V}/subnets/sub-1", (200, subnet())).add("GET", f"{V}/nodes", (200, [node(), node("vm-2", "10.20.0.11", connectivity="private")]))
    router.add("POST", f"{V}/virtual-ips", (201, vip(announcer_vm_ids=["vm-1"])))
    client = sync_client(router)
    client.vpcs.create_vpc_virtual_ip("vpc-1", workspace_id=WS, subnet_id="sub-1", private_ip="10.20.0.50", announcer_vm_ids=[" vm-1 ", "vm-1"])
    assert router.body("POST", f"{V}/virtual-ips") == {"subnet_id": "sub-1", "private_ip": "10.20.0.50", "purpose": "metallb", "announcer_vm_ids": ["vm-1"]}
    with pytest.raises(IbeeValidationError, match="NAT-connected nodes in the same subnet: vm-2"):
        client.vpcs.create_vpc_virtual_ip("vpc-1", workspace_id=WS, subnet_id="sub-1", private_ip="10.20.0.50", announcer_vm_ids=["vm-2"])
    with pytest.raises(IbeeValidationError, match="at least one NAT-connected announcer"):
        client.vpcs.create_vpc_virtual_ip("vpc-1", workspace_id=WS, subnet_id="sub-1", private_ip="10.20.0.50")
    with pytest.raises(IbeeValidationError, match="network or broadcast"):
        client.vpcs.create_vpc_virtual_ip("vpc-1", workspace_id=WS, subnet_id="sub-1", private_ip="10.20.0.255", announcer_vm_ids=["vm-1"])


def test_delete_virtual_ip_guard() -> None:
    router = Router().add("GET", f"{V}/virtual-ips", (200, [vip(public_ip_id="rip-1"), vip(virtual_ip_id="pvip-2")]))
    router.add("GET", f"{V}/nat-gateways", (200, []))
    router.add("DELETE", f"{V}/virtual-ips/pvip-2", (204, None))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError, match="Detach the Reserved IP before deleting this reservation"):
        client.vpcs.delete_vpc_virtual_ip("vpc-1", "pvip-1", workspace_id=WS)
    assert client.vpcs.delete_vpc_virtual_ip("vpc-1", "pvip-2", workspace_id=WS) is None


# async parity -------------------------------------------------------------------------------


def test_async_vpc_flows() -> None:
    router = Router()
    router.add("GET", V, [(200, vpc_record(nat_gateways=[gateway()])), (200, vpc_record())])
    router.add("DELETE", f"{V}/nat-gateways/nat-1", (204, None))
    router.add("DELETE", V, (204, None))
    router.add("GET", f"{V}/virtual-ips", [(200, []), (200, [vip()])])
    router.add("POST", "networking/vpcs", (201, vpc_record(connectivity_type="private")))

    async def run() -> None:
        async with async_transport(router) as http_client:
            client = async_client(router, http_client)
            await client.vpcs.delete_vpc("vpc-1", workspace_id=WS, delete_nat_gateway=True, wait_interval=0)
            assert (await client.vpcs.get_vpc_virtual_ip("vpc-1", "pvip-1", workspace_id=WS)).virtual_ip_id == "pvip-1"
            await client.vpcs.create_vpc(workspace_id=WS, name="n", site_id="s", cidr="192.168.4.0/22", connectivity_type="private")
            with pytest.raises(IbeeValidationError):
                await client.vpcs.create_vpc(workspace_id=WS, name="n", site_id="s", cidr="192.168.5.0/22")

    asyncio.run(run())
    assert ("DELETE", V) in router.calls()
    assert router.body("POST", "networking/vpcs")["cidr"] == "192.168.4.0/22"
