# Hand-written (listed in .fernignore).
"""Billing eligibility client, models, and the portal's billing admission helpers."""

from .messages import (
    ALLOWED_REASONS,
    COMMITTED_MONTHLY_HOURS,
    CREATE_TYPE_LABELS,
    DENIED_REASONS,
    INR_MINIMUM_TOPUP_MINOR,
    TOPUP_GUIDANCE,
    TOPUP_REASONS,
    billing_block_message,
    create_type_label,
    estimate_eligibility_cost_minor,
    is_billing_topup_allowed,
    minimum_topup_minor,
)
from .models import (
    BillingEligibility,
    BillingMode,
    BillingState,
    EnforcementOperation,
    EnforcementSource,
    ServiceEnforcementState,
)


def is_payment_block_error(error: object) -> bool:
    """Whether an exception is a billing/payment wall; see ``ibee.errors.is_payment_block_error``."""
    from ..errors.factory import is_payment_block_error as _impl

    return _impl(error)


__all__ = [
    "ALLOWED_REASONS",
    "BillingEligibility",
    "BillingMode",
    "BillingState",
    "COMMITTED_MONTHLY_HOURS",
    "CREATE_TYPE_LABELS",
    "DENIED_REASONS",
    "EnforcementOperation",
    "EnforcementSource",
    "INR_MINIMUM_TOPUP_MINOR",
    "ServiceEnforcementState",
    "TOPUP_GUIDANCE",
    "TOPUP_REASONS",
    "billing_block_message",
    "create_type_label",
    "estimate_eligibility_cost_minor",
    "is_billing_topup_allowed",
    "is_payment_block_error",
    "minimum_topup_minor",
]
