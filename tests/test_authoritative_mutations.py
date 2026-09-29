"""The shared sync/async mutation runner never performs billing admission."""
import asyncio
import httpx
import pytest

from ibee import Ibee, AsyncIbee
from ibee.core.api_error import ApiError
from ibee.compute_workflows import Call, billing_preflight, run_sync, run_async
from ibee.validation import ENFORCEMENT_OPERATIONS


@pytest.mark.parametrize("resource_type", [
    "vm", "gpu_vm", "snapshot", "backup", "block_storage", "object_storage",
    "s3_credential", "cdn", "custom_domain", "secret_store", "secret",
    "reserved_ip", "nat_gateway", "load_balancer",
])
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("status,code", [
    (200, None), (402, "billing_denied"), (403, "organization_restricted"),
    (423, "organization_suspended"), (403, "key_revoked"),
    (403, "workspace_not_allowed"), (403, "insufficient_scope"),
])
def test_shared_preflight_leaves_mutation_response_authoritative(resource_type, asynchronous, status, code):
    calls = []
    payload = {"ok": True} if code is None else {
        "error": code, "message": "upstream decision", "billing_reason": "insufficient_balance",
        "admission_context_id": "adm_upstream", "required_scope": "product.write",
    }

    def handler(request):
        calls.append(request)
        assert request.url.path == "/v1/product/mutation"
        assert request.url.params["workspace_id"] == "710995"
        return httpx.Response(status, json=payload)

    def flow():
        # All billing-enabled product workflows delegate to this compatibility helper.
        yield from billing_preflight("710995", sku_code="SKU", estimated_cost_minor=999999,
                                     resource_type=resource_type)
        return (yield Call("POST", "product/mutation", params={"workspace_id": "710995"},
                           json={"name": "test"}, main=True))

    def invoke():
        if asynchronous:
            async def run():
                async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as transport:
                    client = AsyncIbee(token="fixture", base_url="https://api.example.test/v1", httpx_client=transport)
                    return await run_async(client._client_wrapper, flow())
            return asyncio.run(run())
        with httpx.Client(transport=httpx.MockTransport(handler)) as transport:
            client = Ibee(token="fixture", base_url="https://api.example.test/v1", httpx_client=transport)
            return run_sync(client._client_wrapper, flow())

    if code is None:
        assert invoke() == payload
    else:
        with pytest.raises(ApiError) as caught:
            invoke()
        assert caught.value.status_code == status
        assert caught.value.code == code
        assert caught.value.admission_context_id == "adm_upstream"
    assert len(calls) == 1
    assert "estimated_cost_minor" not in calls[0].content.decode()


@pytest.mark.parametrize("operation", ENFORCEMENT_OPERATIONS)
def test_explicit_eligibility_denial_is_data_for_every_operation(operation):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={"organization_id": "org", "allowed": False,
                                        "reason": "upstream", "operation": operation})
    with httpx.Client(transport=httpx.MockTransport(handler)) as transport:
        client = Ibee(token="fixture", base_url="https://api.example.test/v1", httpx_client=transport)
        result = client.billing.check_resource_eligibility(workspace_id="710995", operation=operation)
    assert result.allowed is False
    assert result.operation == operation
    assert len(calls) == 1
    assert calls[0].url.path == "/v1/billing/resource-eligibility"


@pytest.mark.parametrize("asynchronous", [False, True])
def test_legacy_admission_helpers_are_noops(asynchronous):
    from ibee.billing import admission

    class NoTransport:
        def __getattr__(self, name):
            raise AssertionError("legacy helper attempted a request")

    if asynchronous:
        asyncio.run(admission.enforce_billing_eligibility_async(NoTransport(), workspace_id="710995", sku_code="SKU", estimated_cost_minor=999999))
        asyncio.run(admission.enforce_compute_plan_eligibility_async(NoTransport(), workspace_id="710995", vm_type="cloud", plan_id="plan", site_id="site"))
    else:
        admission.enforce_billing_eligibility(NoTransport(), workspace_id="710995", sku_code="SKU", estimated_cost_minor=999999)
        admission.enforce_compute_plan_eligibility(NoTransport(), workspace_id="710995", vm_type="cloud", plan_id="plan", site_id="site")
