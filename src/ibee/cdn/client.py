from __future__ import annotations

import typing
from urllib.parse import quote

from ..block_storage.client import _compact, _data
from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.request_options import RequestOptions


def _segment(value: str) -> str:
    return quote(value, safe="")


class CdnClient:
    """CDN, static-website, and custom-domain management."""

    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._http = client_wrapper.httpx_client

    def _request(self, method: str, path: str, *, workspace_id: str, json: typing.Any = None,
                 request_options: typing.Optional[RequestOptions] = None) -> typing.Any:
        return _data(self._http.request(path, method=method, params={"workspace_id": workspace_id}, json=_compact(json),
                                        headers={"content-type": "application/json"} if json is not None else None,
                                        request_options=request_options))

    def generate_cdn_url(self, *, workspace_id: str, bucket_name: str, object_key: str,
                         expires_in: typing.Optional[int] = None, disposition: typing.Optional[str] = None,
                         request_options: typing.Optional[RequestOptions] = None):
        return self._request("POST", "cdn/generate-url", workspace_id=workspace_id,
                             json={"bucket_name": bucket_name, "object_key": object_key,
                                   "expires_in": expires_in, "disposition": disposition},
                             request_options=request_options)

    def list_cdn_distributions(self, *, workspace_id: str, request_options=None):
        return self._request("GET", "cdn/distributions", workspace_id=workspace_id, request_options=request_options)

    def create_cdn_distribution(self, *, workspace_id: str, name: str, origin_id: str,
                                origin_type: str = "bucket", cache_policy: str = "static-assets",
                                request_options=None):
        return self._request("POST", "cdn/distributions", workspace_id=workspace_id,
                             json={"name": name, "origin_type": origin_type, "origin_id": origin_id,
                                   "cache_policy": cache_policy}, request_options=request_options)

    def get_cdn_distribution(self, distribution_id: str, *, workspace_id: str, request_options=None):
        return self._request("GET", f"cdn/distributions/{_segment(distribution_id)}",
                             workspace_id=workspace_id, request_options=request_options)

    def update_cdn_distribution(self, distribution_id: str, *, workspace_id: str,
                                name: typing.Optional[str] = None, cache_policy: typing.Optional[str] = None,
                                enabled: typing.Optional[bool] = None, request_options=None):
        return self._request("PATCH", f"cdn/distributions/{_segment(distribution_id)}",
                             workspace_id=workspace_id, json={"name": name, "cache_policy": cache_policy,
                             "enabled": enabled}, request_options=request_options)

    def delete_cdn_distribution(self, distribution_id: str, *, workspace_id: str, request_options=None):
        return self._request("DELETE", f"cdn/distributions/{_segment(distribution_id)}",
                             workspace_id=workspace_id, request_options=request_options)

    def get_cdn_website_config(self, distribution_id: str, *, workspace_id: str, request_options=None):
        return self._request("GET", f"cdn/distributions/{_segment(distribution_id)}/website-config",
                             workspace_id=workspace_id, request_options=request_options)

    def update_cdn_website_config(self, distribution_id: str, *, workspace_id: str,
                                  index_document: str = "index.html", request_options=None):
        return self._request("PUT", f"cdn/distributions/{_segment(distribution_id)}/website-config",
                             workspace_id=workspace_id, json={"index_document": index_document},
                             request_options=request_options)

    def delete_cdn_website_config(self, distribution_id: str, *, workspace_id: str, request_options=None):
        return self._request("DELETE", f"cdn/distributions/{_segment(distribution_id)}/website-config",
                             workspace_id=workspace_id, request_options=request_options)

    def list_cdn_custom_domains(self, distribution_id: str, *, workspace_id: str, request_options=None):
        return self._request("GET", f"cdn/distributions/{_segment(distribution_id)}/custom-domains",
                             workspace_id=workspace_id, request_options=request_options)

    def create_cdn_custom_domain(self, distribution_id: str, *, workspace_id: str, domain: str,
                                 request_options=None):
        return self._request("POST", f"cdn/distributions/{_segment(distribution_id)}/custom-domains",
                             workspace_id=workspace_id, json={"domain": domain}, request_options=request_options)

    def get_cdn_custom_domain(self, distribution_id: str, domain: str, *, workspace_id: str,
                              request_options=None):
        return self._request("GET", f"cdn/distributions/{_segment(distribution_id)}/custom-domains/{_segment(domain)}",
                             workspace_id=workspace_id, request_options=request_options)

    def delete_cdn_custom_domain(self, distribution_id: str, domain: str, *, workspace_id: str,
                                 request_options=None):
        return self._request("DELETE", f"cdn/distributions/{_segment(distribution_id)}/custom-domains/{_segment(domain)}",
                             workspace_id=workspace_id, request_options=request_options)

    def verify_cdn_custom_domain(self, distribution_id: str, domain: str, *, workspace_id: str,
                                 request_options=None):
        return self._request("POST", f"cdn/distributions/{_segment(distribution_id)}/custom-domains/{_segment(domain)}/verify",
                             workspace_id=workspace_id, request_options=request_options)

    def purge_cdn_cache(self, distribution_id: str, *, workspace_id: str, mode: str,
                        paths: typing.Optional[typing.Sequence[str]] = None,
                        hostnames: typing.Optional[typing.Sequence[str]] = None,
                        tags: typing.Optional[typing.Sequence[str]] = None,
                        prefixes: typing.Optional[typing.Sequence[str]] = None, request_options=None):
        return self._request("POST", f"cdn/distributions/{_segment(distribution_id)}/purge",
                             workspace_id=workspace_id, json={"mode": mode, "paths": paths,
                             "hostnames": hostnames, "tags": tags, "prefixes": prefixes},
                             request_options=request_options)


class AsyncCdnClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._http = client_wrapper.httpx_client

    async def _request(self, method: str, path: str, *, workspace_id: str, json: typing.Any = None,
                       request_options: typing.Optional[RequestOptions] = None) -> typing.Any:
        response = await self._http.request(path, method=method, params={"workspace_id": workspace_id}, json=_compact(json),
                                            headers={"content-type": "application/json"} if json is not None else None,
                                            request_options=request_options)
        return _data(response)

    async def generate_cdn_url(self, *, workspace_id: str, bucket_name: str, object_key: str, **kwargs):
        request_options = kwargs.pop("request_options", None); return await self._request("POST", "cdn/generate-url", workspace_id=workspace_id, json={"bucket_name": bucket_name, "object_key": object_key, **kwargs}, request_options=request_options)
    async def list_cdn_distributions(self, **kwargs): return await self._request("GET", "cdn/distributions", **kwargs)
    async def create_cdn_distribution(self, *, workspace_id: str, name: str, origin_id: str, **kwargs):
        request_options = kwargs.pop("request_options", None); return await self._request("POST", "cdn/distributions", workspace_id=workspace_id, json={"name": name, "origin_id": origin_id, **kwargs}, request_options=request_options)
    async def get_cdn_distribution(self, distribution_id: str, **kwargs): return await self._request("GET", f"cdn/distributions/{_segment(distribution_id)}", **kwargs)
    async def update_cdn_distribution(self, distribution_id: str, *, workspace_id: str, **kwargs):
        request_options = kwargs.pop("request_options", None); return await self._request("PATCH", f"cdn/distributions/{_segment(distribution_id)}", workspace_id=workspace_id, json=kwargs, request_options=request_options)
    async def delete_cdn_distribution(self, distribution_id: str, **kwargs): return await self._request("DELETE", f"cdn/distributions/{_segment(distribution_id)}", **kwargs)
    async def get_cdn_website_config(self, distribution_id: str, **kwargs): return await self._request("GET", f"cdn/distributions/{_segment(distribution_id)}/website-config", **kwargs)
    async def update_cdn_website_config(self, distribution_id: str, *, workspace_id: str, index_document: str = "index.html", request_options=None): return await self._request("PUT", f"cdn/distributions/{_segment(distribution_id)}/website-config", workspace_id=workspace_id, json={"index_document": index_document}, request_options=request_options)
    async def delete_cdn_website_config(self, distribution_id: str, **kwargs): return await self._request("DELETE", f"cdn/distributions/{_segment(distribution_id)}/website-config", **kwargs)
    async def list_cdn_custom_domains(self, distribution_id: str, **kwargs): return await self._request("GET", f"cdn/distributions/{_segment(distribution_id)}/custom-domains", **kwargs)
    async def create_cdn_custom_domain(self, distribution_id: str, *, workspace_id: str, domain: str, request_options=None): return await self._request("POST", f"cdn/distributions/{_segment(distribution_id)}/custom-domains", workspace_id=workspace_id, json={"domain": domain}, request_options=request_options)
    async def get_cdn_custom_domain(self, distribution_id: str, domain: str, **kwargs): return await self._request("GET", f"cdn/distributions/{_segment(distribution_id)}/custom-domains/{_segment(domain)}", **kwargs)
    async def delete_cdn_custom_domain(self, distribution_id: str, domain: str, **kwargs): return await self._request("DELETE", f"cdn/distributions/{_segment(distribution_id)}/custom-domains/{_segment(domain)}", **kwargs)
    async def verify_cdn_custom_domain(self, distribution_id: str, domain: str, **kwargs): return await self._request("POST", f"cdn/distributions/{_segment(distribution_id)}/custom-domains/{_segment(domain)}/verify", **kwargs)
    async def purge_cdn_cache(self, distribution_id: str, *, workspace_id: str, mode: str, **kwargs):
        request_options = kwargs.pop("request_options", None); return await self._request("POST", f"cdn/distributions/{_segment(distribution_id)}/purge", workspace_id=workspace_id, json={"mode": mode, **kwargs}, request_options=request_options)
