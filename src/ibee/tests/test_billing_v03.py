from __future__ import annotations

import asyncio
import datetime as dt
import json

import httpx

from ibee import AsyncIbee, BillingEligibility, Ibee


ELIGIBILITY_RESPONSE = {
    "organization_id": "250612",
    "allowed": True,
    "reason": "sufficient_balance",
    "billing_mode": "PREPAID",
    "billing_state": "CURRENT",
    "currency": "INR",
    "sku_code": "STANDARD-2-8-50",
    "estimated_cost_minor": 120000,
    "effective_balance_minor": 500000,
    "credit_headroom_minor": None,
    "evaluated_at": "2026-08-04T10:30:00Z",
}


def test_sync_billing_eligibility_is_typed_and_sends_contract() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json=ELIGIBILITY_RESPONSE, request=request)

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = client.billing.check_resource_eligibility(
        workspace_id="710995",
        sku_code="STANDARD-2-8-50",
        estimated_cost_minor=120000,
    )

    assert isinstance(result, BillingEligibility)
    assert result.allowed is True
    assert result.billing_mode == "PREPAID"
    assert result.evaluated_at == dt.datetime(2026, 8, 4, 10, 30, tzinfo=dt.timezone.utc)
    assert observed[0].method == "POST"
    assert observed[0].url.path == "/v1/billing/resource-eligibility"
    assert dict(observed[0].url.params) == {"workspace_id": "710995"}
    assert json.loads(observed[0].content) == {
        "sku_code": "STANDARD-2-8-50",
        "estimated_cost_minor": 120000,
    }


def test_optional_request_fields_are_omitted_and_raw_response_is_available() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json=ELIGIBILITY_RESPONSE, request=request)

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = client.billing.with_raw_response.check_resource_eligibility(
        workspace_id="710995"
    )

    assert result.status_code == 200
    assert result.data.reason == "sufficient_balance"
    assert json.loads(observed[0].content) == {}


def test_async_billing_eligibility_matches_sync_surface() -> None:
    observed: list[httpx.Request] = []

    async def run() -> BillingEligibility:
        def handler(request: httpx.Request) -> httpx.Response:
            observed.append(request)
            return httpx.Response(200, json=ELIGIBILITY_RESPONSE, request=request)

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as http_client:
            client = AsyncIbee(
                token="test-token",
                base_url="https://api.example.test/v1",
                httpx_client=http_client,
            )
            return await client.billing.check_resource_eligibility(
                workspace_id="710995",
                sku_code="STANDARD-2-8-50",
            )

    result = asyncio.run(run())

    assert isinstance(result, BillingEligibility)
    assert result.billing_state == "CURRENT"
    assert json.loads(observed[0].content) == {"sku_code": "STANDARD-2-8-50"}
