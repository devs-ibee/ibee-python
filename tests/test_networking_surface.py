"""Request-shape coverage for the generated public networking clients."""

from __future__ import annotations

import httpx

from ibee import Ibee
from ibee.environment import IbeeEnvironment


def test_networking_resources_use_the_public_contract_paths() -> None:
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=[])

    with httpx.Client(transport=httpx.MockTransport(handle)) as http_client:
        client = Ibee(token="test", httpx_client=http_client)
        assert client.vpcs.list_networking_sites(workspace_id="973318") == []
        assert client.vpcs.list_vpcs(workspace_id="973318") == []
        assert client.reserved_ips.list_reserved_ips(workspace_id="973318") == []
        assert client.firewalls.list_firewall_groups(workspace_id="973318") == []
        assert client.load_balancers.list_load_balancers(workspace_id="973318") == []

    assert [request.url.path for request in requests] == [
        "/v1/networking/sites",
        "/v1/networking/vpcs",
        "/v1/networking/reserved-ips",
        "/v1/networking/firewall-groups",
        "/v1/networking/load-balancers",
    ]
    assert all(request.url.params["workspace_id"] == "973318" for request in requests)


def test_both_api_environments_are_explicit() -> None:
    assert IbeeEnvironment.PRODUCTION.value == "https://api.ibee.ai/v1"
    assert IbeeEnvironment.DEVELOPMENT.value == "https://api.ibee.co.in/v1"
