"""Contract 0.14: object links and metadata, the upload helper, billing refusal fields,
load balancer include_deleted, and the shared volume confirmation."""

import asyncio
import base64
import hashlib
import json

import httpx
import pytest
from mockapi import ACCEPTED, VM, WS, Recorder, async_client, client

from ibee.core.api_error import ApiError
from ibee.errors import PaymentRequiredError

S3 = "https://710995.blob.ibeestorage.com"
DATA = b"hello from the ibee sdk\n"
SHA = base64.b64encode(hashlib.sha256(DATA).digest()).decode()


def link(content_type: str = "") -> dict:
    headers = {"Content-Length": str(len(DATA)), "x-amz-checksum-sha256": SHA}
    if content_type:
        headers["Content-Type"] = content_type
    return {"url": f"{S3}/b1/docs/a.txt?X-Amz-Signature=sig", "method": "PUT", "headers": headers,
            "expires_in": 900, "max_bytes": 80000000}


class S3AndApi:
    """The API answers the link; the S3 host answers the PUT."""

    def __init__(self, put_status: int = 200, put_body: str = "") -> None:
        self.requests = []
        self.put_status, self.put_body = put_status, put_body

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.url.host.endswith("ibeestorage.com"):
            return httpx.Response(self.put_status, text=self.put_body, headers={"ETag": '"abc"'})
        body = json.loads(request.content)
        return httpx.Response(200, json=link(body.get("content_type", "")))


def test_object_calls_use_the_contract_paths() -> None:
    rec = Recorder((200, link()), (200, {"url": f"{S3}/b1/docs/a.txt?sig", "expires_in": 120}),
                   (200, {"name": "docs/a.txt", "bucket": "b1", "size_bytes": 24, "checksum_sha256": SHA}))
    c = client(rec, workspace_id=WS)
    up = c.object_storage.create_object_upload_link("b1", "docs/a.txt", size_bytes=24, checksum_sha256=SHA)
    down = c.object_storage.create_object_download_link("b1", "docs/a.txt", expires=120, disposition="attachment")
    meta = c.object_storage.get_object_metadata("b1", "docs/a.txt")
    paths = [(r.method, r.url.path) for r in rec.requests]
    assert paths == [
        ("POST", "/v1/object-storage/buckets/b1/objects/docs/a.txt/upload-link"),
        ("POST", "/v1/object-storage/buckets/b1/objects/docs/a.txt/download-link"),
        ("GET", "/v1/object-storage/buckets/b1/objects/docs/a.txt/metadata"),
    ]
    assert rec.body(0) == {"size_bytes": 24, "checksum_sha256": SHA}
    assert rec.body(1) == {"expires": 120, "disposition": "attachment"}
    assert all(r.url.params["workspace_id"] == WS for r in rec.requests)
    assert (up.max_bytes, down.expires_in, meta.size_bytes, meta.checksum_sha256) == (80000000, 120, 24, SHA)


def test_upload_file_sends_size_and_sha256_then_puts_the_file(tmp_path) -> None:
    path = tmp_path / "a.txt"
    path.write_bytes(DATA)
    api = S3AndApi()
    result = client(api, workspace_id=WS).upload_file("b1", "docs/a.txt", path, content_type="text/plain")
    mint, put = api.requests
    assert mint.url.path.endswith("/objects/docs/a.txt/upload-link")
    assert json.loads(mint.content) == {"size_bytes": len(DATA), "checksum_sha256": SHA, "content_type": "text/plain"}
    assert (put.method, put.url.host, put.content) == ("PUT", "710995.blob.ibeestorage.com", DATA)
    assert put.headers["x-amz-checksum-sha256"] == SHA
    assert put.headers["content-length"] == str(len(DATA))
    assert put.headers["content-type"] == "text/plain"
    assert "authorization" not in put.headers  # the API token stays with the API
    assert (result.size_bytes, result.checksum_sha256, result.etag) == (len(DATA), SHA, '"abc"')


