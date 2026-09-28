"""Key-aware retry policy shared by the SDK transport and the IBEE CLI.

A request is retried only when repeating it cannot create or change anything twice:

* ``GET``, ``HEAD`` and ``OPTIONS`` requests, or
* writes that carry a non-empty idempotency key on a route that honours it
  (see :mod:`ibee.idempotency`).

Such requests are retried on HTTP 429, 502, 503 and 504 only. VM creates are never
retried, even with a key: a replayed create is answered "VM with this name already
exists" instead of returning the first result. The Secret Store identity access read
(``GET /secret-store/identities/{id}/access``) is never retried either: every call
mints a new AppRole secret ID. No other Secret Store write carries a key, so none is retried. HTTP 408, 409, 500
and every other 4xx are never retried. Connection failures where the request was
never sent (``httpx.ConnectError``/``httpx.ConnectTimeout``) are retried for any
method; failures after the request may have been sent are retried only for
retry-safe requests.
"""

from __future__ import annotations

import email.utils
import random
import re
import time
import typing

import httpx

from .idempotency import find_idempotency_key
from .validation import normalize_api_path

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
#: Keyed routes that are still never retried automatically.
NEVER_RETRIED_WRITES = re.compile(r"^/compute/(cloud-vms|gpu-vms)/?$")
#: Reads that create something on every call (a fresh AppRole secret ID) and are never retried.
NEVER_RETRIED_READS = re.compile(r"^/secret-store/identities/[^/]+/access/?$")
RETRYABLE_STATUS_CODES = frozenset({429, 502, 503, 504})
INITIAL_RETRY_DELAY_SECONDS = 1.0
MAX_RETRY_DELAY_SECONDS = 30.0
JITTER_FACTOR = 0.2

#: Transport errors raised before the request reached the server.
NOT_SENT_TRANSPORT_ERRORS: typing.Tuple[typing.Type[BaseException], ...] = (httpx.ConnectError, httpx.ConnectTimeout)
#: Transport errors raised after the request may have been sent.
MAYBE_SENT_TRANSPORT_ERRORS: typing.Tuple[typing.Type[BaseException], ...] = (
    httpx.RemoteProtocolError,
    httpx.ReadError,
    httpx.ReadTimeout,
    httpx.WriteError,
    httpx.WriteTimeout,
)


def is_retry_safe(
    method: str,
    path: typing.Optional[str],
    headers: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    json_body: typing.Any = None,
    params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
) -> bool:
    """Whether repeating this request is safe (read-only, or keyed on a route that deduplicates)."""
    if method.upper() in SAFE_METHODS:
        return NEVER_RETRIED_READS.fullmatch(normalize_api_path(path)) is None
    if method.upper() == "POST" and NEVER_RETRIED_WRITES.fullmatch(normalize_api_path(path)):
        return False
    return find_idempotency_key(method, path, headers, json_body, params) is not None


def should_retry_status(status_code: int) -> bool:
    """Only 429, 502, 503 and 504 are retryable statuses."""
    return status_code in RETRYABLE_STATUS_CODES


def is_retryable_transport_error(error: BaseException, *, retry_safe: bool) -> bool:
    """Whether a transport exception may be retried for a request with the given safety."""
    if isinstance(error, NOT_SENT_TRANSPORT_ERRORS):
        return True
    return retry_safe and isinstance(error, MAYBE_SENT_TRANSPORT_ERRORS)


def _header(headers: typing.Any, name: str) -> typing.Optional[str]:
    if headers is None:
        return None
    getter = getattr(headers, "get", None)
    if getter is None:
        return None
    value = getter(name)
    if value is None and isinstance(headers, typing.Mapping):
        for key, item in headers.items():
            if isinstance(key, str) and key.lower() == name:
                return str(item)
    return None if value is None else str(value)


def parse_retry_after(headers: typing.Any) -> typing.Optional[float]:
    """Seconds to wait from ``retry-after-ms`` or ``Retry-After`` (delta-seconds or HTTP-date); ``None`` if absent."""
    retry_after_ms = _header(headers, "retry-after-ms")
    if retry_after_ms is not None:
        try:
            return max(0.0, float(retry_after_ms) / 1000.0)
        except ValueError:
            pass
    retry_after = _header(headers, "retry-after")
    if retry_after is None:
        return None
    if re.fullmatch(r"\s*[0-9]+(\.[0-9]+)?\s*", retry_after):
        return max(0.0, float(retry_after))
    parsed = email.utils.parsedate_tz(retry_after)
    if parsed is None:
        return None
    if parsed[9] is None:
        parsed = parsed[:9] + (0,) + parsed[10:]
    return max(0.0, email.utils.mktime_tz(parsed) - time.time())


def retry_delay(attempt: int, headers: typing.Any = None) -> float:
    """Delay before retry number ``attempt`` (0-based).

    ``Retry-After`` (or ``retry-after-ms``) wins and is clamped to [0, 30] seconds;
    otherwise ``1 * 2**attempt`` seconds with +/-10% jitter, capped at 30 seconds.
    """
    server_delay = parse_retry_after(headers)
    if server_delay is not None:
        return min(MAX_RETRY_DELAY_SECONDS, max(0.0, server_delay))
    backoff = min(MAX_RETRY_DELAY_SECONDS, INITIAL_RETRY_DELAY_SECONDS * (2.0**attempt))
    return min(MAX_RETRY_DELAY_SECONDS, backoff * (1 + (random.random() - 0.5) * JITTER_FACTOR))


__all__ = [
    "MAX_RETRY_DELAY_SECONDS",
    "NEVER_RETRIED_READS",
    "RETRYABLE_STATUS_CODES",
    "SAFE_METHODS",
    "is_retry_safe",
    "is_retryable_transport_error",
    "parse_retry_after",
    "retry_delay",
    "should_retry_status",
]
