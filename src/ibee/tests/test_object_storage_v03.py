from __future__ import annotations

import json

import httpx

from ibee import Ibee


def _billing_decision() -> dict[str, object]:
    return {
        "organization_id": "organization-1",
        "allowed": True,
        "reason": "eligible",
        "billing_mode": "PREPAID",
        "billing_state": "CURRENT",
        "sku_code": "OBJECTST-STD",
        "evaluated_at": "2026-08-04T10:00:00Z",
    }


def test_object_storage_exposes_bucket_and_s3_credential_lifecycle() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        if request.url.path.endswith("/billing/resource-eligibility"):
            return httpx.Response(200, json=_billing_decision(), request=request)
        return httpx.Response(
            200,
            json={
                "access_key_id": "AK123",
                "name": "ci",
                "status": "active",
                "created_at": "2026-07-31T00:00:00Z",
                "secret_access_key": "returned-once",
            },
            request=request,
        )

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert {
        "list_buckets",
        "create_bucket",
        "get_bucket",
        "update_bucket",
        "delete_bucket",
        "list_s3credentials",
        "create_s3credential",
        "get_s3credential",
        "revoke_s3credential",
    } <= set(dir(client.object_storage))

    result = client.object_storage.create_s3credential(
        workspace_id="607005",
        name="ci",
        permission_type="object_rw",
        bucket_scope="specific",
        allowed_buckets=["assets"],
    )

    assert result.secret_access_key == "returned-once"
    assert len(observed) == 1
    assert observed[0].url.path == "/v1/object-storage/credentials"
    # 0.4.0: permission_type is always sent (the API requires it).
    assert json.loads(observed[0].content) == {
        "name": "ci",
        "permission_type": "object_rw",
        "bucket_scope": "specific",
        "allowed_buckets": ["assets"],
    }


def test_create_bucket_uses_storage_region_without_compute_site_fields() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        if request.url.path.endswith("/billing/resource-eligibility"):
            return httpx.Response(200, json=_billing_decision(), request=request)
        return httpx.Response(
            201,
            json={
                "name": "assets",
                "is_public": False,
                "bucket_lock_enabled": True,
            },
            request=request,
        )

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    client.object_storage.create_bucket(
        workspace_id="607005",
        name="assets",
        region="in-south-1",
        is_public=False,
        object_lock_enabled=True,
        default_retention={"mode": "GOVERNANCE", "days": 30},
        tags=["production"],
    )

    assert len(observed) == 1
    assert observed[0].url.path == "/v1/object-storage/buckets"
    assert json.loads(observed[0].content) == {
        "name": "assets",
        "region": "in-south-1",
        "is_public": False,
        "object_lock_enabled": True,
        "default_retention": {"mode": "GOVERNANCE", "days": 30},
        "tags": ["production"],
    }
