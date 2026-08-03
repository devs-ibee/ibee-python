from __future__ import annotations

import typing

from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.request_options import RequestOptions
from .models import BillingEligibility
from .raw_client import AsyncRawBillingClient, RawBillingClient


class BillingClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._raw_client = RawBillingClient(client_wrapper=client_wrapper)

    @property
    def with_raw_response(self) -> RawBillingClient:
        return self._raw_client

    def check_resource_eligibility(
        self,
        *,
        workspace_id: str,
        sku_code: typing.Optional[str] = None,
        estimated_cost_minor: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> BillingEligibility:
        """
        Check whether billing permits a prospective resource create.

        This is an explicit, read-only preflight. Create methods do not invoke it
        automatically, and product services remain authoritative at create time.
        """
        return self._raw_client.check_resource_eligibility(
            workspace_id=workspace_id,
            sku_code=sku_code,
            estimated_cost_minor=estimated_cost_minor,
            request_options=request_options,
        ).data


class AsyncBillingClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._raw_client = AsyncRawBillingClient(client_wrapper=client_wrapper)

    @property
    def with_raw_response(self) -> AsyncRawBillingClient:
        return self._raw_client

    async def check_resource_eligibility(
        self,
        *,
        workspace_id: str,
        sku_code: typing.Optional[str] = None,
        estimated_cost_minor: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> BillingEligibility:
        """
        Check whether billing permits a prospective resource create.

        This is an explicit, read-only preflight. Create methods do not invoke it
        automatically, and product services remain authoritative at create time.
        """
        response = await self._raw_client.check_resource_eligibility(
            workspace_id=workspace_id,
            sku_code=sku_code,
            estimated_cost_minor=estimated_cost_minor,
            request_options=request_options,
        )
        return response.data
