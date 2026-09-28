# Hand-written (listed in .fernignore).
from __future__ import annotations

import typing

from ..core.api_error import ApiError


class BillingEligibilityError(ApiError):
    """Raised when a billable create cannot obtain an affirmative billing decision.

    Kept for 0.3.0 compatibility. In 0.4.0 the SDK raises the subclasses
    ``BillingDeniedError`` (402, decision not allowed) and ``BillingAdmissionError``
    (502, unusable decision) instead; catching ``BillingEligibilityError`` still
    catches denials.
    """

    def __init__(
        self,
        *,
        reason: str,
        status_code: int,
        decision: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            body={"code": "BILLING_ELIGIBILITY_REQUIRED", "message": reason, "decision": decision},
        )
        self.reason = reason
        self.decision = decision

    def __str__(self) -> str:
        return str(self.reason)
