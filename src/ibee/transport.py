# IBEE hand layer (listed in .fernignore).
"""Request handling on top of the generated HTTP client.

* ``workspace_id``: when a call leaves it empty, the client's default is sent
  (``Ibee(workspace_id=...)`` or ``IBEE_WORKSPACE_ID``).
* ``X-Idempotency-Key``: where the contract has the header and the caller passed
  none, a random UUID is sent, and the same key is reused on every retry.
* Safe retries, at most ``max_retries`` (default 2): GET/HEAD/OPTIONS on 429, 502,
  503 and 504, and writes that carry an idempotency key (the header, or Block
  Storage's ``idempotency_key`` field) on 429 and 503 only. A response that carries
  a billing or admission answer is never retried. Network errors are retried under
  the same rule, and any request whose connection never opened is retried.
  Errors carry ``idempotency_key``, so a caller can retry with the same key.
* Errors: every status >= 400 raises the status-named error class from
  ``ibee.errors`` (``ApiError`` for other statuses) with the body and headers
  exactly as received.
"""

import asyncio
import time
import typing
import uuid

import httpx
from . import errors as _errors
from .core.api_error import ApiError
from .core.http_client import AsyncHttpClient, HttpClient, _retry_timeout, _retry_timeout_from_retries

IDEMPOTENCY_HEADER = "X-Idempotency-Key"
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
#: Substrings of gateway codes that come from billing admission or the catalog quote.
BILLING_MARKERS = ("billing", "admission", "catalog", "quote")

# Indirection so tests can skip real sleeps.
_sleep = time.sleep
_async_sleep = asyncio.sleep


def _key(headers: typing.Mapping[str, typing.Any]) -> typing.Optional[str]:
    for name, value in headers.items():
        if name.lower() == IDEMPOTENCY_HEADER.lower() and value:
            return str(value)
    return None


def _body_key(json_body: typing.Any) -> typing.Optional[str]:
    # Block Storage takes its idempotency key in the body.
    value = json_body.get("idempotency_key") if isinstance(json_body, dict) else None
    return str(value) if value else None


def prepare(
    params: typing.Optional[typing.Dict[str, typing.Any]],
    headers: typing.Optional[typing.Dict[str, typing.Any]],
    request_options: typing.Optional[typing.Mapping[str, typing.Any]],
    workspace_id: typing.Optional[str],
) -> typing.Tuple[typing.Dict[str, typing.Any], typing.Dict[str, typing.Any], typing.Optional[str]]:
    """Fill the default workspace and the idempotency key; returns params, headers and the key sent."""
    params = dict(params or {})
    if "workspace_id" in params and params["workspace_id"] is None and workspace_id:
        params["workspace_id"] = workspace_id
    headers = dict(headers or {})
    extra = dict((request_options or {}).get("additional_headers") or {})
    if IDEMPOTENCY_HEADER in headers and headers[IDEMPOTENCY_HEADER] is None and _key(extra) is None:
        headers[IDEMPOTENCY_HEADER] = str(uuid.uuid4())
    return params, headers, _key(extra) or _key(headers)


def is_billing_answer(response: httpx.Response) -> bool:
    """The body carries a billing or admission decision (``billing_reason``, ``admission_context_id`` or a billing code)."""
    try:
        body = response.json()
    except Exception:
        return False
    if not isinstance(body, dict):
        return False
    if body.get("billing_reason") or body.get("admission_context_id"):
        return True
    detail = body.get("detail")
    code = body.get("error") or (detail.get("code") if isinstance(detail, dict) else None)
    return isinstance(code, str) and any(marker in code.lower() for marker in BILLING_MARKERS)


def should_retry(method: str, response: httpx.Response, keyed: bool) -> bool:
    status = response.status_code
    if method.upper() in SAFE_METHODS:
        allowed = status in (429, 502, 503, 504)
    else:
        allowed = keyed and status in (429, 503)
    return allowed and not is_billing_answer(response)


def _error_classes() -> typing.Dict[int, typing.Type[ApiError]]:
    table: typing.Dict[int, typing.Type[ApiError]] = {}
    for name in _errors.__all__:
        cls = getattr(_errors, name)
        if isinstance(cls, type) and issubclass(cls, ApiError):
            table[typing.cast(int, cls(body=None).status_code)] = cls  # type: ignore[call-arg]
    return table


