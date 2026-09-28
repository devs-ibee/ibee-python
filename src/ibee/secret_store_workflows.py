# Hand-written (listed in .fernignore).
"""Portal-equivalent request flows for Secret Store (stores, secrets, identities and scopes).

Each flow is a generator of :class:`~ibee.compute_workflows.Call` objects driven by
:func:`~ibee.compute_workflows.run_sync` / :func:`~ibee.compute_workflows.run_async`,
so ``Ibee`` and ``AsyncIbee`` share one implementation. Every rule lives in
:mod:`ibee.validation.secret_store` and is checked before the request it guards.

Optional pre-steps (billing preflight, rollback target, rotate and scope checks) need
read scopes; when the token lacks one (403 ``insufficient_scope``) the pre-step is
skipped and the request is sent, because the API enforces the same rule.
"""

from __future__ import annotations

import typing
import warnings
from urllib.parse import quote

from .billing.admission import SECRET_MANAGER_SKU_CODE
from .compute_workflows import Call, Flow, billing_preflight
from .errors.api_errors import InsufficientScopeError
from .errors.bad_gateway_error import BadGatewayError
from .errors.conflict_error import ConflictError
from .errors.secret_store_errors import CasConflictError, convert_error
from .types.batch_create_secrets_response import BatchCreateSecretsResponse
from .types.secret import Secret
from .types.secret_identity import SecretIdentity
from .types.secret_identity_access import SecretIdentityAccess
from .types.secret_identity_action_status import SecretIdentityActionStatus
from .types.secret_identity_list import SecretIdentityList
from .types.secret_identity_scope import SecretIdentityScope
from .types.secret_identity_scope_list import SecretIdentityScopeList
from .types.secret_lifecycle_status import SecretLifecycleStatus
from .types.secret_list import SecretList
from .types.secret_store import SecretStore
from .types.secret_store_list import SecretStoreList
from .types.secret_value import SecretValue
from .types.secret_version import SecretVersion
from .types.secret_versions import SecretVersions
from .validation import IbeeBillingWarning, IbeeValidationError
from .validation.secret_store import (
    SECRET_STORE_PAGE_LIMIT_MAX,
    build_batch_create_body,
    build_identity_create_body,
    build_identity_update_body,
    build_scope_create_body,
    build_scope_update_body,
    build_secret_create_body,
    build_secret_patch_body,
    build_secret_value_body,
    build_store_create_body,
    build_store_update_body,
    check_rollback_target,
    check_rotate_allowed,
    check_scope_store_eligible,
    find_store_by_name,
    normalize_secret_search_query,
    validate_if_exists,
    validate_secret_store_pagination,
    validate_secret_store_resource_id,
    validate_secret_store_workspace_id,
    validate_secret_version,
    validate_secret_versions,
    validate_scope_permissions,
)

PRESTEP_SKIPPED_MESSAGE = "{step} skipped: the API token lacks the '{scope}' scope. The API still enforces the rule."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ws(workspace_id: typing.Any, **extra: typing.Any) -> typing.Dict[str, typing.Any]:
    params: typing.Dict[str, typing.Any] = {"workspace_id": validate_secret_store_workspace_id(workspace_id)}
    params.update({key: value for key, value in extra.items() if value is not None})
    return params


def _seg(value: typing.Any, field: str) -> str:
    return quote(validate_secret_store_resource_id(value, field=field), safe="")


def _store(store_id: typing.Any) -> str:
    return f"secret-store/stores/{_seg(store_id, 'store_id')}"


def _secret(secret_id: typing.Any) -> str:
    return f"secret-store/secrets/{_seg(secret_id, 'secret_id')}"


def _identity(identity_id: typing.Any) -> str:
    return f"secret-store/identities/{_seg(identity_id, 'identity_id')}"


def _scope(scope_id: typing.Any) -> str:
    return f"secret-store/scopes/{_seg(scope_id, 'scope_id')}"


