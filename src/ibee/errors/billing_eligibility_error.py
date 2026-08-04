from __future__ import annotations

import typing

from ..core.api_error import ApiError


class BillingEligibilityError(ApiError):
    """Raised when a billable create cannot obtain an affirmative billing decision."""

    def __init__(
        self,
        *,
        reason: str,
        status_code: int,
        decision: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ) -> None:
        self.reason = reason
        self.decision = decision
        super().__init__(
            status_code=status_code,
            body={"code": "BILLING_ELIGIBILITY_REQUIRED", "message": reason, "decision": decision},
        )

    def __str__(self) -> str:
        return self.reason
