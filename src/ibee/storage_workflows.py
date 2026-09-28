# Hand-written (listed in .fernignore).
"""Portal-equivalent request flows for Block Storage, Object Storage and CDN.

Flows use the :class:`~ibee.compute_workflows.Call` / ``run_sync`` / ``run_async``
pattern, so ``Ibee`` and ``AsyncIbee`` share one implementation. Every rule is
checked with :mod:`ibee.validation` before the request it guards.
"""

from __future__ import annotations

import typing

from . import compute_workflows as cw
from . import operations as _operations
from .compute_workflows import Call, Flow, Sleep, billing_preflight
from .errors.forbidden_error import ForbiddenError
from .errors.not_found_error import NotFoundError
from .errors.operation_errors import OperationFailedError, OperationTimeoutError
from .errors.storage_errors import raise_for_cdn_purge
from .idempotency import build_idempotency_key
from .operations import is_transient_poll_error
from .types.bucket import Bucket
from .types.bucket_list import BucketList
from .types.delete_response import DeleteResponse
from .types.operation_accepted import OperationAccepted
from .types.operation_status import OperationStatus
from .types.s3credential import S3Credential
from .types.s3credential_created import S3CredentialCreated
from .types.s3credential_list import S3CredentialList
from .types.s3credential_revoked import S3CredentialRevoked
from .validation import (
    IbeeValidationError,
    NODE_LEVEL_ADVANCED_NOTE,
    validate_billing_catalog,
    VOLUME_OPERATION_FAILED_MESSAGE,
    VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
    VOLUME_OPERATION_TIMEOUT_MESSAGE,
    VOLUME_OPERATION_TIMEOUT_SECONDS,
    assert_volume_attachable,
    build_block_volume_create_body,
    build_bucket_create_body,
    build_cdn_distribution_create_body,
    build_cdn_distribution_update_body,
    build_cdn_purge_body,
    build_s3_credential_body,
    check_bucket_deletable,
    check_cdn_origin_public,
    check_volume_deletable,
    check_volume_resizable,
    normalize_cdn_domain,
    record_get,
    resolve_object_storage_region,
    resolve_single_attachment,
    validate_block_volume_id,
    validate_block_volume_list_params,
    validate_bucket_list_params,
    validate_bucket_path_name,
    validate_cdn_generate_url,
    validate_cdn_index_document,
    validate_cdn_metrics_range,
    validate_idempotency_key,
    validate_node_safe_detach,
    validate_operation_id,
    validate_poll_interval,
    validate_required_text,
    validate_resize_request,
    validate_vm_detach_confirmation,
    validate_vm_id,
    validate_volume_attach_mode,
    validate_volume_operations_limit,
    validate_volume_vm_state,
    validate_volume_vm_type,
    validate_wait_timeout,
    volume_vm_type,
)
from .billing.admission import CUSTOM_DOMAIN_SKU_CODE, OBJECT_STORAGE_SKU_CODE

__all__ = [
    "CUSTOM_DOMAIN_ESTIMATED_COST_MINOR",
    "CUSTOM_DOMAIN_SKU_CODE",
    "NODE_LEVEL_ADVANCED_NOTE",
    "wait_for_volume_operation",
]

#: Estimate the portal checks (with CUSTOMDO-STD) before adding a CDN custom domain.
CUSTOM_DOMAIN_ESTIMATED_COST_MINOR = 19900
#: ``ibee cdn domains verify --wait`` cadence (the portal asks users to retry after a few minutes).
CDN_DOMAIN_POLL_INTERVAL_SECONDS = 15.0
CDN_DOMAIN_TIMEOUT_SECONDS = 600.0
_CDN_DOMAIN_TERMINAL = frozenset({"active", "failed"})

_ws = cw._ws
_seg = cw._seg
_compact = cw._compact


def _key(idempotency_key: typing.Optional[str], action: str, *identity: typing.Any) -> str:
    """Validate a caller key, or build one (``block-volume-<action>-<identity>-...``)."""
    if idempotency_key is None:
        return build_idempotency_key(f"block-volume-{action}", *identity)
    return validate_idempotency_key(idempotency_key)


# ---------------------------------------------------------------------------
# Waiting for VM attach/detach operations
# ---------------------------------------------------------------------------


