"""Focused request-shape tests for Object Storage bucket creation."""

from __future__ import annotations

import json
import unittest

import httpx

from ibee import AsyncIbee, Ibee


def response_for(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/v1/billing/resource-eligibility":
        return httpx.Response(
            200,
            json={
                "organization_id": "org-1",
                "allowed": True,
                "reason": "eligible",
                "billing_mode": "PREPAID",
                "billing_state": "CURRENT",
                "sku_code": "OBJECTST-STD",
                "evaluated_at": "2026-08-13T00:00:00Z",
            },
        )
    return httpx.Response(
        201,
        json={
            "name": "application-assets",
            "region": "in-south-1",
            "is_public": False,
            "bucket_lock_enabled": False,
        },
    )


class ObjectStorageBucketCreationTests(unittest.TestCase):
    def test_sync_create_bucket_requires_and_sends_region(self) -> None:
        requests: list[httpx.Request] = []

        def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return response_for(request)

        http_client = httpx.Client(transport=httpx.MockTransport(handle))
        self.addCleanup(http_client.close)
        client = Ibee(token="test", httpx_client=http_client)

        client.object_storage.create_bucket(
            workspace_id="973318",
            name="application-assets",
            region="in-south-1",
        )

        bucket_request = next(request for request in requests if request.url.path.endswith("/buckets"))
        body = json.loads(bucket_request.content)
        self.assertEqual(body["region"], "in-south-1")


class AsyncObjectStorageBucketCreationTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_create_bucket_requires_and_sends_region(self) -> None:
        requests: list[httpx.Request] = []

        async def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return response_for(request)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http_client:
            client = AsyncIbee(token="test", httpx_client=http_client)
            await client.object_storage.create_bucket(
                workspace_id="973318",
                name="application-assets",
                region="in-south-1",
            )

        bucket_request = next(request for request in requests if request.url.path.endswith("/buckets"))
        body = json.loads(bucket_request.content)
        self.assertEqual(body["region"], "in-south-1")


if __name__ == "__main__":
    unittest.main()
