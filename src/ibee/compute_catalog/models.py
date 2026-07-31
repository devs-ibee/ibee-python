from __future__ import annotations

import typing

import pydantic

from ..core.pydantic_utilities import IS_PYDANTIC_V2, UniversalBaseModel


class _CatalogModel(UniversalBaseModel):
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


class ComputeSite(_CatalogModel):
    site_id: str
    name: str
    site_code: typing.Optional[str] = None
    location: typing.Optional[str] = None
    region_id: typing.Optional[str] = None
    country_id: typing.Optional[str] = None
    timezone: typing.Optional[str] = None


class ComputeSiteList(_CatalogModel):
    sites: typing.List[ComputeSite]
    count: int


class ComputePlan(_CatalogModel):
    plan_id: str
    vm_type: typing.Literal["cloud", "gpu"]
    name: str
    code: str
    cpu: int
    ram_mb: int
    disk_gb: int
    gpu_count: int
    selectable: bool
    pricing_status: typing.Literal["priced", "unpriced"]
    currency: str
    billing_interval: typing.Literal["HOURLY", "MONTHLY"]
    gpu_model: typing.Optional[str] = None
    gpu_memory_gb: typing.Optional[float] = None
    hourly_price_minor: typing.Optional[int] = None
    monthly_price_minor: typing.Optional[int] = None
    site_id: typing.Optional[str] = None


class ComputePlanList(_CatalogModel):
    plans: typing.List[ComputePlan]
    count: int
    vm_type: typing.Literal["cloud", "gpu"]
    currency: str
    billing_interval: typing.Literal["HOURLY", "MONTHLY"]
    site_id: typing.Optional[str] = None


class ComputeImage(_CatalogModel):
    template_id: str
    name: str
    os_distro: str
    os_type: typing.Literal["linux", "windows"]
    architecture: str
    size_bytes: int
    gpu_compatible: bool
    compatible_vm_types: typing.List[typing.Literal["cloud", "gpu"]]
    site_ids: typing.List[str]
    description: typing.Optional[str] = None
    distro_version: typing.Optional[str] = None
    image_format: typing.Optional[str] = None


class ComputeImageList(_CatalogModel):
    images: typing.List[ComputeImage]
    count: int
    vm_type: typing.Literal["cloud", "gpu"]
    site_id: typing.Optional[str] = None
