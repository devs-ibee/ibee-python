# Hand-written (listed in .fernignore).
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
from ..validation import (
    normalize_eligibility_operation,
    normalize_estimated_cost_minor,
    normalize_sku_code,
    validate_workspace_id,
)
from .models import BillingEligibility

ELIGIBILITY_PATH = "billing/resource-eligibility"


def eligibility_request_body(
    *,
    sku_code: typing.Optional[str] = None,
    estimated_cost_minor: typing.Any = None,
    operation: typing.Optional[str] = None,
) -> typing.Dict[str, typing.Any]:
    """Validate and normalise eligibility inputs; blank or ``None`` values are omitted."""
    body = {
        "sku_code": normalize_sku_code(sku_code),
        "estimated_cost_minor": normalize_estimated_cost_minor(estimated_cost_minor),
        "operation": normalize_eligibility_operation(operation),
    }
    return {key: value for key, value in body.items() if value is not None}


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

    def _post_eligibility(
        self,
        *,
        workspace_id: str,
        body: typing.Dict[str, typing.Any],
        request_options: typing.Optional[RequestOptions],
    ) -> typing.Any:
        return self._client_wrapper.httpx_client.request(
            ELIGIBILITY_PATH,
            method="POST",
            params={"workspace_id": validate_workspace_id(workspace_id)},
            json=body,
            headers={"content-type": "application/json"},
            request_options=request_options,
        )

    def check_resource_eligibility(
        self,
        *,
        workspace_id: str,
        sku_code: typing.Optional[str] = None,
        estimated_cost_minor: typing.Optional[int] = None,
        operation: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> HttpResponse[BillingEligibility]:
        """Check billing eligibility without creating or modifying a resource."""
        body = eligibility_request_body(
            sku_code=sku_code, estimated_cost_minor=estimated_cost_minor, operation=operation
        )
        return _handle_response(
            self._post_eligibility(workspace_id=workspace_id, body=body, request_options=request_options)
        )


class AsyncRawBillingClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def _post_eligibility(
        self,
        *,
        workspace_id: str,
        body: typing.Dict[str, typing.Any],
        request_options: typing.Optional[RequestOptions],
    ) -> typing.Any:
        return await self._client_wrapper.httpx_client.request(
            ELIGIBILITY_PATH,
            method="POST",
            params={"workspace_id": validate_workspace_id(workspace_id)},
            json=body,
            headers={"content-type": "application/json"},
            request_options=request_options,
        )

    async def check_resource_eligibility(
        self,
        *,
        workspace_id: str,
        sku_code: typing.Optional[str] = None,
        estimated_cost_minor: typing.Optional[int] = None,
        operation: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> AsyncHttpResponse[BillingEligibility]:
        """Check billing eligibility without creating or modifying a resource."""
        body = eligibility_request_body(
            sku_code=sku_code, estimated_cost_minor=estimated_cost_minor, operation=operation
        )
        response = await self._post_eligibility(workspace_id=workspace_id, body=body, request_options=request_options)
        parsed = _handle_response(response)
        return AsyncHttpResponse(response=response, data=parsed.data)
