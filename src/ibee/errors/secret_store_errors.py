# Hand-written (listed in .fernignore).
"""Typed errors for Secret Store responses.

Secret Store answers most refusals with HTTP 403 ``FORBIDDEN`` and a message, so
these classes are chosen by message. Every class subclasses the 0.3.0 class for its
status (``ForbiddenError``, ``ConflictError``, ``NotFoundError``, ``BadGatewayError``,
``ServiceUnavailableError``, ``UnprocessableEntityError``), so existing ``except``
clauses keep working. ``hint`` carries a short suggestion when there is one.
"""

from __future__ import annotations

import re
import typing

from ..core.api_error import ApiError
from .api_errors import OrganizationRestrictedError, UnprocessableEntityError, WorkspaceNotAllowedError
from .bad_gateway_error import BadGatewayError
from .conflict_error import ConflictError
from .forbidden_error import ForbiddenError
from .not_found_error import NotFoundError
from .service_unavailable_error import ServiceUnavailableError

LIFECYCLE_MESSAGE = re.compile(
    r"^Operation '([A-Za-z_]+)' is not allowed while organization is (restricted|suspended|deleting|deleted)$"
)
NOT_OWNED_MESSAGE = re.compile(r"^(Store|Secret|Identity|Scope) '([^']+)' does not belong to workspace '([^']+)'$")
STORE_NOT_ACTIVE_MESSAGE = re.compile(r"^Store '(.+)' is not active$")
IDENTITY_DISABLED_MESSAGE = "Identity is disabled"
AUTH_METHOD_MISMATCH_MESSAGE = "rotate-secret-id is only available for AppRole identities"
SCOPE_PERMISSION_PREFIX = "Read-only identities cannot be granted"
READ_ONLY_SCOPE_MESSAGE = "Read-only scopes cannot grant rollback or destroy permissions"


class _HintMixin:
    hint: typing.Optional[str] = None

    def __str__(self) -> str:
        base = ApiError.__str__(typing.cast(ApiError, self))
        hint = getattr(self, "hint", None)
        message = getattr(self, "message", None)
        prefix = f"{message}" + (f" ({hint})" if hint else "")
        return f"{prefix}; {base}" if prefix else base


class OrganizationLifecycleError(OrganizationRestrictedError):
    """403: the organization's lifecycle state does not allow this operation.

    ``state`` is ``restricted``, ``suspended``, ``deleting`` or ``deleted``; ``operation``
    is the operation class (for example ``CREATE_RESOURCE`` or ``READ_RESOURCE``).
    """


class ResourceNotFoundError(_HintMixin, WorkspaceNotAllowedError):
    """403 "<Kind> '<id>' does not belong to workspace '<ws>'".

    Secret Store answers a missing store, secret, identity or scope (and one in another
    workspace) this way. ``kind``, ``resource_id`` and ``workspace_id`` are parsed from the message.
    """

    kind: typing.Optional[str] = None
    resource_id: typing.Optional[str] = None
    workspace_id: typing.Optional[str] = None

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        match = NOT_OWNED_MESSAGE.match(self.message or "")
        if match:
            self.kind, self.resource_id, self.workspace_id = match.group(1).lower(), match.group(2), match.group(3)
        self.hint = "it does not exist or belongs to another workspace"


class StoreNotActiveError(_HintMixin, ForbiddenError):
    """403 "Store '<id>' is not active": the store is archived or being deleted."""

    store_id: typing.Optional[str] = None

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        match = STORE_NOT_ACTIVE_MESSAGE.match(self.message or "")
        self.store_id = match.group(1) if match else None
        self.hint = "restore (unarchive) the store first"


class IdentityDisabledError(_HintMixin, ForbiddenError):
    """403 "Identity is disabled": enable the identity before fetching or rotating its login details."""

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        self.hint = "enable the identity first"


class AuthMethodMismatchError(_HintMixin, ForbiddenError):
    """403: rotate-secret-id was called for a Kubernetes identity (AppRole only)."""


class ScopePermissionError(_HintMixin, ForbiddenError):
    """403: a read-only identity cannot be granted write, rollback or destroy permissions."""

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        self.hint = "change the identity's token_policy_mode to read_write first"