def _optional_bool(value: typing.Any, field: str) -> typing.Optional[bool]:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise IbeeValidationError(f"{field} must be true or false.", code=f"invalid_{field}", field=field)
    return value


def _skip_warning(step: str, error: InsufficientScopeError, default_scope: str) -> None:
    warnings.warn(
        PRESTEP_SKIPPED_MESSAGE.format(step=step, scope=error.required_scope or default_scope),
        UserWarning,
        stacklevel=4,
    )


def secret_manager_preflight(workspace_id: str, *, resource_type: str) -> Flow[None]:
    """The portal's SECRETMA-STD billing check before a store or secret create.

    Continues only when billing answers ``allowed: true`` for ``SECRETMA-STD``
    (``BillingDeniedError`` otherwise). Skipped with an ``IbeeBillingWarning`` when the
    token lacks ``billing.read``: the API edge still enforces billing on the create.
    """
    try:
        yield from billing_preflight(workspace_id, sku_code=SECRET_MANAGER_SKU_CODE, resource_type=resource_type)
    except InsufficientScopeError as exc:
        warnings.warn(
            PRESTEP_SKIPPED_MESSAGE.format(step="Billing preflight", scope=exc.required_scope or "billing.read"),
            IbeeBillingWarning,
            stacklevel=4,
        )


def _page_size(page_size: typing.Any) -> int:
    values = validate_secret_store_pagination(limit=page_size if page_size is not None else SECRET_STORE_PAGE_LIMIT_MAX)
    return values["limit"]


def _collect_pages(
    path: str, params: typing.Dict[str, typing.Any], key: str, page_size: int, parse: typing.Any
) -> Flow[typing.List[typing.Any]]:
    """Request page 1, 2, ... until a short page or ``page * limit >= total``."""
    items: typing.List[typing.Any] = []
    page = 1
    while True:
        data = yield Call("GET", path, params={**params, "page": page, "limit": page_size}, parse=parse)
        batch = list(getattr(data, key, None) or [])
        items.extend(batch)
        total = getattr(data, "total", None)
        if len(batch) < page_size or (isinstance(total, int) and page * page_size >= total):
            return items
        page += 1


# ---------------------------------------------------------------------------
# Stores
# ---------------------------------------------------------------------------


def list_secret_stores(
    *, workspace_id: str, page: typing.Any = None, limit: typing.Any = None, include_archived: typing.Any = None
) -> Flow[SecretStoreList]:
    params = _ws(
        workspace_id,
        include_archived=_optional_bool(include_archived, "include_archived"),
        **validate_secret_store_pagination(page, limit),
    )
    return (yield Call("GET", "secret-store/stores", params=params, parse=SecretStoreList, main=True))


def list_all_secret_stores(
    *, workspace_id: str, include_archived: typing.Any = True, page_size: typing.Any = None
) -> Flow[typing.List[SecretStore]]:
    # None means the documented default (archived stores included, as the portal lists them).
    include = True if include_archived is None else _optional_bool(include_archived, "include_archived")
    params = _ws(workspace_id, include_archived=include)
    return (yield from _collect_pages("secret-store/stores", params, "stores", _page_size(page_size), SecretStoreList))


def create_secret_store(
    *,
    workspace_id: str,
    name: typing.Any,
    description: typing.Any = None,
    preflight_billing: typing.Any = None,
    if_exists: typing.Any = None,
    billing_preflight: typing.Any = None,
) -> Flow[SecretStore]:
    params = _ws(workspace_id)
    body = build_store_create_body(name, description)
    mode = validate_if_exists(if_exists)
    if preflight_billing or billing_preflight:
        yield from secret_manager_preflight(params["workspace_id"], resource_type="secret_store")
    try:
        return (yield Call("POST", "secret-store/stores", params=params, json=body, parse=SecretStore, main=True))
    except ConflictError as exc:
        if mode != "return" or type(exc) is not ConflictError:
            raise
        stores = yield from _collect_pages(
            "secret-store/stores", {**params, "include_archived": True}, "stores", SECRET_STORE_PAGE_LIMIT_MAX, SecretStoreList
        )
        existing = find_store_by_name(stores, body["name"])
        if existing is None:
            raise
        return typing.cast(SecretStore, existing)


