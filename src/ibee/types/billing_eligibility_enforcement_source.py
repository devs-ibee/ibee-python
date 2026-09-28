# Hand-written (listed in .fernignore).

import typing

BillingEligibilityEnforcementSource = typing.Union[
    typing.Literal["BILLING", "MANUAL_ADMIN", "BILLING_AND_MANUAL"], typing.Any
]