def _operation_failed(operation: typing.Any) -> OperationFailedError:
    error = OperationFailedError(operation)
    detail = record_get(operation, "error_message") or VOLUME_OPERATION_FAILED_MESSAGE
    error.message = f"{detail} (operation {error.operation_id})"
    error.args = (error.message,)
    return error


def wait_for_volume_operation(
    *,
    workspace_id: str,
    operation_id: typing.Any,
    timeout: typing.Any = VOLUME_OPERATION_TIMEOUT_SECONDS,
    poll_interval: typing.Any = VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
) -> Flow[OperationStatus]:
    """Poll ``GET /compute/operations/{id}`` like the portal (every 2 s, up to 120 s by default).

    ``succeeded`` returns the operation; ``failed``/``cancelled``/``timed_out`` raise
    :class:`OperationFailedError` with the operation's ``error_message``; the
    client-side timeout raises :class:`OperationTimeoutError`.
    """
    op_id = validate_operation_id(operation_id)
    wait_timeout = validate_wait_timeout(timeout)
    interval = validate_poll_interval(poll_interval, wait_timeout)
    deadline = _operations._clock() + wait_timeout
    failures = 0
    last: typing.Any = None
    while True:
        try:
            current = yield Call("GET", f"compute/operations/{_seg(op_id)}", params=_ws(workspace_id), parse=OperationStatus)
        except Exception as exc:
            if not is_transient_poll_error(exc):
                raise
            failures += 1
            if failures >= _operations.MAX_CONSECUTIVE_POLL_FAILURES:
                raise
        else:
            failures = 0
            last = current
            status = str(record_get(current, "status") or "").strip().lower()
            if status in _operations.SUCCESS_STATUSES:
                return typing.cast(OperationStatus, current)
            if status in _operations.FAILURE_STATUSES:
                raise _operation_failed(current)
        remaining = deadline - _operations._clock()
        if remaining <= 0:
            error = OperationTimeoutError(last, timeout=wait_timeout, operation_id=op_id)
            error.message = f"{VOLUME_OPERATION_TIMEOUT_MESSAGE} (operation {op_id})"
            error.args = (error.message,)
            raise error
        yield Sleep(min(interval, remaining))


# ---------------------------------------------------------------------------
# Block Storage
# ---------------------------------------------------------------------------


def _volume_path(volume_id: str, suffix: str = "") -> str:
    return f"block-storage/volumes/{_seg(volume_id)}{suffix}"


def _get_volume(workspace_id: str, volume_id: str) -> Flow[typing.Any]:
    volume = yield Call("GET", _volume_path(volume_id), params=_ws(workspace_id))
    return volume


def _get_volume_or_none(workspace_id: str, volume_id: str) -> Flow[typing.Any]:
    """Best-effort read: ``None`` when the token lacks ``block-storage.read``."""
    try:
        volume = yield from _get_volume(workspace_id, volume_id)
    except ForbiddenError:
        return None
    return volume


def list_block_volumes(
    *,
    workspace_id: str,
    site_id: typing.Any = None,
    vm_type: typing.Any = None,
    limit: typing.Any = None,
    offset: typing.Any = None,
) -> Flow[typing.Any]:
    params = validate_block_volume_list_params(site_id=site_id, vm_type=vm_type, limit=limit, offset=offset)
    result = yield Call("GET", "block-storage/volumes", params=_ws(workspace_id, **params), main=True)
    return result


def _resolve_site_name(workspace_id: str, site_id: str) -> Flow[typing.Optional[str]]:
    """The portal's site picker: the compute site's name, or ``None`` when sites cannot be read."""
    try:
        data = yield Call("GET", "compute/sites", params=_ws(workspace_id))
    except (ForbiddenError, NotFoundError):
        return None
    sites = record_get(data, "sites")
    if not isinstance(sites, list):
        return None
    for site in sites:
        if str(record_get(site, "site_id") or "").strip() == site_id:
            name = record_get(site, "name")
            return str(name).strip() if name else None
    raise IbeeValidationError(
        "Unknown site_id",
        code="unknown_site_id",
        field="site_id",
        details={"site_ids": [record_get(site, "site_id") for site in sites]},
    )


