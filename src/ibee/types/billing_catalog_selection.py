# Hand-written (listed in .fernignore).

import typing

import pydantic
from ..core.pydantic_utilities import IS_PYDANTIC_V2, UniversalBaseModel


class BillingSkuReference(UniversalBaseModel):
    """One billed SKU: ``sku_id`` and ``sku_code`` (other catalog fields are kept as extras)."""

    sku_id: typing.Union[str, int]
    sku_code: str
    product_code: typing.Optional[str] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


class BillingCatalogSelection(BillingSkuReference):
    """The ``billing_catalog`` object billable requests carry: the SKU bought plus ``attached_skus`` add-ons.

    For a VM volume attach it is the Block Storage SKU stored on the volume when it
    was created (``volume["metadata"]["billing_catalog"]``); the SDK reads it for you.
    """

    attached_skus: typing.Optional[typing.Dict[str, BillingSkuReference]] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
