"""Shared policy cases through supported public methods, sync and async.

The fixture's illustrative vm-1 is replaced with a valid public VM identifier.
The future-product route intentionally has no public SDK method; transport
conformance covers that case separately.
"""

import asyncio
import json
import os
from pathlib import Path

import httpx
import pytest

from ibee import AsyncIbee, Ibee
from ibee.core.api_error import ApiError

WS = "710995"
VM = "0123456789abcdef01234567"
ACCEPTED = {"operation_id": "op_0123456789abcdef01234567", "vm_id": VM,
            "status": "accepted", "submitted_at": "2026-10-04T00:00:00Z"}


def cases():
    path = os.environ.get("IBEE_CONFORMANCE_FIXTURES")
    if path is None:
        return [pytest.param(None, marks=pytest.mark.skip(reason="IBEE_CONFORMANCE_FIXTURES is unset"))]
    fixture = json.loads(Path(path).read_text())
    assert fixture["version"] == 1 and fixture["cases"]
    return [pytest.param(case, id=case["name"]) for case in fixture["cases"]]


def invoke(client, case):
    key = case.get("headers", {}).get("X-Idempotency-Key")
    path = case["path"]
    if path.endswith("/actions/start"):
        return client.cloud_vms.start_cloud_vm(VM, workspace_id=WS, idempotency_key=key)
    if case["method"] == "GET" and path == "/compute/cloud-vms":
        return client.cloud_vms.list_cloud_vms(workspace_id=WS, limit=10)
    if path == "/secret-store/identities/id-1/access":
        return client.secret_store.get_secret_identity_access("id-1", workspace_id=WS)
    if case["method"] == "POST" and path in ("/compute/cloud-vms", "/compute/gpu-vms"):
        args = dict(workspace_id=WS, idempotency_key=key, name="fixture-vm", site_id="site-1",
                    plan_id="plan-1", template_id="image-1", cpu=2, ram_mb=8192, disk_gb=50,
                    os_type="linux", os_distro="ubuntu", preflight_billing=True,
                    billing_catalog={"sku_id": 11, "sku_code": "STANDARD-2-8-50"})
        if path == "/compute/gpu-vms":
            return client.gpu_vms.create_gpu_vm(**args, gpu_count=1, gpu_model="L4")
        return client.cloud_vms.create_cloud_vm(**args)
    raise AssertionError(f"unmapped public fixture: {case['name']}")


@pytest.mark.parametrize("case", cases())
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_public_policy_conformance(case, asynchronous):
    if case["path"] == "/future-product/resources":
        pytest.skip("future-product has no public method; covered by transport conformance")
    calls = []
    headers = {"Retry-After": "0"}
    if "request_id" in case:
        headers["X-Request-ID"] = case["request_id"]

    def handler(request):
        calls.append(request)
        return httpx.Response(case["status"], json=case["response"], headers=headers)

    def run():
        if asynchronous:
            async def execute():
                async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
                    return await invoke(AsyncIbee(token="fixture", base_url="https://fixture.test/v1",
                                                  httpx_client=http, max_retries=3), case)
            return asyncio.run(execute())
        with httpx.Client(transport=httpx.MockTransport(handler)) as http:
            return invoke(Ibee(token="fixture", base_url="https://fixture.test/v1",
                               httpx_client=http, max_retries=3), case)

    with pytest.raises(ApiError) as caught:
        run()
    error = caught.value
    assert error.status_code == case["status"]
    assert error.raw_body == case["response"]
    assert error.request_id == case.get("request_id")
    for source, attr in (("error", "raw_code"), ("billing_reason", "reason"),
                         ("billing_sku_code", "billing_sku_code"), ("admission_context_id", "admission_context_id")):
        if source in case["response"]:
            assert getattr(error, attr) == case["response"][source]
    assert len(calls) == case["attempts"]
    for request in calls:
        assert request.method == case["method"]
        assert request.url.path == "/v1" + case["path"].replace("vm-1", VM)
        assert request.url.params["workspace_id"] == WS
        assert request.headers["Authorization"] == "Bearer fixture"
        for name, value in case.get("headers", {}).items():
            assert request.headers[name] == value
        assert request.content == calls[0].content
    if case["path"] in ("/compute/cloud-vms", "/compute/gpu-vms") and case["method"] == "POST":
        assert json.loads(calls[0].content)["billing_catalog"]["sku_code"] == "STANDARD-2-8-50"


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_public_action_recovers_with_same_generated_key(asynchronous):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(503 if len(calls) == 1 else 202,
                              json={"detail": "busy"} if len(calls) == 1 else ACCEPTED,
                              headers={"Retry-After": "0"})

    if asynchronous:
        async def execute():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
                client = AsyncIbee(token="fixture", httpx_client=http)
                return await client.cloud_vms.start_cloud_vm(VM, workspace_id=WS)
        result = asyncio.run(execute())
    else:
        with httpx.Client(transport=httpx.MockTransport(handler)) as http:
            result = Ibee(token="fixture", httpx_client=http).cloud_vms.start_cloud_vm(VM, workspace_id=WS)
    assert result.operation_id == ACCEPTED["operation_id"]
    assert len(calls) == 2
    assert calls[0].headers["X-Idempotency-Key"]
    assert calls[0].headers["X-Idempotency-Key"] == calls[1].headers["X-Idempotency-Key"]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("currency", [None, "USD", "INR"])
def test_public_catalog_currency(asynchronous, currency):
    calls = []
    payload = {"plans": [], "count": 0, "vm_type": "cloud", "currency": "USD", "billing_interval": "HOURLY"}
    mismatch = {"detail": "Currency must match organization profile currency"}

    def handler(request):
        calls.append(request)
        return httpx.Response(400 if currency == "INR" else 200, json=mismatch if currency == "INR" else payload)

    args = {"workspace_id": WS, "vm_type": "cloud"}
    if currency is not None:
        args["currency"] = currency

    def run():
        if asynchronous:
            async def execute():
                async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
                    return await AsyncIbee(token="fixture", httpx_client=http).compute_catalog.list_compute_plans(**args)
            return asyncio.run(execute())
        with httpx.Client(transport=httpx.MockTransport(handler)) as http:
            return Ibee(token="fixture", httpx_client=http).compute_catalog.list_compute_plans(**args)

    if currency == "INR":
        with pytest.raises(ApiError) as caught:
            run()
        assert caught.value.status_code == 400
        assert caught.value.raw_body == mismatch
    else:
        assert run().currency == "USD"
    assert len(calls) == 1
    assert calls[0].url.path == "/v1/compute/plans"
    assert dict(calls[0].url.params) == args
