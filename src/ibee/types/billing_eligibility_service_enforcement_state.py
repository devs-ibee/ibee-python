# Hand-written (listed in .fernignore).

import typing

BillingEligibilityServiceEnforcementState = typing.Union[
    typing.Literal["NONE", "BLOCK_NEW_PURCHASES", "SUSPEND_METERED_SERVICES", "FULL_PROJECT_SUSPEND"], typing.Any
]
