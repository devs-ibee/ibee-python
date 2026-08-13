from __future__ import annotations

import asyncio
import typing

import httpx
import pytest

from ibee import AsyncIbee, Ibee, IbeeEnvironment, LoadBalancerBackend
from ibee.core.api_error import ApiError

WORKSPACE_ID = "710995"
OperationName = typing.Literal[
    "secret-store", "secret", "bucket", "s3-credential", "nat-gateway",
    "reserved-ip", "l4-load-balancer", "l7-load-balancer", "cloud-vm", "gpu-vm",
]
OPERATIONS: list[OperationName] = [
    "secret-store", "secret", "bucket", "s3-credential", "nat-gateway",
    "reserved-ip", "l4-load-balancer", "l7-load-balancer", "cloud-vm", "gpu-vm",
]


def _sync(client: Ibee, name: OperationName) -> object:
    if name == "secret-store": return client.secret_store.create_secret_store(workspace_id=WORKSPACE_ID, name="production")
    if name == "secret": return client.secret_store.create_secret("store-1", workspace_id=WORKSPACE_ID, secret_name="database-url", value={"url": "secret"})
    if name == "bucket": return client.object_storage.create_bucket(workspace_id=WORKSPACE_ID, name="assets", region="in-south-1")
    if name == "s3-credential": return client.object_storage.create_s3credential(workspace_id=WORKSPACE_ID, name="application")
    if name == "nat-gateway": return client.vpcs.create_nat_gateway("vpc-1", workspace_id=WORKSPACE_ID)
    if name == "reserved-ip": return client.reserved_ips.reserve_ip(workspace_id=WORKSPACE_ID, site_id="site-1")
    if name == "l4-load-balancer": return client.load_balancers.create_l4load_balancer(workspace_id=WORKSPACE_ID, name="tcp", protocol="tcp", backends=[LoadBalancerBackend(target="10.0.0.10", port=80)])
    if name == "l7-load-balancer": return client.load_balancers.create_l7load_balancer(workspace_id=WORKSPACE_ID, name="http", protocol="http", backends=[LoadBalancerBackend(target="10.0.0.10", port=80)])
    common = dict(workspace_id=WORKSPACE_ID, idempotency_key="create-1", name="vm", site_id="site-1", os_distro="ubuntu", os_type="linux", template_id="template-1", cpu=2, ram_mb=8192, plan_id="plan-1")
    if name == "cloud-vm": return client.cloud_vms.create_cloud_vm(**common)
    return client.gpu_vms.create_gpu_vm(**common, gpu_count=1, gpu_model="L4")


async def _async(client: AsyncIbee, name: OperationName) -> object:
    if name == "secret-store": return await client.secret_store.create_secret_store(workspace_id=WORKSPACE_ID, name="production")
    if name == "secret": return await client.secret_store.create_secret("store-1", workspace_id=WORKSPACE_ID, secret_name="database-url", value={"url": "secret"})
    if name == "bucket": return await client.object_storage.create_bucket(workspace_id=WORKSPACE_ID, name="assets", region="in-south-1")
    if name == "s3-credential": return await client.object_storage.create_s3credential(workspace_id=WORKSPACE_ID, name="application")
    if name == "nat-gateway": return await client.vpcs.create_nat_gateway("vpc-1", workspace_id=WORKSPACE_ID)
    if name == "reserved-ip": return await client.reserved_ips.reserve_ip(workspace_id=WORKSPACE_ID, site_id="site-1")
    if name == "l4-load-balancer": return await client.load_balancers.create_l4load_balancer(workspace_id=WORKSPACE_ID, name="tcp", protocol="tcp", backends=[LoadBalancerBackend(target="10.0.0.10", port=80)])
    if name == "l7-load-balancer": return await client.load_balancers.create_l7load_balancer(workspace_id=WORKSPACE_ID, name="http", protocol="http", backends=[LoadBalancerBackend(target="10.0.0.10", port=80)])
    common = dict(workspace_id=WORKSPACE_ID, idempotency_key="create-1", name="vm", site_id="site-1", os_distro="ubuntu", os_type="linux", template_id="template-1", cpu=2, ram_mb=8192, plan_id="plan-1")
    if name == "cloud-vm": return await client.cloud_vms.create_cloud_vm(**common)
    return await client.gpu_vms.create_gpu_vm(**common, gpu_count=1, gpu_model="L4")


def _failure(request: httpx.Request) -> httpx.Response:
    # Use a non-retryable response so this test measures the helper's logical
    # call count; transport retry behavior has separate coverage/configuration.
    return httpx.Response(418, json={"detail": "product response"}, request=request)


@pytest.mark.parametrize("name", OPERATIONS)
def test_sync_create_is_exactly_one_product_request(name: OperationName) -> None:
    seen: list[httpx.Request] = []
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request); return _failure(request)
    client = Ibee(token="test", base_url="https://api.example.test/v1", httpx_client=httpx.Client(transport=httpx.MockTransport(handler)))
    with pytest.raises(ApiError): _sync(client, name)
    assert len(seen) == 1
    assert seen[0].method == "POST"
    assert seen[0].url.params["workspace_id"] == WORKSPACE_ID
    assert "/billing/resource-eligibility" not in seen[0].url.path
    assert "/compute/plans" not in seen[0].url.path


@pytest.mark.parametrize("name", OPERATIONS)
def test_async_create_is_exactly_one_product_request(name: OperationName) -> None:
    seen: list[httpx.Request] = []
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request); return _failure(request)
    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            client = AsyncIbee(token="test", base_url="https://api.example.test/v1", httpx_client=http)
            with pytest.raises(ApiError): await _async(client, name)
    asyncio.run(run())
    assert len(seen) == 1
    assert seen[0].method == "POST"
    assert seen[0].url.params["workspace_id"] == WORKSPACE_ID
    assert "/billing/resource-eligibility" not in seen[0].url.path
    assert "/compute/plans" not in seen[0].url.path


def test_production_environment_alias() -> None:
    assert IbeeEnvironment.PRODUCTION is IbeeEnvironment.DEFAULT
