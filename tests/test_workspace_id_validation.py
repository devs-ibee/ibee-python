"""Workspace selector validation shared by every SDK operation."""

from __future__ import annotations

import unittest

import httpx

from ibee import AsyncIbee, Ibee


ERROR = "workspace_id must be a positive numeric string (for example, '710995')."
INVALID_WORKSPACE_IDS = ("", "0", "01", "-1", "abc", "1.0", " 1")


class WorkspaceIdValidationTests(unittest.TestCase):
    def test_sync_requests_reject_invalid_workspace_ids_before_transport(self) -> None:
        requests: list[httpx.Request] = []

        def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={"sites": [], "count": 0})

        http_client = httpx.Client(transport=httpx.MockTransport(handle))
        self.addCleanup(http_client.close)
        client = Ibee(token="test", httpx_client=http_client)

        for workspace_id in INVALID_WORKSPACE_IDS:
            with self.subTest(workspace_id=workspace_id):
                with self.assertRaisesRegex(ValueError, "positive numeric string") as error:
                    client.compute_catalog.list_compute_sites(workspace_id=workspace_id)
                self.assertEqual(str(error.exception), ERROR)

        self.assertEqual(requests, [])

    def test_sync_requests_accept_positive_numeric_workspace_ids(self) -> None:
        requests: list[httpx.Request] = []

        def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={"sites": [], "count": 0})

        http_client = httpx.Client(transport=httpx.MockTransport(handle))
        self.addCleanup(http_client.close)
        client = Ibee(token="test", httpx_client=http_client)

        client.compute_catalog.list_compute_sites(workspace_id="1")
        client.compute_catalog.list_compute_sites(workspace_id="710995")

        self.assertEqual([request.url.params["workspace_id"] for request in requests], ["1", "710995"])


class AsyncWorkspaceIdValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_requests_reject_invalid_workspace_ids_before_transport(self) -> None:
        requests: list[httpx.Request] = []

        async def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={"sites": []})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http_client:
            client = AsyncIbee(token="test", httpx_client=http_client)
            for workspace_id in INVALID_WORKSPACE_IDS:
                with self.subTest(workspace_id=workspace_id):
                    with self.assertRaisesRegex(ValueError, "positive numeric string") as error:
                        await client.compute_catalog.list_compute_sites(workspace_id=workspace_id)
                    self.assertEqual(str(error.exception), ERROR)

        self.assertEqual(requests, [])


if __name__ == "__main__":
    unittest.main()
