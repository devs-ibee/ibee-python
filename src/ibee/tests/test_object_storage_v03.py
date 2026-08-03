from __future__ import annotations

import json

import httpx

from ibee import Ibee


def test_object_storage_exposes_bucket_and_s3_credential_lifecycle() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
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
        bucket_scope="specific",
        allowed_buckets=["assets"],
    )

    assert result.secret_access_key == "returned-once"
    assert observed[0].url.path == "/v1/object-storage/credentials"
    assert json.loads(observed[0].content) == {
        "name": "ci",
        "bucket_scope": "specific",
        "allowed_buckets": ["assets"],
    }


def test_create_bucket_uses_storage_region_without_compute_site_fields() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(201, json={"bucket_name": "assets"}, request=request)

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

    assert observed[0].url.path == "/v1/object-storage/buckets"
    assert json.loads(observed[0].content) == {
        "name": "assets",
        "region": "in-south-1",
        "is_public": False,
        "object_lock_enabled": True,
        "default_retention": {"mode": "GOVERNANCE", "days": 30},
        "tags": ["production"],
    }
