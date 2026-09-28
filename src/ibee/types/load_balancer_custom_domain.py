# Hand-written (listed in .fernignore).

import typing

import pydantic
from ..core.pydantic_utilities import IS_PYDANTIC_V2, UniversalBaseModel


class LoadBalancerCustomDomain(UniversalBaseModel):
    """Custom domain of an L7 HTTPS load balancer. Create a CNAME from ``hostname`` to ``cname_target``."""

    hostname: str
    cname_target: typing.Optional[str] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
