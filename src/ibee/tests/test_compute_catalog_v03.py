from __future__ import annotations

import httpx

from ibee import Ibee


def test_compute_catalog_is_typed_and_sends_canonical_filters() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        if request.url.path.endswith("/plans"):
            payload = {
                "plans": [],
                "count": 0,
                "vm_type": "gpu",
                "site_id": "site1",
                "currency": "INR",
                "billing_interval": "MONTHLY",
            }
        elif request.url.path.endswith("/images"):
            payload = {
                "images": [],
                "count": 0,
                "vm_type": "gpu",
                "site_id": "site1",
            }
        else:
            payload = {
                "sites": [{"site_id": "site1", "name": "Bengaluru"}],
                "count": 1,
            }
        return httpx.Response(200, json=payload, request=request)

    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    sites = client.compute_catalog.list_compute_sites(workspace_id="607005")
    plans = client.compute_catalog.list_compute_plans(
        workspace_id="607005",
        vm_type="gpu",
        site_id="site1",
        currency="INR",
        billing_interval="MONTHLY",
    )
    images = client.compute_catalog.list_compute_images(
        workspace_id="607005",
        vm_type="gpu",
        site_id="site1",
    )

    assert sites.sites[0].site_id == "site1"
    assert plans.vm_type == "gpu"
    assert images.site_id == "site1"
    assert dict(observed[0].url.params) == {"workspace_id": "607005"}
    assert observed[1].url.params["vm_type"] == "gpu"
    assert observed[1].url.params["billing_interval"] == "MONTHLY"
    assert observed[2].url.params["site_id"] == "site1"
