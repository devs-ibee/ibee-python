"""Client-side validation shared by every IBEE SDK operation and the IBEE CLI.

Every check in this module runs *before* any HTTP request is sent and raises
:class:`IbeeValidationError` on failure. ``IbeeValidationError`` subclasses
:class:`ValueError`, so code written for 0.3.0 that caught ``ValueError`` keeps
working.
"""

from __future__ import annotations

import json
import math
import numbers
import re
import typing
from urllib.parse import urlsplit

from ..errors.ibee_error import IbeeError

if typing.TYPE_CHECKING:
    from ..environment import IbeeEnvironment


class IbeeValidationError(IbeeError, ValueError):
    """Raised when a request fails client-side validation, before any HTTP call.

    Attributes
    ----------
    code : str
        Stable snake_case identifier, for example ``invalid_workspace_id``.
    field : typing.Optional[str]
        The argument that failed validation, when there is one.
    message : str
        Human-readable description (also returned by ``str(error)``).
    details : typing.Any
        Extra context when there is some, for example the resize precheck result
        (``decision``, ``reasons``, ``warnings``) or the eligible plan ids.
    """

    code: str = "validation_error"

    def __init__(
        self,
        message: str,
        *,
        code: str = "validation_error",
        field: typing.Optional[str] = None,
        details: typing.Any = None,
    ) -> None:
        super().__init__(message, code=code)
        self.field = field
        self.details = details


# ---------------------------------------------------------------------------
# workspace_id
# ---------------------------------------------------------------------------

WORKSPACE_ID_PATTERN = re.compile(r"^[1-9][0-9]*$")
WORKSPACE_ID_ERROR = "workspace_id must be a positive numeric string (for example, '710995')."


def validate_workspace_id(workspace_id: typing.Any) -> str:
    """Return ``workspace_id`` as a string, or raise ``IbeeValidationError``.

    A positive ``int`` (not ``bool``) is accepted and converted with ``str()``.
    """
    if isinstance(workspace_id, int) and not isinstance(workspace_id, bool) and workspace_id > 0:
        workspace_id = str(workspace_id)
    if not isinstance(workspace_id, str) or WORKSPACE_ID_PATTERN.fullmatch(workspace_id) is None:
        raise IbeeValidationError(WORKSPACE_ID_ERROR, code="invalid_workspace_id", field="workspace_id")
    return workspace_id


# ---------------------------------------------------------------------------
# Environments, base URLs and tokens
# ---------------------------------------------------------------------------

PRODUCTION_HOST = "api.ibee.ai"
DEVELOPMENT_HOST = "api.ibee.co.in"
PRODUCTION_TOKEN_PREFIX = "ibee_prod_key_"
DEVELOPMENT_TOKEN_PREFIX = "ibee_dev_key_"
_LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})
TOKEN_ENVIRONMENT_MISMATCH_MESSAGE = "The API token environment does not match the configured IBEE endpoint."


def _invalid_base_url(reason: str) -> IbeeValidationError:
    return IbeeValidationError(f"Invalid IBEE base URL: {reason}.", code="invalid_base_url", field="base_url")


