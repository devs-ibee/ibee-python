"""0.4.0 billing eligibility query, portal preflight, and admission copy."""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from ibee import AsyncIbee, Ibee, IbeeValidationError
from ibee.billing import (
    CREATE_TYPE_LABELS,
    billing_block_message,
    estimate_eligibility_cost_minor,
    is_billing_topup_allowed,
    minimum_topup_minor,
)
from ibee.errors import BillingAdmissionError, BillingDeniedError, BillingEligibilityError, PaymentRequiredError

BASE = "https://api.example.test/v1"
WS = "710995"


def _decision(**overrides: object) -> dict:
    decision = {
        "organization_id": "org-1",
        "allowed": True,
        "reason": "ok",
        "billing_mode": "PREPAID",
        "billing_state": "CURRENT",
        "currency": "INR",
        "sku_code": "STANDARD-2-8-50",
        "estimated_cost_minor": 12500,
        "effective_balance_minor": 50000,
        "credit_headroom_minor": None,
        "evaluated_at": "2026-08-04T10:00:00Z",
        "service_enforcement_state": "NONE",
        "enforcement_revision": 3,
        "enforcement_source": "BILLING",
        "enforcement_reason_code": None,
        "operation": "CREATE_RESOURCE",
        "allowed_operations": ["create_resource"],
        "resource_limits": {"vm": 10, "gpu_vm": -1},
    }
    decision.update(overrides)
    return decision


def _client(payload: object, observed: list | None = None) -> Ibee:
    def handler(request: httpx.Request) -> httpx.Response:
        if observed is not None:
            observed.append(request)
        return httpx.Response(200, json=payload, request=request)

    return Ibee(token="t", base_url=BASE, httpx_client=httpx.Client(transport=httpx.MockTransport(handler)))


def test_check_returns_full_typed_decision_and_sends_normalised_inputs() -> None:
    observed: list[httpx.Request] = []
    decision = _client(_decision(), observed).billing.check_resource_eligibility(
        workspace_id=WS, sku_code="  standard-2-8-50 ", estimated_cost_minor=12499.6, operation="create_resource"
    )
    assert json.loads(observed[0].content) == {
        "sku_code": "standard-2-8-50",
        "estimated_cost_minor": 12500,
        "operation": "CREATE_RESOURCE",
    }
    assert decision.service_enforcement_state == "NONE"
    assert decision.enforcement_revision == 3
    assert decision.enforcement_source == "BILLING"
    assert decision.operation == "CREATE_RESOURCE"
    assert decision.allowed_operations == ["create_resource"]
    assert decision.resource_limits == {"vm": 10, "gpu_vm": -1}


def test_check_does_not_raise_on_denial_and_omits_blank_sku() -> None:
    observed: list[httpx.Request] = []
    decision = _client(_decision(allowed=False, reason="insufficient_balance"), observed).billing.check_resource_eligibility(
        workspace_id=WS, sku_code="   "
    )
    assert decision.allowed is False
    assert json.loads(observed[0].content) == {}


@pytest.mark.parametrize(
    ("kwargs", "code"),
    [
        ({"sku_code": "x" * 65}, "invalid_sku_code"),
        ({"estimated_cost_minor": -1}, "invalid_estimated_cost_minor"),
        ({"estimated_cost_minor": float("nan")}, "invalid_estimated_cost_minor"),
        ({"operation": "LAUNCH"}, "invalid_operation"),
        ({"workspace_id": "01"}, "invalid_workspace_id"),
    ],
)
def test_check_validates_before_sending(kwargs: dict, code: str) -> None:
    observed: list[httpx.Request] = []
    arguments = {"workspace_id": WS, **kwargs}
    with pytest.raises(IbeeValidationError) as info:
        _client(_decision(), observed).billing.check_resource_eligibility(**arguments)
    assert info.value.code == code
    assert observed == []


def test_require_returns_allowed_decision_with_case_insensitive_sku() -> None:
    decision = _client(_decision()).billing.require_resource_eligibility(
        workspace_id=WS, sku_code="standard-2-8-50", estimated_cost_minor=12500, resource_type="vm"
    )
    assert decision.allowed is True


def test_require_raises_billing_denied_with_portal_copy() -> None:
    client = _client(_decision(allowed=False, reason="insufficient_balance", sku_code="STANDARD-2-8-50"))
    with pytest.raises(BillingDeniedError) as info:
        client.billing.require_resource_eligibility(workspace_id=WS, sku_code="STANDARD-2-8-50", resource_type="gpu_vm")
    error = info.value
    assert isinstance(error, PaymentRequiredError) and isinstance(error, BillingEligibilityError)
    assert error.status_code == 402
    assert error.code == "billing_denied"
    assert error.reason == "insufficient_balance"
    assert error.sku_code == "STANDARD-2-8-50"
    assert error.topup_allowed is False
    assert error.decision.allowed is False
    assert str(error) == "Your available wallet balance does not cover this GPU VM. Review billing for available actions."


