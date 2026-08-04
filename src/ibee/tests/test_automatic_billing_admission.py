from __future__ import annotations

import asyncio
import json
import typing

import httpx
import pytest

from ibee import AsyncIbee, BillingEligibilityError, Ibee, IbeeEnvironment, LoadBalancerBackend
from ibee.core.api_error import ApiError

WORKSPACE_ID = "workspace-1"

OperationName = typing.Literal[
    "secret-store",
    "secret",
    "bucket",
    "s3-credential",
    "nat-gateway",
    "reserved-ip",
    "l4-load-balancer",
    "l7-load-balancer",
    "cloud-vm",
    "gpu-vm",
]

OPERATIONS: list[tuple[OperationName, str | None]] = [
    ("secret-store", "SECRETMA-STD"),
    ("secret", "SECRETMA-STD"),
    ("bucket", "OBJECTST-STD"),
    ("s3-credential", "OBJECTST-STD"),
    ("nat-gateway", None),
    ("reserved-ip", None),
    ("l4-load-balancer", "LOADBALA-STD"),
    ("l7-load-balancer", "LOADBALA-STD"),
    ("cloud-vm", "STANDARD-2-8-50"),
    ("gpu-vm", "GPU-L4-1-16-64-300"),
]


def _plan_list(name: OperationName) -> dict[str, object]:
    gpu = name == "gpu-vm"
    return {
        "plans": [
            {
                "plan_id": "plan-1",
                "vm_type": "gpu" if gpu else "cloud",
                "name": "Test plan",
                "code": "GPU-L4-1-16-64-300" if gpu else "STANDARD-2-8-50",
                "cpu": 2,
                "ram_mb": 8192,
                "disk_gb": 50,
                "gpu_count": 1 if gpu else 0,
                "gpu_model": "L4" if gpu else None,
                "selectable": True,
                "pricing_status": "priced",
                "currency": "INR",
                "billing_interval": "MONTHLY",
                "monthly_price_minor": 12500,
            }
        ],
        "count": 1,
        "vm_type": "gpu" if gpu else "cloud",
        "currency": "INR",
        "billing_interval": "MONTHLY",
    }


def _decision(*, allowed: bool, sku_code: str | None) -> dict[str, object]:
    return {
        "organization_id": "organization-1",
        "allowed": allowed,
        "reason": "eligible" if allowed else "insufficient_balance",
        "billing_mode": "PREPAID",
        "billing_state": "CURRENT",
        "currency": "INR",
        "sku_code": sku_code,
        "estimated_cost_minor": 12500 if sku_code else None,
        "evaluated_at": "2026-08-04T10:00:00Z",
    }


def _invoke_sync(client: Ibee, name: OperationName) -> object:
    if name == "secret-store":
        return client.secret_store.create_secret_store(workspace_id=WORKSPACE_ID, name="production")
    if name == "secret":
        return client.secret_store.create_secret(
            "store-1", workspace_id=WORKSPACE_ID, secret_name="database-url", value={"url": "secret"}
        )
    if name == "bucket":
        return client.object_storage.create_bucket(workspace_id=WORKSPACE_ID, name="assets")
    if name == "s3-credential":
        return client.object_storage.create_s3credential(workspace_id=WORKSPACE_ID, name="application")
    if name == "nat-gateway":
        return client.vpcs.create_nat_gateway("vpc-1", workspace_id=WORKSPACE_ID)
    if name == "reserved-ip":
        return client.reserved_ips.reserve_ip(workspace_id=WORKSPACE_ID, site_id="site-1")
    if name == "l4-load-balancer":
        return client.load_balancers.create_l4load_balancer(
            workspace_id=WORKSPACE_ID,
            name="tcp",
            protocol="tcp",
            backends=[LoadBalancerBackend(target="10.0.0.10", port=80)],
        )
    if name == "l7-load-balancer":
        return client.load_balancers.create_l7load_balancer(
            workspace_id=WORKSPACE_ID,
            name="http",
            protocol="http",
            backends=[LoadBalancerBackend(target="10.0.0.10", port=80)],
        )
    if name == "cloud-vm":
        return client.cloud_vms.create_cloud_vm(
            workspace_id=WORKSPACE_ID,
            idempotency_key="cloud-create-1",
            name="cloud",
            site_id="site-1",
            os_distro="ubuntu",
            os_type="linux",
            template_id="template-1",
            cpu=2,
            ram_mb=8192,
            plan_id="plan-1",
        )
    return client.gpu_vms.create_gpu_vm(
        workspace_id=WORKSPACE_ID,
        idempotency_key="gpu-create-1",
        name="gpu",
        site_id="site-1",
        os_distro="ubuntu",
        os_type="linux",
        template_id="template-1",
        cpu=2,
        ram_mb=8192,
        gpu_count=1,
        gpu_model="L4",
        plan_id="plan-1",
    )


