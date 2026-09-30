"""0.4.0 portal-parity Secret Store: validation, pre-steps, typed errors and retries."""

from __future__ import annotations

import asyncio
import json
import time
import warnings

import httpx
import pytest

from _compute_fixtures import WS, Router, async_client, async_transport, sync_client
from ibee import AsyncIbee, BatchCreateSecretItem, Ibee, IbeeBillingWarning, IbeeValidationError
from ibee.errors import (
    AuthMethodMismatchError,
    BadGatewayError,
    BillingDeniedError,
    CasConflictError,
    ConflictError,
    DeletionIncompleteError,
    ForbiddenError,
    IdentityDisabledError,
    InsufficientScopeError,
    NotFoundError,
    OrganizationLifecycleError,
    OrganizationRestrictedError,
    ResourceNotFoundError,
    ScopePermissionError,
    ScopeValidationError,
    SecretValueNotFoundError,
    ServiceUnavailableError,
    StoreArchivedError,
    StoreDeletingError,
    StoreNotActiveError,
    UnprocessableEntityError,
    WorkspaceNotAllowedError,
    error_from_response,
)
from ibee.validation import (
    build_identity_create_body,
    build_scope_create_body,
    build_scope_update_body,
    build_store_create_body,
    build_store_update_body,
    check_rollback_target,
    chunk_batch_secrets,
    normalize_batch_secrets,
    normalize_secret_name,
    normalize_secret_search_query,
    normalize_secret_value,
    secret_version_state,
    validate_cas,
    validate_secret_store_pagination,
    validate_secret_store_resource_id,
    validate_secret_store_workspace_id,
    validate_secret_versions,
)

STORE = "st-1"
SECRET = "sec-1"
IDENT = "id-1"
SCOPE = "sc-1"
TS = "2026-09-01T00:00:00Z"

ELIGIBLE = {
    "organization_id": "o",
    "allowed": True,
    "reason": "eligible",
    "billing_mode": "PREPAID",
    "billing_state": "CURRENT",
    "sku_code": "SECRETMA-STD",
    "evaluated_at": TS,
}


def store(**overrides: object) -> dict:
    record = {
        "id": STORE,
        "organization_id": "o",
        "workspace_id": WS,
        "name": "Production",
        "store_key": "production",
        "description": "",
        "status": "active",
        "created_at": TS,
        "updated_at": TS,
    }
    record.update(overrides)
    return record


def secret(**overrides: object) -> dict:
    record = {
        "id": SECRET,
        "organization_id": "o",
        "workspace_id": WS,
        "store_id": STORE,
        "store_key": "production",
        "secret_name": "database-url",
        "status": "active",
        "created_at": TS,
        "updated_at": TS,
    }
    record.update(overrides)
    return record


def identity(**overrides: object) -> dict:
    record = {
        "id": IDENT,
        "organization_id": "o",
        "workspace_id": WS,
        "name": "payments-api",
        "auth_method": "approle",
        "openbao_role_name": "role",
        "status": "active",
        "token_policy_mode": "read_write",
        "created_at": TS,
        "updated_at": TS,
    }
    record.update(overrides)
    return record


def scope(**overrides: object) -> dict:
    record = {
        "id": SCOPE,
        "identity_id": IDENT,
        "scope_type": "store",
        "store_id": STORE,
        "organization_id": "o",
        "workspace_id": WS,
        "access_mode": "read_only",
        "allow_version_read": True,
        "allow_rollback": False,
        "allow_destroy": False,
        "created_at": TS,
    }
    record.update(overrides)
    return record


VERSIONS = {
    "secret_id": SECRET,
    "secret_name": "database-url",
    "current_version": 3,
    "oldest_version": 1,
    "versions": {
        "1": {"version": 1, "created_time": "t1", "deletion_time": "", "destroyed": True},
        "2": {"version": 2, "created_time": "t2", "deletion_time": "t9", "destroyed": False},
        "3": {"version": 3, "created_time": "t3", "deletion_time": "", "destroyed": False},
    },
}
VALUE = {"id": SECRET, "secret_name": "database-url", "data": {"url": "x"}, "metadata": {"version": 4}}


def err(code: str, message: str, details: object = None) -> dict:
    body: dict = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return body