def get_secret_store(*, workspace_id: str, store_id: typing.Any) -> Flow[SecretStore]:
    return (yield Call("GET", _store(store_id), params=_ws(workspace_id), parse=SecretStore, main=True))


def update_secret_store(
    *, workspace_id: str, store_id: typing.Any, name: typing.Any = None, description: typing.Any = None
) -> Flow[SecretStore]:
    path, params = _store(store_id), _ws(workspace_id)
    body = build_store_update_body(name, description)
    return (yield Call("PATCH", path, params=params, json=body, parse=SecretStore, main=True))


def archive_secret_store(*, workspace_id: str, store_id: typing.Any) -> Flow[SecretStore]:
    return (yield Call("POST", f"{_store(store_id)}/archive", params=_ws(workspace_id), parse=SecretStore, main=True))


def unarchive_secret_store(*, workspace_id: str, store_id: typing.Any) -> Flow[SecretStore]:
    return (yield Call("POST", f"{_store(store_id)}/unarchive", params=_ws(workspace_id), parse=SecretStore, main=True))


def permanently_delete_secret_store(*, workspace_id: str, store_id: typing.Any) -> Flow[SecretLifecycleStatus]:
    return (
        yield Call("DELETE", f"{_store(store_id)}/permanent", params=_ws(workspace_id), parse=SecretLifecycleStatus, main=True)
    )


# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------


def list_secrets(
    *, workspace_id: str, store_id: typing.Any, q: typing.Any = None, page: typing.Any = None, limit: typing.Any = None
) -> Flow[SecretList]:
    path = f"{_store(store_id)}/secrets"
    params = _ws(workspace_id, q=normalize_secret_search_query(q), **validate_secret_store_pagination(page, limit))
    return (yield Call("GET", path, params=params, parse=SecretList, main=True))


def list_all_secrets(
    *, workspace_id: str, store_id: typing.Any, q: typing.Any = None, page_size: typing.Any = None
) -> Flow[typing.List[Secret]]:
    path = f"{_store(store_id)}/secrets"
    params = _ws(workspace_id, q=normalize_secret_search_query(q))
    return (yield from _collect_pages(path, params, "secrets", _page_size(page_size), SecretList))


def create_secret(
    *,
    workspace_id: str,
    store_id: typing.Any,
    secret_name: typing.Any,
    value: typing.Any,
    preflight_billing: typing.Any = None,
    billing_preflight: typing.Any = None,
) -> Flow[Secret]:
    path, params = f"{_store(store_id)}/secrets", _ws(workspace_id)
    body = build_secret_create_body(secret_name, value)
    if preflight_billing or billing_preflight:
        yield from secret_manager_preflight(params["workspace_id"], resource_type="secret")
    return (yield Call("POST", path, params=params, json=body, parse=Secret, main=True))


def batch_create_secrets(*, workspace_id: str, store_id: typing.Any, secrets: typing.Any) -> Flow[BatchCreateSecretsResponse]:
    path, params = f"{_store(store_id)}/secrets:batchIngest", _ws(workspace_id)
    body = build_batch_create_body(secrets)
    return (yield Call("POST", path, params=params, json=body, parse=BatchCreateSecretsResponse, main=True))


def get_secret(*, workspace_id: str, secret_id: typing.Any) -> Flow[Secret]:
    return (yield Call("GET", _secret(secret_id), params=_ws(workspace_id), parse=Secret, main=True))


def delete_secret(*, workspace_id: str, secret_id: typing.Any) -> Flow[Secret]:
    return (yield Call("DELETE", _secret(secret_id), params=_ws(workspace_id), parse=Secret, main=True))