def create_block_volume(
    *,
    workspace_id: str,
    name: typing.Any,
    size_gb: typing.Any,
    site_id: typing.Any,
    site_name: typing.Any = None,
    sku_code: typing.Any = None,
    volume_class: typing.Any = "balanced",
    replica_count: typing.Any = 2,
    backup_enabled: typing.Any = True,
    vm_type: typing.Any = None,
    delete_on_termination: typing.Any = None,
    idempotency_key: typing.Optional[str] = None,
    resolve_site_name: typing.Optional[bool] = True,
) -> Flow[typing.Any]:
    body = build_block_volume_create_body(
        name=name,
        size_gb=size_gb,
        site_id=site_id,
        site_name=site_name,
        sku_code=sku_code,
        volume_class=volume_class,
        replica_count=replica_count,
        backup_enabled=backup_enabled,
        vm_type=vm_type,
        delete_on_termination=delete_on_termination,
    )
    key = _key(idempotency_key, "create", body["name"])
    if "site_name" not in body and resolve_site_name is not False:
        resolved = yield from _resolve_site_name(workspace_id, body["site_id"])
        if resolved:
            body["site_name"] = resolved
    body["idempotency_key"] = key
    result = yield Call(
        "POST",
        "block-storage/volumes",
        params=_ws(workspace_id),
        json=body,
        headers={"X-Idempotency-Key": key},
        main=True,
    )
    return result


def get_block_volume(*, workspace_id: str, volume_id: typing.Any) -> Flow[typing.Any]:
    volume_id = validate_block_volume_id(volume_id)
    result = yield Call("GET", _volume_path(volume_id), params=_ws(workspace_id), main=True)
    return result