def scope_denied(scope_name: str = "billing.read") -> dict:
    return {"error": "insufficient_scope", "required_scope": scope_name}


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time, "sleep", lambda seconds: None)


def run(coro):  # type: ignore[no-untyped-def]
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------


def test_secret_name_is_trimmed_lowercased_and_fullmatched() -> None:
    assert normalize_secret_name("  Database-URL ") == "database-url"
    assert normalize_secret_name("a1") == "a1"
    for bad in ("a", "-abc", "has_underscore", "x" * 65, "", "   ", None, "db url"):
        with pytest.raises(IbeeValidationError) as info:
            normalize_secret_name(bad)
        assert info.value.code == "invalid_secret_name"
    # The API's regex accepts a trailing newline; the SDK does not (strip() removes it first,
    # so an internal newline is what must fail).
    with pytest.raises(IbeeValidationError):
        normalize_secret_name("ab\ncd")


def test_secret_value_rules() -> None:
    assert normalize_secret_value({" user ": "ibee", "port": 5432}) == {"user": "ibee", "port": 5432}
    for bad in ({}, [], None, "x", {"": "v"}, {"  ": "v"}, {"k": ""}, {"k": "   "}, {"a": "1", " a": "2"}, {"k": None}):
        with pytest.raises(IbeeValidationError) as info:
            normalize_secret_value(bad)
        assert info.value.code == "invalid_secret_value"
    assert normalize_secret_value({"k": None}, allow_null_values=True) == {"k": None}


def test_store_name_and_update_rules() -> None:
    assert build_store_create_body("  Prod  ", "  main ") == {"name": "Prod", "description": "main"}
    assert build_store_create_body("Prod") == {"name": "Prod"}
    for bad in ("", "   ", "---", "x" * 129, None):
        with pytest.raises(IbeeValidationError):
            build_store_create_body(bad)
    assert build_store_update_body(description=" d ") == {"description": "d"}
    assert build_store_update_body(name="---") == {"name": "---"}  # the key is not regenerated on rename
    with pytest.raises(IbeeValidationError) as info:
        build_store_update_body()
    assert info.value.code == "no_changes"


def test_paging_versions_cas_and_ids() -> None:
    assert validate_secret_store_pagination(1, 200) == {"page": 1, "limit": 200}
    for page, limit in ((0, None), (True, None), (None, 0), (None, 201), (None, False), (1.5, None)):
        with pytest.raises(IbeeValidationError):
            validate_secret_store_pagination(page, limit)
    assert normalize_secret_search_query("  db ") == "db"
    assert normalize_secret_search_query("   ") is None
    with pytest.raises(IbeeValidationError):
        normalize_secret_search_query("q" * 129)
    assert validate_secret_versions([2, 1, 2]) == [2, 1]
    for bad in ([], [0], [True], ["1"], list(range(1, 102)), "12"):
        with pytest.raises(IbeeValidationError):
            validate_secret_versions(bad)
    assert validate_cas(None) is None and validate_cas(0) == 0
    for bad in (-1, True, 1.0):
        with pytest.raises(IbeeValidationError):
            validate_cas(bad)
    assert validate_secret_store_workspace_id(" 710995 ") == "710995"
    assert validate_secret_store_workspace_id(12) == "12"
    for bad in ("7", "0710995", "1" * 129, "abc"):
        with pytest.raises(IbeeValidationError):
            validate_secret_store_workspace_id(bad)
    assert validate_secret_store_resource_id("  st-1 ", field="store_id") == "st-1"
    for bad in ("", "  ", "a/b", "a?b", "a#b", "a\nb", None):
        with pytest.raises(IbeeValidationError):
            validate_secret_store_resource_id(bad, field="store_id")


def test_identity_bodies() -> None:
    assert build_identity_create_body("approle", " api ") == {
        "auth_method": "approle",
        "name": "api",
        "token_policy_mode": "read_only",
    }
    assert build_identity_create_body("kubernetes", "api", "read_write", " ns ", " sa ") == {
        "auth_method": "kubernetes",
        "name": "api",
        "token_policy_mode": "read_write",
        "k8s_namespace": "ns",
        "k8s_service_account": "sa",
    }
    for args in (
        ("kubernetes", "api", None, "ns", None),
        ("kubernetes", "api", None, " ", "sa"),
        ("approle", "api", None, "ns", None),
        ("ldap", "api"),
        ("approle", " "),
        ("approle", "x" * 129),
        ("approle", "api", "admin"),
    ):
        with pytest.raises(IbeeValidationError):
            build_identity_create_body(*args)


