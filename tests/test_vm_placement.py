"""Request-shape tests for optional VM placement."""

from __future__ import annotations

import json
import unittest

import httpx

from ibee import AsyncIbee, Ibee


class VmPlacementTests(unittest.TestCase):
    def test_sync_vm_clients_omit_or_send_site_id(self) -> None:
        requests: list[httpx.Request] = []

        def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(202, json={"operation_id": "op-1"})

        http_client = httpx.Client(transport=httpx.MockTransport(handle))
        self.addCleanup(http_client.close)
        client = Ibee(token="test", httpx_client=http_client)

        client.cloud_vms.create_cloud_vm(
            workspace_id="973318",
            idempotency_key="cloud-default-placement",
            name="web",
            plan_id="shared-2x4",
            template_id="ubuntu-24-04",
            os_distro="ubuntu",
            os_type="linux",
            cpu=2,
            ram_mb=4096,
        )
        client.gpu_vms.create_gpu_vm(
            workspace_id="973318",
            idempotency_key="gpu-explicit-placement",
            name="trainer",
            plan_id="gpu-a100-1x",
            template_id="ubuntu-24-04-cuda",
            os_distro="ubuntu",
            os_type="linux",
            cpu=8,
            ram_mb=32768,
            gpu_count=1,
            gpu_model="A100",
            site_id="site-in-south-1",
        )

        self.assertNotIn("site_id", json.loads(requests[0].content))
        self.assertEqual(json.loads(requests[1].content)["site_id"], "site-in-south-1")


class AsyncVmPlacementTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_vm_clients_omit_or_send_site_id(self) -> None:
        requests: list[httpx.Request] = []

        async def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(202, json={"operation_id": "op-1"})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http_client:
            client = AsyncIbee(token="test", httpx_client=http_client)
            await client.gpu_vms.create_gpu_vm(
                workspace_id="973318",
                idempotency_key="gpu-default-placement",
                name="trainer",
                plan_id="gpu-a100-1x",
                template_id="ubuntu-24-04-cuda",
                os_distro="ubuntu",
                os_type="linux",
                cpu=8,
                ram_mb=32768,
                gpu_count=1,
                gpu_model="A100",
            )
            await client.cloud_vms.create_cloud_vm(
                workspace_id="973318",
                idempotency_key="cloud-explicit-placement",
                name="web",
                plan_id="shared-2x4",
                template_id="ubuntu-24-04",
                os_distro="ubuntu",
                os_type="linux",
                cpu=2,
                ram_mb=4096,
                site_id="site-in-south-1",
            )

        self.assertNotIn("site_id", json.loads(requests[0].content))
        self.assertEqual(json.loads(requests[1].content)["site_id"], "site-in-south-1")


if __name__ == "__main__":
    unittest.main()
