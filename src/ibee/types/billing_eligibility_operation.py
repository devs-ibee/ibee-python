# Hand-written (listed in .fernignore).

import typing

BillingEligibilityOperation = typing.Union[
    typing.Literal[
        "CREATE_RESOURCE",
        "CREATE_CREDENTIAL",
        "INCREASE_CAPACITY",
        "MUTATE_RESOURCE",
        "READ_RESOURCE",
        "DELETE_RESOURCE",
        "REVOKE_CREDENTIAL",
        "SECURITY_RECOVERY",
    ],
    typing.Any,
]
