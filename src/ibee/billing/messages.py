"""Billing admission copy and helpers, matching the IBEE portal.

These helpers accept either a ``BillingEligibility`` decision (or any mapping with
the same keys) or a bare reason string.
"""

from __future__ import annotations

import math
import typing

CREATE_TYPE_LABELS: typing.Dict[str, str] = {
    "vm": "cloud VM",
    "gpu_vm": "GPU VM",
    "block_storage": "block storage volume",
    "object_storage": "object storage bucket",
    "load_balancer": "load balancer",
    "cdn": "CDN distribution",
    "custom_domain": "custom domain",
    "secret_store": "secret store",
    "secret": "secret",
    "snapshot": "snapshot",
    "backup": "backup policy",
    "reserved_ip": "Reserved IP",
    "container_registry": "container registry",
}
DEFAULT_CREATE_LABEL = "resource"

#: Reasons that mean "add credits and retry".
TOPUP_REASONS = frozenset({"initial_topup_required", "insufficient_balance", "billing_limit_exhausted"})
#: Known reasons billing uses to deny a create.
DENIED_REASONS = frozenset(
    {
        "initial_topup_required",
        "insufficient_balance",
        "credit_limit_exceeded",
        "unknown_sku",
        "inactive_sku",
        "billing_limit_exhausted",
        "overage_cap_exceeded",
        "dunning_active",
        "dunning_grace_expired",
    }
)
#: Known reasons billing uses to allow a request.
ALLOWED_REASONS = frozenset({"ok", "usage_based_sku", "status_only", "operation_allowed"})

INR_MINIMUM_TOPUP_MINOR = 200_000
COMMITTED_MONTHLY_HOURS = 731
TOPUP_GUIDANCE = "Add credits in the IBEE portal (Billing > Add Credits), then retry."


def _get(decision: typing.Any, *names: str) -> typing.Any:
    for name in names:
        if isinstance(decision, typing.Mapping):
            value = decision.get(name)
        else:
            value = getattr(decision, name, None)
            if value is None:
                extra = getattr(decision, "model_extra", None) or {}
                value = extra.get(name) if isinstance(extra, dict) else None
        if value is not None:
            return value
    return None


def _decision_reason(decision_or_reason: typing.Any) -> str:
    if decision_or_reason is None:
        return ""
    if isinstance(decision_or_reason, str):
        return decision_or_reason.strip()
    return str(_get(decision_or_reason, "can_create_reason", "reason") or "").strip()


def create_type_label(create_type: typing.Optional[str]) -> str:
    """Human label for a create type (``vm`` -> ``cloud VM``); unknown types give ``resource``."""
    return CREATE_TYPE_LABELS.get(str(create_type or "").strip().lower(), DEFAULT_CREATE_LABEL)


def minimum_topup_minor(currency: typing.Optional[str]) -> int:
    """Minimum wallet top-up in minor units: 200000 (INR 2,000) for INR, otherwise 0."""
    return INR_MINIMUM_TOPUP_MINOR if str(currency or "").strip().upper() == "INR" else 0


def billing_block_message(
    decision_or_reason: typing.Any,
    create_type: typing.Optional[str] = "resource",
    billing_state: typing.Optional[str] = None,
    currency: typing.Optional[str] = None,
) -> str:
    """The portal's explanation for a billing denial."""
    reason = _decision_reason(decision_or_reason)
    if not isinstance(decision_or_reason, str) and decision_or_reason is not None:
        billing_state = billing_state or _get(decision_or_reason, "billing_state")
        currency = currency or _get(decision_or_reason, "currency")
    state = str(billing_state or "").strip().upper()
    label = create_type_label(create_type)
    if reason == "initial_topup_required":
        if currency and str(currency).strip().upper() != "INR":
            return f"Add funds to your wallet before creating your first {label}."
        return f"Add at least ₹2,000 to your wallet before creating your first {label}."
    if reason == "insufficient_balance":
        return f"Your available wallet balance does not cover this {label}. Add credits and try again."
    if reason == "credit_limit_exceeded":
        return f"Creating this {label} would exceed this organization's credit limit."
    if reason == "billing_limit_exhausted" or state == "PAST_DUE":
        return (
            f"Billing needs attention before creating a {label}. "
            "Add credits or settle the outstanding usage, then try again."
        )
    if reason == "overage_cap_exceeded" or state == "HARD_SUSPENDED":
        return (
            f"This organization is billing-suspended, so new {label} creation is blocked. "
            "Please resolve billing before trying again."
        )
    if reason in ("dunning_active", "dunning_grace_expired"):
        return f"An overdue billing case must be resolved before creating this {label}."
    if reason == "unknown_sku":
        return f"Pricing for this {label} could not be verified. Check the plan or SKU and try again."
    return f"Billing did not approve creating this {label}. Please review billing and try again."


def is_billing_topup_allowed(decision_or_reason: typing.Any) -> bool:
    """Whether adding wallet credits can resolve this denial (drives the portal's "Add Credits")."""
    if decision_or_reason is not None and not isinstance(decision_or_reason, str):
        operations = _get(decision_or_reason, "allowed_operations")
        if isinstance(operations, (list, tuple)) and any(
            str(item or "").strip() == "billing_topup" for item in operations
        ):
            return True
        reason = str(_get(decision_or_reason, "reason", "can_create_reason") or "")
    else:
        reason = decision_or_reason or ""
    return reason.strip().lower() in TOPUP_REASONS


def estimate_eligibility_cost_minor(
    billing_interval: typing.Optional[str],
    unit_price_minor: typing.Any,
    count: typing.Any = 1,
    hourly_period_hours: typing.Any = COMMITTED_MONTHLY_HOURS,
) -> int:
    """Estimated cost to send with an eligibility check, as the portal computes it.

    ``HOURLY`` plans are estimated over 731 hours; ``MONTHLY`` and ``YEARLY`` plans
    use their full period price. The result is multiplied by ``count`` and rounded.
    """

    def _finite(value: typing.Any) -> typing.Optional[float]:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return number if math.isfinite(number) and not isinstance(value, bool) else None

    rate = _finite(unit_price_minor)
    rate = max(0.0, rate) if rate is not None else 0.0
    quantity = _finite(count)
    quantity = max(0, math.floor(quantity)) if quantity is not None else 0
    hours = _finite(hourly_period_hours)
    hours = max(0.0, hours) if hours is not None else float(COMMITTED_MONTHLY_HOURS)
    period = rate * hours if str(billing_interval or "").strip().upper() == "HOURLY" else rate
    return int(math.floor(period * quantity + 0.5))


__all__ = [
    "ALLOWED_REASONS",
    "COMMITTED_MONTHLY_HOURS",
    "CREATE_TYPE_LABELS",
    "DENIED_REASONS",
    "INR_MINIMUM_TOPUP_MINOR",
    "TOPUP_GUIDANCE",
    "TOPUP_REASONS",
    "billing_block_message",
    "create_type_label",
    "estimate_eligibility_cost_minor",
    "is_billing_topup_allowed",
    "minimum_topup_minor",
]