class StoreArchivedError(_HintMixin, ConflictError):
    """409 ``STORE_ARCHIVED``: the store is archived; unarchive it first."""

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        self.hint = "unarchive the store first"


class StoreDeletingError(_HintMixin, ConflictError):
    """409 ``STORE_DELETING``: the store is being permanently deleted."""


class SecretValueNotFoundError(_HintMixin, NotFoundError):
    """404 reading a secret value or version: that version is soft-deleted, destroyed or does not exist."""

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        self.hint = "the version is soft-deleted or destroyed; undelete it or write a new value"


class ScopeValidationError(_HintMixin, UnprocessableEntityError):
    """422: the updated scope would be ``read_only`` with rollback or destroy allowed."""

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        self.hint = "send access_mode='read_write' or clear allow_rollback/allow_destroy"


class CasConflictError(_HintMixin, BadGatewayError):
    """502 from a value update that sent ``cas``: most likely the current version differs from ``cas``.

    The API reports a check-and-set mismatch as a generic backing-store failure.
    Read the versions and retry with the current version; this is never retried automatically.
    """

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        self.hint = "the current version differs from cas"


class DeletionIncompleteError(_HintMixin, ServiceUnavailableError):
    """503 ``LIFECYCLE_OPERATION_INCOMPLETE``: a permanent store delete stopped part way.

    The store stays in status ``deleting``; repeating the same call is safe.
    ``failed_steps`` lists the cleanup phases that failed.
    """

    store_id: typing.Optional[str] = None
    failed_steps: typing.List[typing.Any] = []

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        details = self.details if isinstance(self.details, dict) else {}
        self.store_id = details.get("store_id")
        steps = details.get("failed_steps")
        self.failed_steps = list(steps) if isinstance(steps, list) else []
        self.hint = "repeat the same call to finish the deletion"


def select_secret_store_error_class(
    status_code: int, info: typing.Mapping[str, typing.Any], path: str
) -> typing.Optional[typing.Type[ApiError]]:
    """The Secret Store error class for a response, or ``None`` to use the generic mapping."""
    code = info.get("code") or ""
    message = info.get("message") or ""
    if status_code == 403:
        if code in ("insufficient_scope", "workspace_not_allowed") or code.startswith("key_"):
            return None
        if LIFECYCLE_MESSAGE.match(message):
            return OrganizationLifecycleError
        if NOT_OWNED_MESSAGE.match(message):
            return ResourceNotFoundError
        if STORE_NOT_ACTIVE_MESSAGE.match(message):
            return StoreNotActiveError
        if message == IDENTITY_DISABLED_MESSAGE:
            return IdentityDisabledError
        if message == AUTH_METHOD_MISMATCH_MESSAGE:
            return AuthMethodMismatchError
        if message.startswith(SCOPE_PERMISSION_PREFIX):
            return ScopePermissionError
        return None
    if status_code == 404 and re.search(r"^/secret-store/secrets/[^/]+/(value|versions/[^/]+)/?$", path):
        return SecretValueNotFoundError
    if status_code == 409:
        if code == "store_archived":
            return StoreArchivedError
        if code == "store_deleting":
            return StoreDeletingError
        return None
    if status_code == 422 and message.startswith(READ_ONLY_SCOPE_MESSAGE):
        return ScopeValidationError
    if status_code == 503 and code == "lifecycle_operation_incomplete":
        return DeletionIncompleteError
    return None


def convert_error(error: ApiError, cls: typing.Type[ApiError]) -> ApiError:
    """Re-type ``error`` as ``cls`` keeping its body, headers and idempotency key."""
    converted = cls(body=error.body, headers=error.headers)  # type: ignore[call-arg]
    converted.status_code = error.status_code
    converted._populate(getattr(error, "raw_body", error.body))
    converted.idempotency_key = getattr(error, "idempotency_key", None)
    return converted


__all__ = [
    "AuthMethodMismatchError",
    "CasConflictError",
    "DeletionIncompleteError",
    "IdentityDisabledError",
    "OrganizationLifecycleError",
    "ResourceNotFoundError",
    "ScopePermissionError",
    "ScopeValidationError",
    "SecretValueNotFoundError",
    "StoreArchivedError",
    "StoreDeletingError",
    "StoreNotActiveError",
    "convert_error",
    "select_secret_store_error_class",
]