def delete_block_volume(
    *,
    workspace_id: str,
    volume_id: typing.Any,
    force: typing.Any = False,
    idempotency_key: typing.Optional[str] = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[typing.Any]:
    volume_id = validate_block_volume_id(volume_id)
    if not isinstance(force, bool):
        raise IbeeValidationError("force must be true or false.", code="invalid_force", field="force")
    key = _key(idempotency_key, "delete", volume_id)
    if not force and check_state is not False:
        volume = yield from _get_volume_or_none(workspace_id, volume_id)
        if volume is not None:
            check_volume_deletable(volume)
    result = yield Call(
        "DELETE",
        _volume_path(volume_id),
        params=_ws(workspace_id, force=force, idempotency_key=key),
        main=True,
    )
    return result


def list_block_volume_operations(*, workspace_id: str, volume_id: typing.Any, limit: typing.Any = None) -> Flow[typing.Any]:
    volume_id = validate_block_volume_id(volume_id)
    value = validate_volume_operations_limit(limit)
    result = yield Call("GET", _volume_path(volume_id, "/operations"), params=_ws(workspace_id, limit=value), main=True)
    return result


def attach_block_volume(
    *,
    workspace_id: str,
    volume_id: typing.Any,
    node_name: typing.Any,
    mode: typing.Any = "single-writer",
    vm_id: typing.Any = None,
    vm_name: typing.Any = None,
    vm_state: typing.Any = None,
    vm_site_id: typing.Any = None,
    vm_type: typing.Any = "cloud",
    idempotency_key: typing.Optional[str] = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[typing.Any]:
    volume_id = validate_block_volume_id(volume_id)
    body = {
        "node_name": validate_required_text(node_name, field="node_name"),
        "mode": validate_volume_attach_mode("single-writer" if mode is None else mode),
        "vm_id": vm_id,
        "vm_name": vm_name,
        "vm_state": validate_volume_vm_state(vm_state),
        "vm_site_id": vm_site_id.strip() if isinstance(vm_site_id, str) and vm_site_id.strip() else None,
        "vm_type": validate_volume_vm_type("cloud" if vm_type is None else vm_type),
        "idempotency_key": _key(idempotency_key, "attach", volume_id),
    }
    if body["vm_site_id"] and check_state is not False:
        volume = yield from _get_volume_or_none(workspace_id, volume_id)
        volume_site = str(record_get(volume, "site_id") or "").strip() if volume is not None else ""
        if volume_site and volume_site != body["vm_site_id"]:
            site_name = record_get(volume, "site_name") or volume_site
            raise IbeeValidationError(f"Select a server in {site_name}", code="site_mismatch", field="vm_site_id")
    result = yield Call("POST", _volume_path(volume_id, "/attachments"), params=_ws(workspace_id), json=_compact(body), main=True)
    return result


def detach_block_volume(
    *,
    workspace_id: str,
    volume_id: typing.Any,
    node_name: typing.Any = None,
    force: typing.Any = False,
    confirm_unmounted: typing.Any = False,
    vm_state: typing.Any = None,
    vm_type: typing.Any = None,
    reason: typing.Any = None,
    idempotency_key: typing.Optional[str] = None,
) -> Flow[typing.Any]:
    volume_id = validate_block_volume_id(volume_id)
    state = validate_volume_vm_state(vm_state)
    validate_node_safe_detach(force, confirm_unmounted, state)
    kind = validate_volume_vm_type(vm_type)
    key = _key(idempotency_key, "detach", volume_id)
    if node_name is None:
        volume = yield from _get_volume(workspace_id, volume_id)
        attachment = resolve_single_attachment(volume)
        node = str(record_get(attachment, "node_name") or "").strip()
        if not node:
            raise IbeeValidationError("The attachment has no node_name; pass node_name.", code="invalid_node_name", field="node_name")
        kind = kind or volume_vm_type(volume)
    else:
        node = validate_required_text(node_name, field="node_name")
    body = {
        "node_name": node,
        "force": force is True,
        "confirm_unmounted": confirm_unmounted is True,
        "vm_state": state,
        "vm_type": kind or "cloud",
        "reason": reason,
        "idempotency_key": key,
    }
    result = yield Call("POST", _volume_path(volume_id, "/detach"), params=_ws(workspace_id), json=_compact(body), main=True)
    return result


def resize_block_volume(
    *,
    workspace_id: str,
    volume_id: typing.Any,
    new_size_gb: typing.Any,
    vm_state: typing.Any = None,
    allow_online: typing.Any = False,
    idempotency_key: typing.Optional[str] = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[typing.Any]:
    volume_id = validate_block_volume_id(volume_id)
    size, state, online = validate_resize_request(new_size_gb, vm_state, allow_online)
    key = _key(idempotency_key, "resize", volume_id)
    if check_state is not False:
        volume = yield from _get_volume_or_none(workspace_id, volume_id)
        if volume is not None:
            check_volume_resizable(volume, size, state, online)
    body = {"new_size_gb": size, "vm_state": state, "allow_online": online, "idempotency_key": key}
    result = yield Call("POST", _volume_path(volume_id, "/resize"), params=_ws(workspace_id), json=_compact(body), main=True)
    return result


def _family_for(vm_type: str) -> str:
    return "gpu" if vm_type == "gpu" else "cloud"


def attach_block_volume_to_vm(
    *,
    workspace_id: str,
    volume_id: typing.Any,
    vm_id: typing.Any,
    vm_type: typing.Any = None,
    mode: typing.Any = None,
    billing_catalog: typing.Any = None,
    requested_by: typing.Any = None,
    idempotency_key: typing.Optional[str] = None,
    wait: bool = False,
    timeout: typing.Any = VOLUME_OPERATION_TIMEOUT_SECONDS,
    poll_interval: typing.Any = VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
    check_state: typing.Optional[bool] = None,
) -> Flow[typing.Any]:
    """The portal's attach: read the volume, pick the cloud/GPU endpoint from its ``vm_type``, attach, optionally wait."""
    volume_id = validate_block_volume_id(volume_id)
    vm_id = validate_vm_id(vm_id)
    requested_type = validate_volume_vm_type(vm_type)
    validate_volume_attach_mode(mode)
    if billing_catalog is not None:
        # Checked before any request (the VM attach checks it again).
        validate_billing_catalog(billing_catalog, expected_product="block_storage")
    if wait:
        validate_poll_interval(poll_interval, validate_wait_timeout(timeout))
    try:
        volume = yield from _get_volume(workspace_id, volume_id)
    except ForbiddenError:
        if billing_catalog is None:
            raise IbeeValidationError(
                "billing_catalog is required; grant block-storage.read or pass billing_catalog",
                code="volume_unreadable",
                field="billing_catalog",
            )
        volume = None  # vm_type defaults to 'cloud' (as in the TypeScript SDK)
    target_type = requested_type or (volume_vm_type(volume) if volume is not None else "cloud")
    if volume is not None:
        assert_volume_attachable(volume, target_type)
    accepted = yield from cw.attach_volume(
        _family_for(target_type),
        workspace_id=workspace_id,
        vm_id=vm_id,
        volume_id=volume_id,
        idempotency_key=idempotency_key,
        mode=mode,
        billing_catalog=billing_catalog,
        requested_by=requested_by,
        check_state=check_state,
        volume=volume,
        skip_volume_read=volume is None,
    )
    if not wait:
        return accepted
    operation = yield from wait_for_volume_operation(
        workspace_id=workspace_id,
        operation_id=record_get(accepted, "operation_id"),
        timeout=timeout,
        poll_interval=poll_interval,
    )
    refreshed = yield from _get_volume_or_none(workspace_id, volume_id)
    return {"operation": operation, "volume": refreshed}


def detach_block_volume_from_vm(
    *,
    workspace_id: str,
    volume_id: typing.Any,
    vm_id: typing.Any = None,
    vm_type: typing.Any = None,
    confirm_unmounted: typing.Any = False,
    force: typing.Any = False,
    requested_by: typing.Any = None,
    idempotency_key: typing.Optional[str] = None,
    wait: bool = False,
    timeout: typing.Any = VOLUME_OPERATION_TIMEOUT_SECONDS,
    poll_interval: typing.Any = VOLUME_OPERATION_POLL_INTERVAL_SECONDS,
) -> Flow[typing.Any]:
    """The portal's detach: find the VM the volume is attached to, detach it there, optionally wait."""
    volume_id = validate_block_volume_id(volume_id)
    validate_vm_detach_confirmation(confirm_unmounted, force)
    requested_type = validate_volume_vm_type(vm_type)
    target_vm = validate_vm_id(vm_id) if vm_id is not None else None
    if wait:
        validate_poll_interval(poll_interval, validate_wait_timeout(timeout))
    try:
        volume = yield from _get_volume(workspace_id, volume_id)
    except ForbiddenError:
        if target_vm is None:
            raise IbeeValidationError(
                "Reading the volume needs block-storage.read; grant it or pass vm_id and vm_type",
                code="volume_unreadable",
                field="vm_id",
            )
        volume = None
    attachment = None
    if volume is not None:
        attachment = resolve_single_attachment(volume, vm_id=target_vm, for_vm=True)
        target_vm = str(record_get(attachment, "vm_id")).strip()
    kind = (
        requested_type
        or str(record_get(attachment, "vm_type") or "").strip().lower()
        or (volume_vm_type(volume) if volume is not None else "cloud")
    )
    accepted = yield from cw.detach_volume(
        _family_for(kind),
        workspace_id=workspace_id,
        vm_id=typing.cast(str, target_vm),
        volume_id=volume_id,
        idempotency_key=idempotency_key,
        confirm_unmounted=confirm_unmounted,
        force=force,
        requested_by=requested_by,
    )
    if not wait:
        return accepted
    operation = yield from wait_for_volume_operation(
        workspace_id=workspace_id,
        operation_id=record_get(accepted, "operation_id"),
        timeout=timeout,
        poll_interval=poll_interval,
    )
    refreshed = yield from _get_volume_or_none(workspace_id, volume_id)
    return {"operation": operation, "volume": refreshed}


# ---------------------------------------------------------------------------
# Object Storage
# ---------------------------------------------------------------------------


def _bucket_path(bucket_name: str) -> str:
    return f"object-storage/buckets/{_seg(bucket_name)}"


def list_buckets(*, workspace_id: str, limit: typing.Any = None, continuation_token: typing.Any = None) -> Flow[BucketList]:
    params = validate_bucket_list_params(limit, continuation_token)
    result = yield Call("GET", "object-storage/buckets", params=_ws(workspace_id, **params), parse=BucketList, main=True)
    return typing.cast(BucketList, result)


def create_bucket(
    *,
    workspace_id: str,
    name: typing.Any,
    region: typing.Any = None,
    is_public: typing.Any = None,
    object_lock_enabled: typing.Any = None,
    default_retention: typing.Any = None,
    tags: typing.Any = None,
    preflight_billing: typing.Optional[bool] = None,
    base_url: typing.Optional[str] = None,
) -> Flow[Bucket]:
    body = build_bucket_create_body(
        name=name,
        region=resolve_object_storage_region(region, base_url),
        is_public=is_public,
        object_lock_enabled=object_lock_enabled,
        default_retention=default_retention,
        tags=tags,
    )
    if preflight_billing:
        yield from billing_preflight(workspace_id, sku_code=OBJECT_STORAGE_SKU_CODE, resource_type="object_storage")
    result = yield Call("POST", "object-storage/buckets", params=_ws(workspace_id), json=body, parse=Bucket, main=True)
    return typing.cast(Bucket, result)


def get_bucket(*, workspace_id: str, bucket_name: typing.Any) -> Flow[Bucket]:
    name = validate_bucket_path_name(bucket_name)
    result = yield Call("GET", _bucket_path(name), params=_ws(workspace_id), parse=Bucket, main=True)
    return typing.cast(Bucket, result)


def update_bucket(*, workspace_id: str, bucket_name: typing.Any, is_public: typing.Any) -> Flow[Bucket]:
    name = validate_bucket_path_name(bucket_name)
    if not isinstance(is_public, bool):
        raise IbeeValidationError("is_public must be true or false.", code="invalid_is_public", field="is_public")
    result = yield Call(
        "PATCH", _bucket_path(name), params=_ws(workspace_id), json={"is_public": is_public}, parse=Bucket, main=True
    )
    return typing.cast(Bucket, result)


def delete_bucket(
    *,
    workspace_id: str,
    bucket_name: typing.Any,
    skip_preflight: typing.Optional[bool] = False,
    check_state: typing.Optional[bool] = None,
) -> Flow[DeleteResponse]:
    name = validate_bucket_path_name(bucket_name)
    if check_state is not False:
        try:
            bucket = yield Call("GET", _bucket_path(name), params=_ws(workspace_id))
        except ForbiddenError:
            bucket = None  # no object-storage.read: the API still refuses non-empty or locked buckets
        if bucket is not None:
            check_bucket_deletable(bucket, skip_preflight=bool(skip_preflight))
    result = yield Call("DELETE", _bucket_path(name), params=_ws(workspace_id), parse=DeleteResponse, main=True)
    return typing.cast(DeleteResponse, result)


def list_s3credentials(*, workspace_id: str) -> Flow[S3CredentialList]:
    result = yield Call("GET", "object-storage/credentials", params=_ws(workspace_id), parse=S3CredentialList, main=True)
    return typing.cast(S3CredentialList, result)


def create_s3credential(
    *,
    workspace_id: str,
    name: typing.Any = None,
    permission_type: typing.Any = None,
    bucket_scope: typing.Any = None,
    allowed_buckets: typing.Any = None,
    preflight_billing: typing.Optional[bool] = None,
) -> Flow[S3CredentialCreated]:
    try:
        body = build_s3_credential_body(
            name=name, permission_type=permission_type, bucket_scope=bucket_scope, allowed_buckets=allowed_buckets
        )
    except IbeeValidationError as exc:
        if permission_type is None and exc.field == "bucket_scope":
            exc.message = f"{exc.message} (permission_type defaults to admin_rw; pass permission_type='object_rw' or 'object_ro')"
            exc.args = (exc.message,)
        raise
    if preflight_billing:
        yield from billing_preflight(workspace_id, sku_code=OBJECT_STORAGE_SKU_CODE, resource_type="s3_credential")
    result = yield Call(
        "POST", "object-storage/credentials", params=_ws(workspace_id), json=body, parse=S3CredentialCreated, main=True
    )
    return typing.cast(S3CredentialCreated, result)


def _credential_path(access_key_id: typing.Any) -> str:
    return f"object-storage/credentials/{_seg(validate_required_text(access_key_id, field='access_key_id'))}"


def get_s3credential(*, workspace_id: str, access_key_id: typing.Any) -> Flow[S3Credential]:
    path = _credential_path(access_key_id)
    result = yield Call("GET", path, params=_ws(workspace_id), parse=S3Credential, main=True)
    return typing.cast(S3Credential, result)


def delete_s3credential(*, workspace_id: str, access_key_id: typing.Any) -> Flow[S3CredentialRevoked]:
    path = _credential_path(access_key_id)
    result = yield Call("DELETE", path, params=_ws(workspace_id), parse=S3CredentialRevoked, main=True)
    return typing.cast(S3CredentialRevoked, result)


# ---------------------------------------------------------------------------
# CDN
# ---------------------------------------------------------------------------


def _dist_path(distribution_id: typing.Any, suffix: str = "") -> str:
    distribution = validate_required_text(distribution_id, field="distribution_id")
    return f"cdn/distributions/{_seg(distribution)}{suffix}"


def _domain_path(distribution_id: typing.Any, domain: typing.Any, suffix: str = "") -> str:
    return _dist_path(distribution_id, f"/custom-domains/{_seg(normalize_cdn_domain(domain))}{suffix}")


def _simple(method: str, path: str, workspace_id: str, json: typing.Any = None, **params: typing.Any) -> Flow[typing.Any]:
    result = yield Call(method, path, params=_ws(workspace_id, **params), json=json, main=True)
    return result


def generate_cdn_url(
    *, workspace_id: str, bucket_name: typing.Any, object_key: typing.Any, expires_in: typing.Any = None, disposition: typing.Any = None
) -> Flow[typing.Any]:
    body = validate_cdn_generate_url(
        bucket_name=bucket_name, object_key=object_key, expires_in=expires_in, disposition=disposition
    )
    return (yield from _simple("POST", "cdn/generate-url", workspace_id, json=body))


def list_cdn_distributions(*, workspace_id: str) -> Flow[typing.Any]:
    return (yield from _simple("GET", "cdn/distributions", workspace_id))


def list_cdn_cache_policies(*, workspace_id: str) -> Flow[typing.Any]:
    return (yield from _simple("GET", "cdn/distributions/cache-policies", workspace_id))


def create_cdn_distribution(
    *,
    workspace_id: str,
    name: typing.Any,
    origin_id: typing.Any,
    origin_type: typing.Any = "bucket",
    cache_policy: typing.Any = "static-assets",
    check_origin_public: typing.Optional[bool] = None,
    preflight_billing: typing.Optional[bool] = None,
) -> Flow[typing.Any]:
    body = build_cdn_distribution_create_body(
        name=name, origin_id=origin_id, origin_type=origin_type, cache_policy=cache_policy
    )
    if check_origin_public and body["origin_type"] == "bucket":
        try:
            bucket = yield Call("GET", _bucket_path(body["origin_id"]), params=_ws(workspace_id))
        except NotFoundError:
            bucket = None  # origin_id may be a bucket id rather than a name; the API checks it
        if bucket is not None:
            check_cdn_origin_public(bucket)
    if preflight_billing:
        yield from billing_preflight(workspace_id, sku_code=None, resource_type="cdn")
    return (yield from _simple("POST", "cdn/distributions", workspace_id, json=body))


def get_cdn_distribution(*, workspace_id: str, distribution_id: typing.Any) -> Flow[typing.Any]:
    return (yield from _simple("GET", _dist_path(distribution_id), workspace_id))


def update_cdn_distribution(
    *, workspace_id: str, distribution_id: typing.Any, name: typing.Any = None, cache_policy: typing.Any = None, enabled: typing.Any = None
) -> Flow[typing.Any]:
    path = _dist_path(distribution_id)
    body = build_cdn_distribution_update_body(name=name, cache_policy=cache_policy, enabled=enabled)
    return (yield from _simple("PATCH", path, workspace_id, json=body))


def delete_cdn_distribution(*, workspace_id: str, distribution_id: typing.Any) -> Flow[typing.Any]:
    return (yield from _simple("DELETE", _dist_path(distribution_id), workspace_id))


def get_cdn_distribution_metrics(*, workspace_id: str, distribution_id: typing.Any, range: typing.Any = None) -> Flow[typing.Any]:
    path = _dist_path(distribution_id, "/metrics")
    return (yield from _simple("GET", path, workspace_id, range=validate_cdn_metrics_range(range)))


def get_cdn_website_config(*, workspace_id: str, distribution_id: typing.Any) -> Flow[typing.Any]:
    return (yield from _simple("GET", _dist_path(distribution_id, "/website-config"), workspace_id))


def update_cdn_website_config(*, workspace_id: str, distribution_id: typing.Any, index_document: typing.Any = "index.html") -> Flow[typing.Any]:
    path = _dist_path(distribution_id, "/website-config")
    body = {"index_document": validate_cdn_index_document(index_document)}
    return (yield from _simple("PUT", path, workspace_id, json=body))


def delete_cdn_website_config(*, workspace_id: str, distribution_id: typing.Any) -> Flow[typing.Any]:
    return (yield from _simple("DELETE", _dist_path(distribution_id, "/website-config"), workspace_id))


def list_cdn_custom_domains(*, workspace_id: str, distribution_id: typing.Any) -> Flow[typing.Any]:
    return (yield from _simple("GET", _dist_path(distribution_id, "/custom-domains"), workspace_id))


def create_cdn_custom_domain(
    *, workspace_id: str, distribution_id: typing.Any, domain: typing.Any, preflight_billing: typing.Optional[bool] = None
) -> Flow[typing.Any]:
    path = _dist_path(distribution_id, "/custom-domains")
    body = {"domain": normalize_cdn_domain(domain, for_create=True)}
    if preflight_billing:
        yield from billing_preflight(
            workspace_id,
            sku_code=CUSTOM_DOMAIN_SKU_CODE,
            estimated_cost_minor=CUSTOM_DOMAIN_ESTIMATED_COST_MINOR,
            resource_type="custom_domain",
        )
    return (yield from _simple("POST", path, workspace_id, json=body))


def get_cdn_custom_domain(*, workspace_id: str, distribution_id: typing.Any, domain: typing.Any) -> Flow[typing.Any]:
    return (yield from _simple("GET", _domain_path(distribution_id, domain), workspace_id))


def delete_cdn_custom_domain(*, workspace_id: str, distribution_id: typing.Any, domain: typing.Any) -> Flow[typing.Any]:
    return (yield from _simple("DELETE", _domain_path(distribution_id, domain), workspace_id))


def verify_cdn_custom_domain(*, workspace_id: str, distribution_id: typing.Any, domain: typing.Any) -> Flow[typing.Any]:
    return (yield from _simple("POST", _domain_path(distribution_id, domain, "/verify"), workspace_id))


def wait_for_cdn_custom_domain(
    *,
    workspace_id: str,
    distribution_id: typing.Any,
    domain: typing.Any,
    timeout: typing.Any = CDN_DOMAIN_TIMEOUT_SECONDS,
    poll_interval: typing.Any = CDN_DOMAIN_POLL_INTERVAL_SECONDS,
) -> Flow[typing.Any]:
    """Call verify until the domain is ``active`` or ``failed`` (returned, not raised) or ``timeout`` passes."""
    path = _domain_path(distribution_id, domain, "/verify")
    wait_timeout = validate_wait_timeout(timeout)
    interval = validate_poll_interval(poll_interval, wait_timeout)
    deadline = _operations._clock() + wait_timeout
    last: typing.Any = None
    while True:
        last = yield Call("POST", path, params=_ws(workspace_id))
        if str(record_get(last, "status") or "").strip().lower() in _CDN_DOMAIN_TERMINAL:
            return last
        remaining = deadline - _operations._clock()
        if remaining <= 0:
            error = OperationTimeoutError(last, timeout=wait_timeout, operation_id=normalize_cdn_domain(domain))
            status = record_get(last, "status") or "pending"
            message = record_get(last, "message") or "DNS records not yet propagated. Try again in a few minutes."
            error.message = f"Custom domain is still {status} after {wait_timeout:g}s: {message}"
            error.args = (error.message,)
            raise error
        yield Sleep(min(interval, remaining))


def purge_cdn_cache(
    *,
    workspace_id: str,
    distribution_id: typing.Any,
    mode: typing.Any,
    paths: typing.Any = None,
    hostnames: typing.Any = None,
    tags: typing.Any = None,
    prefixes: typing.Any = None,
    raise_on_failure: bool = True,
) -> Flow[typing.Any]:
    path = _dist_path(distribution_id, "/purge")
    body = build_cdn_purge_body(mode, paths=paths, hostnames=hostnames, tags=tags, prefixes=prefixes)
    result = yield from _simple("POST", path, workspace_id, json=body)
    return raise_for_cdn_purge(result) if raise_on_failure else result

