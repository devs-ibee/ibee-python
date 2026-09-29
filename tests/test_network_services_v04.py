"""0.4.0 portal-parity Reserved IPs, firewalls and load balancers."""

from __future__ import annotations

import asyncio
import json

import pytest

from _compute_fixtures import WS, Router, async_client, async_transport, sync_client
from ibee import IbeeValidationError, LoadBalancerBackend, LoadBalancerTls
from ibee.errors import BillingDeniedError, NotFoundError, ReservedIpTargetUnsupportedError
from ibee.validation import (
    build_lb_body,
    normalize_ipv4_remote_targets,
    parse_port_range,
    reserved_ip_attachment_kind,
    validate_reverse_dns,
)

TS = "2026-09-01T10:00:00Z"
RIP = "networking/reserved-ips/rip-1"
CATALOG = {"sku_id": 3, "sku_code": "RESERVED-IP", "unit_price_minor": 100, "billing_options": [1]}
ALLOWED = {"allowed": True, "organization_id": "o", "reason": "ok", "sku_code": "RESERVED-IP"}


def rip(**overrides):
    record = {
        "public_ip_id": "rip-1",
        "address": "203.0.113.10",
        "site_id": "site-1",
        "status": "reserved",
        "reservation_type": "user_reserved",
        "created_at": TS,
        "updated_at": TS,
    }
    record.update(overrides)
    return record


# Reserved IPs ------------------------------------------------------------------------------


def test_reserve_ip_body_and_optional_billing_check() -> None:
    router = Router().add("POST", "networking/reserved-ips", (201, rip()))
    router.add("POST", "billing/resource-eligibility", (200, ALLOWED))
    client = sync_client(router)
    client.reserved_ips.reserve_ip(workspace_id=WS, site_id=" site-1 ", label="  web  ", billing_catalog=CATALOG)
    assert router.body("POST", "networking/reserved-ips") == {
        "site_id": "site-1",
        "label": "web",
        "billing_catalog": {"sku_id": 3, "sku_code": "RESERVED-IP", "unit_price_minor": 100},
    }
    assert router.calls() == [("POST", "networking/reserved-ips")]
    client.reserved_ips.reserve_ip(workspace_id=WS, site_id="site-1", check_billing=True)
    assert ("POST", "billing/resource-eligibility") not in router.calls()
    with pytest.raises(IbeeValidationError, match="Choose a location"):
        client.reserved_ips.reserve_ip(workspace_id=WS, site_id=" ")
    with pytest.raises(IbeeValidationError, match="120"):
        client.reserved_ips.reserve_ip(workspace_id=WS, site_id="s", label="x" * 121)
    with pytest.raises(IbeeValidationError, match="sku_id"):
        client.reserved_ips.reserve_ip(workspace_id=WS, site_id="s", billing_catalog={"sku_code": "RESERVED-IP"})


def test_reserve_ip_edge_denial_is_typed() -> None:
    router = Router().add("POST", "networking/reserved-ips", (402, {"error": "billing_denied", "billing_reason": "initial_topup_required", "billing_sku_code": "RESERVED-IP"}))
    with pytest.raises(BillingDeniedError) as info:
        sync_client(router).reserved_ips.reserve_ip(workspace_id=WS, site_id="site-1")
    assert "Reserved IP" in info.value.message


def test_update_reserved_ip_rules() -> None:
    router = Router().add("PATCH", RIP, (200, rip()))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError, match="At least one Reserved IP field"):
        client.reserved_ips.update_reserved_ip("rip-1", workspace_id=WS)
    client.reserved_ips.update_reserved_ip("rip-1", workspace_id=WS, reverse_dns="")
    assert router.body("PATCH", RIP) == {"reverse_dns": ""}
    client.reserved_ips.update_reserved_ip("rip-1", workspace_id=WS, reverse_dns=" host.example.com. ", label=" a ")
    assert router.body("PATCH", RIP) == {"label": "a", "reverse_dns": "host.example.com."}
    for bad in ("-bad.example.com", "a" * 64 + ".com", "under_score.example.com", ("a." * 127) + "com"):
        with pytest.raises(IbeeValidationError, match="valid FQDN"):
            validate_reverse_dns(bad)
    assert validate_reverse_dns("bücher.example") == "bücher.example"


