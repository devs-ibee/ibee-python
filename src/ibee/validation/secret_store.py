"""Secret Store rules, ported from the IBEE portal and the Secret Store API.

Every check raises :class:`~ibee.validation.IbeeValidationError` before any HTTP
request. Where the portal is stricter than the API (blank keys and values in a
secret value, rollback targets, scope store eligibility) the portal rule is used;
where the API is stricter (secret names, store names that need a letter or digit,
2-128 digit workspace ids) the API rule is used.
"""

from __future__ import annotations

import json
import numbers
import re
import typing
import warnings

from . import IbeeValidationError, encoded_json_size, normalize_api_path, validate_workspace_id

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Secret Store tenant ids: a positive integer with 2 to 128 digits.
SECRET_STORE_WORKSPACE_ID_PATTERN = re.compile(r"[1-9][0-9]{1,127}")
SECRET_STORE_WORKSPACE_ID_ERROR = (
    "workspace_id must be a positive numeric string of 2 to 128 digits for Secret Store requests."
)
#: Secret names: 2-64 characters, lowercase letters, digits and hyphens, starting with a letter or digit.
SECRET_NAME_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{1,63}")
SECRET_NAME_ERROR = (
    "secret_name must be 2-64 characters of lowercase letters, digits and hyphens, "
    "starting with a letter or digit."
)
STORE_NAME_MAX_LENGTH = 128
IDENTITY_NAME_MAX_LENGTH = 128
SECRET_SEARCH_MAX_LENGTH = 128
SECRET_STORE_PAGE_LIMIT_MAX = 200
SECRET_STORE_DEFAULT_PAGE_LIMIT = 50
SECRET_BATCH_MAX_ITEMS = 500
SECRET_VERSIONS_MAX_ITEMS = 100
#: Largest request body the API gateway accepts for Secret Store requests.
SECRET_STORE_MAX_BODY_BYTES = 65536
SECRET_STORE_AUTH_METHODS: typing.Tuple[str, ...] = ("approle", "kubernetes")
SECRET_STORE_ACCESS_MODES: typing.Tuple[str, ...] = ("read_only", "read_write")
TOKEN_POLICY_MODES = SECRET_STORE_ACCESS_MODES
SECRET_STORE_IF_EXISTS: typing.Tuple[str, ...] = ("error", "return")

_FORBIDDEN_ID_CHARS = re.compile(r"[/?#\x00-\x1f\x7f]")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _is_int(value: typing.Any) -> bool:
    return isinstance(value, numbers.Integral) and not isinstance(value, bool)


def _invalid(message: str, *, field: str, code: typing.Optional[str] = None, details: typing.Any = None) -> IbeeValidationError:
    return IbeeValidationError(message, code=code or f"invalid_{field}", field=field, details=details)


def is_secret_store_path(path: typing.Optional[str]) -> bool:
    """Whether ``path`` (relative to the API root) is a Secret Store route."""
    normalized = normalize_api_path(path)
    return normalized == "/secret-store" or normalized.startswith("/secret-store/")


def validate_secret_store_workspace_id(workspace_id: typing.Any) -> str:
    """A positive integer string of 2 to 128 digits (Secret Store rejects shorter or longer tenant ids)."""
    value = validate_workspace_id(workspace_id.strip() if isinstance(workspace_id, str) else workspace_id)
    if SECRET_STORE_WORKSPACE_ID_PATTERN.fullmatch(value) is None:
        raise IbeeValidationError(SECRET_STORE_WORKSPACE_ID_ERROR, code="invalid_workspace_id", field="workspace_id")
    return value


def validate_secret_store_resource_id(value: typing.Any, *, field: str) -> str:
    """Strip; non-empty; no ``/``, ``?``, ``#`` or control characters (the value is URL-encoded by the SDK)."""
    text = value.strip() if isinstance(value, str) else ""
    if not text:
        raise _invalid(f"{field} is required.", field=field)
    if _FORBIDDEN_ID_CHARS.search(text):
        raise _invalid(f"{field} must not contain '/', '?', '#' or control characters.", field=field)
    return text


