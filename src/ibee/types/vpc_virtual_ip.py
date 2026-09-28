# Hand-written (listed in .fernignore).

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import IS_PYDANTIC_V2, UniversalBaseModel


class VpcVirtualIp(UniversalBaseModel):
    """A private virtual IP (VIP) reserved in a VPC subnet, for example a MetalLB service address.

    Not yet part of the published API contract; behaviour may change.
    """

    virtual_ip_id: str
    vpc_id: str
    subnet_id: str
    private_ip: str
    purpose: typing.Optional[typing.Union[typing.Literal["metallb", "custom"], typing.Any]] = None
    announcer_vm_ids: typing.Optional[typing.List[str]] = None
    public_ip_id: typing.Optional[str] = None
    public_ip: typing.Optional[str] = None
    status: typing.Optional[str] = None
    error_message: typing.Optional[str] = None
    account_id: typing.Optional[str] = None
    organization_id: typing.Optional[str] = None
    workspace_id: typing.Optional[str] = None
    site_id: typing.Optional[str] = None
    created_at: typing.Optional[dt.datetime] = None
    updated_at: typing.Optional[dt.datetime] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