def test_release_refuses_while_attached() -> None:
    router = Router().add("GET", RIP, [(200, rip(attached_resource_id="nat-1", attached_resource_type="nat_gateway")), (200, rip(attached_resource_id="vm-1", attached_resource_type="vm")), (200, rip())])
    router.add("DELETE", RIP, (204, None))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError, match="Change or delete the NAT Gateway"):
        client.reserved_ips.release_reserved_ip("rip-1", workspace_id=WS)
    with pytest.raises(IbeeValidationError, match="Detach this IP before releasing it"):
        client.reserved_ips.release_reserved_ip("rip-1", workspace_id=WS)
    assert client.reserved_ips.release_reserved_ip("rip-1", workspace_id=WS) is None
    assert router.calls()[-1] == ("DELETE", RIP)


def test_attach_reserved_ip_states() -> None:
    router = Router().add("GET", RIP, [(200, rip(attached_resource_id="nat-1", attached_resource_type="nat_gateway")), (200, rip(attached_resource_id="nat-1", attached_resource_type="nat_gateway")), (200, rip(attached_resource_id="vm-2", attached_resource_type="vm"))])
    router.add("POST", f"{RIP}/detach", (200, rip()))
    router.add("POST", f"{RIP}/attach", (200, rip(status="attached")))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError, match="detach_from_service=True"):
        client.reserved_ips.attach_reserved_ip("rip-1", workspace_id=WS, vm_id="vm-1")
    client.reserved_ips.attach_reserved_ip("rip-1", workspace_id=WS, vm_id=" vm-1 ", detach_from_service=True)
    assert router.calls()[-2:] == [("POST", f"{RIP}/detach"), ("POST", f"{RIP}/attach")]
    assert router.body("POST", f"{RIP}/attach") == {"vm_id": "vm-1"}
    with pytest.raises(IbeeValidationError, match="use move_reserved_ip"):
        client.reserved_ips.attach_reserved_ip("rip-1", workspace_id=WS, vm_id="vm-1")


def test_attach_to_non_vpc_vm_raises_typed_error() -> None:
    router = Router().add("GET", RIP, (200, rip()))
    router.add("POST", f"{RIP}/attach", (404, {"detail": "Reserved IP attach and move require a VPC network allocation; use /public-ips/convert"}))
    with pytest.raises(ReservedIpTargetUnsupportedError) as info:
        sync_client(router).reserved_ips.attach_reserved_ip("rip-1", workspace_id=WS, vm_id="vm-1")
    assert isinstance(info.value, NotFoundError)
    assert "convert_vm_public_ip_to_reserved_ip" in info.value.message
    other = Router().add("GET", RIP, (200, rip())).add("POST", f"{RIP}/attach", (404, {"detail": "VM not found"}))
    with pytest.raises(NotFoundError) as info2:
        sync_client(other).reserved_ips.attach_reserved_ip("rip-1", workspace_id=WS, vm_id="vm-1")
    assert not isinstance(info2.value, ReservedIpTargetUnsupportedError)


def test_move_reserved_ip_rules() -> None:
    cases = [
        (rip(), "not attached"),
        (rip(attached_resource_id="pvip-1", attached_resource_type="vpc_virtual_ip"), "Detach from the NAT gateway/VIP"),
        (rip(attached_resource_id="vm-1", attached_resource_type="vm", allocation_method="converted"), "converted or provider-network"),
        (rip(attached_resource_id="vm-1", attached_resource_type="vm", attached_network_id="net-1"), "converted or provider-network"),
        (rip(attached_resource_id="vm-2", attached_resource_type="vm", attached_allocation_id="a"), "already attached to that VM"),
    ]
    for record, message in cases:
        router = Router().add("GET", RIP, (200, record))
        with pytest.raises(IbeeValidationError, match=message):
            sync_client(router).reserved_ips.move_reserved_ip("rip-1", workspace_id=WS, vm_id="vm-2")
    router = Router().add("GET", RIP, (200, rip(attached_resource_id="vm-1", attached_resource_type="vm", attached_allocation_id="a")))
    router.add("POST", f"{RIP}/move", (200, rip()))
    sync_client(router).reserved_ips.move_reserved_ip("rip-1", workspace_id=WS, vm_id="vm-2", vpc_id="vpc-1", subnet_id="sub-1")
    assert router.body("POST", f"{RIP}/move") == {"vm_id": "vm-2", "vpc_id": "vpc-1", "subnet_id": "sub-1"}