def test_scope_bodies_and_permission_rule() -> None:
    assert build_scope_create_body(" st-1 ") == {
        "store_id": "st-1",
        "access_mode": "read_only",
        "allow_version_read": True,
        "allow_rollback": False,
        "allow_destroy": False,
    }
    assert build_scope_create_body("st-1", "read_write", False, True, True)["allow_destroy"] is True
    with pytest.raises(IbeeValidationError) as info:
        build_scope_create_body("st-1", allow_rollback=True)
    assert info.value.code == "invalid_scope_permissions"
    with pytest.raises(IbeeValidationError) as info:
        build_scope_create_body("st-1", "read_write", identity_mode="read_only")
    assert info.value.code == "scope_permission_denied"
    assert build_scope_update_body(allow_rollback=True) == {"allow_rollback": True}
    with pytest.raises(IbeeValidationError):
        build_scope_update_body(access_mode="read_only", allow_destroy=True)
    with pytest.raises(IbeeValidationError):
        build_scope_update_body()
    with pytest.raises(IbeeValidationError):
        build_scope_update_body(allow_rollback="yes")


def test_rollback_target_rule_and_version_state() -> None:
    check_rollback_target(VERSIONS, 2)  # soft-deleted versions stay selectable, as in the portal
    for version, code in ((3, "rollback_to_current"), (1, "version_destroyed"), (9, "unknown_version")):
        with pytest.raises(IbeeValidationError) as info:
            check_rollback_target(VERSIONS, version)
        assert info.value.code == code
    states = {key: secret_version_state(value, 3) for key, value in VERSIONS["versions"].items()}
    assert states == {"1": "destroyed", "2": "soft_deleted", "3": "active"}


def test_batch_normalisation_duplicates_and_chunking() -> None:
    with pytest.warns(UserWarning, match="Duplicate secret names"):
        items = normalize_batch_secrets(
            [{"secret_name": "API-KEY", "value": {"k": "v"}}, BatchCreateSecretItem(secret_name="api-key", value={"k": "w"})]
        )
    assert [item["secret_name"] for item in items] == ["api-key", "api-key"]
    with pytest.raises(IbeeValidationError) as info:
        normalize_batch_secrets([{"secret_name": "ok", "value": {"k": "v"}}, {"secret_name": "BAD NAME", "value": {"k": "v"}}])
    assert info.value.field == "secrets[1]"
    for bad in ([], [{"secret_name": "ab", "value": {"k": "v"}}] * 501, "x"):
        with pytest.raises(IbeeValidationError):
            normalize_batch_secrets(bad)
    big = [{"secret_name": f"s{i:03d}", "value": {"k": "v" * 1000}} for i in range(150)]
    chunks = chunk_batch_secrets(big)
    assert sum(len(chunk) for chunk in chunks) == 150 and len(chunks) > 1
    assert all(len(json.dumps({"secrets": chunk}, separators=(",", ":")).encode()) <= 65536 for chunk in chunks)
    assert [len(chunk) for chunk in chunk_batch_secrets(big[:10], max_items=4)] == [4, 4, 2]
    with pytest.raises(IbeeValidationError):
        chunk_batch_secrets([{"secret_name": "ab", "value": {"k": "v" * 70000}}])


# ---------------------------------------------------------------------------
# Requests: stores
# ---------------------------------------------------------------------------


def test_create_store_trims_and_preflights_billing() -> None:
    router = Router().add("POST", "billing/resource-eligibility", (200, ELIGIBLE)).add(
        "POST", "secret-store/stores", (201, store())
    )
    created = sync_client(router).secret_store.create_secret_store(
        workspace_id=WS, name="  Production ", description=" main ", preflight_billing=True
    )
    assert created.id == STORE
    assert router.calls() == [("POST", "secret-store/stores")]
    assert router.body("POST", "secret-store/stores") == {"name": "Production", "description": "main"}


