"""Deprecated billing admission helpers (not used by any SDK method).

.. deprecated:: 0.4.0
   Use ``client.billing.require_resource_eligibility`` and the helpers in
   ``ibee.billing`` instead. This module will be removed in 0.5.0.
"""

from __future__ import annotations

import typing

from ..compute_catalog.raw_client import AsyncRawComputeCatalogClient, RawComputeCatalogClient
from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.request_options import RequestOptions
from ..errors.billing_eligibility_error import BillingEligibilityError
from ..types.compute_plan import ComputePlan
from .models import BillingEligibility
from .raw_client import AsyncRawBillingClient, RawBillingClient

SECRET_MANAGER_SKU_CODE = "SECRETMA-STD"
OBJECT_STORAGE_SKU_CODE = "OBJECTST-STD"
LOAD_BALANCER_SKU_CODE = "LOADBALA-STD"
NAT_GATEWAY_SKU_CODE = "NAT-GATEWAY"
RESERVED_IP_SKU_CODE = "RESERVED-IP"
CUSTOM_DOMAIN_SKU_CODE = "CUSTOMDO-STD"

_SAFE_PREFLIGHT_OPTIONS = (
    "timeout_in_seconds",
    "max_retries",
)


def _preflight_options(request_options: typing.Optional[RequestOptions]) -> typing.Optional[RequestOptions]:
    if request_options is None:
        return None
    safe = {key: request_options[key] for key in _SAFE_PREFLIGHT_OPTIONS if key in request_options}
    return typing.cast(RequestOptions, safe) if safe else None


def _model_dict(model: BillingEligibility) -> typing.Dict[str, typing.Any]:
    if hasattr(model, "model_dump"):
        return typing.cast(typing.Dict[str, typing.Any], model.model_dump(mode="json"))
    return typing.cast(typing.Dict[str, typing.Any], model.dict())


def _require_affirmative_decision(
    decision: BillingEligibility,
    *,
    expected_sku_code: typing.Optional[str],
    expected_cost_minor: typing.Optional[int],
) -> None:
    payload = _model_dict(decision)
    if not decision.allowed:
        raise BillingEligibilityError(
            reason=decision.reason or "Billing denied this resource create.",
            status_code=402,
            decision=payload,
        )

    if not decision.organization_id.strip() or not decision.reason.strip():
        raise BillingEligibilityError(
            reason="Billing returned an incomplete eligibility decision.",
            status_code=503,
            decision=payload,
        )
    if decision.billing_mode is None or decision.billing_state is None or decision.evaluated_at is None:
        raise BillingEligibilityError(
            reason="Billing returned an incomplete eligibility decision.",
            status_code=503,
            decision=payload,
        )

    if expected_sku_code is not None:
        actual_sku = (decision.sku_code or "").strip().upper()
        if actual_sku != expected_sku_code.strip().upper():
            raise BillingEligibilityError(
                reason="Billing did not confirm the requested SKU.",
                status_code=503,
                decision=payload,
            )
    if expected_cost_minor is not None and decision.estimated_cost_minor != expected_cost_minor:
        raise BillingEligibilityError(
            reason="Billing did not confirm the catalog price used for this create.",
            status_code=503,
            decision=payload,
        )


def enforce_billing_eligibility(
    client_wrapper: SyncClientWrapper,
    *,
    workspace_id: str,
    sku_code: typing.Optional[str],
    estimated_cost_minor: typing.Optional[int] = None,
    request_options: typing.Optional[RequestOptions] = None,
) -> None:
    decision = RawBillingClient(client_wrapper=client_wrapper).check_resource_eligibility(
        workspace_id=workspace_id,
        sku_code=sku_code,
        estimated_cost_minor=estimated_cost_minor,
        request_options=_preflight_options(request_options),
    ).data
    _require_affirmative_decision(
        decision,
        expected_sku_code=sku_code,
        expected_cost_minor=estimated_cost_minor,
    )


