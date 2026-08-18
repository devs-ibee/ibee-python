from __future__ import annotations

import typing
from json.decoder import JSONDecodeError

from pydantic import ValidationError

from ..core.api_error import ApiError
from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.http_response import AsyncHttpResponse, HttpResponse
from ..core.parse_error import ParsingError
from ..core.pydantic_utilities import parse_obj_as
from ..core.request_options import RequestOptions
from ..errors.bad_request_error import BadRequestError
from ..errors.forbidden_error import ForbiddenError
from ..errors.unauthorized_error import UnauthorizedError
from ..types.error import Error
from .models import BillingEligibility


def _handle_response(response: typing.Any) -> HttpResponse[BillingEligibility]:
    try:
        if 200 <= response.status_code < 300:
            return HttpResponse(
                response=response,
                data=typing.cast(
                    BillingEligibility,
                    parse_obj_as(type_=BillingEligibility, object_=response.json()),  # type: ignore
                ),
            )
        error_type = {
            400: BadRequestError,
            401: UnauthorizedError,
            403: ForbiddenError,
        }.get(response.status_code)
        if error_type is not None:
            raise error_type(
                headers=dict(response.headers),
                body=typing.cast(Error, parse_obj_as(type_=Error, object_=response.json())),  # type: ignore
            )
        response_json = response.json()
    except JSONDecodeError:
        raise ApiError(status_code=response.status_code, headers=dict(response.headers), body=response.text)
    except ValidationError as exc:
        raise ParsingError(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.json(),
            cause=exc,
        ) from exc
    raise ApiError(status_code=response.status_code, headers=dict(response.headers), body=response_json)


class RawBillingClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def check_resource_eligibility(
        self,
        *,
        workspace_id: str,
        sku_code: typing.Optional[str] = None,
        estimated_cost_minor: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> HttpResponse[BillingEligibility]:
        """Check billing eligibility without creating or modifying a resource."""
        response = self._client_wrapper.httpx_client.request(
            "billing/resource-eligibility",
            method="POST",
            params={"workspace_id": workspace_id},
            json={
                key: value
                for key, value in {
                    "sku_code": sku_code,
                    "estimated_cost_minor": estimated_cost_minor,
                }.items()
                if value is not None
            },
            headers={"content-type": "application/json"},
            request_options=request_options,
        )
        return _handle_response(response)


class AsyncRawBillingClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def check_resource_eligibility(
        self,
        *,
        workspace_id: str,
        sku_code: typing.Optional[str] = None,
        estimated_cost_minor: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncHttpResponse[BillingEligibility]:
        """Check billing eligibility without creating or modifying a resource."""
        response = await self._client_wrapper.httpx_client.request(
            "billing/resource-eligibility",
            method="POST",
            params={"workspace_id": workspace_id},
            json={
                key: value
                for key, value in {
                    "sku_code": sku_code,
                    "estimated_cost_minor": estimated_cost_minor,
                }.items()
                if value is not None
            },
            headers={"content-type": "application/json"},
            request_options=request_options,
        )
        parsed = _handle_response(response)
        return AsyncHttpResponse(response=response, data=parsed.data)