def test_create_store_billing_denied_stops_before_create() -> None:
    denied = {**ELIGIBLE, "allowed": False, "reason": "insufficient_balance"}
    router = Router().add("POST", "secret-store/stores", (402, {"error": "billing_denied", "billing_reason": "insufficient_balance"}))
    with pytest.raises(BillingDeniedError):
        sync_client(router).secret_store.create_secret_store(workspace_id=WS, name="p", preflight_billing=True)
    assert router.calls() == [("POST", "secret-store/stores")]


def test_preflight_without_billing_scope_warns_and_creates() -> None:
    router = Router().add("POST", "billing/resource-eligibility", (403, scope_denied())).add(
        "POST", f"secret-store/stores/{STORE}/secrets", (201, secret())
    )
    sync_client(router).secret_store.create_secret(
        STORE, workspace_id=WS, secret_name="Database-URL", value={" url ": "x"}, preflight_billing=True
    )
    assert ("POST", "billing/resource-eligibility") not in router.calls()
    assert router.body("POST", f"secret-store/stores/{STORE}/secrets") == {
        "secret_name": "database-url",
        "value": {"url": "x"},
    }


def test_create_store_conflict_and_if_exists_return() -> None:
    conflict = (409, err("CONFLICT", "Store with name 'Production' already exists"))
    router = Router().add("POST", "secret-store/stores", conflict)
    with pytest.raises(ConflictError):
        sync_client(router).secret_store.create_secret_store(workspace_id=WS, name="Production")
    assert len(router.requests) == 1  # a 409 is never retried

    router = (
        Router()
        .add("POST", "secret-store/stores", conflict)
        .add("GET", "secret-store/stores", (200, {"stores": [store(name="other", store_key="other"), store(status="archived")], "total": 2, "page": 1, "limit": 200}))
    )
    found = sync_client(router).secret_store.create_secret_store(workspace_id=WS, name=" production ", if_exists="return")
    assert found.id == STORE and found.status == "archived"
    listing = router.last("GET", "secret-store/stores")
    assert listing.url.params["include_archived"] == "true" and listing.url.params["limit"] == "200"


def test_list_stores_validates_and_list_all_pages() -> None:
    client = sync_client(Router())
    with pytest.raises(IbeeValidationError):
        client.secret_store.list_secret_stores(workspace_id=WS, limit=500)
    with pytest.raises(IbeeValidationError):
        client.secret_store.list_secret_stores(workspace_id=WS, include_archived="yes")  # type: ignore[arg-type]
    pages = [
        (200, {"stores": [store(id="a"), store(id="b")], "total": 3, "page": 1, "limit": 2}),
        (200, {"stores": [store(id="c")], "total": 3, "page": 2, "limit": 2}),
    ]
    router = Router().add("GET", "secret-store/stores", pages)
    result = sync_client(router).secret_store.list_all_secret_stores(workspace_id=WS, page_size=2)
    assert [item.id for item in result] == ["a", "b", "c"]
    assert [r.url.params["page"] for r in router.requests] == ["1", "2"]
    assert router.requests[0].url.params["include_archived"] == "true"


def test_update_store_requires_a_field() -> None:
    router = Router()
    with pytest.raises(IbeeValidationError):
        sync_client(router).secret_store.update_secret_store(STORE, workspace_id=WS)
    assert router.requests == []


def test_single_digit_workspace_rejected_for_secret_store_only() -> None:
    router = Router()
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).secret_store.get_secret_store(STORE, workspace_id="7")
    assert info.value.field == "workspace_id"
    with pytest.raises(IbeeValidationError):
        sync_client(router).secret_store.with_raw_response.get_secret_store(STORE, workspace_id="7")
    assert router.requests == []


# ---------------------------------------------------------------------------
# Requests: secrets
# ---------------------------------------------------------------------------


def test_create_secret_rejects_before_any_request() -> None:
    router = Router()
    client = sync_client(router)
    with pytest.raises(IbeeValidationError):
        client.secret_store.create_secret(STORE, workspace_id=WS, secret_name="bad name", value={"k": "v"})
    with pytest.raises(IbeeValidationError):
        client.secret_store.create_secret(STORE, workspace_id=WS, secret_name="ok-name", value={"k": " "})
    with pytest.raises(IbeeValidationError) as info:
        client.secret_store.create_secret(
            STORE, workspace_id=WS, secret_name="big", value={"k": "v" * 70000}, preflight_billing=True
        )
    assert info.value.code == "request_body_too_large"
    with pytest.raises(IbeeValidationError) as info:
        client.secret_store.with_raw_response.update_secret_value(SECRET, workspace_id=WS, value={"k": "v" * 70000})
    assert info.value.code == "request_body_too_large"
    assert router.requests == []