def resolve_base_url(
    base_url: typing.Optional[str] = None,
    environment: typing.Optional[typing.Union["IbeeEnvironment", str]] = None,
) -> str:
    """Resolve and validate the API base URL.

    Precedence: an explicit ``base_url`` wins over ``environment``; with neither,
    production (``https://api.ibee.ai/v1``) is used. The URL must be an absolute
    ``https`` URL (``http`` only for localhost, 127.0.0.1 or ::1) with a host and
    no credentials, query, fragment, or ``.``/``..`` path segments. Any trailing
    ``/`` is removed.
    """
    if base_url is None:
        if environment is None:
            from ..environment import IbeeEnvironment

            environment = IbeeEnvironment.PRODUCTION
        base_url = environment if isinstance(environment, str) else environment.value
    if not isinstance(base_url, str) or not base_url.strip():
        raise _invalid_base_url("it must be a non-empty string")
    url = base_url.strip()
    try:
        parts = urlsplit(url)
        hostname = parts.hostname
        _ = parts.port
    except ValueError as exc:
        raise _invalid_base_url(str(exc)) from exc
    scheme = parts.scheme.lower()
    if scheme not in ("http", "https"):
        raise _invalid_base_url("use an absolute https:// URL")
    if not hostname:
        raise _invalid_base_url("the URL has no host")
    if parts.username is not None or parts.password is not None or "@" in parts.netloc:
        raise _invalid_base_url("credentials are not allowed in the URL")
    if "?" in url or parts.query:
        raise _invalid_base_url("a query string is not allowed")
    if "#" in url or parts.fragment:
        raise _invalid_base_url("a fragment is not allowed")
    if any(segment in (".", "..") for segment in parts.path.split("/")):
        raise _invalid_base_url("'.' and '..' path segments are not allowed")
    if scheme == "http" and hostname.lower() not in _LOOPBACK_HOSTS:
        raise _invalid_base_url("http:// is only allowed for localhost; use https://")
    return url.rstrip("/")


def validate_token(token: typing.Any) -> str:
    """Require a non-empty token string without CR/LF characters."""
    if not isinstance(token, str) or not token.strip():
        raise IbeeValidationError("The API token must be a non-empty string.", code="invalid_token", field="token")
    if "\r" in token or "\n" in token:
        raise IbeeValidationError(
            "The API token must not contain line breaks.", code="invalid_token", field="token"
        )
    return token


def _host_of(base_url: str) -> str:
    try:
        host = urlsplit(base_url).hostname or ""
    except ValueError:
        return ""
    return host.lower().rstrip(".")


def check_token_environment(token: str, base_url: str) -> None:
    """Reject a development token sent to production, or a production token sent to development.

    Only the two public IBEE hosts are checked; any other host (for example a local
    mock server) and tokens without an ``ibee_dev_key_``/``ibee_prod_key_`` prefix
    are accepted.
    """
    host = _host_of(base_url)
    if (host == PRODUCTION_HOST and token.startswith(DEVELOPMENT_TOKEN_PREFIX)) or (
        host == DEVELOPMENT_HOST and token.startswith(PRODUCTION_TOKEN_PREFIX)
    ):
        raise IbeeValidationError(
            TOKEN_ENVIRONMENT_MISMATCH_MESSAGE, code="token_environment_mismatch", field="token"
        )


def validate_token_for_base_url(token: typing.Any, base_url: str) -> str:
    """``validate_token`` followed by ``check_token_environment``."""
    token = validate_token(token)
    check_token_environment(token, base_url)
    return token


# ---------------------------------------------------------------------------
# Idempotency keys
# ---------------------------------------------------------------------------

IDEMPOTENCY_KEY_PATTERN = re.compile(r"^[!-~]{1,128}$")


def validate_idempotency_key(key: typing.Any, *, field: str = "idempotency_key") -> str:
    """A caller-supplied key must be 1-128 printable ASCII characters with no whitespace."""
    if not isinstance(key, str) or IDEMPOTENCY_KEY_PATTERN.fullmatch(key) is None:
        raise IbeeValidationError(
            "idempotency_key must be 1-128 printable ASCII characters without spaces or line breaks.",
            code="invalid_idempotency_key",
            field=field,
        )
    return key


# ---------------------------------------------------------------------------
# Identifiers
# ---------------------------------------------------------------------------


def validate_operation_id(operation_id: typing.Any) -> str:
    """Return the stripped operation id, or raise when it is blank."""
    if not isinstance(operation_id, str) or not operation_id.strip():
        raise IbeeValidationError(
            "operation_id must be a non-empty string.", code="invalid_operation_id", field="operation_id"
        )
    return operation_id.strip()


# ---------------------------------------------------------------------------
# Billing eligibility inputs
# ---------------------------------------------------------------------------

