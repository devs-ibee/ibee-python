"""0.4.0 typed error hierarchy and error-body parsing."""

from __future__ import annotations

import asyncio

import httpx
import pytest

from ibee import AsyncIbee, Ibee
from ibee.core.api_error import ApiError
from ibee.errors import (
    ApiKeyInactiveError,
    BadGatewayError,
    BadRequestError,
    BillingAdmissionError,
    BillingDeniedError,
    BillingEligibilityError,
    BillingForbiddenError,
    ConflictError,
    ForbiddenError,
    GatewayTimeoutError,
    InsufficientScopeError,
    InternalServerError,
    InvalidWorkspaceError,
    NotFoundError,
    OrganizationRestrictedError,
    OrganizationSuspendedError,
    PayloadTooLargeError,
    PaymentRequiredError,
    RouteNotAvailableError,
    ServiceUnavailableError,
    TooManyRequestsError,
    UnauthorizedError,
    UnprocessableEntityError,
    WorkspaceNotAllowedError,
    error_from_response,
    is_payment_block_error,
)
from ibee.types import Error

BASE = "https://api.example.test/v1"


def _edge(error: str, **extra: object) -> dict:
    body = {
        "error": error,
        "required_scope": None,
        "billing_reason": None,
        "billing_sku_code": None,
        "admission_context_id": None,
    }
    body.update(extra)
    return body


@pytest.mark.parametrize(
    ("status", "body", "cls", "code"),
    [
        (400, _edge("invalid_workspace_id"), InvalidWorkspaceError, "invalid_workspace_id"),
        (400, {"detail": "bad"}, BadRequestError, "bad_request"),
        (401, _edge("invalid_api_key"), UnauthorizedError, "invalid_api_key"),
        (402, _edge("billing_denied", billing_reason="insufficient_balance"), BillingDeniedError, "billing_denied"),
        (402, {"detail": "pay"}, PaymentRequiredError, "payment_required"),
        (403, _edge("insufficient_scope", required_scope="vm.write"), InsufficientScopeError, "insufficient_scope"),
        (403, _edge("key_revoked"), ApiKeyInactiveError, "key_revoked"),
        (403, _edge("workspace_not_allowed"), WorkspaceNotAllowedError, "workspace_not_allowed"),
        (403, {"detail": "Workspace does not match API token context"}, WorkspaceNotAllowedError, "forbidden"),
        (403, _edge("unknown_route"), RouteNotAvailableError, "unknown_route"),
        (
            403,
            {"error": {"code": "FORBIDDEN", "message": "Operation 'CREATE_RESOURCE' is not allowed while organization is restricted"}},
            OrganizationRestrictedError,
            "forbidden",
        ),
        (403, {"detail": "Storage namespace changes are restricted"}, OrganizationRestrictedError, "forbidden"),
        (
            403,
            {"error": {"code": "FORBIDDEN", "message": "insufficient_balance"}},
            BillingForbiddenError,
            "forbidden",
        ),
        (403, {"detail": "nope"}, ForbiddenError, "forbidden"),
        (404, {"detail": {"code": "NOT_FOUND", "message": "BillingProfile not found: org"}}, NotFoundError, "not_found"),
        (409, "Operation already in progress", ConflictError, "conflict"),
        (413, _edge("request_body_too_large"), PayloadTooLargeError, "request_body_too_large"),
        (422, {"detail": [{"loc": ["body", "sku_code"], "msg": "too long"}]}, UnprocessableEntityError, "validation_error"),
        (423, {"detail": {"code": "ORG_BILLING_SUSPENDED", "message": "suspended"}}, OrganizationSuspendedError, "org_billing_suspended"),
        (429, "slow down", TooManyRequestsError, "rate_limited"),
        (500, "boom", InternalServerError, "internal_error"),
        (502, _edge("invalid_billing_decision"), BillingAdmissionError, "invalid_billing_decision"),
        (502, {"detail": "upstream"}, BadGatewayError, "bad_gateway"),
        (503, _edge("workspace_verification_unavailable"), ServiceUnavailableError, "workspace_verification_unavailable"),
        (504, "timeout", GatewayTimeoutError, "gateway_timeout"),
        (418, {"detail": "teapot"}, ApiError, "http_418"),
    ],
)
def test_error_from_response_selects_typed_class(status: int, body: object, cls: type, code: str) -> None:
    error = error_from_response(status, body, {"x-request-id": "req-1"}, "key-1")
    assert type(error) is cls
    assert isinstance(error, ApiError)
    assert error.status_code == status
    assert error.code == code
    assert error.request_id == "req-1"
    assert error.idempotency_key == "key-1"
    assert error.message