def get_secret_value(*, workspace_id: str, secret_id: typing.Any) -> Flow[SecretValue]:
    return (yield Call("GET", f"{_secret(secret_id)}/value", params=_ws(workspace_id), parse=SecretValue, main=True))


def update_secret_value(
    *, workspace_id: str, secret_id: typing.Any, value: typing.Any, cas: typing.Any = None
) -> Flow[SecretValue]:
    path, params = f"{_secret(secret_id)}/value", _ws(workspace_id)
    body = build_secret_value_body(value, cas)
    try:
        return (yield Call("PUT", path, params=params, json=body, parse=SecretValue, main=True))
    except BadGatewayError as exc:
        if "cas" in body and type(exc) is BadGatewayError:
            raise convert_error(exc, CasConflictError) from exc
        raise


def patch_secret_value(*, workspace_id: str, secret_id: typing.Any, value: typing.Any) -> Flow[SecretValue]:
    path, params = f"{_secret(secret_id)}/value", _ws(workspace_id)
    body = build_secret_patch_body(value)
    return (yield Call("PATCH", path, params=params, json=body, parse=SecretValue, main=True))


def _versions_record(workspace_id: str, secret_id: typing.Any) -> Flow[typing.Dict[str, typing.Any]]:
    data = yield Call("GET", f"{_secret(secret_id)}/versions", params=_ws(workspace_id))
    return data if isinstance(data, dict) else {}


def undelete_secret(*, workspace_id: str, secret_id: typing.Any, versions: typing.Any = None) -> Flow[Secret]:
    path, params = f"{_secret(secret_id)}/undelete", _ws(workspace_id)
    if versions is None:
        record = yield from _versions_record(params["workspace_id"], secret_id)
        current = record.get("current_version")
        if not isinstance(current, int) or current < 1:
            raise IbeeValidationError(
                "The secret has no current version to undelete; pass versions explicitly.",
                code="invalid_versions",
                field="versions",
            )
        versions = [current]
    body = {"versions": validate_secret_versions(versions)}
    return (yield Call("POST", path, params=params, json=body, parse=Secret, main=True))


def destroy_secret_versions(*, workspace_id: str, secret_id: typing.Any, versions: typing.Any) -> Flow[SecretLifecycleStatus]:
    path, params = f"{_secret(secret_id)}/destroy", _ws(workspace_id)
    body = {"versions": validate_secret_versions(versions)}
    return (yield Call("POST", path, params=params, json=body, parse=SecretLifecycleStatus, main=True))


def permanently_delete_secret(*, workspace_id: str, secret_id: typing.Any) -> Flow[SecretLifecycleStatus]:
    return (
        yield Call("DELETE", f"{_secret(secret_id)}/permanent", params=_ws(workspace_id), parse=SecretLifecycleStatus, main=True)
    )


def list_secret_versions(*, workspace_id: str, secret_id: typing.Any) -> Flow[SecretVersions]:
    return (yield Call("GET", f"{_secret(secret_id)}/versions", params=_ws(workspace_id), parse=SecretVersions, main=True))


def get_secret_version(*, workspace_id: str, secret_id: typing.Any, version: typing.Any) -> Flow[SecretVersion]:
    path = f"{_secret(secret_id)}/versions/{validate_secret_version(version)}"
    return (yield Call("GET", path, params=_ws(workspace_id), parse=SecretVersion, main=True))


def rollback_secret(
    *, workspace_id: str, secret_id: typing.Any, version: typing.Any, check_target: typing.Any = True
) -> Flow[SecretValue]:
    path, params = f"{_secret(secret_id)}/rollback", _ws(workspace_id)
    target = validate_secret_version(version)
    if check_target is not False:
        try:
            record = yield from _versions_record(params["workspace_id"], secret_id)
        except InsufficientScopeError as exc:
            _skip_warning("Rollback target check", exc, "secret-store.read")
        else:
            check_rollback_target(record, target)
    return (yield Call("POST", path, params=params, json={"version": target}, parse=SecretValue, main=True))


