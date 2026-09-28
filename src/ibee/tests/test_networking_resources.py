from __future__ import annotations

import json

import httpx

from ibee import Ibee


def _client(handler) -> Ibee:
    return Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def test_networking_resources_expose_the_complete_public_surface() -> None:
    client = _client(lambda request: httpx.Response(200, json=[], request=request))

    assert {
        "list_networking_sites",
        "list_vpcs",
        "create_vpc",
        "get_vpc",
        "update_vpc",
        "delete_vpc",
        "list_vpc_subnets",
        "create_vpc_subnet",
        "get_vpc_subnet",
        "update_vpc_subnet",
        "delete_vpc_subnet",
        "list_vpc_nodes",
        "attach_vpc_node",
        "detach_vpc_node",
        "list_nat_gateways",
        "create_nat_gateway",
        "delete_nat_gateway",
        "list_nat_port_forwarding_rules",
        "create_nat_port_forwarding_rule",
        "update_nat_port_forwarding_rule",
        "delete_nat_port_forwarding_rule",
    } <= set(dir(client.vpcs))
    assert {
        "list_reserved_ips",
        "reserve_ip",
        "get_reserved_ip",
        "update_reserved_ip",
        "release_reserved_ip",
        "attach_reserved_ip",
        "move_reserved_ip",
        "detach_reserved_ip",
    } <= set(dir(client.reserved_ips))
    assert {
        "list_firewall_groups",
        "create_firewall_group",
        "get_firewall_group",
        "delete_firewall_group",
        "create_firewall_rule",
        "update_firewall_rule",
        "delete_firewall_rule",
        "list_firewall_group_attachments",
        "attach_firewall_group",
        "detach_firewall_group",
    } <= set(dir(client.firewalls))
    assert {
        "list_load_balancers",
        "create_l4load_balancer",
        "create_l7load_balancer",
        "get_load_balancer",
        "delete_load_balancer",
        "update_l4load_balancer",
        "update_l7load_balancer",
        "get_load_balancer_status",
    } <= set(dir(client.load_balancers))


def test_networking_request_uses_public_path_workspace_and_bearer_token() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(
            200,
            json=[
                {
                    "site_id": "site_blr_01",
                    "site_name": "Bengaluru",
                    "available": True,
                }
            ],
            request=request,
        )

    result = _client(handler).vpcs.list_networking_sites(workspace_id="607005")

    assert result[0].site_id == "site_blr_01"
    assert observed[0].url.path == "/v1/networking/sites"
    assert observed[0].url.params["workspace_id"] == "607005"
    assert observed[0].headers["authorization"] == "Bearer test-token"


def test_move_reserved_ip_uses_move_path_and_attachment_payload() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(
            200,
            json={
                "public_ip_id": "ip1",
                "address": "203.0.113.10",
                "site_id": "site1",
                "status": "attached",
                "created_at": "2026-07-31T00:00:00Z",
                "updated_at": "2026-07-31T00:00:00Z",
            },
            request=request,
        )

    result = _client(handler).reserved_ips.move_reserved_ip(
        "ip1",
        workspace_id="607005",
        vm_id="vm2",
        vpc_id="vpc1",
        subnet_id="subnet1",
        check_state=False,  # 0.4.0 reads the IP first by default; this test covers the request shape only
    )

    assert result.public_ip_id == "ip1"
    assert observed[0].url.path == "/v1/networking/reserved-ips/ip1/move"
    assert json.loads(observed[0].content) == {
        "vm_id": "vm2",
        "vpc_id": "vpc1",
        "subnet_id": "subnet1",
    }
