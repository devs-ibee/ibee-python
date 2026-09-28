# Hand-written (listed in .fernignore).
"""Typed HTTP error classes added in 0.4.0.

Every class subclasses the 0.3.0 class for its status code (or ``ApiError``), so
existing ``except`` clauses keep working.
"""

from __future__ import annotations

import re
import typing

from ..core.api_error import ApiError
from .bad_gateway_error import BadGatewayError
from .bad_request_error import BadRequestError
from .forbidden_error import ForbiddenError


class InvalidWorkspaceError(BadRequestError):
    """400 ``workspace_id_required`` / ``invalid_workspace_id`` from the API edge."""


class InsufficientScopeError(ForbiddenError):
    """403 ``insufficient_scope``: the API token lacks ``required_scope``."""


class WorkspaceNotAllowedError(ForbiddenError):
    """403: the workspace does not belong to the API token's organization or context."""


class ApiKeyInactiveError(ForbiddenError):
    """403 ``key_revoked`` / ``key_disabled`` / ``key_inactive`` / ``key_expired``."""


class RouteNotAvailableError(ForbiddenError):
    """403 ``unknown_route``: the path is not part of the public API."""


_RESTRICTED_MESSAGE = re.compile(r"^Operation '([A-Za-z_]+)' is not allowed while organization is ([A-Za-z_]+)$")


class OrganizationRestrictedError(ForbiddenError):
    """403: the organization is restricted and the operation is not allowed in that state.

    ``state`` and ``operation`` are filled when the server reports them.
    """

    state: typing.Optional[str] = None
    operation: typing.Optional[str] = None

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        match = _RESTRICTED_MESSAGE.match(self.message or "")
        if match:
            self.operation, self.state = match.group(1), match.group(2)
        elif isinstance(self.details, dict):
            self.state = self.details.get("state") or self.details.get("organization_state")
            self.operation = self.details.get("operation")


class PayloadTooLargeError(ApiError):
    """413: the request body is larger than the API accepts (64 KiB for create requests)."""

    def __init__(self, body: typing.Any, headers: typing.Optional[typing.Dict[str, str]] = None):
        super().__init__(status_code=413, headers=headers, body=body)


class UnprocessableEntityError(ApiError):
    """422: request field validation failed; ``message`` lists ``field: problem`` pairs."""

    def __init__(self, body: typing.Any, headers: typing.Optional[typing.Dict[str, str]] = None):
        super().__init__(status_code=422, headers=headers, body=body)


class OrganizationSuspendedError(ApiError):
    """423: the organization is suspended by billing (``ORG_BILLING_SUSPENDED``)."""

    billing_state: typing.Optional[str] = None
    service_enforcement_state: typing.Optional[str] = None
    allowed_operations: typing.List[str] = []

    def __init__(self, body: typing.Any, headers: typing.Optional[typing.Dict[str, str]] = None):
        super().__init__(status_code=423, headers=headers, body=body)

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        source = self.details if isinstance(self.details, dict) else (
            self.raw_body if isinstance(self.raw_body, dict) else {}
        )
        self.billing_state = source.get("billing_state")
        self.service_enforcement_state = source.get("service_enforcement_state")
        operations = source.get("allowed_operations")
        self.allowed_operations = [str(item) for item in operations] if isinstance(operations, list) else []


class TooManyRequestsError(ApiError):
    """429: rate limited; ``retry_after`` holds the server's wait hint in seconds, if any."""

    def __init__(self, body: typing.Any, headers: typing.Optional[typing.Dict[str, str]] = None):
        super().__init__(status_code=429, headers=headers, body=body)


class InternalServerError(ApiError):
    """500: unexpected server error (never retried automatically)."""

    def __init__(self, body: typing.Any, headers: typing.Optional[typing.Dict[str, str]] = None):
        super().__init__(status_code=500, headers=headers, body=body)


class GatewayTimeoutError(ApiError):
    """504: the gateway timed out waiting for the service."""

    def __init__(self, body: typing.Any, headers: typing.Optional[typing.Dict[str, str]] = None):
        super().__init__(status_code=504, headers=headers, body=body)


__all__ = [
    "ApiKeyInactiveError",
    "BadGatewayError",
    "GatewayTimeoutError",
    "InsufficientScopeError",
    "InternalServerError",
    "InvalidWorkspaceError",
    "OrganizationRestrictedError",
    "OrganizationSuspendedError",
    "PayloadTooLargeError",
    "RouteNotAvailableError",
    "TooManyRequestsError",
    "UnprocessableEntityError",
    "WorkspaceNotAllowedError",
]