# ---------------------------------------------------------------------------
# Identities
# ---------------------------------------------------------------------------


def list_secret_identities(*, workspace_id: str, store_id: typing.Any) -> Flow[SecretIdentityList]:
    return (
        yield Call("GET", f"{_store(store_id)}/identities", params=_ws(workspace_id), parse=SecretIdentityList, main=True)
    )


def create_secret_identity(
    *,
    workspace_id: str,
    store_id: typing.Any,
    auth_method: typing.Any,
    name: typing.Any,
    token_policy_mode: typing.Any = None,
    k8s_namespace: typing.Any = None,
    k8s_service_account: typing.Any = None,
) -> Flow[SecretIdentity]:
    path, params = f"{_store(store_id)}/identities", _ws(workspace_id)
    body = build_identity_create_body(auth_method, name, token_policy_mode, k8s_namespace, k8s_service_account)
    return (yield Call("POST", path, params=params, json=body, parse=SecretIdentity, main=True))


def get_secret_identity(*, workspace_id: str, identity_id: typing.Any) -> Flow[SecretIdentity]:
    return (yield Call("GET", _identity(identity_id), params=_ws(workspace_id), parse=SecretIdentity, main=True))


def delete_secret_identity(*, workspace_id: str, identity_id: typing.Any) -> Flow[SecretIdentityActionStatus]:
    return (
        yield Call("DELETE", _identity(identity_id), params=_ws(workspace_id), parse=SecretIdentityActionStatus, main=True)
    )


def update_secret_identity(
    *, workspace_id: str, identity_id: typing.Any, token_policy_mode: typing.Any = None
) -> Flow[SecretIdentity]:
    path, params = _identity(identity_id), _ws(workspace_id)
    body = build_identity_update_body(token_policy_mode)
    return (yield Call("PATCH", path, params=params, json=body, parse=SecretIdentity, main=True))


def disable_secret_identity(*, workspace_id: str, identity_id: typing.Any) -> Flow[SecretIdentity]:
    return (
        yield Call("POST", f"{_identity(identity_id)}/disable", params=_ws(workspace_id), parse=SecretIdentity, main=True)
    )


def enable_secret_identity(*, workspace_id: str, identity_id: typing.Any) -> Flow[SecretIdentity]:
    return (
        yield Call("POST", f"{_identity(identity_id)}/enable", params=_ws(workspace_id), parse=SecretIdentity, main=True)
    )


def get_secret_identity_access(*, workspace_id: str, identity_id: typing.Any) -> Flow[SecretIdentityAccess]:
    return (
        yield Call("GET", f"{_identity(identity_id)}/access", params=_ws(workspace_id), parse=SecretIdentityAccess, main=True)
    )


def _identity_record(workspace_id: str, identity_id: typing.Any) -> Flow[typing.Dict[str, typing.Any]]:
    data = yield Call("GET", _identity(identity_id), params=_ws(workspace_id))
    return data if isinstance(data, dict) else {}


def rotate_secret_identity_secret_id(
    *, workspace_id: str, identity_id: typing.Any, check_auth_method: typing.Any = False
) -> Flow[SecretIdentityAccess]:
    path, params = f"{_identity(identity_id)}/rotate-secret-id", _ws(workspace_id)
    if check_auth_method:
        try:
            identity = yield from _identity_record(params["workspace_id"], identity_id)
        except InsufficientScopeError as exc:
            _skip_warning("Rotate precondition check", exc, "secret-store.read")
        else:
            check_rotate_allowed(identity)
    return (yield Call("POST", path, params=params, parse=SecretIdentityAccess, main=True))


def revoke_secret_identity_sessions(*, workspace_id: str, identity_id: typing.Any) -> Flow[SecretIdentityActionStatus]:
    return (
        yield Call(
            "POST", f"{_identity(identity_id)}/revoke", params=_ws(workspace_id), parse=SecretIdentityActionStatus, main=True
        )
    )