def test_list_secrets_query_trimmed_and_blank_omitted() -> None:
    router = Router().add("GET", f"secret-store/stores/{STORE}/secrets", (200, {"secrets": [secret()], "total": 1, "page": 1, "limit": 100}))
    client = sync_client(router)
    client.secret_store.list_secrets(STORE, workspace_id=WS, q="  db ", page=1, limit=100)
    client.secret_store.list_secrets(STORE, workspace_id=WS, q="   ")
    first, second = router.requests
    assert first.url.params["q"] == "db" and first.url.params["limit"] == "100"
    assert "q" not in second.url.params
    assert [s.id for s in client.secret_store.list_all_secrets(STORE, workspace_id=WS, q="db")] == [SECRET]


def test_batch_create_normalises_items() -> None:
    router = Router().add(
        "POST",
        f"secret-store/stores/{STORE}/secrets:batchIngest",
        (200, {"results": [], "created_count": 1, "skipped_count": 0, "failed_count": 0}),
    )
    sync_client(router).secret_store.batch_create_secrets(
        STORE, workspace_id=WS, secrets=[BatchCreateSecretItem(secret_name=" API-Key ", value={" k ": "v"})]
    )
    assert router.body("POST", f"secret-store/stores/{STORE}/secrets:batchIngest") == {
        "secrets": [{"secret_name": "api-key", "value": {"k": "v"}}]
    }


def test_update_value_cas_mismatch_is_typed() -> None:
    bad_gateway = (502, err("OPENBAO_ERROR", "OpenBao request failed"))
    router = Router().add("PUT", f"secret-store/secrets/{SECRET}/value", bad_gateway)
    client = sync_client(router)
    with pytest.raises(CasConflictError) as info:
        client.secret_store.update_secret_value(SECRET, workspace_id=WS, value={"k": "v"}, cas=3)
    assert isinstance(info.value, BadGatewayError) and "cas" in str(info.value)
    assert router.body("PUT", f"secret-store/secrets/{SECRET}/value") == {"value": {"k": "v"}, "cas": 3}
    with pytest.raises(BadGatewayError) as plain:
        client.secret_store.update_secret_value(SECRET, workspace_id=WS, value={"k": "v"})
    assert not isinstance(plain.value, CasConflictError)
    with pytest.raises(IbeeValidationError):
        client.secret_store.update_secret_value(SECRET, workspace_id=WS, value={"k": "v"}, cas=True)


def test_patch_value_allows_null_deletes() -> None:
    router = Router().add("PATCH", f"secret-store/secrets/{SECRET}/value", (200, VALUE))
    sync_client(router).secret_store.patch_secret_value(SECRET, workspace_id=WS, value={" old ": None, "new": "v"})
    assert router.body("PATCH", f"secret-store/secrets/{SECRET}/value") == {"value": {"old": None, "new": "v"}}


def test_undelete_defaults_to_current_version() -> None:
    router = (
        Router()
        .add("GET", f"secret-store/secrets/{SECRET}/versions", (200, VERSIONS))
        .add("POST", f"secret-store/secrets/{SECRET}/undelete", (200, secret()))
    )
    client = sync_client(router)
    client.secret_store.undelete_secret(SECRET, workspace_id=WS)
    assert router.body("POST", f"secret-store/secrets/{SECRET}/undelete") == {"versions": [3]}
    client.secret_store.undelete_secret(SECRET, workspace_id=WS, versions=[2, 2, 1])
    assert router.body("POST", f"secret-store/secrets/{SECRET}/undelete") == {"versions": [2, 1]}


def test_get_version_rejects_zero() -> None:
    router = Router()
    with pytest.raises(IbeeValidationError):
        sync_client(router).secret_store.get_secret_version(SECRET, 0, workspace_id=WS)
    assert router.requests == []


