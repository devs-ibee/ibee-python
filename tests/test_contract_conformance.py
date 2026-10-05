"""Contract conformance against the optional, shared platform policy fixtures."""

import asyncio
import json
import os
from pathlib import Path

import httpx
import pytest

from ibee import AsyncIbee, Ibee
from ibee.core.api_error import ApiError


def _cases():
    path = os.environ.get("IBEE_CONFORMANCE_FIXTURES")
    if path is None:
        return [pytest.param(None, marks=pytest.mark.skip(reason="IBEE_CONFORMANCE_FIXTURES is unset"))]
    # An explicitly configured missing/invalid file must fail collection, never skip.
    fixture = json.loads(Path(path).read_text(encoding="utf-8"))
    assert fixture["version"] == 1
    assert fixture["cases"], "conformance fixture must contain cases"
    return [pytest.param(case, id=case["name"]) for case in fixture["cases"]]


@pytest.mark.parametrize("case", _cases())
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_shared_policy_transport_conformance(case, asynchronous):
    calls = []
    response_headers = {"Retry-After": "0"}
    if "request_id" in case:
        response_headers["X-Request-ID"] = case["request_id"]

    def handler(request):
        calls.append(request)
        return httpx.Response(case["status"], json=case["response"], headers=response_headers)

    options = {
        "method": case["method"],
        "path": case["path"].lstrip("/"),
        "params": {"workspace_id": "710995"},
        "headers": case.get("headers", {}),
        "json": {} if case["method"] != "GET" else None,
    }

    def invoke():
        if asynchronous:
            async def run():
                async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as transport:
                    client = AsyncIbee(token="fixture", base_url="https://api.example.test/v1",
                                       httpx_client=transport, max_retries=3)
                    return await client._client_wrapper.httpx_client.request(**options)
            return asyncio.run(run())
        with httpx.Client(transport=httpx.MockTransport(handler)) as transport:
            client = Ibee(token="fixture", base_url="https://api.example.test/v1",
                          httpx_client=transport, max_retries=3)
            return client._client_wrapper.httpx_client.request(**options)

    with pytest.raises(ApiError) as caught:
        invoke()
    error = caught.value
    assert error.status_code == case["status"]
    assert error.raw_body == case["response"]
    assert error.request_id == case.get("request_id")
    response = case["response"]
    if isinstance(response.get("error"), str):
        assert error.code == response["error"].strip().lower()
        assert error.raw_code == response["error"]
    if "billing_reason" in response:
        assert error.reason == response["billing_reason"]
    if "admission_context_id" in response:
        assert error.admission_context_id == response["admission_context_id"]
    if "billing_sku_code" in response:
        assert error.billing_sku_code == response["billing_sku_code"]
    assert len(calls) == case["attempts"]
    for request in calls:
        # Every attempt is the original request; no billing diagnostic is inserted.
        assert request.method == case["method"]
        assert request.url.path == "/v1" + case["path"]
        assert dict(request.url.params) == {"workspace_id": "710995"}
        for name, value in case.get("headers", {}).items():
            assert request.headers[name] == value
        assert request.content == calls[0].content