ENFORCEMENT_OPERATIONS: typing.Tuple[str, ...] = (
    "CREATE_RESOURCE",
    "CREATE_CREDENTIAL",
    "INCREASE_CAPACITY",
    "MUTATE_RESOURCE",
    "READ_RESOURCE",
    "DELETE_RESOURCE",
    "REVOKE_CREDENTIAL",
    "SECURITY_RECOVERY",
)
MAX_SKU_CODE_LENGTH = 64


def normalize_sku_code(sku_code: typing.Any) -> typing.Optional[str]:
    """Strip the SKU; blank means "omit". Otherwise it must be 1-64 characters."""
    if sku_code is None:
        return None
    if not isinstance(sku_code, str):
        raise IbeeValidationError("sku_code must be a string.", code="invalid_sku_code", field="sku_code")
    value = sku_code.strip()
    if not value:
        return None
    if len(value) > MAX_SKU_CODE_LENGTH:
        raise IbeeValidationError(
            f"sku_code must be at most {MAX_SKU_CODE_LENGTH} characters.", code="invalid_sku_code", field="sku_code"
        )
    return value


def round_half_away_from_zero(value: float) -> int:
    """Round like JavaScript ``Math.round`` for non-negative values."""
    return int(math.floor(value + 0.5))


def normalize_estimated_cost_minor(value: typing.Any) -> typing.Optional[int]:
    """Integer >= 0; finite non-negative floats are rounded; NaN, inf, negatives and bools are rejected."""
    if value is None:
        return None
    error = IbeeValidationError(
        "estimated_cost_minor must be a finite number >= 0 (minor currency units).",
        code="invalid_estimated_cost_minor",
        field="estimated_cost_minor",
    )
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise error
    if isinstance(value, numbers.Integral):
        if value < 0:
            raise error
        return int(value)
    as_float = float(value)
    if not math.isfinite(as_float) or as_float < 0:
        raise error
    return round_half_away_from_zero(as_float)


def normalize_eligibility_operation(operation: typing.Any) -> typing.Optional[str]:
    """Upper-case and check against the billing enforcement operations; ``None`` means omit."""
    if operation is None:
        return None
    if isinstance(operation, str):
        value = operation.strip().upper()
        if value in ENFORCEMENT_OPERATIONS:
            return value
    raise IbeeValidationError(
        "operation must be one of: " + ", ".join(ENFORCEMENT_OPERATIONS) + ".",
        code="invalid_operation",
        field="operation",
    )


# ---------------------------------------------------------------------------
# Waiting for asynchronous operations
# ---------------------------------------------------------------------------

DEFAULT_WAIT_TIMEOUT_SECONDS = 1200.0
DEFAULT_POLL_INTERVAL_SECONDS = 5.0
MIN_WAIT_TIMEOUT_SECONDS = 1.0
MAX_WAIT_TIMEOUT_SECONDS = 7200.0
MIN_POLL_INTERVAL_SECONDS = 1.0
MAX_POLL_INTERVAL_SECONDS = 60.0


def _is_number(value: typing.Any) -> bool:
    return isinstance(value, numbers.Real) and not isinstance(value, bool) and math.isfinite(float(value))


def validate_wait_timeout(timeout: typing.Any) -> float:
    """1 <= timeout <= 7200 seconds."""
    if not _is_number(timeout) or not MIN_WAIT_TIMEOUT_SECONDS <= float(timeout) <= MAX_WAIT_TIMEOUT_SECONDS:
        raise IbeeValidationError(
            "timeout must be between 1 and 7200 seconds.", code="invalid_timeout", field="timeout"
        )
    return float(timeout)


def validate_poll_interval(poll_interval: typing.Any, timeout: float) -> float:
    """1 <= poll_interval <= 60 seconds and poll_interval <= timeout."""
    if (
        not _is_number(poll_interval)
        or not MIN_POLL_INTERVAL_SECONDS <= float(poll_interval) <= MAX_POLL_INTERVAL_SECONDS
        or float(poll_interval) > timeout
    ):
        raise IbeeValidationError(
            "poll_interval must be between 1 and 60 seconds and not longer than timeout.",
            code="invalid_poll_interval",
            field="poll_interval",
        )
    return float(poll_interval)