def test_rollback_checks_target_like_the_portal() -> None:
    versions_path = f"secret-store/secrets/{SECRET}/versions"
    rollback_path = f"secret-store/secrets/{SECRET}/rollback"
    router = Router().add("GET", versions_path, (200, VERSIONS)).add("POST", rollback_path, (200, VALUE))
    client = sync_client(router)
    for version in (3, 1, 7):
        with pytest.raises(IbeeValidationError):
            client.secret_store.rollback_secret(SECRET, workspace_id=WS, version=version)
    assert ("POST", rollback_path) not in router.calls()
    client.secret_store.rollback_secret(SECRET, workspace_id=WS, version=2)
    assert router.body("POST", rollback_path) == {"version": 2}

    router = Router().add("POST", rollback_path, (200, VALUE))
    sync_client(router).secret_store.rollback_secret(SECRET, workspace_id=WS, version=3, check_target=False)
    assert router.calls() == [("POST", rollback_path)]

    router = Router().add("GET", versions_path, (403, scope_denied("secret-store.read"))).add("POST", rollback_path, (200, VALUE))
    with pytest.warns(UserWarning, match="secret-store.read"):
        sync_client(router).secret_store.rollback_secret(SECRET, workspace_id=WS, version=3)
    assert router.calls()[-1] == ("POST", rollback_path)


# ---------------------------------------------------------------------------
# Requests: identities and scopes
# ---------------------------------------------------------------------------


def test_create_identity_sends_portal_body() -> None:
    router = Router().add("POST", f"secret-store/stores/{STORE}/identities", (201, identity()))
    client = sync_client(router)
    client.secret_store.create_secret_identity(STORE, workspace_id=WS, auth_method="approle", name=" api ")
    assert router.body("POST", f"secret-store/stores/{STORE}/identities") == {
        "auth_method": "approle",
        "name": "api",
        "token_policy_mode": "read_only",
    }
    with pytest.raises(IbeeValidationError):
        client.secret_store.create_secret_identity(STORE, workspace_id=WS, auth_method="kubernetes", name="k")
    assert len(router.requests) == 1


def test_update_identity_requires_mode() -> None:
    router = Router()
    with pytest.raises(IbeeValidationError):
        sync_client(router).secret_store.update_secret_identity(IDENT, workspace_id=WS)
    assert router.requests == []


def test_rotate_checks_auth_method_when_asked() -> None:
    rotate = f"secret-store/identities/{IDENT}/rotate-secret-id"
    router = Router().add("GET", f"secret-store/identities/{IDENT}", (200, identity(auth_method="kubernetes")))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).secret_store.rotate_secret_identity_secret_id(IDENT, workspace_id=WS, check_auth_method=True)
    assert info.value.code == "auth_method_mismatch"
    router = Router().add("GET", f"secret-store/identities/{IDENT}", (200, identity(status="disabled")))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).secret_store.rotate_secret_identity_secret_id(IDENT, workspace_id=WS, check_auth_method=True)
    assert info.value.code == "identity_disabled"
    access = {"identity_id": IDENT, "auth_method": "approle", "role_id": "r", "secret_id": "s"}
    router = Router().add("POST", rotate, (200, access))
    sync_client(router).secret_store.rotate_secret_identity_secret_id(IDENT, workspace_id=WS)
    assert router.calls() == [("POST", rotate)]


def test_scope_create_check_store() -> None:
    scopes_path = f"secret-store/identities/{IDENT}/scopes"

    def build(ident: dict, scopes: list, stores: list) -> Router:
        return (
            Router()
            .add("GET", f"secret-store/identities/{IDENT}", (200, ident))
            .add("GET", scopes_path, (200, {"scopes": scopes, "total": len(scopes)}))
            .add("GET", "secret-store/stores", (200, {"stores": stores, "total": len(stores), "page": 1, "limit": 200}))
            .add("POST", scopes_path, (201, scope(store_id="st-2")))
        )

    cases = [
        (identity(), [scope()], [store()], STORE, "scope_already_exists"),
        (identity(), [], [store(id="st-2", status="archived")], "st-2", "store_not_active"),
        (identity(), [], [], "st-2", "store_not_found"),
        (identity(token_policy_mode="read_only"), [], [store(id="st-2")], "st-2", "scope_permission_denied"),
    ]
    for ident, scopes, stores, store_id, code in cases:
        router = build(ident, scopes, stores)
        with pytest.raises(IbeeValidationError) as info:
            sync_client(router).secret_store.create_secret_identity_scope(
                IDENT, workspace_id=WS, store_id=store_id, access_mode="read_write", check_store=True
            )
        assert info.value.code == code
        assert ("POST", scopes_path) not in router.calls()

    router = build(identity(), [scope()], [store(), store(id="st-2")])
    sync_client(router).secret_store.create_secret_identity_scope(IDENT, workspace_id=WS, store_id="st-2", check_store=True)
    assert router.body("POST", scopes_path) == {
        "store_id": "st-2",
        "access_mode": "read_only",
        "allow_version_read": True,
        "allow_rollback": False,
        "allow_destroy": False,
    }


