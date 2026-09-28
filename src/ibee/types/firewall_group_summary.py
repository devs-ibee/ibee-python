# Hand-written (listed in .fernignore).

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import IS_PYDANTIC_V2, UniversalBaseModel


class FirewallGroupSummary(UniversalBaseModel):
    """A firewall group without its rules, as shown in the portal's firewall list.

    Not yet part of the published API contract; behaviour may change.
    """

    firewall_group_id: str
    name: str
    description: typing.Optional[str] = None
    status: typing.Optional[str] = None
    is_default: typing.Optional[bool] = None
    linked_instance_count: typing.Optional[int] = None
    rule_count: typing.Optional[int] = None
    created_at: typing.Optional[dt.datetime] = None
    updated_at: typing.Optional[dt.datetime] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