def test_upload_file_takes_bytes_and_open_files(tmp_path) -> None:
    api = S3AndApi()
    c = client(api, workspace_id=WS)
    c.upload_file("b1", "a.bin", DATA)
    path = tmp_path / "a.bin"
    path.write_bytes(DATA)
    with open(path, "rb") as handle:
        c.upload_file("b1", "a.bin", handle, expires=60)
    puts = [r for r in api.requests if r.method == "PUT"]
    assert [r.content for r in puts] == [DATA, DATA]
    assert json.loads(api.requests[2].content)["expires"] == 60


def test_refused_upload_raises_with_the_s3_answer() -> None:
    api = S3AndApi(403, "<Error><Code>SignatureDoesNotMatch</Code></Error>")
    with pytest.raises(ApiError) as info:
        client(api, workspace_id=WS).upload_file("b1", "a.bin", DATA)
    assert info.value.status_code == 403
    assert "SignatureDoesNotMatch" in info.value.body


def test_async_upload_file() -> None:
    api = S3AndApi()

    async def run():
        return await async_client(api, workspace_id=WS).upload_file("b1", "a.bin", DATA)

    result = asyncio.run(run())
    assert [r.method for r in api.requests] == ["POST", "PUT"]
    assert "authorization" not in api.requests[1].headers
    assert result.checksum_sha256 == SHA


def test_initial_topup_refusal_fields() -> None:
    body = {"error": "billing_denied", "billing_reason": "initial_topup_required",
            "message": "Add at least Rs 500 to your wallet.", "required_topup_minor": 50000,
            "billing_currency": "INR", "request_id": "r-1"}
    rec = Recorder((402, body))
    with pytest.raises(PaymentRequiredError) as info:
        client(rec, workspace_id=WS).reserved_ips.reserve_ip(site_id="VGA")
    error = info.value
    assert (error.code, error.billing_reason, error.required_topup_minor, error.billing_currency) == (
        "billing_denied", "initial_topup_required", 50000, "INR")
    assert "required_topup_minor: 50000" in str(error) and "billing_currency: INR" in str(error)


def test_refusal_fields_are_none_when_billing_sent_none() -> None:
    rec = Recorder((402, {"error": "billing_denied", "billing_reason": "insufficient_balance"}))
    with pytest.raises(PaymentRequiredError) as info:
        client(rec, workspace_id=WS).reserved_ips.reserve_ip(site_id="VGA")
    assert (info.value.required_topup_minor, info.value.billing_currency) == (None, None)


@pytest.mark.parametrize(("call", "status"), [
    (lambda c: c.secret_manager.enable_secret_manager_workspace(namespace="e2e"), 402),
    (lambda c: c.load_balancers.delete_load_balancer("lb-1"), 423),
])
def test_new_declared_statuses_raise_typed_errors(call, status) -> None:
    rec = Recorder((status, {"error": "billing_denied" if status == 402 else "organization_restricted"}))
    with pytest.raises(ApiError) as info:
        call(client(rec, workspace_id=WS, max_retries=0))
    assert info.value.status_code == status


def test_list_load_balancers_include_deleted() -> None:
    rec = Recorder((200, {"items": [], "total": 0, "page": 1, "page_size": 50}))
    client(rec, workspace_id=WS).load_balancers.list_load_balancers(include_deleted=True)
    assert rec.requests[0].url.params["include_deleted"] == "true"


def test_attach_volume_shared_access_confirmed() -> None:
    rec = Recorder((202, ACCEPTED))
    client(rec, workspace_id=WS).cloud_vms.attach_cloud_vm_volume(
        VM, volume_id="vol-1", billing_catalog={"sku_code": "BS-100"}, mode="multi-writer",
        shared_access_confirmed=True)
    assert rec.body()["mode"] == "multi-writer" and rec.body()["shared_access_confirmed"] is True
