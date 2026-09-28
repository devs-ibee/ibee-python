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
    the API root) is used to word billing denials for the resource being created and
    to pick the Secret Store error classes (see :mod:`ibee.errors.secret_store_errors`).
    """
    header_dict = dict(headers) if headers is not None else None
    info = parse_error_payload(status_code, body, header_dict)
    cls: typing.Optional[typing.Type[ApiError]] = None
    if path is not None:
        from ..validation import normalize_api_path
        from .secret_store_errors import select_secret_store_error_class

        normalized = normalize_api_path(path)
        if normalized.startswith("/secret-store/"):
            cls = select_secret_store_error_class(status_code, info, normalized)
    if cls is None:
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


#: Structured codes (error ``code``, operation ``error_code``) that mean a payment wall.
PAYMENT_BLOCK_CODES = frozenset(
    {"billing_denied", "payment_required", "insufficient_balance", "insufficient_funds"} | _DENIED_REASONS
)
#: Conservative text fallback, used only when an error carries no structured code: whole phrases,
#: never a bare "insufficient" (``insufficient_scope``, "insufficient capacity") or "balance" ("load balancer").
PAYMENT_BLOCK_PHRASES = (
    "insufficient balance",
    "insufficient wallet balance",
    "insufficient funds",
    "insufficient credit",
    "payment required",
    "add a payment method",
    "top up",
    "top-up",
)


def _lookup(error: typing.Any, *names: str) -> typing.Any:
    for name in names:
        value = error.get(name) if isinstance(error, typing.Mapping) else getattr(error, name, None)
        if value is not None:
            return value
    return None


def _norm(value: typing.Any) -> str:
    return str(getattr(value, "value", value) or "").strip().lower()


def is_payment_block_error(error: typing.Any) -> bool:
    """Whether an exception is a billing/payment wall rather than an ordinary failure.

    Checked in order (the TypeScript SDK applies the same rules):

    1. ``BillingDeniedError`` / ``BillingForbiddenError`` -> ``True``.
    2. A missing scope (``InsufficientScopeError`` or code ``insufficient_scope``) -> ``False``.
    3. HTTP status 402 -> ``True``.
    4. A structured code (``code``, or an operation's ``error_code``) or billing reason (``reason``,
       parsed from ``billing_reason``) of ``billing_denied``, ``payment_required``,
       ``insufficient_balance``, ``insufficient_funds`` or a billing denial reason such as
       ``initial_topup_required`` or ``credit_limit_exceeded`` -> ``True``.
    5. An API error whose body carried its own code -> ``False`` (the code is authoritative).
    6. Otherwise only the server's (or exception's) message is checked, for whole phrases such as
       "insufficient balance", "payment required", "add a payment method" or "top up".
    """
    if error is None:
        return False
    if isinstance(error, (BillingDeniedError, BillingForbiddenError)):
        return True
    code = _norm(_lookup(error, "code"))
    if isinstance(error, InsufficientScopeError) or code == "insufficient_scope":
        return False
    status = _lookup(error, "status_code", "status")
    if status == 402:
        return True
    reason = _norm(_lookup(error, "reason", "billing_reason"))
    error_code = _norm(_lookup(error, "error_code"))
    if code in PAYMENT_BLOCK_CODES or error_code in PAYMENT_BLOCK_CODES or reason in PAYMENT_BLOCK_CODES:
        return True
    if isinstance(error, ApiError):
        if getattr(error, "raw_code", None):
            return False
        message = getattr(error, "message", None)
        if message == _fallback_message(error.status_code):
            message = None  # the SDK's placeholder, not a server message
    else:
        message = _lookup(error, "message")
        if message is None and isinstance(error, BaseException) and error.args:
            message = error.args[0]
    lowered = " ".join(str(message or "").lower().split())
    return any(phrase in lowered for phrase in PAYMENT_BLOCK_PHRASES)


def _fallback_message(status_code: typing.Optional[int]) -> str:
    return f"IBEE API error {status_code}" if status_code is not None else "IBEE API error"


__all__ = [
    "PAYMENT_BLOCK_CODES",
    "PAYMENT_BLOCK_PHRASES",
    "create_type_for_path",
    "error_from_response",
    "is_payment_block_error",
]