# ---------------------------------------------------------------------------
# Scopes
# ---------------------------------------------------------------------------


def list_secret_identity_scopes(*, workspace_id: str, identity_id: typing.Any) -> Flow[SecretIdentityScopeList]:
    return (
        yield Call("GET", f"{_identity(identity_id)}/scopes", params=_ws(workspace_id), parse=SecretIdentityScopeList, main=True)
    )


def create_secret_identity_scope(
    *,
    workspace_id: str,
    identity_id: typing.Any,
    store_id: typing.Any,
    access_mode: typing.Any = None,
    allow_version_read: typing.Any = None,
    allow_rollback: typing.Any = None,
    allow_destroy: typing.Any = None,
    check_store: typing.Any = False,
) -> Flow[SecretIdentityScope]:
    path, params = f"{_identity(identity_id)}/scopes", _ws(workspace_id)
    body = build_scope_create_body(store_id, access_mode, allow_version_read, allow_rollback, allow_destroy)
    if check_store:
        ws = params["workspace_id"]
        try:
            identity = yield from _identity_record(ws, identity_id)
            scopes = yield Call("GET", path, params=_ws(ws))
            stores = yield from _collect_pages(
                "secret-store/stores", _ws(ws, include_archived=True), "stores", SECRET_STORE_PAGE_LIMIT_MAX, SecretStoreList
            )
        except InsufficientScopeError as exc:
            _skip_warning("Scope store check", exc, "secret-store.read")
        else:
            validate_scope_permissions(
                body["access_mode"],
                body["allow_rollback"],
                body["allow_destroy"],
                identity_mode=identity.get("token_policy_mode"),
            )
            scope_rows = scopes.get("scopes") if isinstance(scopes, dict) else None
            check_scope_store_eligible(body["store_id"], stores, scope_rows or [])
    return (yield Call("POST", path, params=params, json=body, parse=SecretIdentityScope, main=True))


def update_secret_identity_scope(
    *,
    workspace_id: str,
    scope_id: typing.Any,
    access_mode: typing.Any = None,
    allow_version_read: typing.Any = None,
    allow_rollback: typing.Any = None,
    allow_destroy: typing.Any = None,
) -> Flow[SecretIdentityScope]:
    path, params = _scope(scope_id), _ws(workspace_id)
    body = build_scope_update_body(access_mode, allow_version_read, allow_rollback, allow_destroy)
    return (yield Call("PATCH", path, params=params, json=body, parse=SecretIdentityScope, main=True))


def delete_secret_identity_scope(*, workspace_id: str, scope_id: typing.Any) -> Flow[SecretIdentityActionStatus]:
    return (yield Call("DELETE", _scope(scope_id), params=_ws(workspace_id), parse=SecretIdentityActionStatus, main=True))


__all__ = [
    "archive_secret_store",
    "batch_create_secrets",
    "create_secret",
    "create_secret_identity",
    "create_secret_identity_scope",
    "create_secret_store",
    "delete_secret",
    "delete_secret_identity",
    "delete_secret_identity_scope",
    "destroy_secret_versions",
    "disable_secret_identity",
    "enable_secret_identity",
    "get_secret",
    "get_secret_identity",
    "get_secret_identity_access",
    "get_secret_store",
    "get_secret_value",
    "get_secret_version",
    "list_all_secret_stores",
    "list_all_secrets",
    "list_secret_identities",
    "list_secret_identity_scopes",
    "list_secret_stores",
    "list_secret_versions",
    "list_secrets",
    "patch_secret_value",
    "permanently_delete_secret",
    "permanently_delete_secret_store",
    "revoke_secret_identity_sessions",
    "rollback_secret",
    "rotate_secret_identity_secret_id",
    "secret_manager_preflight",
    "undelete_secret",
    "unarchive_secret_store",
    "update_secret_identity",
    "update_secret_identity_scope",
    "update_secret_store",
    "update_secret_value",
]