def test_detach_reserved_ip_noop_and_converted_guard() -> None:
    router = Router().add("GET", RIP, (200, rip()))
    assert sync_client(router).reserved_ips.detach_reserved_ip("rip-1", workspace_id=WS).public_ip_id == "rip-1"
    assert router.calls() == [("GET", RIP)]
    router = Router().add("GET", RIP, (200, rip(attached_resource_id="vm-1", attached_resource_type="vm", allocation_method="converted")))
    with pytest.raises(IbeeValidationError, match="still the VM's active public IP"):
        sync_client(router).reserved_ips.detach_reserved_ip("rip-1", workspace_id=WS)
    router = Router().add("GET", RIP, (200, rip(attached_resource_id="nat-1", attached_resource_type="nat_gateway")))
    router.add("POST", f"{RIP}/detach", (200, rip()))
    sync_client(router).reserved_ips.detach_reserved_ip("rip-1", workspace_id=WS)
    assert router.calls()[-1] == ("POST", f"{RIP}/detach")


def test_attachment_kind() -> None:
    assert reserved_ip_attachment_kind(rip()) == "none"
    assert reserved_ip_attachment_kind(rip(attached_resource_id="n", attached_resource_type="nat_gateway")) == "nat_gateway"
    assert reserved_ip_attachment_kind(rip(attached_resource_id="v", attached_resource_type="vm", attached_network_id="x")) == "direct"
    assert reserved_ip_attachment_kind(rip(attached_resource_id="v", attached_resource_type="vm", allocation_method="converted")) == "converted_active"
    assert reserved_ip_attachment_kind(rip(attached_resource_id="v", attached_resource_type="vm", attached_allocation_id="a")) == "vpc"


def test_convert_vm_public_ip_runs_billing_check_by_default() -> None:
    router = Router().add("POST", "billing/resource-eligibility", (200, ALLOWED))
    router.add("POST", "networking/reserved-ips/convert", (201, rip(allocation_method="converted")))
    result = sync_client(router).reserved_ips.convert_vm_public_ip_to_reserved_ip(
        workspace_id=WS, vm_id=" vm-1 ", site_id="site-1", label=" keep ", billing_catalog=CATALOG
    )
    assert result.allocation_method == "converted"
    assert router.calls() == [("POST", "networking/reserved-ips/convert")]
    assert router.body("POST", "networking/reserved-ips/convert") == {
        "vm_id": "vm-1",
        "site_id": "site-1",
        "label": "keep",
        "billing_catalog": {"sku_id": 3, "sku_code": "RESERVED-IP", "unit_price_minor": 100},
    }
    denied = Router().add("POST", "networking/reserved-ips/convert", (402, {"error": "billing_denied", "billing_reason": "insufficient_balance"}))
    with pytest.raises(BillingDeniedError):
        sync_client(denied).reserved_ips.convert_vm_public_ip_to_reserved_ip(workspace_id=WS, vm_id="vm-1", site_id="site-1")
    assert denied.calls() == [("POST", "networking/reserved-ips/convert")]
    skip = Router().add("POST", "networking/reserved-ips/convert", (201, rip()))
    sync_client(skip).reserved_ips.convert_vm_public_ip_to_reserved_ip(workspace_id=WS, vm_id="vm-1", site_id="site-1", billing_check=False)
    assert skip.calls() == [("POST", "networking/reserved-ips/convert")]


def test_attach_reserved_ip_to_virtual_ip() -> None:
    router = Router().add("GET", RIP, [(200, rip(attached_resource_id="vm-1", attached_resource_type="vm")), (200, rip())])
    router.add("POST", f"{RIP}/attach-virtual-ip", (200, rip(attached_resource_type="vpc_virtual_ip")))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError, match="choose an unattached address"):
        client.reserved_ips.attach_reserved_ip_to_virtual_ip("rip-1", workspace_id=WS, virtual_ip_id="pvip-1")
    client.reserved_ips.attach_reserved_ip_to_virtual_ip("rip-1", workspace_id=WS, virtual_ip_id=" pvip-1 ")
    assert router.body("POST", f"{RIP}/attach-virtual-ip") == {"virtual_ip_id": "pvip-1"}


