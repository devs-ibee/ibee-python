"""Deprecated compatibility no-ops; use billing.check_resource_eligibility for diagnostics."""

from __future__ import annotations

import typing

from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.request_options import RequestOptions

SECRET_MANAGER_SKU_CODE = "SECRETMA-STD"
OBJECT_STORAGE_SKU_CODE = "OBJECTST-STD"
LOAD_BALANCER_SKU_CODE = "LOADBALA-STD"
NAT_GATEWAY_SKU_CODE = "NAT-GATEWAY"
RESERVED_IP_SKU_CODE = "RESERVED-IP"
CUSTOM_DOMAIN_SKU_CODE = "CUSTOMDO-STD"


def enforce_billing_eligibility(
    client_wrapper: SyncClientWrapper,
    *,
    workspace_id: str,
    sku_code: typing.Optional[str],
    estimated_cost_minor: typing.Optional[int] = None,
    request_options: typing.Optional[RequestOptions] = None,
) -> None:
    """Deprecated no-op. The upstream mutation decides admission and pricing."""
    return None


async def enforce_billing_eligibility_async(
    client_wrapper: AsyncClientWrapper,
    *,
    workspace_id: str,
    sku_code: typing.Optional[str],
    estimated_cost_minor: typing.Optional[int] = None,
    request_options: typing.Optional[RequestOptions] = None,
) -> None:
    """Deprecated no-op. The upstream mutation decides admission and pricing."""
    return None


def enforce_compute_plan_eligibility(
    client_wrapper: SyncClientWrapper,
    *,
    workspace_id: str,
    vm_type: typing.Literal["cloud", "gpu"],
    plan_id: str,
    site_id: typing.Optional[str],
    request_options: typing.Optional[RequestOptions] = None,
) -> None:
    """Deprecated no-op. The upstream mutation decides admission and pricing."""
    return None


async def enforce_compute_plan_eligibility_async(
    client_wrapper: AsyncClientWrapper,
    *,
    workspace_id: str,
    vm_type: typing.Literal["cloud", "gpu"],
    plan_id: str,
    site_id: typing.Optional[str],
    request_options: typing.Optional[RequestOptions] = None,
) -> None:
    """Deprecated no-op. The upstream mutation decides admission and pricing."""
    return None
