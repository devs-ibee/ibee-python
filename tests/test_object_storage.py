"""Focused request-shape tests for Object Storage bucket creation."""

from __future__ import annotations

import json
import unittest

import httpx

from ibee import AsyncIbee, Ibee


class ObjectStorageBucketCreationTests(unittest.TestCase):
    def test_sync_create_bucket_omits_region_by_default(self) -> None:
        requests: list[httpx.Request] = []

        def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(201, json={"name": "application-assets"})

        http_client = httpx.Client(transport=httpx.MockTransport(handle))
        self.addCleanup(http_client.close)
        client = Ibee(token="test", httpx_client=http_client)

        client.object_storage.create_bucket(workspace_id="973318", name="application-assets")

        body = json.loads(requests[0].content)
        self.assertNotIn("region", body)


class AsyncObjectStorageBucketCreationTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_create_bucket_omits_region_by_default(self) -> None:
        requests: list[httpx.Request] = []

        async def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(201, json={"name": "application-assets"})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http_client:
            client = AsyncIbee(token="test", httpx_client=http_client)
            await client.object_storage.create_bucket(
                workspace_id="973318",
                name="application-assets",
            )

        body = json.loads(requests[0].content)
        self.assertNotIn("region", body)


if __name__ == "__main__":
    unittest.main()