async def _invoke_async(client: AsyncIbee, name: OperationName) -> object:
    if name == "secret-store":
        return await client.secret_store.create_secret_store(workspace_id=WORKSPACE_ID, name="production")
    if name == "secret":
        return await client.secret_store.create_secret(
            "store-1", workspace_id=WORKSPACE_ID, secret_name="database-url", value={"url": "secret"}
        )
    if name == "bucket":
        return await client.object_storage.create_bucket(workspace_id=WORKSPACE_ID, name="assets")
    if name == "s3-credential":
        return await client.object_storage.create_s3credential(workspace_id=WORKSPACE_ID, name="application")
    if name == "nat-gateway":
        return await client.vpcs.create_nat_gateway("vpc-1", workspace_id=WORKSPACE_ID)
    if name == "reserved-ip":
        return await client.reserved_ips.reserve_ip(workspace_id=WORKSPACE_ID, site_id="site-1")
    if name == "l4-load-balancer":
        return await client.load_balancers.create_l4load_balancer(
            workspace_id=WORKSPACE_ID,
            name="tcp",
            protocol="tcp",
            backends=[LoadBalancerBackend(target="10.0.0.10", port=80)],
        )
    if name == "l7-load-balancer":
        return await client.load_balancers.create_l7load_balancer(
            workspace_id=WORKSPACE_ID,
            name="http",
            protocol="http",
            backends=[LoadBalancerBackend(target="10.0.0.10", port=80)],
        )
    if name == "cloud-vm":
        return await client.cloud_vms.create_cloud_vm(
            workspace_id=WORKSPACE_ID,
            idempotency_key="cloud-create-1",
            name="cloud",
            site_id="site-1",
            os_distro="ubuntu",
            os_type="linux",
            template_id="template-1",
            cpu=2,
            ram_mb=8192,
            plan_id="plan-1",
        )
    return await client.gpu_vms.create_gpu_vm(
        workspace_id=WORKSPACE_ID,
        idempotency_key="gpu-create-1",
        name="gpu",
        site_id="site-1",
        os_distro="ubuntu",
        os_type="linux",
        template_id="template-1",
        cpu=2,
        ram_mb=8192,
        gpu_count=1,
        gpu_model="L4",
        plan_id="plan-1",
    )


def _denial_handler(name: OperationName, sku_code: str | None, observed: list[httpx.Request]):
    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        if request.url.path.endswith("/compute/plans"):
            return httpx.Response(200, json=_plan_list(name), request=request)
        if request.url.path.endswith("/billing/resource-eligibility"):
            return httpx.Response(200, json=_decision(allowed=False, sku_code=sku_code), request=request)
        return httpx.Response(500, json={"detail": "resource POST must not run"}, request=request)

    return handler


