# Hand-written (listed in .fernignore).
"""CDN client (``client.cdn``) with the portal's rules.

See :mod:`ibee.storage_workflows` for the request flows and
:mod:`ibee.validation.storage` for the client-side rules.
"""

from __future__ import annotations

import typing

from .. import storage_workflows as sw
from ..compute_workflows import clean_kwargs, run_async, run_sync
from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.request_options import RequestOptions

__all__ = ["AsyncCdnClient", "CdnClient"]


class CdnClient:
    """CDN distributions, static-website hosting, custom domains and cache purges.

    Every method validates its arguments before any request (``IbeeValidationError``)
    and raises typed ``ApiError`` subclasses for error responses. Results are plain dicts.
    """

    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper
        self._http = client_wrapper.httpx_client

    def generate_cdn_url(
        self,
        *,
        workspace_id: str,
        bucket_name: str,
        object_key: str,
        expires_in: typing.Optional[int] = None,
        disposition: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Generates a CDN URL for an object. Requires scope: cdn.write.
        ``expires_in`` is an integer >= 1 (seconds); ``disposition`` is ``inline`` or ``attachment``.
        """
        return run_sync(self._client_wrapper, sw.generate_cdn_url(**clean_kwargs(locals())), request_options)

    def list_cdn_distributions(
        self, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """Lists CDN distributions (``{"distributions": [...], "count": n}``). Requires scope: cdn.read."""
        return run_sync(self._client_wrapper, sw.list_cdn_distributions(**clean_kwargs(locals())), request_options)

    def list_cdn_cache_policies(
        self, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Lists the CDN cache policies (``{"policies": [{id, name, description, headers}]}``).
        Requires scope: cdn.read.

        Not yet part of the published API contract; behaviour may change. The list can include
        ``public-development``, which ``create_cdn_distribution`` and ``update_cdn_distribution`` do
        not accept (like the portal, they take ``static-assets``, ``media``, ``short`` and ``no-cache``).
        """
        return run_sync(self._client_wrapper, sw.list_cdn_cache_policies(**clean_kwargs(locals())), request_options)

    def create_cdn_distribution(
        self,
        *,
        workspace_id: str,
        name: str,
        origin_id: str,
        origin_type: str = "bucket",
        cache_policy: str = "static-assets",
        check_origin_public: typing.Optional[bool] = None,
        preflight_billing: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Creates a CDN distribution. Requires scope: cdn.write.

        Only public buckets can be CDN origins. The API returns the existing distribution when the
        bucket already has one.

        Parameters
        ----------
        name : str
            1-128 characters (trimmed).
        origin_id : str
            The origin bucket's name (as the portal sends) or id.
        origin_type : str
            ``bucket`` (default) or ``custom``. Custom origins cannot be created through the public
            API yet.
        cache_policy : str
            ``static-assets`` (default), ``media``, ``short`` or ``no-cache``.
        check_origin_public : typing.Optional[bool]
            ``True`` reads the bucket first and refuses a private one (needs ``object-storage.read``;
            skipped when no bucket has that name).
        preflight_billing : typing.Optional[bool]
            ``True`` runs the portal's billing eligibility check first (needs ``billing.read``).
        """
        return run_sync(self._client_wrapper, sw.create_cdn_distribution(**clean_kwargs(locals())), request_options)

    def get_cdn_distribution(
        self, distribution_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """Returns a CDN distribution. Requires scope: cdn.read."""
        return run_sync(self._client_wrapper, sw.get_cdn_distribution(**clean_kwargs(locals())), request_options)

    def update_cdn_distribution(
        self,
        distribution_id: str,
        *,
        workspace_id: str,
        name: typing.Optional[str] = None,
        cache_policy: typing.Optional[str] = None,
        enabled: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Updates a CDN distribution. Requires scope: cdn.write. Pass at least one of ``name``
        (1-128 characters), ``cache_policy`` or ``enabled``.
        """
        return run_sync(self._client_wrapper, sw.update_cdn_distribution(**clean_kwargs(locals())), request_options)

    def delete_cdn_distribution(
        self, distribution_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Any:
        """
        Deletes a CDN distribution. Requires scope: cdn.write. This removes its DNS record and all
        its custom domains, and purges its cache.
        """
        return run_sync(self._client_wrapper, sw.delete_cdn_distribution(**clean_kwargs(locals())), request_options)

    def get_cdn_distribution_metrics(
        self,
        distribution_id: str,
        *,
        workspace_id: str,
        range: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Returns traffic, cache and performance metrics for a distribution. Requires scope: cdn.read.
        ``range`` is ``24h`` (default), ``7d`` or ``30d``.

        Not yet part of the published API contract; behaviour may change.
        """
        return run_sync(self._client_wrapper, sw.get_cdn_distribution_metrics(**clean_kwargs(locals())), request_options)

    def get_cdn_website_config(
        self, distribution_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Returns the static-website (SPA) configuration. Requires scope: cdn.read. ``NotFoundError``
        also means website hosting is not configured (the portal shows it as disabled).
        """
        return run_sync(self._client_wrapper, sw.get_cdn_website_config(**clean_kwargs(locals())), request_options)

    def update_cdn_website_config(
        self,
        distribution_id: str,
        *,
        workspace_id: str,
        index_document: str = "index.html",
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Enables static-website hosting. Requires scope: cdn.write. ``index_document`` must exist in
        the origin bucket: a relative path of printable ASCII characters (at most 1024 bytes, no
        leading ``/``, no backslash, no empty, ``.`` or ``..`` segments).
        """
        return run_sync(self._client_wrapper, sw.update_cdn_website_config(**clean_kwargs(locals())), request_options)

    def delete_cdn_website_config(
        self, distribution_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """Disables static-website hosting. Requires scope: cdn.write."""
        return run_sync(self._client_wrapper, sw.delete_cdn_website_config(**clean_kwargs(locals())), request_options)

    def list_cdn_custom_domains(
        self, distribution_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """Lists a distribution's custom domains. Requires scope: cdn.read."""
        return run_sync(self._client_wrapper, sw.list_cdn_custom_domains(**clean_kwargs(locals())), request_options)

    def create_cdn_custom_domain(
        self,
        distribution_id: str,
        *,
        workspace_id: str,
        domain: str,
        preflight_billing: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Adds a custom domain (billed). Requires scope: cdn.write.

        ``domain`` is trimmed and lower-cased; it must be a valid host name of 3-253 characters with
        a subdomain (for example ``cdn.example.com``). Then create the returned
        ``validation.cname_record`` at your DNS provider and call ``verify_cdn_custom_domain``.
        ``preflight_billing=True`` runs the portal's billing check first (CUSTOMDO-STD, needs ``billing.read``).
        """
        return run_sync(self._client_wrapper, sw.create_cdn_custom_domain(**clean_kwargs(locals())), request_options)

    def get_cdn_custom_domain(
        self, distribution_id: str, domain: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """Returns a custom domain. Requires scope: cdn.read. ``domain`` is trimmed and lower-cased."""
        return run_sync(self._client_wrapper, sw.get_cdn_custom_domain(**clean_kwargs(locals())), request_options)

    def delete_cdn_custom_domain(
        self, distribution_id: str, domain: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Removes a custom domain. Requires scope: cdn.write. Also delete its CNAME record at your
        DNS provider.
        """
        return run_sync(self._client_wrapper, sw.delete_cdn_custom_domain(**clean_kwargs(locals())), request_options)

    def verify_cdn_custom_domain(
        self, distribution_id: str, domain: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Checks a custom domain's DNS and certificate. Requires scope: cdn.write. ``status`` is
        ``pending_validation``, ``pending_tls``, ``active`` or ``failed``; anything but ``active``
        usually means the DNS records have not propagated yet.
        """
        return run_sync(self._client_wrapper, sw.verify_cdn_custom_domain(**clean_kwargs(locals())), request_options)

    def wait_for_cdn_custom_domain(
        self,
        distribution_id: str,
        domain: str,
        *,
        workspace_id: str,
        timeout: float = 600.0,
        poll_interval: float = 15.0,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Calls ``verify_cdn_custom_domain`` every ``poll_interval`` seconds (1-60, default 15) until
        the status is ``active`` or ``failed`` (returned) or ``timeout`` seconds (default 600) pass
        (``OperationTimeoutError``).
        """
        return run_sync(self._client_wrapper, sw.wait_for_cdn_custom_domain(**clean_kwargs(locals())), request_options)

    def purge_cdn_cache(
        self,
        distribution_id: str,
        *,
        workspace_id: str,
        mode: str,
        paths: typing.Optional[typing.Sequence[str]] = None,
        hostnames: typing.Optional[typing.Sequence[str]] = None,
        tags: typing.Optional[typing.Sequence[str]] = None,
        prefixes: typing.Optional[typing.Sequence[str]] = None,
        raise_on_failure: bool = True,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Purges cached content. Requires scope: cdn.write.

        ``mode`` picks the one selector to pass: ``url`` -> ``paths`` (1-30; entries without
        ``://`` get a leading ``/``; full URLs must be ``https://`` without credentials or fragment),
        ``hostname`` -> ``hostnames`` (1-100, lower-cased), ``tag`` -> ``tags`` (1-100),
        ``prefix`` -> ``prefixes`` (1-100, no ``?`` or ``#``), ``all`` -> none (purges everything).

        The API reports some failures as HTTP 200 with ``success: false`` (common for ``prefix``
        and ``tag``); that raises ``CdnPurgeFailedError`` unless ``raise_on_failure=False``.
        """
        return run_sync(self._client_wrapper, sw.purge_cdn_cache(**clean_kwargs(locals())), request_options)


class AsyncCdnClient:
    """Async variant of :class:`CdnClient`.

    Every method validates its arguments before any request (``IbeeValidationError``)
    and raises typed ``ApiError`` subclasses for error responses. Results are plain dicts.
    """

    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper
        self._http = client_wrapper.httpx_client

    async def generate_cdn_url(
        self,
        *,
        workspace_id: str,
        bucket_name: str,
        object_key: str,
        expires_in: typing.Optional[int] = None,
        disposition: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Generates a CDN URL for an object. Requires scope: cdn.write.
        ``expires_in`` is an integer >= 1 (seconds); ``disposition`` is ``inline`` or ``attachment``.
        """
        return await run_async(self._client_wrapper, sw.generate_cdn_url(**clean_kwargs(locals())), request_options)

    async def list_cdn_distributions(
        self, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """Lists CDN distributions (``{"distributions": [...], "count": n}``). Requires scope: cdn.read."""
        return await run_async(self._client_wrapper, sw.list_cdn_distributions(**clean_kwargs(locals())), request_options)

    async def list_cdn_cache_policies(
        self, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Lists the CDN cache policies (``{"policies": [{id, name, description, headers}]}``).
        Requires scope: cdn.read.

        Not yet part of the published API contract; behaviour may change. The list can include
        ``public-development``, which ``create_cdn_distribution`` and ``update_cdn_distribution`` do
        not accept (like the portal, they take ``static-assets``, ``media``, ``short`` and ``no-cache``).
        """
        return await run_async(self._client_wrapper, sw.list_cdn_cache_policies(**clean_kwargs(locals())), request_options)

    async def create_cdn_distribution(
        self,
        *,
        workspace_id: str,
        name: str,
        origin_id: str,
        origin_type: str = "bucket",
        cache_policy: str = "static-assets",
        check_origin_public: typing.Optional[bool] = None,
        preflight_billing: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Creates a CDN distribution. Requires scope: cdn.write.

        Only public buckets can be CDN origins. The API returns the existing distribution when the
        bucket already has one.

        Parameters
        ----------
        name : str
            1-128 characters (trimmed).
        origin_id : str
            The origin bucket's name (as the portal sends) or id.
        origin_type : str
            ``bucket`` (default) or ``custom``. Custom origins cannot be created through the public
            API yet.
        cache_policy : str
            ``static-assets`` (default), ``media``, ``short`` or ``no-cache``.
        check_origin_public : typing.Optional[bool]
            ``True`` reads the bucket first and refuses a private one (needs ``object-storage.read``;
            skipped when no bucket has that name).
        preflight_billing : typing.Optional[bool]
            ``True`` runs the portal's billing eligibility check first (needs ``billing.read``).
        """
        return await run_async(self._client_wrapper, sw.create_cdn_distribution(**clean_kwargs(locals())), request_options)

    async def get_cdn_distribution(
        self, distribution_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """Returns a CDN distribution. Requires scope: cdn.read."""
        return await run_async(self._client_wrapper, sw.get_cdn_distribution(**clean_kwargs(locals())), request_options)

    async def update_cdn_distribution(
        self,
        distribution_id: str,
        *,
        workspace_id: str,
        name: typing.Optional[str] = None,
        cache_policy: typing.Optional[str] = None,
        enabled: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Updates a CDN distribution. Requires scope: cdn.write. Pass at least one of ``name``
        (1-128 characters), ``cache_policy`` or ``enabled``.
        """
        return await run_async(self._client_wrapper, sw.update_cdn_distribution(**clean_kwargs(locals())), request_options)

    async def delete_cdn_distribution(
        self, distribution_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Any:
        """
        Deletes a CDN distribution. Requires scope: cdn.write. This removes its DNS record and all
        its custom domains, and purges its cache.
        """
        return await run_async(self._client_wrapper, sw.delete_cdn_distribution(**clean_kwargs(locals())), request_options)

    async def get_cdn_distribution_metrics(
        self,
        distribution_id: str,
        *,
        workspace_id: str,
        range: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Returns traffic, cache and performance metrics for a distribution. Requires scope: cdn.read.
        ``range`` is ``24h`` (default), ``7d`` or ``30d``.

        Not yet part of the published API contract; behaviour may change.
        """
        return await run_async(self._client_wrapper, sw.get_cdn_distribution_metrics(**clean_kwargs(locals())), request_options)

    async def get_cdn_website_config(
        self, distribution_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Returns the static-website (SPA) configuration. Requires scope: cdn.read. ``NotFoundError``
        also means website hosting is not configured (the portal shows it as disabled).
        """
        return await run_async(self._client_wrapper, sw.get_cdn_website_config(**clean_kwargs(locals())), request_options)

    async def update_cdn_website_config(
        self,
        distribution_id: str,
        *,
        workspace_id: str,
        index_document: str = "index.html",
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Enables static-website hosting. Requires scope: cdn.write. ``index_document`` must exist in
        the origin bucket: a relative path of printable ASCII characters (at most 1024 bytes, no
        leading ``/``, no backslash, no empty, ``.`` or ``..`` segments).
        """
        return await run_async(self._client_wrapper, sw.update_cdn_website_config(**clean_kwargs(locals())), request_options)

    async def delete_cdn_website_config(
        self, distribution_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """Disables static-website hosting. Requires scope: cdn.write."""
        return await run_async(self._client_wrapper, sw.delete_cdn_website_config(**clean_kwargs(locals())), request_options)

    async def list_cdn_custom_domains(
        self, distribution_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """Lists a distribution's custom domains. Requires scope: cdn.read."""
        return await run_async(self._client_wrapper, sw.list_cdn_custom_domains(**clean_kwargs(locals())), request_options)

    async def create_cdn_custom_domain(
        self,
        distribution_id: str,
        *,
        workspace_id: str,
        domain: str,
        preflight_billing: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Adds a custom domain (billed). Requires scope: cdn.write.

        ``domain`` is trimmed and lower-cased; it must be a valid host name of 3-253 characters with
        a subdomain (for example ``cdn.example.com``). Then create the returned
        ``validation.cname_record`` at your DNS provider and call ``verify_cdn_custom_domain``.
        ``preflight_billing=True`` runs the portal's billing check first (CUSTOMDO-STD, needs ``billing.read``).
        """
        return await run_async(self._client_wrapper, sw.create_cdn_custom_domain(**clean_kwargs(locals())), request_options)

    async def get_cdn_custom_domain(
        self, distribution_id: str, domain: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """Returns a custom domain. Requires scope: cdn.read. ``domain`` is trimmed and lower-cased."""
        return await run_async(self._client_wrapper, sw.get_cdn_custom_domain(**clean_kwargs(locals())), request_options)

    async def delete_cdn_custom_domain(
        self, distribution_id: str, domain: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Removes a custom domain. Requires scope: cdn.write. Also delete its CNAME record at your
        DNS provider.
        """
        return await run_async(self._client_wrapper, sw.delete_cdn_custom_domain(**clean_kwargs(locals())), request_options)

    async def verify_cdn_custom_domain(
        self, distribution_id: str, domain: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Checks a custom domain's DNS and certificate. Requires scope: cdn.write. ``status`` is
        ``pending_validation``, ``pending_tls``, ``active`` or ``failed``; anything but ``active``
        usually means the DNS records have not propagated yet.
        """
        return await run_async(self._client_wrapper, sw.verify_cdn_custom_domain(**clean_kwargs(locals())), request_options)

    async def wait_for_cdn_custom_domain(
        self,
        distribution_id: str,
        domain: str,
        *,
        workspace_id: str,
        timeout: float = 600.0,
        poll_interval: float = 15.0,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Calls ``verify_cdn_custom_domain`` every ``poll_interval`` seconds (1-60, default 15) until
        the status is ``active`` or ``failed`` (returned) or ``timeout`` seconds (default 600) pass
        (``OperationTimeoutError``).
        """
        return await run_async(self._client_wrapper, sw.wait_for_cdn_custom_domain(**clean_kwargs(locals())), request_options)

    async def purge_cdn_cache(
        self,
        distribution_id: str,
        *,
        workspace_id: str,
        mode: str,
        paths: typing.Optional[typing.Sequence[str]] = None,
        hostnames: typing.Optional[typing.Sequence[str]] = None,
        tags: typing.Optional[typing.Sequence[str]] = None,
        prefixes: typing.Optional[typing.Sequence[str]] = None,
        raise_on_failure: bool = True,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Purges cached content. Requires scope: cdn.write.

        ``mode`` picks the one selector to pass: ``url`` -> ``paths`` (1-30; entries without
        ``://`` get a leading ``/``; full URLs must be ``https://`` without credentials or fragment),
        ``hostname`` -> ``hostnames`` (1-100, lower-cased), ``tag`` -> ``tags`` (1-100),
        ``prefix`` -> ``prefixes`` (1-100, no ``?`` or ``#``), ``all`` -> none (purges everything).

        The API reports some failures as HTTP 200 with ``success: false`` (common for ``prefix``
        and ``tag``); that raises ``CdnPurgeFailedError`` unless ``raise_on_failure=False``.
        """
        return await run_async(self._client_wrapper, sw.purge_cdn_cache(**clean_kwargs(locals())), request_options)