# Firewalls -------------------------------------------------------------------------------

FW = "networking/firewall-groups"


def summary(i: int, name: str = "") -> dict:
    return {"firewall_group_id": f"fw-{i}", "name": name or f"group-{i}", "status": "active", "is_default": False, "rule_count": 2}


def group(**overrides):
    record = {
        "firewall_group_id": "fw-1",
        "organization_id": "o",
        "workspace_id": WS,
        "name": "web",
        "is_default": False,
        "status": "active",
        "rules": [
            {"rule_id": "sys-1", "protocol": "tcp", "port_start": 22, "system_managed": True, "enabled": True, "created_at": TS, "updated_at": TS},
            {"rule_id": "r-1", "protocol": "tcp", "port_start": 80, "system_managed": False, "enabled": True, "created_at": TS, "updated_at": TS},
        ],
        "created_at": TS,
        "updated_at": TS,
    }
    record.update(overrides)
    return record


def test_firewall_summaries_page_through_everything() -> None:
    router = Router().add("GET", FW, [(200, [summary(i) for i in range(100)]), (200, [summary(i) for i in range(100, 103)])])
    items = sync_client(router).firewalls.list_firewall_group_summaries(workspace_id=WS)
    assert len(items) == 103 and items[0].rule_count == 2
    params = [dict(r.url.params) for r in router.requests]
    assert params[0] == {"workspace_id": WS, "summary": "true", "limit": "100", "offset": "0"}
    assert params[1]["offset"] == "100"
    one = Router().add("GET", FW, (200, [summary(1)]))
    sync_client(one).firewalls.list_firewall_group_summaries(workspace_id=WS, limit=5)
    assert dict(one.requests[0].url.params) == {"workspace_id": WS, "summary": "true", "limit": "5", "offset": "0"}


def test_create_firewall_group_rules() -> None:
    router = Router().add("GET", FW, (200, [summary(1, "Web")])).add("POST", FW, (201, group(name="api")))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError, match="already exists"):
        client.firewalls.create_firewall_group(workspace_id=WS, name=" web ")
    with pytest.raises(IbeeValidationError, match="platform-managed"):
        client.firewalls.create_firewall_group(workspace_id=WS, name="api", is_default=True)
    with pytest.raises(IbeeValidationError, match="120 characters"):
        client.firewalls.create_firewall_group(workspace_id=WS, name="x" * 121)
    client.firewalls.create_firewall_group(workspace_id=WS, name=" api ", description="  ", is_default=False)
    assert router.body("POST", FW) == {"name": "api"}


def test_firewall_rule_bodies() -> None:
    router = Router().add("POST", f"{FW}/fw-1/rules", (201, group()))
    client = sync_client(router)
    client.firewalls.create_firewall_rule("fw-1", workspace_id=WS, port_start=22)
    assert router.body("POST", f"{FW}/fw-1/rules") == {
        "protocol": "tcp",
        "port_start": 22,
        "port_end": 22,
        "remote_targets": ["0.0.0.0/0"],
        "action": "allow",
        "direction": "ingress",
    }
    client.firewalls.create_firewall_rule("fw-1", workspace_id=WS, protocol="icmp", remote_targets=["10.0.0.5", "10.0.0.0/8", "10.1.2.3/8"], description=" ping ")
    body = router.body("POST", f"{FW}/fw-1/rules")
    assert body["remote_targets"] == ["10.0.0.5/32", "10.0.0.0/8"] and "port_start" not in body and body["description"] == "ping"
    with pytest.raises(IbeeValidationError, match="Port is required for TCP and UDP"):
        client.firewalls.create_firewall_rule("fw-1", workspace_id=WS, protocol="udp")
    with pytest.raises(IbeeValidationError, match="not used by any rules"):
        client.firewalls.create_firewall_rule("fw-1", workspace_id=WS, protocol="any", port_start=1)
    with pytest.raises(IbeeValidationError, match="greater than or equal"):
        client.firewalls.create_firewall_rule("fw-1", workspace_id=WS, port_start=90, port_end=80)
    with pytest.raises(IbeeValidationError, match="Any, TCP, UDP, and ICMP"):
        client.firewalls.create_firewall_rule("fw-1", workspace_id=WS, protocol="gre")
    with pytest.raises(IbeeValidationError, match="Only IPv4"):
        client.firewalls.create_firewall_rule("fw-1", workspace_id=WS, port_start=22, remote_targets=["::/0"])


