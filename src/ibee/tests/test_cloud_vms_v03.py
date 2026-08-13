from __future__ import annotations

import json

import httpx
import pytest

from ibee import Ibee
from ibee.errors import ForbiddenError, NotFoundError


def _plan_list() -> dict[str, object]:
    return {
        "plans": [
            {
                "plan_id": "plan-1",
                "vm_type": "cloud",
                "name": "Standard",
                "code": "STANDARD-2-8-50",
                "cpu": 2,
                "ram_mb": 4096,
                "disk_gb": 50,
                "gpu_count": 0,
                "selectable": True,
                "pricing_status": "priced",
                "currency": "INR",
                "billing_interval": "MONTHLY",
                "monthly_price_minor": 12500,
            }
        ],
        "count": 1,
        "vm_type": "cloud",
        "currency": "INR",
        "billing_interval": "MONTHLY",
    }


def _billing_decision() -> dict[str, object]:
    return {
        "organization_id": "organization-1",
        "allowed": True,
        "reason": "eligible",
        "billing_mode": "PREPAID",
        "billing_state": "CURRENT",
        "sku_code": "STANDARD-2-8-50",
        "estimated_cost_minor": 12500,
        "evaluated_at": "2026-08-04T10:00:00Z",
    }


def test_cloud_vm_create_omits_site_for_automatic_placement() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        if request.url.path.endswith("/compute/plans"):
            return httpx.Response(200, json=_plan_list(), request=request)
        if request.url.path.endswith("/billing/resource-eligibility"):
            return httpx.Response(200, json=_billing_decision(), request=request)
        return httpx.Response(
            202,
            json={
                "operation_id": "op-1",
                "vm_id": "vm-1",
                "status": "accepted",
                "submitted_at": "2026-08-04T10:00:00Z",
            },
            request=request,
        )

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    client.cloud_vms.create_cloud_vm(
        workspace_id="710995",
        idempotency_key="automatic-placement",
        name="web-automatic",
        os_distro="ubuntu",
        os_type="linux",
        template_id="template-1",
        cpu=2,
        ram_mb=4096,
        plan_id="plan-1",
    )

    assert "site_id" not in json.loads(observed[2].content)
    assert observed[2].headers["x-idempotency-key"] == "automatic-placement"


def test_cloud_vm_lifecycle_paths_tenant_scope_and_idempotency() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        path = request.url.path
        if path.endswith("/compute/plans"):
            payload: object = _plan_list()
        elif path.endswith("/billing/resource-eligibility"):
            payload = _billing_decision()
        elif request.method == "GET" and path.endswith("/cloud-vms"):
            payload: object = []
        elif request.method == "GET" and path.endswith("/metrics"):
            payload = {
                "vm_id": "vm-1",
                "vm_type": "cloud",
                "power_state": "running",
                "monitoring_status": "active",
                "month_rx_bytes": 0,
                "month_tx_bytes": 0,
            }
        elif request.method == "GET" and "/operations/" in path:
            payload = {
                "operation_id": "op-1",
                "vm_id": "vm-1",
                "action": "create",
                "status": "succeeded",
                "submitted_at": "2026-08-04T10:00:00Z",
                "updated_at": "2026-08-04T10:00:01Z",
            }
        elif request.method == "GET":
            payload = {"id": "vm-1", "name": "web-1", "status": "running"}
        else:
            payload = {
                "operation_id": "op-1",
                "vm_id": "vm-1",
                "status": "accepted",
                "submitted_at": "2026-08-04T10:00:00Z",
            }
        return httpx.Response(200, json=payload, request=request)

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    client.cloud_vms.list_cloud_vms(workspace_id="710995")
    client.cloud_vms.create_cloud_vm(
        workspace_id="710995",
        idempotency_key="create-key",
        name="web-1",
        site_id="site-1",
        os_distro="ubuntu",
        os_type="linux",
        template_id="template-1",
        cpu=2,
        ram_mb=4096,
        plan_id="plan-1",
    )
    client.cloud_vms.get_cloud_vm("vm-1", workspace_id="710995")
    client.cloud_vms.start_cloud_vm(
        "vm-1", workspace_id="710995", idempotency_key="start-key"
    )
    client.cloud_vms.stop_cloud_vm(
        "vm-1", workspace_id="710995", idempotency_key="stop-key", force=True
    )
    client.cloud_vms.reboot_cloud_vm(
        "vm-1", workspace_id="710995", idempotency_key="reboot-key"
    )
    client.cloud_vms.get_cloud_vm_metrics("vm-1", workspace_id="710995")
    operation = client.cloud_vms.get_compute_operation("op-1", workspace_id="710995")
    client.cloud_vms.delete_cloud_vm(
        "vm-1", workspace_id="710995", idempotency_key="delete-key"
    )

    assert [request.url.path for request in observed] == [
        "/v1/compute/cloud-vms",
        "/v1/compute/plans",
        "/v1/billing/resource-eligibility",
        "/v1/compute/cloud-vms",
        "/v1/compute/cloud-vms/vm-1",
        "/v1/compute/cloud-vms/vm-1/actions/start",
        "/v1/compute/cloud-vms/vm-1/actions/stop",
        "/v1/compute/cloud-vms/vm-1/actions/reboot",
        "/v1/compute/cloud-vms/vm-1/metrics",
        "/v1/compute/operations/op-1",
        "/v1/compute/cloud-vms/vm-1",
    ]
    assert all(request.url.params["workspace_id"] == "710995" for request in observed)
    assert observed[3].headers["x-idempotency-key"] == "create-key"
    assert observed[5].headers["x-idempotency-key"] == "start-key"
    assert observed[6].headers["x-idempotency-key"] == "stop-key"
    assert observed[7].headers["x-idempotency-key"] == "reboot-key"
    assert observed[10].headers["x-idempotency-key"] == "delete-key"
    create_body = json.loads(observed[3].content)
    assert create_body["site_id"] == "site-1"
    assert create_body["plan_id"] == "plan-1"
    assert json.loads(observed[6].content) == {"force": True}
    assert operation.action == "create"
    assert operation.status == "succeeded"


@pytest.mark.parametrize(
    ("status_code", "method", "expected_error"),
    [
        (403, "list", ForbiddenError),
        (404, "get", NotFoundError),
    ],
)
def test_cloud_vm_common_api_errors_are_typed(
    status_code: int,
    method: str,
    expected_error: type[Exception],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"}, request=request)

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(expected_error):
        if method == "list":
            client.cloud_vms.list_cloud_vms(workspace_id="710995")
        else:
            client.cloud_vms.get_cloud_vm("vm-1", workspace_id="710995")
