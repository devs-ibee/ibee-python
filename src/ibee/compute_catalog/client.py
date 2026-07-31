# Compute catalog client (sites / plans / images). Mirrors the Fern-generated
# resource clients: a thin wrapper over the raw client that returns the parsed
# payload. Discovery responses are validated into typed catalog models.

import typing

from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.request_options import RequestOptions
from .models import ComputeImageList, ComputePlanList, ComputeSiteList
from .raw_client import AsyncRawComputeCatalogClient, RawComputeCatalogClient


class ComputeCatalogClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._raw_client = RawComputeCatalogClient(client_wrapper=client_wrapper)

    @property
    def with_raw_response(self) -> RawComputeCatalogClient:
        return self._raw_client

    def list_compute_sites(
        self,
        *,
        workspace_id: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ComputeSiteList:
        """Return sites where cloud and GPU VMs can be placed. Requires scope: vm.read."""
        return self._raw_client.list_compute_sites(
            workspace_id=workspace_id,
            request_options=request_options,
        ).data

    def list_compute_plans(
        self,
        *,
        workspace_id: str,
        vm_type: typing.Literal["cloud", "gpu"],
        site_id: typing.Optional[str] = None,
        currency: typing.Optional[str] = None,
        billing_interval: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ComputePlanList:
        """Return billable plans for cloud or GPU VMs. Requires scope: vm.read."""
        return self._raw_client.list_compute_plans(
            workspace_id=workspace_id, vm_type=vm_type, site_id=site_id,
            currency=currency, billing_interval=billing_interval,
            request_options=request_options,
        ).data

    def list_compute_images(
        self,
        *,
        workspace_id: str,
        vm_type: typing.Literal["cloud", "gpu"],
        site_id: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ComputeImageList:
        """Return OS templates compatible with cloud or GPU VMs. Requires scope: vm.read."""
        return self._raw_client.list_compute_images(
            workspace_id=workspace_id, vm_type=vm_type, site_id=site_id,
            request_options=request_options,
        ).data


class AsyncComputeCatalogClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._raw_client = AsyncRawComputeCatalogClient(client_wrapper=client_wrapper)

    @property
    def with_raw_response(self) -> AsyncRawComputeCatalogClient:
        return self._raw_client

    async def list_compute_sites(
        self,
        *,
        workspace_id: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ComputeSiteList:
        """Return sites where cloud and GPU VMs can be placed. Requires scope: vm.read."""
        return (await self._raw_client.list_compute_sites(
            workspace_id=workspace_id,
            request_options=request_options,
        )).data

    async def list_compute_plans(
        self,
        *,
        workspace_id: str,
        vm_type: typing.Literal["cloud", "gpu"],
        site_id: typing.Optional[str] = None,
        currency: typing.Optional[str] = None,
        billing_interval: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ComputePlanList:
        """Return billable plans for cloud or GPU VMs. Requires scope: vm.read."""
        return (await self._raw_client.list_compute_plans(
            workspace_id=workspace_id, vm_type=vm_type, site_id=site_id,
            currency=currency, billing_interval=billing_interval,
            request_options=request_options,
        )).data

    async def list_compute_images(
        self,
        *,
        workspace_id: str,
        vm_type: typing.Literal["cloud", "gpu"],
        site_id: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ComputeImageList:
        """Return OS templates compatible with cloud or GPU VMs. Requires scope: vm.read."""
        return (await self._raw_client.list_compute_images(
            workspace_id=workspace_id, vm_type=vm_type, site_id=site_id,
            request_options=request_options,
        )).data