def test_firewall_rule_update_and_delete_protect_system_rules() -> None:
    router = Router().add("GET", f"{FW}/fw-1", (200, group()))
    router.add("PATCH", f"{FW}/fw-1/rules/r-1", (200, group())).add("DELETE", f"{FW}/fw-1/rules/r-1", (200, group()))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError, match="cannot be updated"):
        client.firewalls.update_firewall_rule("fw-1", "sys-1", workspace_id=WS, enabled=False)
    with pytest.raises(IbeeValidationError, match="cannot be removed"):
        client.firewalls.delete_firewall_rule("fw-1", "sys-1", workspace_id=WS)
    with pytest.raises(IbeeValidationError, match="At least one firewall rule field"):
        client.firewalls.update_firewall_rule("fw-1", "r-1", workspace_id=WS)
    with pytest.raises(IbeeValidationError, match="Port is required"):
        client.firewalls.update_firewall_rule("fw-1", "r-1", workspace_id=WS, protocol="udp")
    client.firewalls.update_firewall_rule("fw-1", "r-1", workspace_id=WS, enabled=False)
    assert router.body("PATCH", f"{FW}/fw-1/rules/r-1") == {"enabled": False}
    client.firewalls.delete_firewall_rule("fw-1", "r-1", workspace_id=WS)
    assert router.calls()[-1] == ("DELETE", f"{FW}/fw-1/rules/r-1")


def test_firewall_attachments_paging_and_attach() -> None:
    router = Router().add("GET", f"{FW}/fw-1/attachments", (200, [])).add("POST", f"{FW}/fw-1/attachments", (200, group()))
    client = sync_client(router)
    client.firewalls.list_firewall_group_attachments("fw-1", workspace_id=WS, limit=500, skip=0)
    with pytest.raises(IbeeValidationError):
        client.firewalls.list_firewall_group_attachments("fw-1", workspace_id=WS, limit=501)
    client.firewalls.attach_firewall_group("fw-1", workspace_id=WS, vm_id=" vm-1 ")
    assert router.body("POST", f"{FW}/fw-1/attachments") == {"vm_id": "vm-1"}


def test_port_and_target_helpers() -> None:
    assert parse_port_range(" 22 ") == (22, 22)
    assert parse_port_range("8000 - 8080") == (8000, 8080)
    for bad in ("0", "22-", "90-80", "abc", "70000"):
        with pytest.raises(IbeeValidationError):
            parse_port_range(bad)
    assert normalize_ipv4_remote_targets("10.0.0.1, 10.0.0.1/32") == ["10.0.0.1/32"]


# Load balancers -------------------------------------------------------------------------------

LB = "networking/load-balancers"


def lb(**overrides):
    record = {
        "lb_id": "lb-1",
        "organization_id": "o",
        "workspace_id": WS,
        "name": "web",
        "layer": "l7",
        "protocol": "https",
        "status": "active",
        "endpoint": {"host": "x", "port": 443},
        "url": "https://x",
        "endpoint_url": "https://x",
        "backends": [],
        "created_at": TS,
        "updated_at": TS,
        "custom_domain": {"hostname": "app.example.com", "cname_target": "lb.ibee.example"},
    }
    record.update(overrides)
    return record


def test_list_load_balancers_filters() -> None:
    router = Router().add("GET", LB, (200, [lb()]))
    client = sync_client(router)
    items = client.load_balancers.list_load_balancers(workspace_id=WS, status="deleted", layer="l7", protocol="https", limit=10)
    assert items[0].custom_domain.cname_target == "lb.ibee.example"
    assert dict(router.requests[0].url.params) == {"workspace_id": WS, "status": "deleted", "layer": "l7", "protocol": "https", "include_deleted": "true", "limit": "10"}
    with pytest.raises(IbeeValidationError, match="protocol"):
        client.load_balancers.list_load_balancers(workspace_id=WS, layer="l4", protocol="https")
    with pytest.raises(IbeeValidationError):
        client.load_balancers.list_load_balancers(workspace_id=WS, limit=501)