def validate_secret_store_pagination(page: typing.Any = None, limit: typing.Any = None) -> typing.Dict[str, int]:
    """``page`` an integer >= 1 and ``limit`` an integer 1-200 (``bool`` rejected); returns the values to send."""
    values: typing.Dict[str, int] = {}
    if page is not None:
        if not _is_int(page) or int(page) < 1:
            raise _invalid("page must be an integer >= 1.", field="page")
        values["page"] = int(page)
    if limit is not None:
        if not _is_int(limit) or not 1 <= int(limit) <= SECRET_STORE_PAGE_LIMIT_MAX:
            raise _invalid(f"limit must be an integer between 1 and {SECRET_STORE_PAGE_LIMIT_MAX}.", field="limit")
        values["limit"] = int(limit)
    return values


def normalize_secret_search_query(q: typing.Any) -> typing.Optional[str]:
    """Strip; blank means omit; at most 128 characters."""
    if q is None:
        return None
    if not isinstance(q, str):
        raise _invalid("q must be a string.", field="q")
    value = q.strip()
    if not value:
        return None
    if len(value) > SECRET_SEARCH_MAX_LENGTH:
        raise _invalid(f"q must be at most {SECRET_SEARCH_MAX_LENGTH} characters.", field="q")
    return value


def assert_secret_store_body_size(body: typing.Any) -> None:
    """Reject a request body whose compact UTF-8 JSON encoding exceeds 64 KiB (the gateway answers 413)."""
    if body is None:
        return
    size = encoded_json_size(body)
    if size > SECRET_STORE_MAX_BODY_BYTES:
        raise IbeeValidationError(
            f"The request body is {size} bytes; Secret Store requests are limited to {SECRET_STORE_MAX_BODY_BYTES} bytes.",
            code="request_body_too_large",
            field="body",
            details={"size": size, "limit": SECRET_STORE_MAX_BODY_BYTES},
        )


def check_secret_store_request(method: str, path: typing.Optional[str], params: typing.Any, body: typing.Any) -> None:
    """Transport hook: the Secret Store workspace id and body size rules, for every Secret Store request."""
    if not is_secret_store_path(path):
        return
    if isinstance(params, typing.Mapping) and "workspace_id" in params:
        validate_secret_store_workspace_id(params.get("workspace_id"))
    if method.upper() in ("POST", "PUT", "PATCH"):
        assert_secret_store_body_size(body)


# ---------------------------------------------------------------------------
# Stores
# ---------------------------------------------------------------------------


def normalize_store_name(name: typing.Any, *, creating: bool = True) -> str:
    """Strip; 1-128 characters; on create it must contain at least one letter or digit.

    The API derives the store key from the name and refuses names without a letter or digit.
    """
    if not isinstance(name, str) or not name.strip():
        raise _invalid("Store name is required.", field="name")
    value = name.strip()
    if len(value) > STORE_NAME_MAX_LENGTH:
        raise _invalid(f"Store name must be at most {STORE_NAME_MAX_LENGTH} characters.", field="name")
    if creating and re.search(r"[A-Za-z0-9]", value) is None:
        raise _invalid(
            "Store name must contain at least one letter or number to generate a store key.", field="name"
        )
    return value


def normalize_store_description(description: typing.Any) -> typing.Optional[str]:
    """``None`` stays ``None``; otherwise a string, stripped (no length limit)."""
    if description is None:
        return None
    if not isinstance(description, str):
        raise _invalid("description must be a string.", field="description")
    return description.strip()


def build_store_create_body(name: typing.Any, description: typing.Any = None) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {"name": normalize_store_name(name, creating=True)}
    normalized_description = normalize_store_description(description)
    if normalized_description is not None:
        body["description"] = normalized_description
    assert_secret_store_body_size(body)
    return body