_ERROR_CLASSES: typing.Dict[int, typing.Type[ApiError]] = {}


def raise_for_status(response: httpx.Response, idempotency_key: typing.Optional[str]) -> None:
    if response.status_code < 400:
        return
    if not _ERROR_CLASSES:
        _ERROR_CLASSES.update(_error_classes())
    try:
        body: typing.Any = response.json()
    except Exception:
        body = response.text
    headers = dict(response.headers)
    cls = _ERROR_CLASSES.get(response.status_code)
    error = cls(body=body, headers=headers) if cls else ApiError(status_code=response.status_code, headers=headers, body=body)  # type: ignore[call-arg]
    error.idempotency_key = idempotency_key
    raise error


def _retry_transport_error(exc: httpx.TransportError, retry_safe: bool) -> bool:
    # A connection that never opened sent nothing, so any request may be retried.
    return retry_safe or isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout))


def _options(request_options: typing.Any) -> typing.Dict[str, typing.Any]:
    # The generated client must not retry on its own: this layer decides.
    return {**(request_options or {}), "max_retries": 0}


class IbeeHttpClient(HttpClient):
    workspace_id: typing.Optional[str] = None

    def request(  # type: ignore[override]
        self, path: typing.Optional[str] = None, *, method: str, params: typing.Any = None, headers: typing.Any = None,
        request_options: typing.Any = None, retries: int = 0, **kwargs: typing.Any,
    ) -> httpx.Response:
        params, headers, key = prepare(params, headers, request_options, self.workspace_id)
        key = key or _body_key(kwargs.get("json"))
        max_retries = (request_options or {}).get("max_retries", self.base_max_retries)
        retry_safe = method.upper() in SAFE_METHODS or key is not None
        attempt = 0
        while True:
            try:
                response = super().request(
                    path, method=method, params=params, headers=headers, request_options=_options(request_options), **kwargs
                )
            except httpx.TransportError as exc:
                if not _retry_transport_error(exc, retry_safe) or attempt >= max_retries:
                    exc.idempotency_key = key  # type: ignore[attr-defined]
                    raise
                _sleep(_retry_timeout_from_retries(attempt))
            else:
                if attempt >= max_retries or not should_retry(method, response, key is not None):
                    raise_for_status(response, key)
                    return response
                _sleep(_retry_timeout(response, attempt))
            attempt += 1


class AsyncIbeeHttpClient(AsyncHttpClient):
    workspace_id: typing.Optional[str] = None

    async def request(  # type: ignore[override]
        self, path: typing.Optional[str] = None, *, method: str, params: typing.Any = None, headers: typing.Any = None,
        request_options: typing.Any = None, retries: int = 0, **kwargs: typing.Any,
    ) -> httpx.Response:
        params, headers, key = prepare(params, headers, request_options, self.workspace_id)
        key = key or _body_key(kwargs.get("json"))
        max_retries = (request_options or {}).get("max_retries", self.base_max_retries)
        retry_safe = method.upper() in SAFE_METHODS or key is not None
        attempt = 0
        while True:
            try:
                response = await super().request(
                    path, method=method, params=params, headers=headers, request_options=_options(request_options), **kwargs
                )
            except httpx.TransportError as exc:
                if not _retry_transport_error(exc, retry_safe) or attempt >= max_retries:
                    exc.idempotency_key = key  # type: ignore[attr-defined]
                    raise
                await _async_sleep(_retry_timeout_from_retries(attempt))
            else:
                if attempt >= max_retries or not should_retry(method, response, key is not None):
                    raise_for_status(response, key)
                    return response
                await _async_sleep(_retry_timeout(response, attempt))
            attempt += 1


def install(client_wrapper: typing.Any, workspace_id: typing.Optional[str]) -> None:
    """Swap the generated HTTP client of ``client_wrapper`` for the IBEE one (same settings)."""
    http = client_wrapper.httpx_client
    http.__class__ = AsyncIbeeHttpClient if isinstance(http, AsyncHttpClient) else IbeeHttpClient
    http.workspace_id = workspace_id
