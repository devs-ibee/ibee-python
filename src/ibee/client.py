# IBEE hand layer (listed in .fernignore). Everything else comes from ``base_client.py``.
"""``Ibee`` and ``AsyncIbee``: the generated clients plus configuration from the environment.

Configuration, first match wins:

* token: ``token=``, then ``IBEE_API_TOKEN``, then ``IBEE_TOKEN``;
* workspace: ``workspace_id=``, then ``IBEE_WORKSPACE_ID`` (sent when a call passes none);
* endpoint: ``base_url=``, ``environment=``, ``IBEE_BASE_URL``, ``IBEE_ENDPOINT``, then
  ``IBEE_ENV`` (``dev``/``development`` or ``prod``/``production``); default production.
  The base URL must be ``https`` (``http`` only for localhost) with no credentials,
  query or fragment.

Requests then go through :mod:`ibee.transport` (workspace default, idempotency keys,
safe retries, errors). Every method is the generated one: the request is sent as you
pass it and the server's answer comes back unchanged.
"""

import os
import typing
from urllib.parse import urlsplit

from .base_client import AsyncBaseIbee, BaseIbee
from .environment import IbeeEnvironment
from .transport import install


class IbeeValidationError(ValueError):
    """Bad client configuration, raised before any request is sent (``code``, ``field``, ``message``)."""

    def __init__(self, message: str, *, code: str, field: typing.Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.field = field


def environment_from_name(name: typing.Optional[str]) -> IbeeEnvironment:
    """``dev``/``development`` or ``prod``/``production`` (empty means production)."""
    value = (name or "").strip().lower()
    if value in ("dev", "development"):
        return IbeeEnvironment.DEVELOPMENT
    if value in ("", "prod", "production"):
        return IbeeEnvironment.PRODUCTION
    raise IbeeValidationError(
        "Invalid IBEE_ENV: use dev, development, prod or production", code="invalid_environment", field="environment"
    )


def resolve_base_url(
    base_url: typing.Optional[str] = None, environment: typing.Optional[IbeeEnvironment] = None
) -> str:
    """The base URL to use, from the arguments or the environment variables, checked as described above."""
    url = base_url or (environment.value if environment is not None else None)
    url = url or os.environ.get("IBEE_BASE_URL") or os.environ.get("IBEE_ENDPOINT")
    url = (url or environment_from_name(os.environ.get("IBEE_ENV")).value).strip()
    try:
        parts = urlsplit(url)
        host = (parts.hostname or "").lower()
        parts.port  # noqa: B018 - raises on an invalid port
    except ValueError as exc:
        raise IbeeValidationError(f"Invalid IBEE base URL: {exc}.", code="invalid_base_url", field="base_url") from exc
    reason = None
    if parts.scheme not in ("https", "http") or not host:
        reason = "use an absolute https:// URL"
    elif parts.scheme == "http" and host not in ("localhost", "127.0.0.1", "::1"):
        reason = "http:// is only allowed for localhost; use https://"
    elif "@" in parts.netloc or parts.query or parts.fragment or "?" in url or "#" in url:
        reason = "credentials, a query string and a fragment are not allowed"
    elif any(segment in (".", "..") for segment in parts.path.split("/")):
        reason = "'.' and '..' path segments are not allowed"
    if reason:
        raise IbeeValidationError(f"Invalid IBEE base URL: {reason}.", code="invalid_base_url", field="base_url")
    return url.rstrip("/")


def _token(token: typing.Any, required: bool = True) -> typing.Any:
    token = token if token is not None else os.environ.get("IBEE_API_TOKEN") or os.environ.get("IBEE_TOKEN")
    if token is None and required:
        raise IbeeValidationError(
            "No API token: pass token= or set IBEE_API_TOKEN.", code="missing_token", field="token"
        )
    return token


class Ibee(BaseIbee):
    """The IBEE client. Takes the generated ``BaseIbee`` options (``headers``, ``timeout``,
    ``max_retries``, ``follow_redirects``, ``httpx_client``, ``logging``) plus ``workspace_id``."""

    def __init__(
        self,
        *,
        token: typing.Optional[typing.Union[str, typing.Callable[[], str]]] = None,
        workspace_id: typing.Optional[str] = None,
        base_url: typing.Optional[str] = None,
        environment: typing.Optional[IbeeEnvironment] = None,
        **kwargs: typing.Any,
    ):
        url = resolve_base_url(base_url, environment)
        super().__init__(base_url=url, token=_token(token), **kwargs)
        install(self._client_wrapper, workspace_id or os.environ.get("IBEE_WORKSPACE_ID"))


class AsyncIbee(AsyncBaseIbee):
    """Async variant of :class:`Ibee` (also takes ``async_token``)."""

    def __init__(
        self,
        *,
        token: typing.Optional[typing.Union[str, typing.Callable[[], str]]] = None,
        workspace_id: typing.Optional[str] = None,
        base_url: typing.Optional[str] = None,
        environment: typing.Optional[IbeeEnvironment] = None,
        async_token: typing.Optional[typing.Callable[[], typing.Awaitable[str]]] = None,
        **kwargs: typing.Any,
    ):
        url = resolve_base_url(base_url, environment)
        token = _token(token, required=async_token is None)
        super().__init__(
            base_url=url,
            token=token if token is not None else "",
            async_token=async_token,
            **kwargs,
        )
        install(self._client_wrapper, workspace_id or os.environ.get("IBEE_WORKSPACE_ID"))