def build_store_update_body(name: typing.Any = None, description: typing.Any = None) -> typing.Dict[str, typing.Any]:
    """At least one of ``name`` or ``description``; the store key is not regenerated on rename."""
    body: typing.Dict[str, typing.Any] = {}
    if name is not None:
        body["name"] = normalize_store_name(name, creating=False)
    normalized_description = normalize_store_description(description)
    if normalized_description is not None:
        body["description"] = normalized_description
    if not body:
        raise IbeeValidationError(
            "Provide name or description to update the store.", code="no_changes", field="name"
        )
    assert_secret_store_body_size(body)
    return body


def validate_if_exists(if_exists: typing.Any) -> str:
    if if_exists is None:
        return "error"
    if if_exists == "reuse":
        return "return"
    if if_exists not in SECRET_STORE_IF_EXISTS:
        raise _invalid("if_exists must be 'error' or 'return'.", field="if_exists")
    return typing.cast(str, if_exists)


def _lookup(value: typing.Any) -> str:
    return str(value or "").strip().lower()


def find_store_by_name(stores: typing.Iterable[typing.Any], name: str) -> typing.Any:
    """The store whose name or store key equals ``name`` (trimmed, case-insensitive), as the portal matches."""
    wanted = _lookup(name)
    for store in stores:
        store_name = store.get("name") if isinstance(store, dict) else getattr(store, "name", None)
        store_key = store.get("store_key") if isinstance(store, dict) else getattr(store, "store_key", None)
        if _lookup(store_name) == wanted or _lookup(store_key) == wanted:
            return store
    return None


# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------


def normalize_secret_name(name: typing.Any, *, field: str = "secret_name") -> str:
    """Strip and lower-case (as the portal does), then require ``[a-z0-9][a-z0-9-]{1,63}``."""
    if not isinstance(name, str) or not name.strip():
        raise _invalid("secret_name is required.", field=field, code="invalid_secret_name")
    value = name.strip().lower()
    if SECRET_NAME_PATTERN.fullmatch(value) is None:
        raise _invalid(SECRET_NAME_ERROR, field=field, code="invalid_secret_name")
    return value