@pytest.mark.parametrize(
    "payload",
    [
        _decision(allowed="true"),
        {k: v for k, v in _decision().items() if k != "allowed"},
        _decision(organization_id=""),
        _decision(reason=None),
        _decision(sku_code="OTHER-SKU"),
        ["not", "an", "object"],
    ],
)
def test_require_rejects_invalid_decisions(payload: object) -> None:
    with pytest.raises(BillingAdmissionError) as info:
        _client(payload).billing.require_resource_eligibility(workspace_id=WS, sku_code="standard-2-8-50")
    assert info.value.status_code == 502
    assert info.value.code == "invalid_billing_decision"


def test_async_require_parity() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_decision(allowed=False, reason="credit_limit_exceeded"), request=request)

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            client = AsyncIbee(token="t", base_url=BASE, httpx_client=http_client)
            checked = await client.billing.check_resource_eligibility(workspace_id=WS, operation="read_resource")
            assert checked.allowed is False
            await client.billing.require_resource_eligibility(workspace_id=WS, resource_type="block_storage")

    with pytest.raises(BillingDeniedError) as info:
        asyncio.run(run())
    assert str(info.value) == "Creating this block storage volume would exceed this organization's credit limit."
    assert info.value.topup_allowed is False


def test_billing_block_message_matches_portal() -> None:
    assert billing_block_message("initial_topup_required", "vm") == (
        "Billing requires an initial wallet top-up before creating your first cloud VM. Review billing for available actions."
    )
    assert billing_block_message({"reason": "initial_topup_required", "currency": "USD"}, "cdn") == (
        "Billing requires an initial wallet top-up before creating your first CDN distribution. Review billing for available actions."
    )
    assert billing_block_message({"reason": "x", "billing_state": "PAST_DUE"}, "snapshot").startswith(
        "Billing needs attention before creating a snapshot."
    )
    assert billing_block_message({"reason": "x", "billing_state": "HARD_SUSPENDED"}, "reserved_ip") == (
        "This organization is billing-suspended, so new Reserved IP creation is blocked. "
        "Please resolve billing before trying again."
    )
    assert billing_block_message("dunning_grace_expired", "secret") == (
        "An overdue billing case must be resolved before creating this secret."
    )
    assert billing_block_message("unknown_sku", "load_balancer") == (
        "Pricing for this load balancer could not be verified. Check the plan or SKU and try again."
    )
    assert billing_block_message("something_new", "bogus") == (
        "Billing did not approve creating this resource. Please review billing and try again."
    )
    assert CREATE_TYPE_LABELS["container_registry"] == "container registry"


def test_topup_rules_and_minimums() -> None:
    assert not is_billing_topup_allowed("Initial_Topup_Required ")
    assert not is_billing_topup_allowed({"reason": "billing_limit_exhausted"})
    assert is_billing_topup_allowed({"reason": "x", "allowed_operations": ["billing_topup"]})
    assert not is_billing_topup_allowed("credit_limit_exceeded")
    assert not is_billing_topup_allowed(None)
    assert minimum_topup_minor("inr") is None
    assert minimum_topup_minor("USD") is None


@pytest.mark.parametrize("reason", ["initial_topup_required", "insufficient_balance", "billing_limit_exhausted"])
@pytest.mark.parametrize("operations", [None, [], "billing_topup", {}, [True, 1, None], ["BILLING_TOPUP"], [" billing_topup "]])
def test_topup_permission_is_never_inferred(reason: str, operations: object) -> None:
    payload = {"reason": reason, "allowed_operations": operations}
    assert not is_billing_topup_allowed(payload)
    assert "add credits" not in billing_block_message(payload).lower()


@pytest.mark.parametrize("currency", [None, "", "INR", "USD", "EUR"])
def test_feedback_never_invents_a_currency_or_minimum(currency: object) -> None:
    payload = {"reason": "initial_topup_required", "currency": currency, "allowed_operations": ["billing_topup"]}
    assert billing_block_message(payload, "vm") == (
        "Billing requires an initial wallet top-up before creating your first cloud VM. You can add credits in the IBEE portal."
    )
    assert minimum_topup_minor(currency) is None


def test_typed_diagnostic_preserves_explicit_topup_permission() -> None:
    client = _client(_decision(allowed=False, reason="insufficient_balance", allowed_operations=["billing_topup"]))
    with pytest.raises(BillingDeniedError) as info:
        client.billing.require_resource_eligibility(workspace_id=WS)
    assert info.value.topup_allowed is True
    assert "You can add credits" in str(info.value)


def test_estimate_eligibility_cost_minor() -> None:
    assert estimate_eligibility_cost_minor("HOURLY", 10) == 7310
    assert estimate_eligibility_cost_minor("HOURLY", 10, count=3) == 21930
    assert estimate_eligibility_cost_minor("MONTHLY", 12500, count=2.9) == 25000
    assert estimate_eligibility_cost_minor("YEARLY", 99999) == 99999
    assert estimate_eligibility_cost_minor("HOURLY", -5) == 0
    assert estimate_eligibility_cost_minor("HOURLY", float("inf")) == 0
    assert estimate_eligibility_cost_minor("HOURLY", 1.5, hourly_period_hours=float("nan")) == 1097
