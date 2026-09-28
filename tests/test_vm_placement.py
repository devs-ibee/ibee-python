"""Request-shape tests for VM placement (site_id is required since 0.4.0)."""

from __future__ import annotations

import json
import unittest

import httpx

from ibee import AsyncIbee, Ibee, IbeeValidationError


def response_for(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/v1/compute/plans":
        vm_type = request.url.params["vm_type"]
        plan_id = "gpu-a100-1x" if vm_type == "gpu" else "shared-2x4"
        return httpx.Response(
            200,
            json={
                "plans": [
                    {
                        "plan_id": plan_id,
                        "vm_type": vm_type,
                        "name": plan_id,
                        "code": "VM-PLAN",
                        "cpu": 2,
                        "ram_mb": 4096,
                        "disk_gb": 40,
                        "gpu_count": 1 if vm_type == "gpu" else 0,
                        "selectable": True,
                        "pricing_status": "priced",
                        "currency": "INR",
                        "billing_interval": "HOURLY",
                        "hourly_price_minor": 100,
                        "gpu_model": "A100" if vm_type == "gpu" else None,
                        "billing_catalog": {"sku_id": 3, "sku_code": "VM-PLAN"},
                    }
                ],
                "count": 1,
                "vm_type": vm_type,
                "currency": "INR",
                "billing_interval": "HOURLY",
            },
        )
    if request.url.path == "/v1/compute/images":
        vm_type = request.url.params["vm_type"]
        template = "ubuntu-24-04-cuda" if vm_type == "gpu" else "ubuntu-24-04"
        return httpx.Response(
            200,
            json={"images": [{"template_id": template, "os_type": "linux", "os_distro": "ubuntu", "compatible_vm_types": [vm_type], "site_ids": []}]},
        )
    if request.url.path == "/v1/billing/resource-eligibility":
        body = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "organization_id": "org-1",
                "allowed": True,
                "reason": "eligible",
                "billing_mode": "PREPAID",
                "billing_state": "CURRENT",
                "sku_code": body["sku_code"],
                "estimated_cost_minor": body["estimated_cost_minor"],
                "evaluated_at": "2026-08-13T00:00:00Z",
            },
        )
    return httpx.Response(
        202,
        json={
            "operation_id": "op-1",
            "vm_id": "vm-1",
            "status": "accepted",
            "submitted_at": "2026-08-13T00:00:00Z",
        },
    )


class VmPlacementTests(unittest.TestCase):
    def test_sync_vm_clients_require_and_send_site_id(self) -> None:
        requests: list[httpx.Request] = []

        def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return response_for(request)

        http_client = httpx.Client(transport=httpx.MockTransport(handle))
        self.addCleanup(http_client.close)
        client = Ibee(token="test", httpx_client=http_client)

        with self.assertRaises(IbeeValidationError):
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
        self.assertEqual(requests, [])
        client.gpu_vms.create_gpu_vm(
            workspace_id="973318",
            idempotency_key="gpu-explicit-placement",
            name="trainer",
            plan_id="gpu-a100-1x",
            template_id="ubuntu-24-04-cuda",
            os_distro="ubuntu",
            os_type="linux",
            gpu_count=1,
            gpu_model="A100",
            site_id="site-in-south-1",
        )

        creates = [
            request
            for request in requests
            if request.url.path in ("/v1/compute/cloud-vms", "/v1/compute/gpu-vms")
        ]
        body = json.loads(creates[0].content)
        self.assertEqual(body["site_id"], "site-in-south-1")
        self.assertEqual((body["cpu"], body["ram_mb"], body["disk_gb"], body["gpu_count"]), (2, 4096, 40, 1))
        self.assertEqual(body["billing_catalog"]["sku_code"], "VM-PLAN")
        plans = [request for request in requests if request.url.path == "/v1/compute/plans"]
        self.assertEqual(plans[0].url.params["site_id"], "site-in-south-1")


class AsyncVmPlacementTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_vm_clients_require_and_send_site_id(self) -> None:
        requests: list[httpx.Request] = []

        async def handle(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return response_for(request)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http_client:
            client = AsyncIbee(token="test", httpx_client=http_client)
            with self.assertRaises(IbeeValidationError):
                await client.gpu_vms.create_gpu_vm(
                    workspace_id="973318",
                    idempotency_key="gpu-default-placement",
                    name="trainer",
                    plan_id="gpu-a100-1x",
                    template_id="ubuntu-24-04-cuda",
                )
            self.assertEqual(requests, [])
            await client.cloud_vms.create_cloud_vm(
                workspace_id="973318",
                idempotency_key="cloud-explicit-placement",
                name="web",
                plan_id="shared-2x4",
                template_id="ubuntu-24-04",
                site_id="site-in-south-1",
            )

        creates = [
            request
            for request in requests
            if request.url.path in ("/v1/compute/cloud-vms", "/v1/compute/gpu-vms")
        ]
        body = json.loads(creates[0].content)
        self.assertEqual(body["site_id"], "site-in-south-1")
        self.assertEqual((body["cpu"], body["ram_mb"], body["disk_gb"], body["os_type"]), (2, 4096, 40, "linux"))


if __name__ == "__main__":
    unittest.main()
