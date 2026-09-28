# Hand-written (listed in .fernignore).
"""Map an error HTTP response to the most specific typed ``ApiError`` subclass."""

from __future__ import annotations

import re
import typing

from ..core.api_error import ApiError, parse_error_payload
from ..core.pydantic_utilities import parse_obj_as
from ..types.error import Error
from .api_errors import (
    ApiKeyInactiveError,
    GatewayTimeoutError,
    InsufficientScopeError,
    InternalServerError,
    InvalidWorkspaceError,
    OrganizationRestrictedError,
    OrganizationSuspendedError,
    PayloadTooLargeError,
    RouteNotAvailableError,
    TooManyRequestsError,
    UnprocessableEntityError,
    WorkspaceNotAllowedError,
)
from .bad_gateway_error import BadGatewayError
from .bad_request_error import BadRequestError
from .billing_errors import BillingAdmissionError, BillingDeniedError, BillingForbiddenError
from .compute_errors import ResizeBlockedError
from .conflict_error import ConflictError
from .forbidden_error import ForbiddenError
from .not_found_error import NotFoundError
from .payment_required_error import PaymentRequiredError
from .service_unavailable_error import ServiceUnavailableError
from .unauthorized_error import UnauthorizedError

#: Statuses whose ``.body`` is the generated ``Error`` model (0.3.0 behaviour).
TYPED_BODY_STATUSES = frozenset({400, 401, 402, 403, 404, 409, 502, 503})

_WORKSPACE_CODES = frozenset({"workspace_id_required", "invalid_workspace_id"})
_KEY_INACTIVE_CODES = frozenset({"key_revoked", "key_disabled", "key_inactive", "key_expired"})
_BILLING_ADMISSION_CODES = frozenset(
    {
        "billing_admission_error",
        "invalid_billing_decision",
        "compute_catalog_error",
        "invalid_compute_catalog_response",
        "ambiguous_compute_plan",
        "unpriced_compute_plan",
        "product_catalog_error",
        "invalid_product_catalog_response",
        "block_storage_plan_unavailable",
        "ambiguous_block_storage_plan",
    }
)
_WORKSPACE_MISMATCH_MESSAGES = ("does not match api token context", "does not belong to workspace")
_RESTRICTED_MESSAGE = re.compile(r"^Operation '[A-Za-z_]+' is not allowed while organization is [A-Za-z_]+$")
_STORAGE_RESTRICTED_MESSAGES = frozenset(
    {"Storage namespace changes are restricted", "Storage namespace is not active"}
)
_DENIED_REASONS = frozenset(
    {
        "initial_topup_required",
        "insufficient_balance",
        "credit_limit_exceeded",
        "unknown_sku",
        "inactive_sku",
        "billing_limit_exhausted",
        "overage_cap_exceeded",
        "dunning_active",
        "dunning_grace_expired",
    }
)

_CREATE_TYPE_BY_PATH: typing.Tuple[typing.Tuple[typing.Pattern[str], str], ...] = tuple(
    (re.compile(pattern), create_type)
    for pattern, create_type in (
        (r"^/compute/cloud-vms/?$", "vm"),
        (r"^/compute/gpu-vms/?$", "gpu_vm"),
        (r"^/block-storage/volumes/?$", "block_storage"),
        (r"^/object-storage/buckets/?$", "object_storage"),
        (r"^/object-storage/credentials/?$", "s3_credential"),
        (r"^/networking/load-balancers/(l4|l7)/?$", "load_balancer"),
        (r"^/networking/reserved-ips/?$", "reserved_ip"),
        (r"^/networking/vpcs/[^/]+/nat-gateways/?$", "nat_gateway"),
        (r"^/cdn/distributions/[^/]+/custom-domains/?$", "custom_domain"),
        (r"^/cdn/distributions/?$", "cdn"),
        (r"^/secret-store/stores/[^/]+/secrets/?$", "secret"),
        (r"^/secret-store/stores/?$", "secret_store"),
    )
)


def create_type_for_path(path: typing.Optional[str]) -> str:
    """Billing create type for a create path (used to word 402 messages)."""
    from ..validation import normalize_api_path

    normalized = normalize_api_path(path)
    for pattern, create_type in _CREATE_TYPE_BY_PATH:
        if pattern.fullmatch(normalized):
            return create_type
    return "resource"


