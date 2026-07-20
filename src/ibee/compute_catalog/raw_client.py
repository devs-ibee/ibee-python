# Compute catalog raw client. Mirrors the Fern-generated resource clients
# (e.g. cloud_vms/raw_client.py) so it uses the same shared core, error
# handling, and request pipeline. Endpoints are read-only GETs; the payload is
# returned as parsed JSON (typing.Any) rather than a typed model.

import typing
from json.decoder import JSONDecodeError

from ..core.api_error import ApiError
from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.http_response import AsyncHttpResponse, HttpResponse
from ..core.pydantic_utilities import parse_obj_as
from ..core.request_options import RequestOptions
from ..errors.forbidden_error import ForbiddenError
from ..errors.unauthorized_error import UnauthorizedError
from ..types.error import Error


def _params(workspace_id: str, extra: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
    params: typing.Dict[str, typing.Any] = {"workspace_id": workspace_id}
    params.update({k: v for k, v in extra.items() if v is not None})
    return params


def _handle(_response: typing.Any) -> HttpResponse[typing.Any]:
    try:
        if 200 <= _response.status_code < 300:
            return HttpResponse(response=_response, data=_response.json())
        if _response.status_code == 401:
            raise UnauthorizedError(
                headers=dict(_response.headers),
                body=typing.cast(Error, parse_obj_as(type_=Error, object_=_response.json())),  # type: ignore
            )
        if _response.status_code == 403:
            raise ForbiddenError(
                headers=dict(_response.headers),
                body=typing.cast(Error, parse_obj_as(type_=Error, object_=_response.json())),  # type: ignore
            )
        _response_json = _response.json()
    except JSONDecodeError:
        raise ApiError(status_code=_response.status_code, headers=dict(_response.headers), body=_response.text)
    raise ApiError(status_code=_response.status_code, headers=dict(_response.headers), body=_response_json)


class RawComputeCatalogClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def list_compute_sites(
        self,
        *,
        workspace_id: str,
        region_id: typing.Optional[str] = None,
        country_id: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> HttpResponse[typing.Any]:
        _response = self._client_wrapper.httpx_client.request(
            "compute/sites",
            method="GET",
            params=_params(workspace_id, {"region_id": region_id, "country_id": country_id}),
            request_options=request_options,
        )
        return _handle(_response)

    def list_compute_plans(
        self,
        *,
        workspace_id: str,
        vm_type: typing.Optional[str] = None,
        site_id: typing.Optional[str] = None,
        currency: typing.Optional[str] = None,
        billing_interval: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> HttpResponse[typing.Any]:
        _response = self._client_wrapper.httpx_client.request(
            "compute/plans",
            method="GET",
            params=_params(workspace_id, {
                "vm_type": vm_type, "site_id": site_id,
                "currency": currency, "billing_interval": billing_interval,
            }),
            request_options=request_options,
        )
        return _handle(_response)

    def list_compute_images(
        self,
        *,
        workspace_id: str,
        vm_type: typing.Optional[str] = None,
        currency: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> HttpResponse[typing.Any]:
        _response = self._client_wrapper.httpx_client.request(
            "compute/images",
            method="GET",
            params=_params(workspace_id, {"vm_type": vm_type, "currency": currency}),
            request_options=request_options,
        )
        return _handle(_response)


class AsyncRawComputeCatalogClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def list_compute_sites(
        self,
        *,
        workspace_id: str,
        region_id: typing.Optional[str] = None,
        country_id: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncHttpResponse[typing.Any]:
        _response = await self._client_wrapper.httpx_client.request(
            "compute/sites",
            method="GET",
            params=_params(workspace_id, {"region_id": region_id, "country_id": country_id}),
            request_options=request_options,
        )
        _sync = _handle(_response)
        return AsyncHttpResponse(response=_response, data=_sync.data)

    async def list_compute_plans(
        self,
        *,
        workspace_id: str,
        vm_type: typing.Optional[str] = None,
        site_id: typing.Optional[str] = None,
        currency: typing.Optional[str] = None,
        billing_interval: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncHttpResponse[typing.Any]:
        _response = await self._client_wrapper.httpx_client.request(
            "compute/plans",
            method="GET",
            params=_params(workspace_id, {
                "vm_type": vm_type, "site_id": site_id,
                "currency": currency, "billing_interval": billing_interval,
            }),
            request_options=request_options,
        )
        _sync = _handle(_response)
        return AsyncHttpResponse(response=_response, data=_sync.data)

    async def list_compute_images(
        self,
        *,
        workspace_id: str,
        vm_type: typing.Optional[str] = None,
        currency: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncHttpResponse[typing.Any]:
        _response = await self._client_wrapper.httpx_client.request(
            "compute/images",
            method="GET",
            params=_params(workspace_id, {"vm_type": vm_type, "currency": currency}),
            request_options=request_options,
        )
        _sync = _handle(_response)
        return AsyncHttpResponse(response=_response, data=_sync.data)