def test_identity_access_is_never_retried() -> None:
    path = f"secret-store/identities/{IDENT}/access"
    router = Router().add("GET", path, (503, err("SERVICE_UNAVAILABLE", "try later")))
    client = Ibee(token="t", base_url="https://api.example.test/v1", httpx_client=httpx.Client(transport=httpx.MockTransport(router)), max_retries=3)
    with pytest.raises(ServiceUnavailableError):
        client.secret_store.get_secret_identity_access(IDENT, workspace_id=WS)
    assert len(router.requests) == 1
    router = Router().add("GET", f"secret-store/identities/{IDENT}", (503, err("SERVICE_UNAVAILABLE", "x")), (200, identity()))
    client = Ibee(token="t", base_url="https://api.example.test/v1", httpx_client=httpx.Client(transport=httpx.MockTransport(router)), max_retries=3)
    client.secret_store.get_secret_identity(IDENT, workspace_id=WS)
    assert len(router.requests) == 2


# ---------------------------------------------------------------------------
# Error mapping
# ---------------------------------------------------------------------------

P_STORE = "secret-store/stores/st-1"


@pytest.mark.parametrize(
    ("status", "body", "path", "cls", "parents"),
    [
        (403, err("FORBIDDEN", f"Store 'st-1' does not belong to workspace '{WS}'"), P_STORE, ResourceNotFoundError, (WorkspaceNotAllowedError, ForbiddenError)),
        (403, err("FORBIDDEN", "Operation 'CREATE_RESOURCE' is not allowed while organization is suspended"), "secret-store/stores", OrganizationLifecycleError, (OrganizationRestrictedError, ForbiddenError)),
        (403, err("FORBIDDEN", "Store 'st-1' is not active"), "secret-store/stores/st-1/identities", StoreNotActiveError, (ForbiddenError,)),
        (403, err("FORBIDDEN", "Identity is disabled"), "secret-store/identities/i/access", IdentityDisabledError, (ForbiddenError,)),
        (403, err("FORBIDDEN", "rotate-secret-id is only available for AppRole identities"), "secret-store/identities/i/rotate-secret-id", AuthMethodMismatchError, (ForbiddenError,)),
        (403, err("FORBIDDEN", "Read-only identities cannot be granted write, rollback, or destroy permissions"), "secret-store/identities/i/scopes", ScopePermissionError, (ForbiddenError,)),
        (403, scope_denied("secret-store.write"), "secret-store/stores", InsufficientScopeError, (ForbiddenError,)),
        (409, err("STORE_ARCHIVED", "Store 'st-1' is archived. Unarchive it first."), P_STORE, StoreArchivedError, (ConflictError,)),
        (409, err("STORE_DELETING", "Store 'st-1' is being deleted."), P_STORE, StoreDeletingError, (ConflictError,)),
        (404, err("NOT_FOUND", "Secret version not found"), "secret-store/secrets/s/value", SecretValueNotFoundError, (NotFoundError,)),
        (422, err("VALIDATION_ERROR", "Read-only scopes cannot grant rollback or destroy permissions"), "secret-store/scopes/s", ScopeValidationError, (UnprocessableEntityError,)),
        (503, err("LIFECYCLE_OPERATION_INCOMPLETE", "Store deletion incomplete", {"store_id": "st-1", "failed_steps": ["kv"]}), f"{P_STORE}/permanent", DeletionIncompleteError, (ServiceUnavailableError,)),
    ],
)
def test_secret_store_error_mapping(status: int, body: dict, path: str, cls: type, parents: tuple) -> None:
    error = error_from_response(status, body, {}, path=path)
    assert type(error) is cls
    for parent in parents:
        assert isinstance(error, parent)