async def enforce_billing_eligibility_async(
    client_wrapper: AsyncClientWrapper,
    *,
    workspace_id: str,
    sku_code: typing.Optional[str],
    estimated_cost_minor: typing.Optional[int] = None,
    request_options: typing.Optional[RequestOptions] = None,
) -> None:
    response = await AsyncRawBillingClient(client_wrapper=client_wrapper).check_resource_eligibility(
        workspace_id=workspace_id,
        sku_code=sku_code,
        estimated_cost_minor=estimated_cost_minor,
        request_options=_preflight_options(request_options),
    )
    _require_affirmative_decision(
        response.data,
        expected_sku_code=sku_code,
        expected_cost_minor=estimated_cost_minor,
    )


def _select_plan(plans: typing.Sequence[ComputePlan], *, plan_id: str) -> ComputePlan:
    matches = [plan for plan in plans if plan.plan_id == plan_id]
    if not matches:
        raise BillingEligibilityError(
            reason=f"Compute plan '{plan_id}' is unavailable in the selected placement.",
            status_code=503,
        )
    plan = matches[0]
    if any(
        (
            candidate.code,
            candidate.billing_interval,
            candidate.hourly_price_minor,
            candidate.monthly_price_minor,
        )
        != (
            plan.code,
            plan.billing_interval,
            plan.hourly_price_minor,
            plan.monthly_price_minor,
        )
        for candidate in matches
    ):
        raise BillingEligibilityError(
            reason=f"Compute plan '{plan_id}' resolved to conflicting SKU or price data.",
            status_code=503,
        )
    if not plan.selectable or plan.pricing_status != "priced" or not plan.code.strip():
        raise BillingEligibilityError(
            reason=f"Compute plan '{plan_id}' is not selectable with confirmed pricing.",
            status_code=503,
        )
    return plan


def _plan_cost(plan: ComputePlan) -> int:
    if plan.billing_interval == "HOURLY":
        cost = plan.hourly_price_minor
    else:
        cost = plan.monthly_price_minor
    if cost is None or cost < 0:
        raise BillingEligibilityError(
            reason=f"Compute plan '{plan.plan_id}' has no confirmed {plan.billing_interval.lower()} price.",
            status_code=503,
        )
    return cost


def enforce_compute_plan_eligibility(
    client_wrapper: SyncClientWrapper,
    *,
    workspace_id: str,
    vm_type: typing.Literal["cloud", "gpu"],
    plan_id: str,
    site_id: typing.Optional[str],
    request_options: typing.Optional[RequestOptions] = None,
) -> None:
    plans = RawComputeCatalogClient(client_wrapper=client_wrapper).list_compute_plans(
        workspace_id=workspace_id,
        vm_type=vm_type,
        site_id=site_id,
        request_options=_preflight_options(request_options),
    ).data.plans
    plan = _select_plan(plans, plan_id=plan_id)
    enforce_billing_eligibility(
        client_wrapper,
        workspace_id=workspace_id,
        sku_code=plan.code,
        estimated_cost_minor=_plan_cost(plan),
        request_options=request_options,
    )


async def enforce_compute_plan_eligibility_async(
    client_wrapper: AsyncClientWrapper,
    *,
    workspace_id: str,
    vm_type: typing.Literal["cloud", "gpu"],
    plan_id: str,
    site_id: typing.Optional[str],
    request_options: typing.Optional[RequestOptions] = None,
) -> None:
    response = await AsyncRawComputeCatalogClient(client_wrapper=client_wrapper).list_compute_plans(
        workspace_id=workspace_id,
        vm_type=vm_type,
        site_id=site_id,
        request_options=_preflight_options(request_options),
    )
    plan = _select_plan(response.data.plans, plan_id=plan_id)
    await enforce_billing_eligibility_async(
        client_wrapper,
        workspace_id=workspace_id,
        sku_code=plan.code,
        estimated_cost_minor=_plan_cost(plan),
        request_options=request_options,
    )
