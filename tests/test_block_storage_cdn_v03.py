from __future__ import annotations

import json

import httpx

from ibee import Ibee


def test_block_storage_and_cdn_expose_all_23_new_operations() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json={}, request=request)

    client = Ibee(
        token="test",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    workspace = "710995"
    block = client.block_storage
    block.list_block_volumes(workspace_id=workspace)
    block.create_block_volume(workspace_id=workspace, name="data", size_gb=100,
                              site_id="site-1", sku_code="BLOCKSTO-NVME", resolve_site_name=False)
    block.get_block_volume("64b0000000000000000000b1", workspace_id=workspace)
    block.delete_block_volume("64b0000000000000000000b1", workspace_id=workspace, force=True)
    block.list_block_volume_operations("64b0000000000000000000b1", workspace_id=workspace)
    block.attach_block_volume("64b0000000000000000000b1", workspace_id=workspace, node_name="node-1")
    block.detach_block_volume("64b0000000000000000000b1", workspace_id=workspace, node_name="node-1", confirm_unmounted=True)
    block.resize_block_volume("64b0000000000000000000b1", workspace_id=workspace, new_size_gb=200, check_state=False)

    cdn = client.cdn
    cdn.generate_cdn_url(workspace_id=workspace, bucket_name="assets", object_key="a b.png")
    cdn.list_cdn_distributions(workspace_id=workspace)
    cdn.create_cdn_distribution(workspace_id=workspace, name="assets", origin_id="bucket-1")
    cdn.get_cdn_distribution("dist/1", workspace_id=workspace)
    cdn.update_cdn_distribution("dist/1", workspace_id=workspace, enabled=False)
    cdn.delete_cdn_distribution("dist/1", workspace_id=workspace)
    cdn.get_cdn_website_config("dist/1", workspace_id=workspace)
    cdn.update_cdn_website_config("dist/1", workspace_id=workspace, index_document="home.html")
    cdn.delete_cdn_website_config("dist/1", workspace_id=workspace)
    cdn.list_cdn_custom_domains("dist/1", workspace_id=workspace)
    cdn.create_cdn_custom_domain("dist/1", workspace_id=workspace, domain="cdn.example.com")
    cdn.get_cdn_custom_domain("dist/1", "cdn.example.com", workspace_id=workspace)
    cdn.delete_cdn_custom_domain("dist/1", "cdn.example.com", workspace_id=workspace)
    cdn.verify_cdn_custom_domain("dist/1", "cdn.example.com", workspace_id=workspace)
    cdn.purge_cdn_cache("dist/1", workspace_id=workspace, mode="all", raise_on_failure=False)

    assert len(observed) == 23
    assert all(request.url.params["workspace_id"] == workspace for request in observed)
    assert observed[2].url.raw_path.startswith(b"/v1/block-storage/volumes/64b0000000000000000000b1")
    assert observed[11].url.raw_path.startswith(b"/v1/cdn/distributions/dist%2F1")

    block_create = observed[1]
    assert block_create.method == "POST"
    create_body = json.loads(block_create.content)
    # 0.4.0: the SDK fills a portal-style idempotency key so retries are safe.
    assert create_body.pop("idempotency_key").startswith("block-volume-create-data-")
    assert create_body == {
        "name": "data",
        "size_gb": 100,
        "site_id": "site-1",
        "sku_code": "BLOCKSTO-NVME",
        "volume_class": "balanced",
        "replica_count": 2,
        "backup_enabled": True,
    }
    assert "billing_catalog" not in json.loads(block_create.content)
    assert observed[10].method == "POST"
    assert all("billing/resource-eligibility" not in request.url.path for request in observed)


def test_new_resources_keep_workspace_validation_before_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"transport must not run: {request.url}")

    client = Ibee(
        token="test",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    for call in (
        lambda: client.block_storage.list_block_volumes(workspace_id="0"),
        lambda: client.cdn.list_cdn_distributions(workspace_id="not-numeric"),
    ):
        try:
            call()
        except ValueError as exc:
            assert "positive numeric" in str(exc)
        else:
            raise AssertionError("invalid workspace_id was accepted")