# ---------------------------------------------------------------------------
# Paging parameters
# ---------------------------------------------------------------------------

VM_SORT_FIELDS: typing.Tuple[str, ...] = ("created_at", "name", "status", "os_type")
SORT_DIRECTIONS: typing.Tuple[str, ...] = ("asc", "desc")
MAX_SEARCH_LENGTH = 120


def _is_int(value: typing.Any) -> bool:
    return isinstance(value, numbers.Integral) and not isinstance(value, bool)


def validate_limit(
    limit: typing.Any, *, maximum: int, minimum: int = 1, field: str = "limit"
) -> typing.Optional[int]:
    """``None`` or an integer between ``minimum`` and ``maximum``."""
    if limit is None:
        return None
    if not _is_int(limit) or not minimum <= int(limit) <= maximum:
        raise IbeeValidationError(
            f"{field} must be an integer between {minimum} and {maximum}.", code=f"invalid_{field}", field=field
        )
    return int(limit)


def validate_offset(offset: typing.Any, *, field: str = "offset") -> typing.Optional[int]:
    """``None`` or an integer >= 0."""
    if offset is None:
        return None
    if not _is_int(offset) or int(offset) < 0:
        raise IbeeValidationError(f"{field} must be an integer >= 0.", code=f"invalid_{field}", field=field)
    return int(offset)


def validate_search(search: typing.Any, *, max_length: int = MAX_SEARCH_LENGTH) -> typing.Optional[str]:
    """Strip; blank means omit; at most ``max_length`` characters."""
    if search is None:
        return None
    if not isinstance(search, str):
        raise IbeeValidationError("search must be a string.", code="invalid_search", field="search")
    value = search.strip()
    if not value:
        return None
    if len(value) > max_length:
        raise IbeeValidationError(
            f"search must be at most {max_length} characters.", code="invalid_search", field="search"
        )
    return value


def validate_choice(
    value: typing.Any, choices: typing.Sequence[str], *, field: str, code: typing.Optional[str] = None
) -> typing.Optional[str]:
    """``None`` or one of ``choices`` (exact match)."""
    if value is None:
        return None
    if not isinstance(value, str) or value not in choices:
        raise IbeeValidationError(
            f"{field} must be one of: {', '.join(choices)}.", code=code or f"invalid_{field}", field=field
        )
    return value


