# Hand-written (listed in .fernignore).
"""Billing admission errors."""

from __future__ import annotations

import typing

from ..core.api_error import ApiError
from .bad_gateway_error import BadGatewayError
from .billing_eligibility_error import BillingEligibilityError
from .forbidden_error import ForbiddenError
from .payment_required_error import PaymentRequiredError


def _field(decision: typing.Any, name: str) -> typing.Any:
    if decision is None:
        return None
    if isinstance(decision, typing.Mapping):
        return decision.get(name)
    return getattr(decision, name, None)


class BillingDeniedError(PaymentRequiredError, BillingEligibilityError):
    """Billing did not approve a create (HTTP 402, ``code == "billing_denied"``).

    Raised by ``billing.require_resource_eligibility`` when the decision's
    ``allowed`` is not exactly ``True``, and for a 402 from the API edge on a
    billable create.

    Attributes
    ----------
    reason : typing.Optional[str]
        Billing reason code, for example ``insufficient_balance``.
    sku_code : typing.Optional[str]
        SKU billing evaluated.
    admission_context_id : typing.Optional[str]
        Edge admission reference, useful for support.
    topup_allowed : bool
        ``True`` when adding wallet credits in the portal can resolve the denial.
    decision : typing.Any
        The full eligibility decision, when available.
    message : str
        The portal's explanation (also ``str(error)``).
    """

    def __init__(
        self,
        body: typing.Any = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        *,
        decision: typing.Any = None,
        reason: typing.Optional[str] = None,
        sku_code: typing.Optional[str] = None,
        admission_context_id: typing.Optional[str] = None,
        create_type: typing.Optional[str] = "resource",
    ) -> None:
        self.decision = decision
        self.create_type = create_type or "resource"
        self._explicit_reason = reason
        self._explicit_sku_code = sku_code
        self._explicit_admission_context_id = admission_context_id
        if body is None:
            body = {
                "error": "billing_denied",
                "billing_reason": reason if reason is not None else _field(decision, "reason"),
                "billing_sku_code": sku_code if sku_code is not None else _field(decision, "sku_code"),
                "admission_context_id": admission_context_id,
            }
        ApiError.__init__(self, status_code=402, headers=headers, body=body)

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        from ..billing.messages import billing_block_message, is_billing_topup_allowed

        decision = getattr(self, "decision", None)
        self.code = "billing_denied"
        self.reason = (
            getattr(self, "_explicit_reason", None) or self.reason or _field(decision, "reason")
        )
        self.sku_code = (
            getattr(self, "_explicit_sku_code", None) or self.billing_sku_code or _field(decision, "sku_code")
        )
        self.admission_context_id = (
            getattr(self, "_explicit_admission_context_id", None) or self.admission_context_id
        )
        source = decision if decision is not None else (self.reason or "")
        self.topup_allowed = is_billing_topup_allowed(source)
        self.message = billing_block_message(source, getattr(self, "create_type", "resource"))

    def __str__(self) -> str:
        return self.message


class BillingAdmissionError(BadGatewayError):
    """Billing admission could not produce a usable decision (HTTP 502).

    Codes include ``invalid_billing_decision`` (for example the decision was
    incomplete or priced a different SKU), ``billing_admission_error`` and the
    catalog/plan resolution codes returned by the API edge. Not retried.
    """

    def __init__(
        self,
        body: typing.Any,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        *,
        decision: typing.Any = None,
    ) -> None:
        self.decision = decision
        super().__init__(body=body, headers=headers)

    def __str__(self) -> str:
        return f"{self.message} ({self.code})"


class BillingForbiddenError(ForbiddenError):
    """HTTP 403 where a service reports a billing denial reason as the message."""

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        self.reason = (self.message or "").strip() or self.reason


__all__ = ["BillingAdmissionError", "BillingDeniedError", "BillingForbiddenError"]
