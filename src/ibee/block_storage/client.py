# Hand-written (listed in .fernignore).
"""Block Storage client (``client.block_storage``) with the portal's rules.

See :mod:`ibee.storage_workflows` for the request flows and
:mod:`ibee.validation.storage` for the client-side rules.
"""

from __future__ import annotations

import typing

from .. import storage_workflows as sw
from ..compute_workflows import clean_kwargs, run_async, run_sync
from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.request_options import RequestOptions
from ..pagination import apaginate_offset, paginate_offset
from ..types.operation_status import OperationStatus
from ..validation import (
    VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
    VOLUME_OPERATION_TIMEOUT_SECONDS,
    validate_block_volume_list_params,
    validate_page_size,
)

__all__ = ["AsyncBlockStorageClient", "BlockStorageClient"]


class BlockStorageClient:
    """Block Storage volumes through the public API, with the portal's rules.

    Every method validates its arguments before any request (``IbeeValidationError``)
    and raises typed ``ApiError`` subclasses for error responses. Volume records are
    returned as plain dicts.
    """

    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper
        self._http = client_wrapper.httpx_client

    def list_block_volumes(
        self,
        *,
        workspace_id: str,
        site_id: typing.Optional[str] = None,
        vm_type: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """
        Lists block volumes (newest first). Requires scope: block-storage.read.

        The API returns at most ``limit`` volumes (default 100); use ``iter_block_volumes`` or
        ``list_all_block_volumes`` to read every page.

        Parameters
        ----------
        workspace_id : str
            The workspace ID to scope this request to.
        site_id : typing.Optional[str]
            Only volumes in this site.
        vm_type : typing.Optional[str]
            ``cloud`` or ``gpu``: only volumes created for that kind of VM.
        limit : typing.Optional[int]
            Page size, 1-1000 (API default 100).
        offset : typing.Optional[int]
            Number of volumes to skip (>= 0).
        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.
        """
        return run_sync(self._client_wrapper, sw.list_block_volumes(**clean_kwargs(locals())), request_options)

    def iter_block_volumes(
        self,
        *,
        workspace_id: str,
        site_id: typing.Optional[str] = None,
        vm_type: typing.Optional[str] = None,
        page_size: int = 100,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Iterator[typing.Dict[str, typing.Any]]:
        """Yields every block volume, fetching ``page_size`` (1-1000) volumes per request."""
        size = validate_page_size(page_size, maximum=1000)
        validate_block_volume_list_params(site_id=site_id, vm_type=vm_type)
        return paginate_offset(
            lambda limit, offset: self.list_block_volumes(
                workspace_id=workspace_id, site_id=site_id, vm_type=vm_type, limit=limit, offset=offset,
                request_options=request_options,
            ) or [],
            page_size=size,
            id_keys=("id", "_id"),
        )

    def list_all_block_volumes(
        self,
        *,
        workspace_id: str,
        site_id: typing.Optional[str] = None,
        vm_type: typing.Optional[str] = None,
        page_size: int = 100,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """Every block volume in the workspace, as one list (see ``iter_block_volumes``)."""
        return list(self.iter_block_volumes(workspace_id=workspace_id, site_id=site_id, vm_type=vm_type,
                                            page_size=page_size, request_options=request_options))

    def create_block_volume(
        self,
        *,
        workspace_id: str,
        name: str,
        size_gb: int,
        site_id: str,
        site_name: typing.Optional[str] = None,
        sku_code: typing.Optional[str] = None,
        volume_class: str = "balanced",
        replica_count: int = 2,
        backup_enabled: bool = True,
        vm_type: typing.Optional[str] = None,
        delete_on_termination: typing.Optional[bool] = None,
        idempotency_key: typing.Optional[str] = None,
        resolve_site_name: bool = True,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Creates a block volume like the portal. Requires scope: block-storage.write.

        The API checks billing and uses the site's Block Storage plan; no ``billing_catalog`` is
        sent. Creation is synchronous: the result is ``{"volume": ..., "operation": ...}`` with the
        volume ``ready``.

        Parameters
        ----------
        workspace_id : str
            The workspace ID to scope this request to.
        name : str
            3-255 lowercase letters, numbers and hyphens (the portal rule), unique in the workspace.
        size_gb : int
            Whole GB, 10-10000. The site's plan may allow only some sizes (the API answers 400).
        site_id : str
            Compute site ID (from ``compute_catalog.list_compute_sites``).
        site_name : typing.Optional[str]
            Site display name. When omitted and ``resolve_site_name`` is true, it is read from the
            compute sites (needs ``vm.read``; skipped when not allowed), and an unknown ``site_id``
            is rejected.
        sku_code : typing.Optional[str]
            Block Storage SKU when a site has several plans (upper-cased; root-disk SKUs rejected).
        volume_class : str
            ``capacity``, ``balanced`` (default) or ``performance``.
        replica_count : int
            1-5 (default 2).
        backup_enabled : bool
            Default ``True``.
        vm_type : typing.Optional[str]
            ``cloud`` (API default) or ``gpu``. A GPU VM can attach only a volume created with
            ``vm_type="gpu"``. Not yet part of the published API contract; behaviour may change.
        delete_on_termination : typing.Optional[bool]
            Delete the volume when its VM is deleted (API default ``False``). Not yet part of the
            published API contract; behaviour may change.
        idempotency_key : typing.Optional[str]
            Makes retries safe; generated when omitted and sent in the body and as ``X-Idempotency-Key``.
        resolve_site_name : bool
            ``False`` skips the compute-sites lookup.
        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.
        """
        return run_sync(self._client_wrapper, sw.create_block_volume(**clean_kwargs(locals())), request_options)

    def get_block_volume(
        self, volume_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Returns a block volume, including ``attachments``, ``vm_type`` and ``metadata.billing_catalog``.
        Requires scope: block-storage.read. ``volume_id`` is 24 hexadecimal characters.
        """
        return run_sync(self._client_wrapper, sw.get_block_volume(**clean_kwargs(locals())), request_options)

    def delete_block_volume(
        self,
        volume_id: str,
        *,
        workspace_id: str,
        force: bool = False,
        idempotency_key: typing.Optional[str] = None,
        check_state: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Deletes a block volume. Requires scope: block-storage.write.

        Like the portal, the volume is read first (skipped when the token lacks
        ``block-storage.read``): an attached volume is refused ("Detach this volume from all servers
        before deleting.") and so is one in the middle of another operation. ``force=True`` skips
        these checks and makes the API detach the volume from every server and erase all data.
        ``idempotency_key`` is sent as a query parameter and generated when omitted (not yet part of
        the published API contract; behaviour may change). Deletion is synchronous.

        Parameters
        ----------
        check_state : typing.Optional[bool]
            ``False`` skips reading the volume first.
        """
        return run_sync(self._client_wrapper, sw.delete_block_volume(**clean_kwargs(locals())), request_options)

    def list_block_volume_operations(
        self,
        volume_id: str,
        *,
        workspace_id: str,
        limit: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """
        Lists a volume's operations, newest first. Requires scope: block-storage.read.
        ``limit`` is 1-200 (API default 20).
        """
        return run_sync(self._client_wrapper, sw.list_block_volume_operations(**clean_kwargs(locals())), request_options)

    def attach_block_volume_to_vm(
        self,
        volume_id: str,
        vm_id: str,
        *,
        workspace_id: str,
        vm_type: typing.Optional[str] = None,
        mode: typing.Optional[str] = None,
        billing_catalog: typing.Optional[typing.Dict[str, typing.Any]] = None,
        requested_by: typing.Optional[str] = None,
        idempotency_key: typing.Optional[str] = None,
        wait: bool = False,
        timeout: float = VOLUME_OPERATION_TIMEOUT_SECONDS,
        poll_interval: float = VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
        check_state: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Attaches a block volume to a cloud or GPU VM the way the portal does. Requires scopes:
        block-storage.read and vm.write (vm.read for the VM checks).

        The volume is read first: it must be unattached and idle, the VM must be in the volume's
        site and of the volume's ``vm_type`` (which also picks the cloud or GPU endpoint), and the
        volume's Block Storage SKU is sent as ``billing_catalog``. With ``wait=True`` the operation
        is polled (every 2 s, up to 120 s by default) and ``{"operation": ..., "volume": ...}`` is
        returned; otherwise the accepted operation.

        Parameters
        ----------
        vm_type : typing.Optional[str]
            ``cloud`` or ``gpu``; must match the volume. Defaults to the volume's ``vm_type``.
        mode : typing.Optional[str]
            ``single-writer`` (default, as the portal) or ``multi-writer``.
        billing_catalog : typing.Optional[typing.Dict[str, typing.Any]]
            Only needed when the token cannot read the volume (then pass ``vm_type`` too).
        wait : bool
            Poll the operation until it finishes; raises ``OperationFailedError`` or ``OperationTimeoutError``.
        """
        return run_sync(self._client_wrapper, sw.attach_block_volume_to_vm(**clean_kwargs(locals())), request_options)

    def detach_block_volume_from_vm(
        self,
        volume_id: str,
        vm_id: typing.Optional[str] = None,
        *,
        workspace_id: str,
        vm_type: typing.Optional[str] = None,
        confirm_unmounted: bool = False,
        force: bool = False,
        requested_by: typing.Optional[str] = None,
        idempotency_key: typing.Optional[str] = None,
        wait: bool = False,
        timeout: float = VOLUME_OPERATION_TIMEOUT_SECONDS,
        poll_interval: float = VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Detaches a block volume from its VM the way the portal does. Requires scopes:
        block-storage.read and vm.write.

        Unmount the volume inside the server first and pass ``confirm_unmounted=True`` (the portal's
        mandatory tick), or ``force=True``. The VM is found from the volume's attachments when
        ``vm_id`` is omitted. With ``wait=True`` the operation is polled and
        ``{"operation": ..., "volume": ...}`` is returned.
        """
        return run_sync(self._client_wrapper, sw.detach_block_volume_from_vm(**clean_kwargs(locals())), request_options)

    def attach_block_volume(
        self,
        volume_id: str,
        *,
        workspace_id: str,
        node_name: str,
        mode: str = "single-writer",
        vm_id: typing.Optional[str] = None,
        vm_name: typing.Optional[str] = None,
        vm_state: typing.Optional[str] = None,
        vm_site_id: typing.Optional[str] = None,
        vm_type: str = "cloud",
        idempotency_key: typing.Optional[str] = None,
        check_state: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Advanced: records a storage-node attachment only and does not attach the disk to a VM.
        Use ``attach_block_volume_to_vm`` for VMs. Do not manage the same attachment through both
        surfaces. Requires scope: block-storage.write.

        ``mode`` is ``single-writer``/``multi-writer``, ``vm_state`` ``running``/``stopped``/
        ``suspended`` and ``vm_type`` ``cloud``/``gpu``. When ``vm_site_id`` is given the volume is
        read first and a different site is refused.
        """
        return run_sync(self._client_wrapper, sw.attach_block_volume(**clean_kwargs(locals())), request_options)

    def detach_block_volume(
        self,
        volume_id: str,
        *,
        workspace_id: str,
        node_name: typing.Optional[str] = None,
        force: bool = False,
        confirm_unmounted: bool = False,
        vm_state: typing.Optional[str] = None,
        vm_type: typing.Optional[str] = None,
        reason: typing.Optional[str] = None,
        idempotency_key: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Advanced: removes a storage-node attachment. Use ``detach_block_volume_from_vm`` for VMs.
        Requires scope: block-storage.write.

        A safe detach needs ``confirm_unmounted=True``, ``force=True`` or ``vm_state`` ``stopped``/
        ``suspended``. When ``node_name`` is omitted the volume is read and its only attachment is
        used (``vm_type`` then defaults to the volume's).
        """
        return run_sync(self._client_wrapper, sw.detach_block_volume(**clean_kwargs(locals())), request_options)

    def resize_block_volume(
        self,
        volume_id: str,
        *,
        workspace_id: str,
        new_size_gb: int,
        vm_state: typing.Optional[str] = None,
        allow_online: bool = False,
        idempotency_key: typing.Optional[str] = None,
        check_state: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Grows a block volume. Requires scope: block-storage.write.

        The volume is read first (skipped without ``block-storage.read`` or with
        ``check_state=False``): shrinking is refused, an attached volume needs ``vm_state``
        ``stopped``/``suspended`` or ``allow_online=True``, and a volume in the middle of another
        operation is refused. The same size is accepted by the API as a no-op. After growing, extend
        the filesystem inside the server.
        """
        return run_sync(self._client_wrapper, sw.resize_block_volume(**clean_kwargs(locals())), request_options)

    def wait_for_volume_operation(
        self,
        operation_id: str,
        *,
        workspace_id: str,
        timeout: float = VOLUME_OPERATION_TIMEOUT_SECONDS,
        poll_interval: float = VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> OperationStatus:
        """
        Polls a VM volume attach/detach operation like the portal (every 2 s, up to 120 s).
        Raises ``OperationFailedError`` (with the operation's error message) or ``OperationTimeoutError``.
        """
        return run_sync(self._client_wrapper, sw.wait_for_volume_operation(**clean_kwargs(locals())), request_options)


class AsyncBlockStorageClient:
    """Async variant of :class:`BlockStorageClient`.

    Every method validates its arguments before any request (``IbeeValidationError``)
    and raises typed ``ApiError`` subclasses for error responses. Volume records are
    returned as plain dicts.
    """

    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper
        self._http = client_wrapper.httpx_client

    async def list_block_volumes(
        self,
        *,
        workspace_id: str,
        site_id: typing.Optional[str] = None,
        vm_type: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """
        Lists block volumes (newest first). Requires scope: block-storage.read.

        The API returns at most ``limit`` volumes (default 100); use ``iter_block_volumes`` or
        ``list_all_block_volumes`` to read every page.

        Parameters
        ----------
        workspace_id : str
            The workspace ID to scope this request to.
        site_id : typing.Optional[str]
            Only volumes in this site.
        vm_type : typing.Optional[str]
            ``cloud`` or ``gpu``: only volumes created for that kind of VM.
        limit : typing.Optional[int]
            Page size, 1-1000 (API default 100).
        offset : typing.Optional[int]
            Number of volumes to skip (>= 0).
        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.
        """
        return await run_async(self._client_wrapper, sw.list_block_volumes(**clean_kwargs(locals())), request_options)

    def iter_block_volumes(
        self,
        *,
        workspace_id: str,
        site_id: typing.Optional[str] = None,
        vm_type: typing.Optional[str] = None,
        page_size: int = 100,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.AsyncIterator[typing.Dict[str, typing.Any]]:
        """Yields every block volume, fetching ``page_size`` (1-1000) volumes per request."""
        size = validate_page_size(page_size, maximum=1000)
        validate_block_volume_list_params(site_id=site_id, vm_type=vm_type)

        async def fetch(limit: int, offset: int) -> typing.List[typing.Any]:
            page = await self.list_block_volumes(
                workspace_id=workspace_id, site_id=site_id, vm_type=vm_type, limit=limit, offset=offset,
                request_options=request_options,
            )
            return page or []

        return apaginate_offset(fetch, page_size=size, id_keys=("id", "_id"))

    async def list_all_block_volumes(
        self,
        *,
        workspace_id: str,
        site_id: typing.Optional[str] = None,
        vm_type: typing.Optional[str] = None,
        page_size: int = 100,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """Every block volume in the workspace, as one list (see ``iter_block_volumes``)."""
        return [item async for item in self.iter_block_volumes(workspace_id=workspace_id, site_id=site_id,
                                                                  vm_type=vm_type, page_size=page_size,
                                                                  request_options=request_options)]

    async def create_block_volume(
        self,
        *,
        workspace_id: str,
        name: str,
        size_gb: int,
        site_id: str,
        site_name: typing.Optional[str] = None,
        sku_code: typing.Optional[str] = None,
        volume_class: str = "balanced",
        replica_count: int = 2,
        backup_enabled: bool = True,
        vm_type: typing.Optional[str] = None,
        delete_on_termination: typing.Optional[bool] = None,
        idempotency_key: typing.Optional[str] = None,
        resolve_site_name: bool = True,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Creates a block volume like the portal. Requires scope: block-storage.write.

        The API checks billing and uses the site's Block Storage plan; no ``billing_catalog`` is
        sent. Creation is synchronous: the result is ``{"volume": ..., "operation": ...}`` with the
        volume ``ready``.

        Parameters
        ----------
        workspace_id : str
            The workspace ID to scope this request to.
        name : str
            3-255 lowercase letters, numbers and hyphens (the portal rule), unique in the workspace.
        size_gb : int
            Whole GB, 10-10000. The site's plan may allow only some sizes (the API answers 400).
        site_id : str
            Compute site ID (from ``compute_catalog.list_compute_sites``).
        site_name : typing.Optional[str]
            Site display name. When omitted and ``resolve_site_name`` is true, it is read from the
            compute sites (needs ``vm.read``; skipped when not allowed), and an unknown ``site_id``
            is rejected.
        sku_code : typing.Optional[str]
            Block Storage SKU when a site has several plans (upper-cased; root-disk SKUs rejected).
        volume_class : str
            ``capacity``, ``balanced`` (default) or ``performance``.
        replica_count : int
            1-5 (default 2).
        backup_enabled : bool
            Default ``True``.
        vm_type : typing.Optional[str]
            ``cloud`` (API default) or ``gpu``. A GPU VM can attach only a volume created with
            ``vm_type="gpu"``. Not yet part of the published API contract; behaviour may change.
        delete_on_termination : typing.Optional[bool]
            Delete the volume when its VM is deleted (API default ``False``). Not yet part of the
            published API contract; behaviour may change.
        idempotency_key : typing.Optional[str]
            Makes retries safe; generated when omitted and sent in the body and as ``X-Idempotency-Key``.
        resolve_site_name : bool
            ``False`` skips the compute-sites lookup.
        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.
        """
        return await run_async(self._client_wrapper, sw.create_block_volume(**clean_kwargs(locals())), request_options)

    async def get_block_volume(
        self, volume_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Dict[str, typing.Any]:
        """
        Returns a block volume, including ``attachments``, ``vm_type`` and ``metadata.billing_catalog``.
        Requires scope: block-storage.read. ``volume_id`` is 24 hexadecimal characters.
        """
        return await run_async(self._client_wrapper, sw.get_block_volume(**clean_kwargs(locals())), request_options)

    async def delete_block_volume(
        self,
        volume_id: str,
        *,
        workspace_id: str,
        force: bool = False,
        idempotency_key: typing.Optional[str] = None,
        check_state: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Deletes a block volume. Requires scope: block-storage.write.

        Like the portal, the volume is read first (skipped when the token lacks
        ``block-storage.read``): an attached volume is refused ("Detach this volume from all servers
        before deleting.") and so is one in the middle of another operation. ``force=True`` skips
        these checks and makes the API detach the volume from every server and erase all data.
        ``idempotency_key`` is sent as a query parameter and generated when omitted (not yet part of
        the published API contract; behaviour may change). Deletion is synchronous.

        Parameters
        ----------
        check_state : typing.Optional[bool]
            ``False`` skips reading the volume first.
        """
        return await run_async(self._client_wrapper, sw.delete_block_volume(**clean_kwargs(locals())), request_options)

    async def list_block_volume_operations(
        self,
        volume_id: str,
        *,
        workspace_id: str,
        limit: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """
        Lists a volume's operations, newest first. Requires scope: block-storage.read.
        ``limit`` is 1-200 (API default 20).
        """
        return await run_async(self._client_wrapper, sw.list_block_volume_operations(**clean_kwargs(locals())), request_options)

    async def attach_block_volume_to_vm(
        self,
        volume_id: str,
        vm_id: str,
        *,
        workspace_id: str,
        vm_type: typing.Optional[str] = None,
        mode: typing.Optional[str] = None,
        billing_catalog: typing.Optional[typing.Dict[str, typing.Any]] = None,
        requested_by: typing.Optional[str] = None,
        idempotency_key: typing.Optional[str] = None,
        wait: bool = False,
        timeout: float = VOLUME_OPERATION_TIMEOUT_SECONDS,
        poll_interval: float = VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
        check_state: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Attaches a block volume to a cloud or GPU VM the way the portal does. Requires scopes:
        block-storage.read and vm.write (vm.read for the VM checks).

        The volume is read first: it must be unattached and idle, the VM must be in the volume's
        site and of the volume's ``vm_type`` (which also picks the cloud or GPU endpoint), and the
        volume's Block Storage SKU is sent as ``billing_catalog``. With ``wait=True`` the operation
        is polled (every 2 s, up to 120 s by default) and ``{"operation": ..., "volume": ...}`` is
        returned; otherwise the accepted operation.

        Parameters
        ----------
        vm_type : typing.Optional[str]
            ``cloud`` or ``gpu``; must match the volume. Defaults to the volume's ``vm_type``.
        mode : typing.Optional[str]
            ``single-writer`` (default, as the portal) or ``multi-writer``.
        billing_catalog : typing.Optional[typing.Dict[str, typing.Any]]
            Only needed when the token cannot read the volume (then pass ``vm_type`` too).
        wait : bool
            Poll the operation until it finishes; raises ``OperationFailedError`` or ``OperationTimeoutError``.
        """
        return await run_async(self._client_wrapper, sw.attach_block_volume_to_vm(**clean_kwargs(locals())), request_options)

    async def detach_block_volume_from_vm(
        self,
        volume_id: str,
        vm_id: typing.Optional[str] = None,
        *,
        workspace_id: str,
        vm_type: typing.Optional[str] = None,
        confirm_unmounted: bool = False,
        force: bool = False,
        requested_by: typing.Optional[str] = None,
        idempotency_key: typing.Optional[str] = None,
        wait: bool = False,
        timeout: float = VOLUME_OPERATION_TIMEOUT_SECONDS,
        poll_interval: float = VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Detaches a block volume from its VM the way the portal does. Requires scopes:
        block-storage.read and vm.write.

        Unmount the volume inside the server first and pass ``confirm_unmounted=True`` (the portal's
        mandatory tick), or ``force=True``. The VM is found from the volume's attachments when
        ``vm_id`` is omitted. With ``wait=True`` the operation is polled and
        ``{"operation": ..., "volume": ...}`` is returned.
        """
        return await run_async(self._client_wrapper, sw.detach_block_volume_from_vm(**clean_kwargs(locals())), request_options)

    async def attach_block_volume(
        self,
        volume_id: str,
        *,
        workspace_id: str,
        node_name: str,
        mode: str = "single-writer",
        vm_id: typing.Optional[str] = None,
        vm_name: typing.Optional[str] = None,
        vm_state: typing.Optional[str] = None,
        vm_site_id: typing.Optional[str] = None,
        vm_type: str = "cloud",
        idempotency_key: typing.Optional[str] = None,
        check_state: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Advanced: records a storage-node attachment only and does not attach the disk to a VM.
        Use ``attach_block_volume_to_vm`` for VMs. Do not manage the same attachment through both
        surfaces. Requires scope: block-storage.write.

        ``mode`` is ``single-writer``/``multi-writer``, ``vm_state`` ``running``/``stopped``/
        ``suspended`` and ``vm_type`` ``cloud``/``gpu``. When ``vm_site_id`` is given the volume is
        read first and a different site is refused.
        """
        return await run_async(self._client_wrapper, sw.attach_block_volume(**clean_kwargs(locals())), request_options)

    async def detach_block_volume(
        self,
        volume_id: str,
        *,
        workspace_id: str,
        node_name: typing.Optional[str] = None,
        force: bool = False,
        confirm_unmounted: bool = False,
        vm_state: typing.Optional[str] = None,
        vm_type: typing.Optional[str] = None,
        reason: typing.Optional[str] = None,
        idempotency_key: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Advanced: removes a storage-node attachment. Use ``detach_block_volume_from_vm`` for VMs.
        Requires scope: block-storage.write.

        A safe detach needs ``confirm_unmounted=True``, ``force=True`` or ``vm_state`` ``stopped``/
        ``suspended``. When ``node_name`` is omitted the volume is read and its only attachment is
        used (``vm_type`` then defaults to the volume's).
        """
        return await run_async(self._client_wrapper, sw.detach_block_volume(**clean_kwargs(locals())), request_options)

    async def resize_block_volume(
        self,
        volume_id: str,
        *,
        workspace_id: str,
        new_size_gb: int,
        vm_state: typing.Optional[str] = None,
        allow_online: bool = False,
        idempotency_key: typing.Optional[str] = None,
        check_state: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Grows a block volume. Requires scope: block-storage.write.

        The volume is read first (skipped without ``block-storage.read`` or with
        ``check_state=False``): shrinking is refused, an attached volume needs ``vm_state``
        ``stopped``/``suspended`` or ``allow_online=True``, and a volume in the middle of another
        operation is refused. The same size is accepted by the API as a no-op. After growing, extend
        the filesystem inside the server.
        """
        return await run_async(self._client_wrapper, sw.resize_block_volume(**clean_kwargs(locals())), request_options)

    async def wait_for_volume_operation(
        self,
        operation_id: str,
        *,
        workspace_id: str,
        timeout: float = VOLUME_OPERATION_TIMEOUT_SECONDS,
        poll_interval: float = VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> OperationStatus:
        """
        Polls a VM volume attach/detach operation like the portal (every 2 s, up to 120 s).
        Raises ``OperationFailedError`` (with the operation's error message) or ``OperationTimeoutError``.
        """
        return await run_async(self._client_wrapper, sw.wait_for_volume_operation(**clean_kwargs(locals())), request_options)