def test_error_messages_and_fields_per_shape() -> None:
    scope = error_from_response(403, _edge("insufficient_scope", required_scope="billing.read"))
    assert scope.required_scope == "billing.read"

    secret = error_from_response(400, {"error": {"code": "VALIDATION_ERROR", "message": "bad name", "details": {"f": 1}}})
    assert (secret.code, secret.raw_code, secret.message, secret.details) == (
        "validation_error",
        "VALIDATION_ERROR",
        "bad name",
        {"f": 1},
    )

    validation = error_from_response(
        422,
        {"detail": [{"loc": ["body", "sku_code"], "msg": "too long"}, {"loc": ["query", "limit"], "msg": "too big"}]},
    )
    assert validation.message == "sku_code: too long, limit: too big"

    plain = error_from_response(409, "Name already exists")
    assert plain.message == "Name already exists" and plain.raw_body == "Name already exists"

    empty = error_from_response(503, None)
    assert empty.message == "IBEE API error 503" and empty.retryable is True

    restricted = error_from_response(
        403, {"error": {"code": "FORBIDDEN", "message": "Operation 'CREATE_RESOURCE' is not allowed while organization is restricted"}}
    )
    assert isinstance(restricted, OrganizationRestrictedError)
    assert (restricted.operation, restricted.state) == ("CREATE_RESOURCE", "restricted")

    suspended = error_from_response(
        423,
        {"detail": {"code": "ORG_BILLING_SUSPENDED", "billing_state": "HARD_SUSPENDED", "allowed_operations": ["billing_topup"]}},
    )
    assert isinstance(suspended, OrganizationSuspendedError)
    assert suspended.billing_state == "HARD_SUSPENDED" and suspended.allowed_operations == ["billing_topup"]

    limited = error_from_response(429, "slow", {"Retry-After": "7"})
    assert limited.retry_after == 7.0


def test_edge_billing_denial_uses_portal_copy() -> None:
    error = error_from_response(
        402,
        _edge(
            "billing_denied",
            billing_reason="initial_topup_required",
            billing_sku_code="STANDARD-2-8",
            admission_context_id="adm-1",
        ),
        path="compute/cloud-vms",
    )
    assert isinstance(error, BillingDeniedError)
    assert isinstance(error, PaymentRequiredError) and isinstance(error, BillingEligibilityError)
    assert error.reason == "initial_topup_required"
    assert error.sku_code == "STANDARD-2-8"
    assert error.admission_context_id == "adm-1"
    assert error.topup_allowed is True
    assert str(error) == "Add at least ₹2,000 to your wallet before creating your first cloud VM."
    assert is_payment_block_error(error)


def test_typed_body_keeps_0_3_0_error_model() -> None:
    error = error_from_response(404, {"detail": "Operation not found"})
    assert isinstance(error.body, Error)
    assert error.body.detail == "Operation not found"
    listed = error_from_response(400, {"detail": [{"loc": ["x"], "msg": "bad"}]})
    assert listed.body == {"detail": [{"loc": ["x"], "msg": "bad"}]}


def test_is_payment_block_error() -> None:
    assert is_payment_block_error(error_from_response(402, {"detail": "x"}))
    assert is_payment_block_error(error_from_response(400, {"error": {"code": "INSUFFICIENT_FUNDS", "message": "x"}}))
    assert is_payment_block_error(error_from_response(400, {"detail": "Please top up your wallet"}))
    assert not is_payment_block_error(error_from_response(400, {"detail": "balance of load is off"}))
    assert not is_payment_block_error(ValueError("nope"))
    assert not is_payment_block_error(None)


def test_transport_raises_typed_errors_for_every_method() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403, json=_edge("insufficient_scope", required_scope="vm.read"), headers={"x-request-id": "r-9"}, request=request
        )

    client = Ibee(token="t", base_url=BASE, httpx_client=httpx.Client(transport=httpx.MockTransport(handler)))
    with pytest.raises(InsufficientScopeError) as info:
        client.cloud_vms.list_cloud_vms(workspace_id="710995")
    assert info.value.required_scope == "vm.read"
    assert info.value.request_id == "r-9"
    # A 0.3.0 except clause still matches.
    assert isinstance(info.value, ForbiddenError)


def test_async_transport_raises_typed_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Operation not found"}, request=request)

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            client = AsyncIbee(token="t", base_url=BASE, httpx_client=http_client)
            await client.cloud_vms.get_compute_operation("op-1", workspace_id="710995")

    with pytest.raises(NotFoundError) as info:
        asyncio.run(run())
    assert info.value.code == "not_found"
    assert info.value.message == "Operation not found"
