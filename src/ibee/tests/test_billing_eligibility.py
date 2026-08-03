from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from ibee import AsyncIbee, BillingEligibility, Ibee
from ibee.errors import ForbiddenError


def _decision(*, allowed: bool = True) -> dict[str, object]:
    return {
        "organization_id": "organizations-250612",
        "allowed": allowed,
        "reason": "eligible" if allowed else "insufficient_balance",
        "billing_mode": "PREPAID",
        "billing_state": "CURRENT",
        "currency": "INR",
        "sku_code": "vm.standard-2x4",
        "estimated_cost_minor": 12_500,
        "effective_balance_minor": 50_000,
        "credit_headroom_minor": 0,
        "evaluated_at": "2026-08-04T10:00:00Z",
    }


def test_billing_eligibility_is_explicit_typed_preflight() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json=_decision(), request=request)

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = client.billing.check_resource_eligibility(
        workspace_id="workspaces-710995",
        sku_code="vm.standard-2x4",
        estimated_cost_minor=12_500,
    )

    assert isinstance(result, BillingEligibility)
    assert result.allowed is True
    assert result.reason == "eligible"
    assert len(observed) == 1
    request = observed[0]
    assert request.method == "POST"
    assert request.url.path == "/v1/billing/resource-eligibility"
    assert dict(request.url.params) == {"workspace_id": "workspaces-710995"}
    assert json.loads(request.content) == {
        "sku_code": "vm.standard-2x4",
        "estimated_cost_minor": 12_500,
    }
    assert request.headers["authorization"] == "Bearer test-token"


def test_billing_eligibility_omits_unspecified_optional_inputs() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json=_decision(allowed=False), request=request)

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = client.billing.check_resource_eligibility(workspace_id="workspace-1")

    assert result.allowed is False
    assert result.reason == "insufficient_balance"
    assert json.loads(observed[0].content) == {}


def test_billing_eligibility_preserves_typed_forbidden_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"detail": "Forbidden"}, request=request)

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(ForbiddenError):
        client.billing.check_resource_eligibility(workspace_id="another-workspace")


def test_async_billing_eligibility_uses_same_contract() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json=_decision(), request=request)

    async def run() -> BillingEligibility:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            client = AsyncIbee(
                token="test-token",
                base_url="https://api.example.test/v1",
                httpx_client=http_client,
            )
            return await client.billing.check_resource_eligibility(
                workspace_id="workspace-1",
                sku_code="vm.standard-2x4",
            )

    result = asyncio.run(run())

    assert result.allowed is True
    assert observed[0].url.path == "/v1/billing/resource-eligibility"
    assert json.loads(observed[0].content) == {"sku_code": "vm.standard-2x4"}
