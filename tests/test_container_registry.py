"""Container Registry: generated calls, the ``Idempotency-Key`` default, answers unchanged."""

import asyncio
import uuid

import pytest
from mockapi import WS, Recorder, async_client, client

from ibee.errors import ConflictError, ForbiddenError

REG = "6f1c2c1e-8d3b-4c55-9a43-0d6c1f0b9e11"
TOKEN = "0b8f6a52-2d0e-4c1b-8a35-9f5e3c7d2a10"
REGISTRY = {
    "registry_id": REG, "registry_name": "acme-apps", "registry_kind": "CUSTOMER", "organization_id": "1",
    "workspace_id": WS, "visibility": "PRIVATE", "security": {"vulnerability_pull_policy": "ALLOW"},
    "desired_state": "ACTIVE", "observed_state": "PROVISIONING", "generation": 1, "observed_generation": 0,
    "created_at": "2026-10-20T00:00:00Z", "updated_at": "2026-10-20T00:00:00Z", "deleted_at": None,
}
OPERATION = {
    "operation_id": "1d5d2a3e-55b5-4b7e-9d4c-2f3e0a1b2c3d", "registry_id": REG, "kind": "UPGRADE", "status": "PENDING",
    "sku_code": "REGISTRY-STORAGE-500GB", "quota_bytes": 500_000_000_000, "quota_gb": 500,
    "created_at": "2026-10-20T00:00:00Z", "effective_at": None,
}
SECRET = {
    "token_id": TOKEN, "token_name": "ci", "username": "robot$acme+ci", "secret": "s3cr3t", "permission": "PULL_PUSH",
    "registry_ids": [REG], "expires_at": None, "created_at": "2026-10-20T00:00:00Z",
}
SKU = {"sku_code": "REGISTRY-STORAGE-500GB"}


def test_create_sends_the_body_as_given() -> None:
    rec = Recorder((202, REGISTRY))
    created = client(rec, workspace_id=WS).container_registry.create_container_registry(
        registry_name="acme-apps", confirm_registry_name="acme-apps", billing_catalog={"sku_code": "REGISTRY-STORAGE-250GB"},
    )
    request = rec.requests[0]
    assert (request.method, request.url.path) == ("POST", "/v1/container-registry/registries")
    assert request.url.params["workspace_id"] == WS
    assert rec.body() == {
        "registry_name": "acme-apps", "confirm_registry_name": "acme-apps", "billing_catalog": {"sku_code": "REGISTRY-STORAGE-250GB"},
    }
    assert created.observed_state == "PROVISIONING"


def test_upgrade_gets_a_random_idempotency_key() -> None:
    rec = Recorder((202, OPERATION))
    client(rec, workspace_id=WS).container_registry.upgrade_container_registry_package(REG, billing_catalog=SKU)
    headers = rec.requests[0].headers
    uuid.UUID(headers["idempotency-key"])
    assert "x-idempotency-key" not in headers


def test_upgrade_caller_key_is_sent_unchanged() -> None:
    rec = Recorder((202, OPERATION))
    api = client(rec, workspace_id=WS).container_registry
    api.upgrade_container_registry_package(REG, billing_catalog=SKU, idempotency_key="up-1")
    api.upgrade_container_registry_package(
        REG, billing_catalog=SKU, request_options={"additional_headers": {"Idempotency-Key": "up-2"}}
    )
    assert [r.headers["idempotency-key"] for r in rec.requests] == ["up-1", "up-2"]


def test_upgrade_retry_reuses_the_key() -> None:
    rec = Recorder((503, {"detail": "busy"}), (202, OPERATION))
    client(rec, workspace_id=WS).container_registry.upgrade_container_registry_package(REG, billing_catalog=SKU)
    keys = [r.headers["idempotency-key"] for r in rec.requests]
    assert len(keys) == 2 and keys[0] == keys[1]


def test_upgrade_billing_refusal_is_raised_unchanged_and_not_retried() -> None:
    body = {"detail": {"code": "billing_resource_not_eligible", "reason": "kyc_required"}}
    rec = Recorder((403, body))
    with pytest.raises(ForbiddenError) as info:
        client(rec, workspace_id=WS).container_registry.upgrade_container_registry_package(REG, billing_catalog=SKU)
    assert len(rec.requests) == 1
    assert info.value.body == body
    assert info.value.idempotency_key == rec.requests[0].headers["idempotency-key"]


def test_registry_conflict_is_raised_unchanged() -> None:
    body = {"detail": {"code": "registry_not_empty", "message": "Empty the registry first."}}
    rec = Recorder((409, body))
    with pytest.raises(ConflictError) as info:
        client(rec, workspace_id=WS).container_registry.delete_container_registry(REG, confirm_registry_name="acme-apps")
    assert rec.requests[0].url.params["confirm_registry_name"] == "acme-apps"
    assert info.value.body == body


def test_token_create_returns_the_secret_once_as_sent() -> None:
    rec = Recorder((201, SECRET))
    token = client(rec, workspace_id=WS).container_registry.create_container_registry_access_token(
        REG, token_name="ci", permission="PULL_PUSH"
    )
    assert rec.body() == {"token_name": "ci", "permission": "PULL_PUSH"}
    assert (token.username, token.secret) == ("robot$acme+ci", "s3cr3t")


def test_paging_uses_page_and_page_size() -> None:
    rec = Recorder((200, {"items": [], "total": 0, "page": 2, "page_size": 100}))
    client(rec, workspace_id=WS).container_registry.list_container_registries(page=2, page_size=100)
    params = rec.requests[0].url.params
    assert (params["page"], params["page_size"]) == ("2", "100")


def test_async_upgrade_gets_a_key_too() -> None:
    rec = Recorder((202, OPERATION))

    async def run() -> None:
        await async_client(rec, workspace_id=WS).container_registry.upgrade_container_registry_package(REG, billing_catalog=SKU)

    asyncio.run(run())
    uuid.UUID(rec.requests[0].headers["idempotency-key"])