def test_create_l4_defaults_tls_and_validates_policy() -> None:
    router = Router().add("POST", f"{LB}/l4", (201, lb(layer="l4", protocol="tls_passthrough")))
    client = sync_client(router)
    client.load_balancers.create_l4load_balancer(
        workspace_id=WS,
        name=" tcp ",
        protocol="tls_passthrough",
        backends=[LoadBalancerBackend(target=" api ", port=443), {"type": "ip", "target": "10.0.0.5", "port": 443, "weight": 5}],
        policy={"timeout_ms": 1000, "retries": {"attempts": 2}},
        health_check={"active": {"type": "tcp", "interval_ms": 5000}},
    )
    body = router.body("POST", f"{LB}/l4")
    assert body["name"] == "tcp"
    assert body["tls"] == {"mode": "passthrough", "certificate_source": "managed"}
    assert body["backends"] == [
        {"type": "service", "target": "api", "port": 443, "weight": 100, "tls": False},
        {"type": "ip", "target": "10.0.0.5", "port": 443, "weight": 5, "tls": False},
    ]
    assert body["policy"] == {"timeout_ms": 1000, "retries": {"attempts": 2, "per_retry_timeout_ms": 5000, "on": ["5xx", "reset", "connect-failure"]}}
    assert body["health_check"] == {"active": {"type": "tcp", "interval_ms": 5000}}
    assert "health_check" not in build_lb_body(layer="l4", name="n", protocol="tcp", backends=[{"target": "a", "port": 1}])


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"protocol": "http"}, "protocol"),
        ({"backends": []}, "at least one backend"),
        ({"backends": [{"type": "ip", "target": "nope", "port": 1}]}, "valid IP address"),
        ({"backends": [{"type": "hostname", "target": "localhost", "port": 1}]}, "fully qualified hostname"),
        ({"backends": [{"target": "svc:80", "port": 1}]}, "without a slash or port"),
        ({"backends": [{"target": "svc", "port": 0}]}, "port"),
        ({"backends": [{"target": "svc", "port": 1, "weight": 1001}]}, "weight"),
        ({"routing": {"sticky_header": "X-User-ID"}}, "only available on L7"),
        ({"policy": {"timeout_ms": 50}}, "timeout_ms"),
        ({"policy": {"bogus": 1}}, "Unknown policy"),
        ({"health_check": {"active": {"type": "tcp", "path": "/x"}}}, "not supported for tcp"),
        ({"health_check": {"passive": {"base_ejection_time_ms": 10}}}, "base_ejection_time_ms"),
        ({"tls": {"mode": "passthrough", "certificate_source": "custom"}}, "Custom certificates"),
        ({"protocol": "tcp", "tls": {"mode": "passthrough"}}, "not supported for tcp"),
    ],
)
def test_create_l4_rejections(overrides, message) -> None:
    kwargs = dict(workspace_id=WS, name="n", protocol="tls_passthrough", backends=[{"target": "svc", "port": 80}])
    kwargs.update(overrides)
    with pytest.raises(IbeeValidationError, match=message):
        sync_client(Router()).load_balancers.create_l4load_balancer(**kwargs)


