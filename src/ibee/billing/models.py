from __future__ import annotations

import datetime as dt
import typing

import pydantic

from ..core.pydantic_utilities import IS_PYDANTIC_V2, UniversalBaseModel

BillingMode = typing.Literal["PREPAID", "POSTPAID"]
BillingState = typing.Literal[
    "CURRENT",
    "PAYMENT_DUE",
    "PAST_DUE",
    "SOFT_SUSPENDED",
    "HARD_SUSPENDED",
]


class BillingEligibility(UniversalBaseModel):
    """Billing admission decision for a prospective resource create."""

    organization_id: str
    allowed: bool
    reason: str
    billing_mode: typing.Optional[BillingMode] = None
    billing_state: typing.Optional[BillingState] = None
    currency: typing.Optional[str] = None
    sku_code: typing.Optional[str] = None
    estimated_cost_minor: typing.Optional[int] = None
    effective_balance_minor: typing.Optional[int] = None
    credit_headroom_minor: typing.Optional[int] = None
    evaluated_at: typing.Optional[dt.datetime] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(
            extra="allow",
            frozen=True,
        )
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