def validate_vm_list_params(
    *,
    limit: typing.Any = None,
    offset: typing.Any = None,
    search: typing.Any = None,
    sort_by: typing.Any = None,
    sort_direction: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """Validate cloud/GPU VM list paging parameters; returns only the values to send."""
    values = {
        "limit": validate_limit(limit, maximum=100),
        "offset": validate_offset(offset),
        "search": validate_search(search),
        "sort_by": validate_choice(sort_by, VM_SORT_FIELDS, field="sort_by"),
        "sort_direction": validate_choice(sort_direction, SORT_DIRECTIONS, field="sort_direction"),
    }
    return {key: value for key, value in values.items() if value is not None}


def validate_page_size(page_size: typing.Any, *, maximum: int) -> int:
    """Auto-paging page size: an integer between 1 and ``maximum``."""
    value = validate_limit(page_size, maximum=maximum, field="page_size")
    if value is None:
        raise IbeeValidationError(
            f"page_size must be an integer between 1 and {maximum}.", code="invalid_page_size", field="page_size"
        )
    return value


# ---------------------------------------------------------------------------
# Billable-create request bodies
# ---------------------------------------------------------------------------

MAX_BILLABLE_BODY_BYTES = 65536
BILLABLE_CREATE_PATHS: typing.Tuple[typing.Pattern[str], ...] = tuple(
    re.compile(pattern)
    for pattern in (
        r"^/secret-store/stores/?$",
        r"^/secret-store/stores/[^/]+/secrets/?$",
        r"^/object-storage/buckets/?$",
        r"^/object-storage/credentials/?$",
        r"^/networking/vpcs/[^/]+/nat-gateways/?$",
        r"^/networking/reserved-ips/?$",
        r"^/networking/load-balancers/(l4|l7)/?$",
        r"^/compute/(cloud-vms|gpu-vms)/?$",
        r"^/block-storage/volumes/?$",
        r"^/cdn/distributions/?$",
        r"^/cdn/distributions/[^/]+/custom-domains/?$",
    )
)


def normalize_api_path(path: typing.Optional[str]) -> str:
    """Return ``path`` relative to the API root as ``/segment/...`` (a leading ``v1/`` is dropped)."""
    value = "/" + (path or "").split("?", 1)[0].lstrip("/")
    if value == "/v1" or value.startswith("/v1/"):
        value = value[3:] or "/"
    return value


def is_billable_create(method: str, path: typing.Optional[str]) -> bool:
    """Whether the public edge runs billing admission (and a 64 KiB body limit) for this request."""
    if method.upper() != "POST":
        return False
    normalized = normalize_api_path(path)
    return any(pattern.fullmatch(normalized) for pattern in BILLABLE_CREATE_PATHS)


def encoded_json_size(body: typing.Any) -> int:
    """Size in bytes of the compact UTF-8 JSON encoding of ``body``."""
    return len(json.dumps(body, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8"))


def check_billable_body_size(method: str, path: typing.Optional[str], body: typing.Any) -> None:
    """Reject billable-create bodies over 64 KiB before sending them (the edge would answer 413)."""
    if body is None or not is_billable_create(method, path):
        return
    if encoded_json_size(body) > MAX_BILLABLE_BODY_BYTES:
        raise IbeeValidationError(
            f"The request body exceeds the {MAX_BILLABLE_BODY_BYTES}-byte limit for create requests.",
            code="request_body_too_large",
            field="body",
        )


__all__ = [
    "BILLABLE_CREATE_PATHS",
    "DEFAULT_POLL_INTERVAL_SECONDS",
    "DEFAULT_WAIT_TIMEOUT_SECONDS",
    "ENFORCEMENT_OPERATIONS",
    "IDEMPOTENCY_KEY_PATTERN",
    "IbeeError",
    "IbeeValidationError",
    "MAX_BILLABLE_BODY_BYTES",
    "SORT_DIRECTIONS",
    "VM_SORT_FIELDS",
    "WORKSPACE_ID_ERROR",
    "WORKSPACE_ID_PATTERN",
    "check_billable_body_size",
    "check_token_environment",
    "is_billable_create",
    "normalize_api_path",
    "normalize_eligibility_operation",
    "normalize_estimated_cost_minor",
    "normalize_sku_code",
    "resolve_base_url",
    "round_half_away_from_zero",
    "validate_choice",
    "validate_idempotency_key",
    "validate_limit",
    "validate_offset",
    "validate_operation_id",
    "validate_page_size",
    "validate_poll_interval",
    "validate_search",
    "validate_token",
    "validate_token_for_base_url",
    "validate_vm_list_params",
    "validate_wait_timeout",
    "validate_workspace_id",
]

# Compute, recovery, billing-SKU, networking and storage rules (0.4.0). Imported last: they build on the helpers above.
from . import billing_catalog, compute, network_services, networking, recovery, secret_store, storage  # noqa: E402
from .billing_catalog import *  # noqa: E402,F401,F403
from .compute import *  # noqa: E402,F401,F403
from .network_services import *  # noqa: E402,F401,F403
from .networking import *  # noqa: E402,F401,F403
from .recovery import *  # noqa: E402,F401,F403
from .secret_store import *  # noqa: E402,F401,F403
from .storage import *  # noqa: E402,F401,F403

__all__ += [  # noqa: PLE0605
    *billing_catalog.__all__,
    *compute.__all__,
    *recovery.__all__,
    *networking.__all__,
    *network_services.__all__,
    *secret_store.__all__,
    *storage.__all__,
]