def test_error_details_are_parsed() -> None:
    lifecycle = error_from_response(
        403, err("FORBIDDEN", "Operation 'READ_RESOURCE' is not allowed while organization is deleting"), path="secret-store/stores"
    )
    assert (lifecycle.state, lifecycle.operation) == ("deleting", "READ_RESOURCE")
    missing = error_from_response(403, err("FORBIDDEN", f"Identity 'id-9' does not belong to workspace '{WS}'"), path="secret-store/identities/id-9")
    assert (missing.kind, missing.resource_id, missing.workspace_id) == ("identity", "id-9", WS)
    incomplete = error_from_response(
        503, err("LIFECYCLE_OPERATION_INCOMPLETE", "x", {"store_id": "st-1", "failed_steps": ["kv", "policies"]}), path=f"{P_STORE}/permanent"
    )
    assert incomplete.failed_steps == ["kv", "policies"] and incomplete.retryable and incomplete.store_id == "st-1"
    # Outside Secret Store the 0.4.0 generic mapping is unchanged.
    other = error_from_response(403, err("FORBIDDEN", f"Store 'x' does not belong to workspace '{WS}'"), path="compute/cloud-vms")
    assert type(other) is WorkspaceNotAllowedError


def test_typed_errors_reach_the_caller() -> None:
    router = Router().add("PATCH", P_STORE, (409, err("STORE_ARCHIVED", "Store 'st-1' is archived. Unarchive it first.")))
    with pytest.raises(StoreArchivedError) as info:
        sync_client(router).secret_store.update_secret_store(STORE, workspace_id=WS, name="n")
    assert info.value.hint == "unarchive the store first"
    router = Router().add("DELETE", f"{P_STORE}/permanent", (503, err("LIFECYCLE_OPERATION_INCOMPLETE", "x", {"failed_steps": ["kv"]})))
    with pytest.raises(DeletionIncompleteError):
        sync_client(router).secret_store.permanently_delete_secret_store(STORE, workspace_id=WS)


# ---------------------------------------------------------------------------
# Async parity
# ---------------------------------------------------------------------------


def test_async_client_applies_the_same_rules() -> None:
    versions_path = f"secret-store/secrets/{SECRET}/versions"

    async def main() -> None:
        router = (
            Router()
            .add("POST", "billing/resource-eligibility", (200, ELIGIBLE))
            .add("POST", f"secret-store/stores/{STORE}/secrets", (201, secret()))
            .add("GET", versions_path, (200, VERSIONS))
            .add("POST", f"secret-store/secrets/{SECRET}/rollback", (200, VALUE))
            .add("GET", "secret-store/stores", (200, {"stores": [store()], "total": 1, "page": 1, "limit": 200}))
            .add("PUT", f"secret-store/secrets/{SECRET}/value", (502, err("OPENBAO_ERROR", "OpenBao request failed")))
        )
        async with async_transport(router) as http:
            client: AsyncIbee = async_client(router, http)
            await client.secret_store.create_secret(
                STORE, workspace_id=WS, secret_name=" DB ", value={"k": "v"}, preflight_billing=True
            )
            assert router.body("POST", f"secret-store/stores/{STORE}/secrets")["secret_name"] == "db"
            with pytest.raises(IbeeValidationError):
                await client.secret_store.rollback_secret(SECRET, workspace_id=WS, version=3)
            await client.secret_store.rollback_secret(SECRET, workspace_id=WS, version=2)
            assert [s.id for s in await client.secret_store.list_all_secret_stores(workspace_id=WS)] == [STORE]
            with pytest.raises(CasConflictError):
                await client.secret_store.update_secret_value(SECRET, workspace_id=WS, value={"k": "v"}, cas=0)
            with pytest.raises(IbeeValidationError):
                await client.secret_store.create_secret_identity_scope(IDENT, workspace_id=WS, store_id=STORE, allow_destroy=True)

    run(main())


def test_no_warning_on_normal_create() -> None:
    router = Router().add("POST", "secret-store/stores", (201, store()))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        sync_client(router).secret_store.create_secret_store(workspace_id=WS, name="p")