def _select_class(status_code: int, info: typing.Dict[str, typing.Any], raw_body: typing.Any) -> typing.Type[ApiError]:
    code = info["code"]
    message = info["message"] or ""
    if status_code == 400:
        return InvalidWorkspaceError if code in _WORKSPACE_CODES else BadRequestError
    if status_code == 401:
        return UnauthorizedError
    if status_code == 402:
        return BillingDeniedError if code == "billing_denied" else PaymentRequiredError
    if status_code == 403:
        lowered = message.lower()
        if code == "insufficient_scope":
            return InsufficientScopeError
        if code in _KEY_INACTIVE_CODES:
            return ApiKeyInactiveError
        if code == "workspace_not_allowed" or any(text in lowered for text in _WORKSPACE_MISMATCH_MESSAGES):
            return WorkspaceNotAllowedError
        if code == "unknown_route":
            return RouteNotAvailableError
        if (
            code == "organization_restricted"
            or _RESTRICTED_MESSAGE.match(message)
            or message in _STORAGE_RESTRICTED_MESSAGES
        ):
            return OrganizationRestrictedError
        if (
            code == "forbidden"
            and isinstance(raw_body, dict)
            and isinstance(raw_body.get("error"), dict)
            and message.strip().lower() in _DENIED_REASONS
        ):
            return BillingForbiddenError
        return ForbiddenError
    if status_code == 404:
        return NotFoundError
    if status_code == 409:
        detail = raw_body.get("detail") if isinstance(raw_body, dict) else None
        if isinstance(detail, dict) and detail.get("decision"):
            return ResizeBlockedError
        return ConflictError
    if status_code == 413:
        return PayloadTooLargeError
    if status_code == 422:
        return UnprocessableEntityError
    if status_code == 423:
        return OrganizationSuspendedError
    if status_code == 429:
        return TooManyRequestsError
    if status_code == 500:
        return InternalServerError
    if status_code == 502:
        return BillingAdmissionError if code in _BILLING_ADMISSION_CODES else BadGatewayError
    if status_code == 503:
        return ServiceUnavailableError
    if status_code == 504:
        return GatewayTimeoutError
    return ApiError


def _typed_body(status_code: int, raw_body: typing.Any) -> typing.Any:
    if status_code in TYPED_BODY_STATUSES and isinstance(raw_body, dict):
        try:
            return parse_obj_as(type_=Error, object_=raw_body)  # type: ignore
        except Exception:
            return raw_body
    return raw_body


def error_from_response(
    status_code: int,
    body: typing.Any,
    headers: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    idempotency_key: typing.Optional[str] = None,
    *,
    path: typing.Optional[str] = None,
) -> ApiError:
    """Build the most specific ``ApiError`` subclass for an error response.

    ``body`` is the parsed JSON body (or the response text). ``path`` (relative to
    the API root) is only used to word billing denials for the resource being created.
    """
    header_dict = dict(headers) if headers is not None else None
    info = parse_error_payload(status_code, body, header_dict)
    cls = _select_class(status_code, info, body)
    typed_body = _typed_body(status_code, body)
    error: ApiError
    if cls is ApiError:
        error = ApiError(status_code=status_code, headers=header_dict, body=typed_body)
    elif cls is BillingDeniedError:
        error = BillingDeniedError(typed_body, header_dict, create_type=create_type_for_path(path))
    else:
        error = cls(body=typed_body, headers=header_dict)  # type: ignore[call-arg]
    if error.status_code != status_code:
        error.status_code = status_code
    error._populate(body)
    error.idempotency_key = idempotency_key
    return error


def is_payment_block_error(error: typing.Any) -> bool:
    """Whether an exception is a billing/payment wall rather than an ordinary failure.

    True for ``BillingDeniedError``/``BillingForbiddenError``, any HTTP 402, codes
    ``billing_denied``/``insufficient_balance``/``insufficient_funds``, or a message
    mentioning "insufficient", "payment required", "add a payment method" or "top up".
    """
    if error is None:
        return False
    if isinstance(error, (BillingDeniedError, BillingForbiddenError)):
        return True
    status = getattr(error, "status_code", None)
    if status is None:
        status = getattr(error, "status", None)
    if status == 402:
        return True
    code = str(getattr(error, "code", "") or "").strip().lower()
    if code in ("billing_denied", "insufficient_balance", "insufficient_funds"):
        return True
    message = str(getattr(error, "message", None) or (error.args[0] if getattr(error, "args", None) else "") or "")
    lowered = message.lower()
    return any(
        text in lowered for text in ("insufficient", "payment required", "add a payment method", "top up")
    )


__all__ = ["create_type_for_path", "error_from_response", "is_payment_block_error"]
