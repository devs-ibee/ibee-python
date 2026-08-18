from __future__ import annotations

import typing
from urllib.parse import quote

from ..core.api_error import ApiError
from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.request_options import RequestOptions


def _data(response: typing.Any) -> typing.Any:
    if 200 <= response.status_code < 300:
        if response.status_code == 204 or not response.content:
            return None
        return response.json()
    try:
        body: typing.Any = response.json()
    except ValueError:
        body = response.text
    raise ApiError(status_code=response.status_code, headers=dict(response.headers), body=body)


def _compact(value: typing.Any) -> typing.Any:
    if not isinstance(value, dict):
        return value
    return {key: item for key, item in value.items() if item is not None}


class BlockStorageClient:
    """Block Storage management through the public API edge."""

    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._http = client_wrapper.httpx_client

    def _request(self, method: str, path: str, *, workspace_id: str, json: typing.Any = None,
                 params: typing.Optional[typing.Dict[str, typing.Any]] = None,
                 request_options: typing.Optional[RequestOptions] = None) -> typing.Any:
        query = {"workspace_id": workspace_id, **(params or {})}
        return _data(self._http.request(path, method=method, params=query, json=_compact(json),
                                        headers={"content-type": "application/json"} if json is not None else None,
                                        request_options=request_options))

    def list_block_volumes(self, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None):
        return self._request("GET", "block-storage/volumes", workspace_id=workspace_id, request_options=request_options)

    def create_block_volume(self, *, workspace_id: str, name: str, size_gb: int, site_id: str,
                            site_name: typing.Optional[str] = None, sku_code: typing.Optional[str] = None,
                            volume_class: str = "balanced", replica_count: int = 2,
                            backup_enabled: bool = True, idempotency_key: typing.Optional[str] = None,
                            request_options: typing.Optional[RequestOptions] = None):
        return self._request("POST", "block-storage/volumes", workspace_id=workspace_id, json={
            "name": name, "size_gb": size_gb, "site_id": site_id, "site_name": site_name,
            "sku_code": sku_code,
            "volume_class": volume_class, "replica_count": replica_count,
            "backup_enabled": backup_enabled, "idempotency_key": idempotency_key,
        }, request_options=request_options)

    def get_block_volume(self, volume_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None):
        return self._request("GET", f"block-storage/volumes/{quote(volume_id, safe='')}", workspace_id=workspace_id, request_options=request_options)

    def delete_block_volume(self, volume_id: str, *, workspace_id: str, force: bool = False,
                            request_options: typing.Optional[RequestOptions] = None):
        return self._request("DELETE", f"block-storage/volumes/{quote(volume_id, safe='')}", workspace_id=workspace_id,
                             params={"force": force}, request_options=request_options)

    def list_block_volume_operations(self, volume_id: str, *, workspace_id: str,
                                     request_options: typing.Optional[RequestOptions] = None):
        return self._request("GET", f"block-storage/volumes/{quote(volume_id, safe='')}/operations",
                             workspace_id=workspace_id, request_options=request_options)

    def attach_block_volume(self, volume_id: str, *, workspace_id: str, node_name: str,
                            mode: str = "single-writer", vm_id: typing.Optional[str] = None,
                            vm_name: typing.Optional[str] = None, vm_state: typing.Optional[str] = None,
                            vm_site_id: typing.Optional[str] = None, vm_type: str = "cloud",
                            idempotency_key: typing.Optional[str] = None,
                            request_options: typing.Optional[RequestOptions] = None):
        return self._request("POST", f"block-storage/volumes/{quote(volume_id, safe='')}/attachments",
                             workspace_id=workspace_id, json={"node_name": node_name, "mode": mode,
                             "vm_id": vm_id, "vm_name": vm_name, "vm_state": vm_state,
                             "vm_site_id": vm_site_id, "vm_type": vm_type,
                             "idempotency_key": idempotency_key}, request_options=request_options)

    def detach_block_volume(self, volume_id: str, *, workspace_id: str, node_name: str,
                            force: bool = False, confirm_unmounted: bool = False,
                            vm_state: typing.Optional[str] = None, vm_type: str = "cloud",
                            reason: typing.Optional[str] = None, idempotency_key: typing.Optional[str] = None,
                            request_options: typing.Optional[RequestOptions] = None):
        return self._request("POST", f"block-storage/volumes/{quote(volume_id, safe='')}/detach",
                             workspace_id=workspace_id, json={"node_name": node_name, "force": force,
                             "confirm_unmounted": confirm_unmounted, "vm_state": vm_state,
                             "vm_type": vm_type, "reason": reason, "idempotency_key": idempotency_key},
                             request_options=request_options)

    def resize_block_volume(self, volume_id: str, *, workspace_id: str, new_size_gb: int,
                            vm_state: typing.Optional[str] = None, allow_online: bool = False,
                            idempotency_key: typing.Optional[str] = None,
                            request_options: typing.Optional[RequestOptions] = None):
        return self._request("POST", f"block-storage/volumes/{quote(volume_id, safe='')}/resize",
                             workspace_id=workspace_id, json={"new_size_gb": new_size_gb,
                             "vm_state": vm_state, "allow_online": allow_online,
                             "idempotency_key": idempotency_key}, request_options=request_options)


class AsyncBlockStorageClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._http = client_wrapper.httpx_client

    async def _request(self, method: str, path: str, *, workspace_id: str, json: typing.Any = None,
                       params: typing.Optional[typing.Dict[str, typing.Any]] = None,
                       request_options: typing.Optional[RequestOptions] = None) -> typing.Any:
        query = {"workspace_id": workspace_id, **(params or {})}
        response = await self._http.request(path, method=method, params=query, json=_compact(json),
                                            headers={"content-type": "application/json"} if json is not None else None,
                                            request_options=request_options)
        return _data(response)

    async def list_block_volumes(self, **kwargs): return await self._request("GET", "block-storage/volumes", **kwargs)
    async def create_block_volume(self, *, workspace_id: str, name: str, size_gb: int, site_id: str,
                                  **kwargs):
        request_options = kwargs.pop("request_options", None)
        return await self._request("POST", "block-storage/volumes", workspace_id=workspace_id,
                                   json={"name": name, "size_gb": size_gb, "site_id": site_id,
                                         **kwargs}, request_options=request_options)
    async def get_block_volume(self, volume_id: str, **kwargs): return await self._request("GET", f"block-storage/volumes/{quote(volume_id, safe='')}", **kwargs)
    async def delete_block_volume(self, volume_id: str, *, workspace_id: str, force: bool = False, request_options=None): return await self._request("DELETE", f"block-storage/volumes/{quote(volume_id, safe='')}", workspace_id=workspace_id, params={"force": force}, request_options=request_options)
    async def list_block_volume_operations(self, volume_id: str, **kwargs): return await self._request("GET", f"block-storage/volumes/{quote(volume_id, safe='')}/operations", **kwargs)
    async def attach_block_volume(self, volume_id: str, *, workspace_id: str, node_name: str, **kwargs):
        request_options = kwargs.pop("request_options", None); return await self._request("POST", f"block-storage/volumes/{quote(volume_id, safe='')}/attachments", workspace_id=workspace_id, json={"node_name": node_name, **kwargs}, request_options=request_options)
    async def detach_block_volume(self, volume_id: str, *, workspace_id: str, node_name: str, **kwargs):
        request_options = kwargs.pop("request_options", None); return await self._request("POST", f"block-storage/volumes/{quote(volume_id, safe='')}/detach", workspace_id=workspace_id, json={"node_name": node_name, **kwargs}, request_options=request_options)
    async def resize_block_volume(self, volume_id: str, *, workspace_id: str, new_size_gb: int, **kwargs):
        request_options = kwargs.pop("request_options", None); return await self._request("POST", f"block-storage/volumes/{quote(volume_id, safe='')}/resize", workspace_id=workspace_id, json={"new_size_gb": new_size_gb, **kwargs}, request_options=request_options)