def normalize_secret_value(
    value: typing.Any, *, allow_null_values: bool = False, field: str = "value"
) -> typing.Dict[str, typing.Any]:
    """A JSON object with at least one key after stripping keys; no blank or colliding keys.

    String values must not be empty or whitespace-only (the portal never sends them).
    With ``allow_null_values`` (patch), ``None`` deletes that key.
    """
    if not isinstance(value, typing.Mapping):
        raise _invalid(f"{field} must be a JSON object (dict) of key/value pairs.", field=field, code="invalid_secret_value")
    normalized: typing.Dict[str, typing.Any] = {}
    for raw_key, item in value.items():
        if not isinstance(raw_key, str) or not raw_key.strip():
            raise _invalid(f"{field} keys must be non-empty strings.", field=field, code="invalid_secret_value")
        key = raw_key.strip()
        if key in normalized:
            raise _invalid(
                f"{field} has two keys that are both '{key}' after trimming spaces.",
                field=field,
                code="invalid_secret_value",
            )
        if item is None and not allow_null_values:
            raise _invalid(f"{field}['{key}'] must not be null.", field=field, code="invalid_secret_value")
        if isinstance(item, str) and not item.strip():
            raise _invalid(f"{field}['{key}'] must not be empty.", field=field, code="invalid_secret_value")
        normalized[key] = item
    if not normalized:
        raise _invalid(f"{field} needs at least one key/value pair.", field=field, code="invalid_secret_value")
    try:
        json.dumps(normalized, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise _invalid(f"{field} must contain only JSON values.", field=field, code="invalid_secret_value") from exc
    return normalized


def build_secret_create_body(secret_name: typing.Any, value: typing.Any) -> typing.Dict[str, typing.Any]:
    body = {"secret_name": normalize_secret_name(secret_name), "value": normalize_secret_value(value)}
    assert_secret_store_body_size(body)
    return body


def _item_fields(item: typing.Any) -> typing.Tuple[typing.Any, typing.Any]:
    if isinstance(item, typing.Mapping):
        return item.get("secret_name"), item.get("value")
    return getattr(item, "secret_name", None), getattr(item, "value", None)


def normalize_batch_secrets(secrets: typing.Any) -> typing.List[typing.Dict[str, typing.Any]]:
    """1-500 items, each normalised like ``create_secret``.

    Duplicate names (after normalisation) are allowed; the API reports the later ones
    as ``skipped`` with ``duplicate_in_request``. A ``UserWarning`` is emitted for them.
    """
    if isinstance(secrets, (str, bytes)) or not isinstance(secrets, typing.Iterable):
        raise _invalid("secrets must be a list of {secret_name, value} items.", field="secrets")
    items = list(secrets)
    if not 1 <= len(items) <= SECRET_BATCH_MAX_ITEMS:
        raise _invalid(f"secrets must contain between 1 and {SECRET_BATCH_MAX_ITEMS} items.", field="secrets")
    normalized: typing.List[typing.Dict[str, typing.Any]] = []
    seen: typing.Set[str] = set()
    duplicates: typing.List[str] = []
    for index, item in enumerate(items):
        name, value = _item_fields(item)
        try:
            entry = {"secret_name": normalize_secret_name(name), "value": normalize_secret_value(value)}
        except IbeeValidationError as exc:
            raise IbeeValidationError(
                f"secrets[{index}]: {exc.message}", code=exc.code, field=f"secrets[{index}]", details=exc.details
            ) from exc
        if entry["secret_name"] in seen:
            duplicates.append(entry["secret_name"])
        seen.add(entry["secret_name"])
        normalized.append(entry)
    if duplicates:
        warnings.warn(
            "Duplicate secret names in the batch will be skipped by the API: " + ", ".join(sorted(set(duplicates))),
            UserWarning,
            stacklevel=3,
        )
    return normalized


def build_batch_create_body(secrets: typing.Any) -> typing.Dict[str, typing.Any]:
    body = {"secrets": normalize_batch_secrets(secrets)}
    assert_secret_store_body_size(body)
    return body


def chunk_batch_secrets(
    secrets: typing.Sequence[typing.Mapping[str, typing.Any]],
    *,
    max_items: int = SECRET_BATCH_MAX_ITEMS,
    max_bytes: int = SECRET_STORE_MAX_BODY_BYTES,
) -> typing.List[typing.List[typing.Dict[str, typing.Any]]]:
    """Split normalised batch items into consecutive request bodies of <= ``max_items`` and <= ``max_bytes``.

    Raises ``IbeeValidationError`` when a single item alone is too large.
    """
    chunks: typing.List[typing.List[typing.Dict[str, typing.Any]]] = []
    current: typing.List[typing.Dict[str, typing.Any]] = []
    for index, raw in enumerate(secrets):
        item = dict(raw)
        candidate = current + [item]
        if len(candidate) > max_items or encoded_json_size({"secrets": candidate}) > max_bytes:
            if not current:
                raise IbeeValidationError(
                    f"secrets[{index}] alone exceeds the {max_bytes}-byte request limit.",
                    code="request_body_too_large",
                    field=f"secrets[{index}]",
                )
            chunks.append(current)
            current = [item]
            if encoded_json_size({"secrets": current}) > max_bytes:
                raise IbeeValidationError(
                    f"secrets[{index}] alone exceeds the {max_bytes}-byte request limit.",
                    code="request_body_too_large",
                    field=f"secrets[{index}]",
                )
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def validate_secret_version(version: typing.Any, *, field: str = "version") -> int:
    """An ``int`` (not ``bool``) >= 1."""
    if not _is_int(version) or int(version) < 1:
        raise _invalid(f"{field} must be an integer >= 1.", field=field, code="invalid_version")
    return int(version)


def validate_secret_versions(versions: typing.Any) -> typing.List[int]:
    """1-100 integers >= 1, de-duplicated in order."""
    if isinstance(versions, (str, bytes)) or not isinstance(versions, typing.Iterable):
        raise _invalid("versions must be a list of integers >= 1.", field="versions")
    result: typing.List[int] = []
    for item in versions:
        if not _is_int(item) or int(item) < 1:
            raise _invalid("versions must contain only integers >= 1.", field="versions")
        if int(item) not in result:
            result.append(int(item))
    if not 1 <= len(result) <= SECRET_VERSIONS_MAX_ITEMS:
        raise _invalid(f"versions must contain between 1 and {SECRET_VERSIONS_MAX_ITEMS} versions.", field="versions")
    return result


def validate_cas(cas: typing.Any) -> typing.Optional[int]:
    """``None`` or an ``int`` (not ``bool``) >= 0. ``0`` writes only when the secret has no versions."""
    if cas is None:
        return None
    if not _is_int(cas) or int(cas) < 0:
        raise _invalid("cas must be an integer >= 0.", field="cas")
    return int(cas)


def build_secret_value_body(value: typing.Any, cas: typing.Any = None) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {"value": normalize_secret_value(value)}
    normalized_cas = validate_cas(cas)
    if normalized_cas is not None:
        body["cas"] = normalized_cas
    assert_secret_store_body_size(body)
    return body


def build_secret_patch_body(value: typing.Any) -> typing.Dict[str, typing.Any]:
    body = {"value": normalize_secret_value(value, allow_null_values=True)}
    assert_secret_store_body_size(body)
    return body


def _field(record: typing.Any, name: str) -> typing.Any:
    if isinstance(record, typing.Mapping):
        return record.get(name)
    return getattr(record, name, None)


def check_rollback_target(versions_record: typing.Any, version: int) -> None:
    """The portal's rollback rule: not the current version, a known version, and not destroyed."""
    current = _field(versions_record, "current_version")
    versions = _field(versions_record, "versions") or {}
    if current is not None and version == current:
        raise IbeeValidationError(
            f"Version {version} is already the current version.", code="rollback_to_current", field="version"
        )
    summary = versions.get(str(version)) if isinstance(versions, typing.Mapping) else None
    if summary is None:
        raise IbeeValidationError(
            f"Version {version} does not exist for this secret.",
            code="unknown_version",
            field="version",
            details={"available_versions": sorted(int(key) for key in versions if str(key).isdigit())}
            if isinstance(versions, typing.Mapping)
            else None,
        )
    if _field(summary, "destroyed"):
        raise IbeeValidationError(
            f"Version {version} was destroyed and cannot be restored.", code="version_destroyed", field="version"
        )


def secret_version_state(summary: typing.Any, current_version: typing.Any) -> str:
    """Portal status label for a version row: destroyed, active, soft_deleted or available."""
    if _field(summary, "destroyed"):
        return "destroyed"
    if _field(summary, "version") == current_version:
        return "active"
    if _field(summary, "deletion_time"):
        return "soft_deleted"
    return "available"


# ---------------------------------------------------------------------------
# Identities and scopes
# ---------------------------------------------------------------------------


def _enum(value: typing.Any, choices: typing.Sequence[str], *, field: str) -> str:
    if not isinstance(value, str) or value not in choices:
        raise _invalid(f"{field} must be one of: {', '.join(choices)}.", field=field)
    return value


def normalize_identity_name(name: typing.Any) -> str:
    """Strip; 1-128 characters (it cannot be changed later)."""
    if not isinstance(name, str) or not name.strip():
        raise _invalid("Identity name is required.", field="name")
    value = name.strip()
    if len(value) > IDENTITY_NAME_MAX_LENGTH:
        raise _invalid(f"Identity name must be at most {IDENTITY_NAME_MAX_LENGTH} characters.", field="name")
    return value


def build_identity_create_body(
    auth_method: typing.Any,
    name: typing.Any,
    token_policy_mode: typing.Any = None,
    k8s_namespace: typing.Any = None,
    k8s_service_account: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """The portal's identity body: ``token_policy_mode`` always sent (default ``read_only``);
    Kubernetes needs both fields (stripped); AppRole must not carry them."""
    method = _enum(auth_method, SECRET_STORE_AUTH_METHODS, field="auth_method")
    body: typing.Dict[str, typing.Any] = {
        "auth_method": method,
        "name": normalize_identity_name(name),
        "token_policy_mode": _enum(
            "read_only" if token_policy_mode is None else token_policy_mode, TOKEN_POLICY_MODES, field="token_policy_mode"
        ),
    }
    if method == "kubernetes":
        namespace = k8s_namespace.strip() if isinstance(k8s_namespace, str) else ""
        account = k8s_service_account.strip() if isinstance(k8s_service_account, str) else ""
        if not namespace or not account:
            raise IbeeValidationError(
                "k8s_namespace and k8s_service_account are required for Kubernetes identities.",
                code="invalid_kubernetes_identity",
                field="k8s_namespace" if not namespace else "k8s_service_account",
            )
        body["k8s_namespace"] = namespace
        body["k8s_service_account"] = account
    elif (isinstance(k8s_namespace, str) and k8s_namespace.strip()) or (
        isinstance(k8s_service_account, str) and k8s_service_account.strip()
    ):
        raise IbeeValidationError(
            "k8s_namespace and k8s_service_account apply only to Kubernetes identities.",
            code="invalid_approle_identity",
            field="k8s_namespace",
        )
    assert_secret_store_body_size(body)
    return body


def build_identity_update_body(token_policy_mode: typing.Any) -> typing.Dict[str, typing.Any]:
    """``token_policy_mode`` is required (the name cannot be changed)."""
    if token_policy_mode is None:
        raise _invalid("token_policy_mode is required (read_only or read_write).", field="token_policy_mode")
    return {"token_policy_mode": _enum(token_policy_mode, TOKEN_POLICY_MODES, field="token_policy_mode")}


def validate_scope_permissions(
    access_mode: typing.Any,
    allow_rollback: typing.Any = None,
    allow_destroy: typing.Any = None,
    *,
    identity_mode: typing.Any = None,
) -> None:
    """A ``read_only`` scope cannot allow rollback or destroy; a ``read_only`` identity only gets ``read_only`` scopes."""
    if identity_mode == "read_only" and (access_mode == "read_write" or allow_rollback is True or allow_destroy is True):
        raise IbeeValidationError(
            "Read-only identities cannot be granted write, rollback, or destroy permissions.",
            code="scope_permission_denied",
            field="access_mode",
        )
    if access_mode == "read_only" and (allow_rollback is True or allow_destroy is True):
        raise IbeeValidationError(
            "Read-only scopes cannot grant rollback or destroy permissions; use access_mode='read_write'.",
            code="invalid_scope_permissions",
            field="allow_rollback" if allow_rollback is True else "allow_destroy",
        )


def _optional_bool(value: typing.Any, *, field: str) -> typing.Optional[bool]:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise _invalid(f"{field} must be true or false.", field=field)
    return value


def build_scope_create_body(
    store_id: typing.Any,
    access_mode: typing.Any = None,
    allow_version_read: typing.Any = None,
    allow_rollback: typing.Any = None,
    allow_destroy: typing.Any = None,
    *,
    identity_mode: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """The portal's scope body with explicit defaults (read_only, version read allowed, no rollback/destroy)."""
    body = {
        "store_id": validate_secret_store_resource_id(store_id, field="store_id"),
        "access_mode": _enum("read_only" if access_mode is None else access_mode, SECRET_STORE_ACCESS_MODES, field="access_mode"),
        "allow_version_read": True
        if allow_version_read is None
        else _optional_bool(allow_version_read, field="allow_version_read"),
        "allow_rollback": bool(_optional_bool(allow_rollback, field="allow_rollback")),
        "allow_destroy": bool(_optional_bool(allow_destroy, field="allow_destroy")),
    }
    validate_scope_permissions(
        body["access_mode"], body["allow_rollback"], body["allow_destroy"], identity_mode=identity_mode
    )
    return body


def build_scope_update_body(
    access_mode: typing.Any = None,
    allow_version_read: typing.Any = None,
    allow_rollback: typing.Any = None,
    allow_destroy: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """At least one field; fields sent together must be consistent (the API checks the merged scope)."""
    body: typing.Dict[str, typing.Any] = {}
    if access_mode is not None:
        body["access_mode"] = _enum(access_mode, SECRET_STORE_ACCESS_MODES, field="access_mode")
    for field, value in (
        ("allow_version_read", allow_version_read),
        ("allow_rollback", allow_rollback),
        ("allow_destroy", allow_destroy),
    ):
        normalized = _optional_bool(value, field=field)
        if normalized is not None:
            body[field] = normalized
    if not body:
        raise IbeeValidationError(
            "Provide at least one of access_mode, allow_version_read, allow_rollback or allow_destroy.",
            code="no_changes",
            field="access_mode",
        )
    validate_scope_permissions(body.get("access_mode"), body.get("allow_rollback"), body.get("allow_destroy"))
    return body


def check_scope_store_eligible(
    store_id: str,
    stores: typing.Iterable[typing.Any],
    scopes: typing.Iterable[typing.Any],
) -> None:
    """The portal's store picker: the store must be active and not already granted to the identity."""
    granted = {str(_field(scope, "store_id")) for scope in scopes}
    if store_id in granted:
        raise IbeeValidationError(
            f"Store '{store_id}' is already granted to this identity; update its scope instead.",
            code="scope_already_exists",
            field="store_id",
        )
    for store in stores:
        if str(_field(store, "id")) == store_id:
            status = str(_field(store, "status") or "").lower()
            if status != "active":
                raise IbeeValidationError(
                    f"Store '{store_id}' is {status or 'not active'}; only active stores can be granted.",
                    code="store_not_active",
                    field="store_id",
                )
            return
    raise IbeeValidationError(
        f"Store '{store_id}' was not found among the workspace's stores.", code="store_not_found", field="store_id"
    )


def check_rotate_allowed(identity: typing.Any) -> None:
    """Rotate is offered only for active AppRole identities (as in the portal)."""
    if _field(identity, "auth_method") != "approle":
        raise IbeeValidationError(
            "rotate-secret-id is only available for AppRole identities.", code="auth_method_mismatch", field="identity_id"
        )
    if _field(identity, "status") != "active":
        raise IbeeValidationError(
            "Identity is disabled; enable it before rotating its secret ID.", code="identity_disabled", field="identity_id"
        )


__all__ = [
    "IDENTITY_NAME_MAX_LENGTH",
    "SECRET_BATCH_MAX_ITEMS",
    "SECRET_NAME_ERROR",
    "SECRET_NAME_PATTERN",
    "SECRET_SEARCH_MAX_LENGTH",
    "SECRET_STORE_ACCESS_MODES",
    "SECRET_STORE_AUTH_METHODS",
    "SECRET_STORE_DEFAULT_PAGE_LIMIT",
    "SECRET_STORE_IF_EXISTS",
    "SECRET_STORE_MAX_BODY_BYTES",
    "SECRET_STORE_PAGE_LIMIT_MAX",
    "SECRET_STORE_WORKSPACE_ID_ERROR",
    "SECRET_STORE_WORKSPACE_ID_PATTERN",
    "SECRET_VERSIONS_MAX_ITEMS",
    "STORE_NAME_MAX_LENGTH",
    "TOKEN_POLICY_MODES",
    "assert_secret_store_body_size",
    "build_batch_create_body",
    "build_identity_create_body",
    "build_identity_update_body",
    "build_scope_create_body",
    "build_scope_update_body",
    "build_secret_create_body",
    "build_secret_patch_body",
    "build_secret_value_body",
    "build_store_create_body",
    "build_store_update_body",
    "check_rollback_target",
    "check_rotate_allowed",
    "check_scope_store_eligible",
    "check_secret_store_request",
    "chunk_batch_secrets",
    "find_store_by_name",
    "is_secret_store_path",
    "normalize_batch_secrets",
    "normalize_identity_name",
    "normalize_secret_name",
    "normalize_secret_search_query",
    "normalize_secret_value",
    "normalize_store_description",
    "normalize_store_name",
    "secret_version_state",
    "validate_cas",
    "validate_if_exists",
    "validate_scope_permissions",
    "validate_secret_store_pagination",
    "validate_secret_store_resource_id",
    "validate_secret_store_workspace_id",
    "validate_secret_version",
    "validate_secret_versions",
]