@pytest.mark.parametrize(("name", "sku_code"), OPERATIONS)
def test_every_sync_billable_create_stops_before_resource_post_when_billing_denies(
    name: OperationName,
    sku_code: str | None,
) -> None:
    observed: list[httpx.Request] = []
    handler = _denial_handler(name, sku_code, observed)
    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(BillingEligibilityError) as exc_info:
        _invoke_sync(client, name)

    assert exc_info.value.status_code == 402
    billing_requests = [request for request in observed if request.url.path.endswith("/billing/resource-eligibility")]
    assert len(billing_requests) == 1
    if name in {"cloud-vm", "gpu-vm"}:
        expected_body = {"sku_code": sku_code, "estimated_cost_minor": 12500}
    elif sku_code:
        expected_body = {"sku_code": sku_code}
    else:
        expected_body = {}
    assert json.loads(billing_requests[0].content) == expected_body
    assert not [
        request
        for request in observed
        if request.method == "POST" and not request.url.path.endswith("/billing/resource-eligibility")
    ]


@pytest.mark.parametrize(("name", "sku_code"), OPERATIONS)
def test_every_async_billable_create_stops_before_resource_post_when_billing_denies(
    name: OperationName,
    sku_code: str | None,
) -> None:
    observed: list[httpx.Request] = []
    handler = _denial_handler(name, sku_code, observed)

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            client = AsyncIbee(
                token="test-token",
                base_url="https://api.example.test/v1",
                httpx_client=http_client,
            )
            with pytest.raises(BillingEligibilityError) as exc_info:
                await _invoke_async(client, name)
            assert exc_info.value.status_code == 402

    asyncio.run(run())

    assert not [
        request
        for request in observed
        if request.method == "POST" and not request.url.path.endswith("/billing/resource-eligibility")
    ]


@pytest.mark.parametrize(
    "decision",
    [
        _decision(allowed=True, sku_code="WRONG-SKU"),
        {**_decision(allowed=True, sku_code="OBJECTST-STD"), "evaluated_at": None},
    ],
)
def test_allowed_but_unconfirmed_billing_decision_fails_closed(decision: dict[str, object]) -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json=decision, request=request)

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(BillingEligibilityError) as exc_info:
        client.object_storage.create_bucket(workspace_id=WORKSPACE_ID, name="assets")

    assert exc_info.value.status_code == 503
    assert len(observed) == 1


def test_unavailable_billing_preflight_fails_closed_before_resource_post() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(404, json={"detail": "not found"}, request=request)

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(ApiError):
        client.object_storage.create_bucket(workspace_id=WORKSPACE_ID, name="assets")
    assert len(observed) == 1
    assert observed[0].url.path.endswith("/billing/resource-eligibility")


def test_unknown_compute_plan_fails_before_billing_or_create() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(
            200,
            json={**_plan_list("cloud-vm"), "plans": []},
            request=request,
        )

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(BillingEligibilityError, match="unavailable"):
        _invoke_sync(client, "cloud-vm")
    assert [request.url.path for request in observed] == ["/v1/compute/plans"]


def test_compute_billing_must_confirm_the_catalog_price() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        if request.url.path.endswith("/compute/plans"):
            return httpx.Response(200, json=_plan_list("cloud-vm"), request=request)
        return httpx.Response(
            200,
            json={
                **_decision(allowed=True, sku_code="STANDARD-2-8-50"),
                "estimated_cost_minor": 999,
            },
            request=request,
        )

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(BillingEligibilityError, match="catalog price"):
        _invoke_sync(client, "cloud-vm")
    assert [request.url.path for request in observed] == [
        "/v1/compute/plans",
        "/v1/billing/resource-eligibility",
    ]


def test_production_environment_is_a_backward_compatible_default_alias() -> None:
    assert IbeeEnvironment.PRODUCTION is IbeeEnvironment.DEFAULT
    assert IbeeEnvironment.PRODUCTION.value == "https://api.ibee.ai/v1"
    assert IbeeEnvironment.DEVELOPMENT.value == "https://api.ibee.co.in/v1"