def test_create_l7_https_defaults_rules_and_custom_domain() -> None:
    router = Router().add("POST", f"{LB}/l7", (201, lb())).add("POST", "billing/resource-eligibility", (200, {**ALLOWED, "sku_code": "LOADBALA-STD"}))
    client = sync_client(router)
    client.load_balancers.create_l7load_balancer(
        workspace_id=WS,
        name="web",
        protocol="https",
        backends=[{"target": "web", "port": 8080}],
        routing={"algorithm": "least_request", "sticky_header": " X-User-ID "},
        rules=[{"priority": 1, "path_prefix": " ", "headers": {" x-env ": " prod "}}],
        custom_domain={"hostname": " App.Example.com. "},
        observability={"logs_enabled": True},
        check_billing=True,
    )
    body = router.body("POST", f"{LB}/l7")
    assert ("POST", "billing/resource-eligibility") not in router.calls()
    assert body["tls"] == {"mode": "terminate", "certificate_source": "managed"}
    assert body["routing"] == {"algorithm": "least_request", "sticky_header": "X-User-ID"}
    assert body["rules"] == [{"priority": 1, "path_prefix": "/", "headers": {"x-env": "prod"}}]
    assert body["custom_domain"] == {"hostname": "app.example.com"}
    assert body["observability"] == {"logs_enabled": True}
    with pytest.raises(IbeeValidationError, match="only supported for l7 https"):
        client.load_balancers.create_l7load_balancer(workspace_id=WS, name="w", protocol="http", backends=[{"target": "w", "port": 80}], custom_domain={"hostname": "a.b.com"})
    with pytest.raises(IbeeValidationError, match="must start with '/'"):
        client.load_balancers.create_l7load_balancer(workspace_id=WS, name="w", protocol="http", backends=[{"target": "w", "port": 80}], rules=[{"path_prefix": "api"}])
    with pytest.raises(IbeeValidationError, match="Custom certificates"):
        client.load_balancers.create_l7load_balancer(workspace_id=WS, name="w", protocol="https", backends=[{"target": "w", "port": 80}], tls=LoadBalancerTls(mode="terminate", certificate_source="custom", cert_pem="x", key_pem="y"))


def test_update_load_balancers() -> None:
    router = Router().add("PATCH", f"{LB}/l7/lb-1", (200, lb())).add("PATCH", f"{LB}/l4/lb-1", (200, lb(layer="l4", protocol="tcp")))
    client = sync_client(router)
    client.load_balancers.update_l7load_balancer("lb-1", workspace_id=WS, custom_domain=None)
    assert json.loads(router.last("PATCH", f"{LB}/l7/lb-1").content) == {"custom_domain": None}
    client.load_balancers.update_l7load_balancer("lb-1", workspace_id=WS, name=" n ", policy={"proxy_protocol_enabled": True})
    assert router.body("PATCH", f"{LB}/l7/lb-1") == {"name": "n", "policy": {"proxy_protocol_enabled": True}}
    with pytest.raises(IbeeValidationError, match="At least one load balancer field"):
        client.load_balancers.update_l7load_balancer("lb-1", workspace_id=WS)
    with pytest.raises(IbeeValidationError, match="only available on L7"):
        build_lb_body(layer="l4", update=True, rules=[{"path_prefix": "/"}])
    client.load_balancers.update_l4load_balancer("lb-1", workspace_id=WS, health_check={"active": {"type": "http", "path": "/ready"}})
    assert router.body("PATCH", f"{LB}/l4/lb-1") == {"health_check": {"active": {"type": "http", "path": "/ready"}}}


def test_get_load_balancer_include_deleted() -> None:
    router = Router().add("GET", f"{LB}/lb-1", (200, lb(deleted_at=TS, deleted_by="u")))
    result = sync_client(router).load_balancers.get_load_balancer("lb-1", workspace_id=WS, include_deleted=True)
    assert result.deleted_by == "u"
    assert router.requests[0].url.params["include_deleted"] == "true"


def test_async_network_services_parity() -> None:
    router = Router()
    router.add("GET", RIP, (200, rip(attached_resource_id="nat-1", attached_resource_type="nat_gateway")))
    router.add("GET", FW, (200, [summary(1)]))
    router.add("POST", f"{LB}/l4", (201, lb(layer="l4", protocol="tcp")))

    async def run() -> None:
        async with async_transport(router) as http_client:
            client = async_client(router, http_client)
            with pytest.raises(IbeeValidationError, match="NAT Gateway"):
                await client.reserved_ips.release_reserved_ip("rip-1", workspace_id=WS)
            assert len(await client.firewalls.list_firewall_group_summaries(workspace_id=WS)) == 1
            await client.load_balancers.create_l4load_balancer(workspace_id=WS, name="t", protocol="tcp", backends=[{"target": "svc", "port": 80}])
            with pytest.raises(IbeeValidationError):
                await client.load_balancers.update_l4load_balancer("lb-1", workspace_id=WS)

    asyncio.run(run())
    assert "tls" not in router.body("POST", f"{LB}/l4")
