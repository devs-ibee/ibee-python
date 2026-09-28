# Hand-written (listed in .fernignore).
from __future__ import annotations

import typing

from ..core.api_error import ApiError


class BillingEligibilityError(ApiError):
    """Raised when a billable create cannot obtain an affirmative billing decision.

    Kept for 0.3.0 compatibility. In 0.4.0 the SDK raises ``BillingDeniedError``
    (402, a subclass of this class and of ``PaymentRequiredError``) for denials, and
    ``BillingAdmissionError`` (502, a ``BadGatewayError`` subclass, not a subclass
    of this class) for unusable decisions. Catch both if you need both.
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
