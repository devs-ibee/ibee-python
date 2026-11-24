# IBEE hand layer (listed in .fernignore).
"""Upload one file with an upload link: ``client.upload_file(bucket, key, file)``.

The helper does the three steps the contract describes for ``createObjectUploadLink``:

1. read the file and compute its size and SHA-256 (base64, as the contract asks);
2. call the generated ``object_storage.create_object_upload_link`` with them;
3. ``PUT`` the file to the link with exactly the headers in the answer.

The file goes to the workspace's S3 host, never through the API, and the API token is
not sent with it. Nothing is checked before sending: the server decides the size limit
(one link carries at most ``max_bytes``) and refuses what it does not accept, and a
refused ``PUT`` raises :class:`ibee.core.api_error.ApiError` with the S3 gateway's
answer unchanged. Confirm the result with ``object_storage.get_object_metadata``.
"""

import base64
import dataclasses
import hashlib
import os
import typing

import httpx

from .core.api_error import ApiError

#: A path, the bytes themselves, or an open binary file.
FileInput = typing.Union[str, "os.PathLike[str]", bytes, bytearray, memoryview, typing.BinaryIO]


@dataclasses.dataclass(frozen=True)
class UploadedObject:
    """What was uploaded: the key, the size and SHA-256 sent, and the S3 gateway's ETag."""

    bucket_name: str
    object_path: str
    size_bytes: int
    checksum_sha256: str
    etag: typing.Optional[str]


def checksum_sha256(data: bytes) -> str:
    """The SHA-256 of ``data``, base64-encoded (44 characters), as upload links take it."""
    return base64.b64encode(hashlib.sha256(data).digest()).decode("ascii")


def read_file(file: FileInput) -> bytes:
    """The whole file as bytes (one upload link carries one whole file)."""
    if isinstance(file, (bytes, bytearray, memoryview)):
        return bytes(file)
    if isinstance(file, (str, os.PathLike)):
        with open(file, "rb") as handle:
            return handle.read()
    data = file.read()
    if isinstance(data, str):
        raise TypeError("open the file in binary mode ('rb')")
    return bytes(data)


def _put_request(http: httpx.Client | httpx.AsyncClient, link: typing.Any, data: bytes) -> httpx.Request:
    # httpx sets Content-Length from the body (the same value the link signed).
    headers = {k: v for k, v in (link.headers or {}).items() if k.lower() != "content-length"}
    request = http.build_request(str(link.method or "PUT"), link.url, content=data, headers=headers)
    # Never send the API token or a client default Authorization to the S3 host.
    request.headers.pop("authorization", None)
    return request


def _result(bucket_name: str, object_path: str, data: bytes, checksum: str, response: httpx.Response) -> UploadedObject:
    if response.status_code >= 300:
        raise ApiError(status_code=response.status_code, headers=dict(response.headers), body=response.text)
    return UploadedObject(bucket_name, object_path, len(data), checksum, response.headers.get("etag"))


def _http(client: typing.Any) -> typing.Any:
    # The client's own httpx client (same proxies, TLS and timeout settings).
    return client._client_wrapper.httpx_client.httpx_client


def upload_file(
    client: typing.Any,
    bucket_name: str,
    object_path: str,
    file: FileInput,
    *,
    content_type: typing.Optional[str] = None,
    expires: typing.Optional[int] = None,
    workspace_id: typing.Optional[str] = None,
) -> UploadedObject:
    """Upload ``file`` to ``object_path`` in ``bucket_name`` with one upload link (see the module docstring)."""
    data = read_file(file)
    checksum = checksum_sha256(data)
    extra: typing.Dict[str, typing.Any] = {}
    if content_type is not None:
        extra["content_type"] = content_type
    if expires is not None:
        extra["expires"] = expires
    link = client.object_storage.create_object_upload_link(
        bucket_name, object_path, size_bytes=len(data), checksum_sha256=checksum, workspace_id=workspace_id, **extra
    )
    http = _http(client)
    response = http.send(_put_request(http, link, data))
    return _result(bucket_name, object_path, data, checksum, response)


async def upload_file_async(
    client: typing.Any,
    bucket_name: str,
    object_path: str,
    file: FileInput,
    *,
    content_type: typing.Optional[str] = None,
    expires: typing.Optional[int] = None,
    workspace_id: typing.Optional[str] = None,
) -> UploadedObject:
    """Async :func:`upload_file`, for :class:`ibee.AsyncIbee`."""
    data = read_file(file)
    checksum = checksum_sha256(data)
    extra: typing.Dict[str, typing.Any] = {}
    if content_type is not None:
        extra["content_type"] = content_type
    if expires is not None:
        extra["expires"] = expires
    link = await client.object_storage.create_object_upload_link(
        bucket_name, object_path, size_bytes=len(data), checksum_sha256=checksum, workspace_id=workspace_id, **extra
    )
    http = _http(client)
    response = await http.send(_put_request(http, link, data))
    return _result(bucket_name, object_path, data, checksum, response)
