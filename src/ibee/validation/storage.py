"""Block Storage, Object Storage and CDN rules, ported from the IBEE portal.

Every check raises :class:`~ibee.validation.IbeeValidationError` before any HTTP
request. Where the portal is stricter than the API (volume names, the 10 GB
minimum volume size, the S3 credential name length, CDN cache policies), the
portal rule is used.
"""

from __future__ import annotations

import numbers
import re
import typing
from urllib.parse import urlsplit

from . import IbeeValidationError, validate_limit, validate_offset
from .billing_catalog import validate_billing_catalog
from .compute import record_get

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _is_int(value: typing.Any) -> bool:
    return isinstance(value, numbers.Integral) and not isinstance(value, bool)


def _int_value(value: typing.Any, *, field: str, minimum: int, maximum: int, message: typing.Optional[str] = None) -> int:
    """An ``int`` (not ``bool``; a float without fraction is accepted) between ``minimum`` and ``maximum``."""
    if isinstance(value, float) and not isinstance(value, bool) and value.is_integer():
        value = int(value)
    if not _is_int(value) or not minimum <= int(value) <= maximum:
        raise IbeeValidationError(
            message or f"{field} must be an integer between {minimum} and {maximum}.", code=f"invalid_{field}", field=field
        )
    return int(value)


def _required_text(value: typing.Any, *, field: str, message: typing.Optional[str] = None) -> str:
    text = value.strip() if isinstance(value, str) else ""
    if not text:
        raise IbeeValidationError(message or f"{field} is required.", code=f"invalid_{field}", field=field)
    return text


def _bool(value: typing.Any, *, field: str) -> bool:
    if not isinstance(value, bool):
        raise IbeeValidationError(f"{field} must be true or false.", code=f"invalid_{field}", field=field)
    return value


def _choice(value: typing.Any, choices: typing.Sequence[str], *, field: str) -> str:
    raw = getattr(value, "value", value)
    if not isinstance(raw, str) or raw not in choices:
        raise IbeeValidationError(
            f"{field} must be one of: {', '.join(choices)}.", code=f"invalid_{field}", field=field
        )
    return raw


# ---------------------------------------------------------------------------
# Block Storage
# ---------------------------------------------------------------------------

BLOCK_VOLUME_ID_PATTERN = re.compile(r"^[0-9a-fA-F]{24}$")
BLOCK_VOLUME_NAME_PATTERN = re.compile(r"^[a-z0-9-]{3,255}$")
BLOCK_VOLUME_MIN_SIZE_GB = 10
BLOCK_VOLUME_MAX_SIZE_GB = 10000
BLOCK_VOLUME_CLASSES: typing.Tuple[str, ...] = ("capacity", "balanced", "performance")
BLOCK_VOLUME_VM_TYPES: typing.Tuple[str, ...] = ("cloud", "gpu")
BLOCK_VOLUME_VM_STATES: typing.Tuple[str, ...] = ("running", "stopped", "suspended")
BLOCK_VOLUME_ATTACH_MODES: typing.Tuple[str, ...] = ("single-writer", "multi-writer")
BLOCK_VOLUME_TRANSIENT_STATES = frozenset({"creating", "attaching", "detaching", "resizing", "deleting"})
#: Default wait for VM attach/detach operations (the portal polls every 2 s for up to 2 minutes).
VOLUME_OPERATION_POLL_INTERVAL_SECONDS = 2.0
VOLUME_OPERATION_TIMEOUT_SECONDS = 120.0
VOLUME_OPERATION_TIMEOUT_MESSAGE = "Operation timed out. Please refresh to check the latest state."
VOLUME_OPERATION_FAILED_MESSAGE = "Volume operation failed"
DETACH_BEFORE_DELETE_MESSAGE = "Detach this volume from all servers before deleting."
VM_DETACH_CONFIRM_MESSAGE = "Unmount the volume inside the server, then pass confirm_unmounted=True (or force=True)"
NODE_SAFE_DETACH_MESSAGE = "Safe detach requires VM state or explicit unmount confirmation."
RESIZE_SHRINK_MESSAGE = "Shrink is not supported. Resize is increase-only."
RESIZE_ATTACHED_MESSAGE = "Attached volume resize requires vm_state=stopped/suspended or allow_online=true."
NODE_LEVEL_ADVANCED_NOTE = (
    "Advanced: records a storage-node attachment only and does not attach the disk to a VM. "
    "Use attach_block_volume_to_vm for VMs. Do not manage the same attachment through both surfaces."
)


def validate_block_volume_id(volume_id: typing.Any, *, field: str = "volume_id") -> str:
    """A block volume id: 24 hexadecimal characters (surrounding spaces removed)."""
    text = volume_id.strip() if isinstance(volume_id, str) else ""
    if not BLOCK_VOLUME_ID_PATTERN.fullmatch(text):
        raise IbeeValidationError(
            f"{field} must be a block volume ID (24 hexadecimal characters).", code="invalid_volume_id", field=field
        )
    return text


def suggest_block_volume_name(name: str) -> str:
    """The portal's normalisation of a typed name: lower-case, other characters replaced with ``-``."""
    return re.sub(r"[^a-z0-9-]", "-", name.lower())


def validate_block_volume_name(name: typing.Any) -> str:
    """The portal's volume-name rule. Never renames silently; the error suggests a valid name."""
    text = name.strip() if isinstance(name, str) else ""
    if not text:
        raise IbeeValidationError("Enter a volume name to continue", code="invalid_volume_name", field="name")
    if len(text) < 3:
        raise IbeeValidationError(
            "Volume name must be at least 3 characters", code="invalid_volume_name", field="name"
        )
    if not BLOCK_VOLUME_NAME_PATTERN.fullmatch(text):
        suggestion = suggest_block_volume_name(text)[:255]
        raise IbeeValidationError(
            f"Lowercase letters, numbers, and hyphens only (try '{suggestion}')",
            code="invalid_volume_name",
            field="name",
            details={"suggestion": suggestion},
        )
    return text


def validate_block_volume_size(size_gb: typing.Any, *, field: str = "size_gb", minimum: int = BLOCK_VOLUME_MIN_SIZE_GB) -> int:
    """An integer size in GB (``bool`` and fractional values rejected, never rounded)."""
    return _int_value(
        size_gb,
        field=field,
        minimum=minimum,
        maximum=BLOCK_VOLUME_MAX_SIZE_GB,
        message=f"{field} must be a whole number of GB between {minimum} and {BLOCK_VOLUME_MAX_SIZE_GB}.",
    )


def normalize_block_sku_code(sku_code: typing.Any) -> typing.Optional[str]:
    """``None`` stays ``None``; otherwise stripped, non-empty, upper-cased and not a ``ROOTDISK-`` SKU."""
    if sku_code is None:
        return None
    text = sku_code.strip().upper() if isinstance(sku_code, str) else ""
    if not text:
        raise IbeeValidationError("sku_code must not be blank.", code="invalid_sku_code", field="sku_code")
    if text.startswith("ROOTDISK-"):
        raise IbeeValidationError(
            "VM root disk is included in the VM plan and must not have a separate SKU",
            code="invalid_sku_code",
            field="sku_code",
        )
    return text


def validate_volume_vm_type(vm_type: typing.Any, *, field: str = "vm_type") -> typing.Optional[str]:
    if vm_type is None:
        return None
    return _choice(vm_type, BLOCK_VOLUME_VM_TYPES, field=field)


def validate_volume_vm_state(vm_state: typing.Any) -> typing.Optional[str]:
    if vm_state is None:
        return None
    return _choice(vm_state, BLOCK_VOLUME_VM_STATES, field="vm_state")


def validate_volume_attach_mode(mode: typing.Any) -> typing.Optional[str]:
    if mode is None:
        return None
    return _choice(mode, BLOCK_VOLUME_ATTACH_MODES, field="mode")


def build_block_volume_create_body(
    *,
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
) -> typing.Dict[str, typing.Any]:
    """The public create body. Billing and placement internals are never sent."""
    body: typing.Dict[str, typing.Any] = {
        "name": validate_block_volume_name(name),
        "size_gb": validate_block_volume_size(size_gb),
        "site_id": _required_text(site_id, field="site_id", message="Please select a location (site_id is required)."),
    }
    if site_name is not None:
        text = site_name.strip() if isinstance(site_name, str) else ""
        if text:
            body["site_name"] = text
    code = normalize_block_sku_code(sku_code)
    if code is not None:
        body["sku_code"] = code
    body["volume_class"] = _choice(volume_class if volume_class is not None else "balanced", BLOCK_VOLUME_CLASSES, field="volume_class")
    body["replica_count"] = _int_value(2 if replica_count is None else replica_count, field="replica_count", minimum=1, maximum=5)
    body["backup_enabled"] = _bool(True if backup_enabled is None else backup_enabled, field="backup_enabled")
    if vm_type is not None:
        body["vm_type"] = _choice(vm_type, BLOCK_VOLUME_VM_TYPES, field="vm_type")
    if delete_on_termination is not None:
        body["delete_on_termination"] = _bool(delete_on_termination, field="delete_on_termination")
    return body


def validate_block_volume_list_params(
    *, site_id: typing.Any = None, vm_type: typing.Any = None, limit: typing.Any = None, offset: typing.Any = None
) -> typing.Dict[str, typing.Any]:
    """List filters: ``site_id`` (non-blank), ``vm_type``, ``limit`` 1-1000, ``offset`` >= 0."""
    params: typing.Dict[str, typing.Any] = {}
    if site_id is not None:
        params["site_id"] = _required_text(site_id, field="site_id")
    if vm_type is not None:
        params["vm_type"] = _choice(vm_type, BLOCK_VOLUME_VM_TYPES, field="vm_type")
    value = validate_limit(limit, maximum=1000)
    if value is not None:
        params["limit"] = value
    value = validate_offset(offset)
    if value is not None:
        params["offset"] = value
    return params


def validate_volume_operations_limit(limit: typing.Any) -> typing.Optional[int]:
    return validate_limit(limit, maximum=200)


def volume_state(volume: typing.Any) -> str:
    return str(record_get(volume, "state") or record_get(volume, "status") or "").strip().lower()


def volume_attachments(volume: typing.Any) -> typing.List[typing.Any]:
    attachments = record_get(volume, "attachments")
    return list(attachments) if isinstance(attachments, (list, tuple)) else []


def volume_vm_type(volume: typing.Any) -> str:
    return str(record_get(volume, "vm_type") or "cloud").strip().lower() or "cloud"


def check_volume_not_transient(volume: typing.Any, action: str) -> None:
    state = volume_state(volume)
    if state in BLOCK_VOLUME_TRANSIENT_STATES:
        raise IbeeValidationError(
            f"Volume is currently '{state}'. Retry {action} once workflow completes.",
            code="volume_busy",
            field="volume_id",
        )


def check_volume_deletable(volume: typing.Any) -> None:
    """Portal delete guard: the volume must be detached and not in a transient state."""
    attachments = volume_attachments(volume)
    if attachments:
        servers = [
            str(record_get(item, "vm_name") or record_get(item, "vm_id") or record_get(item, "node_name") or "")
            for item in attachments
        ]
        raise IbeeValidationError(
            DETACH_BEFORE_DELETE_MESSAGE,
            code="volume_attached",
            field="volume_id",
            details={
                "attachments": [
                    {"vm_id": record_get(item, "vm_id"), "vm_name": record_get(item, "vm_name")} for item in attachments
                ],
                "servers": [name for name in servers if name],
            },
        )
    check_volume_not_transient(volume, "delete")


def validate_resize_request(new_size_gb: typing.Any, vm_state: typing.Any = None, allow_online: typing.Any = None) -> typing.Tuple[int, typing.Optional[str], bool]:
    size = validate_block_volume_size(new_size_gb, field="new_size_gb", minimum=1)
    state = validate_volume_vm_state(vm_state)
    online = False if allow_online is None else _bool(allow_online, field="allow_online")
    return size, state, online


def check_volume_resizable(volume: typing.Any, new_size_gb: int, vm_state: typing.Optional[str], allow_online: bool) -> bool:
    """Backend resize rules. Returns ``True`` when the size is unchanged (a no-op)."""
    check_volume_not_transient(volume, "resize")
    current = record_get(volume, "size_gb")
    if _is_int(current) and new_size_gb < int(current):
        raise IbeeValidationError(
            RESIZE_SHRINK_MESSAGE, code="resize_shrink_not_supported", field="new_size_gb", details={"size_gb": current}
        )
    if volume_attachments(volume) and not allow_online and vm_state not in ("stopped", "suspended"):
        raise IbeeValidationError(RESIZE_ATTACHED_MESSAGE, code="resize_requires_offline", field="vm_state")
    return _is_int(current) and new_size_gb == int(current)


def validate_vm_detach_confirmation(confirm_unmounted: typing.Any, force: typing.Any) -> None:
    """VM-side detach: ``confirm_unmounted=True`` or ``force=True`` (the portal requires the tick)."""
    if confirm_unmounted is not True and force is not True:
        raise IbeeValidationError(VM_DETACH_CONFIRM_MESSAGE, code="confirmation_required", field="confirm_unmounted")


def validate_node_safe_detach(force: typing.Any, confirm_unmounted: typing.Any, vm_state: typing.Optional[str]) -> None:
    """Node-level detach: ``force``, ``confirm_unmounted``, or a stopped/suspended ``vm_state``."""
    if force is True or confirm_unmounted is True or vm_state in ("stopped", "suspended"):
        return
    raise IbeeValidationError(NODE_SAFE_DETACH_MESSAGE, code="confirmation_required", field="confirm_unmounted")


def require_billing_catalog(value: typing.Any, *, context: str = "billing_catalog") -> typing.Dict[str, typing.Any]:
    """Port of the portal's ``requireBillingCatalog`` (sku_id, sku_code, no root-disk SKUs)."""
    return validate_billing_catalog(value, context=context, expected_product="block_storage")


def resolve_volume_billing_catalog(volume: typing.Any) -> typing.Dict[str, typing.Any]:
    """The Block Storage SKU stored on the volume (``billing_catalog`` or ``metadata.billing_catalog``)."""
    catalog = record_get(volume, "billing_catalog")
    if catalog is None:
        metadata = record_get(volume, "metadata")
        catalog = record_get(metadata, "billing_catalog") if metadata is not None else None
    if not catalog:
        volume_id = record_get(volume, "id") or record_get(volume, "_id") or record_get(volume, "name") or ""
        raise IbeeValidationError(
            " ".join(f"Volume {volume_id} has no billing catalog; pass billing_catalog explicitly".split()),
            code="invalid_billing_catalog",
            field="billing_catalog",
        )
    name = record_get(volume, "name") or record_get(volume, "id") or "volume"
    return require_billing_catalog(catalog, context=f"Block volume {name}")


def assert_volume_attachable(volume: typing.Any, target_vm_type: str, vm: typing.Any = None) -> None:
    """Portal and backend attach guards: detached, same VM type, same site."""
    if volume_attachments(volume):
        raise IbeeValidationError(
            "Volume is already attached; detach it first", code="volume_attached", field="volume_id"
        )
    check_volume_not_transient(volume, "attach")
    source_type = volume_vm_type(volume)
    if source_type != target_vm_type:
        raise IbeeValidationError(
            f"Volume was created for {source_type} VMs and cannot attach to a {target_vm_type} VM",
            code="vm_type_mismatch",
            field="vm_id",
        )
    volume_site = str(record_get(volume, "site_id") or "").strip()
    vm_site = str(record_get(vm, "site_id") or "").strip() if vm is not None else ""
    if volume_site and vm_site and volume_site != vm_site:
        site_name = record_get(volume, "site_name") or volume_site
        raise IbeeValidationError(f"Select a server in {site_name}", code="site_mismatch", field="vm_id")


def resolve_single_attachment(
    volume: typing.Any,
    *,
    vm_id: typing.Optional[str] = None,
    node_name: typing.Optional[str] = None,
    for_vm: bool = False,
) -> typing.Any:
    """Pick the attachment a detach refers to (by ``vm_id``, ``node_name``, or the only one)."""
    attachments = volume_attachments(volume)
    if not attachments:
        raise IbeeValidationError("Volume is not attached to any server", code="volume_not_attached", field="volume_id")
    if vm_id is not None:
        matches = [item for item in attachments if str(record_get(item, "vm_id") or "").strip() == vm_id]
        if not matches:
            raise IbeeValidationError(
                "The volume is not attached to this VM.", code="volume_not_attached", field="vm_id"
            )
        return matches[0]
    if node_name is not None:
        matches = [item for item in attachments if str(record_get(item, "node_name") or "").strip() == node_name]
        if not matches:
            raise IbeeValidationError(
                "Volume is not attached to the requested node", code="volume_not_attached", field="node_name"
            )
        return matches[0]
    if len(attachments) > 1:
        what = "several VMs; pass vm_id" if for_vm else "several targets; pass vm_id/node_name"
        raise IbeeValidationError(f"Volume is attached to {what}", code="ambiguous_attachment", field="vm_id" if for_vm else "node_name")
    attachment = attachments[0]
    if for_vm and not str(record_get(attachment, "vm_id") or "").strip():
        raise IbeeValidationError(
            "This attachment has no VM ID; use detach_block_volume with node_name",
            code="attachment_without_vm",
            field="vm_id",
        )
    return attachment


# ---------------------------------------------------------------------------
# Object Storage
# ---------------------------------------------------------------------------

BUCKET_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
BUCKET_NAME_RULE_MESSAGE = (
    "Bucket name must start and end with a letter or number, and contain only lowercase letters, numbers, and hyphens"
)
OBJECT_STORAGE_REGION_BY_HOST: typing.Dict[str, str] = {"api.ibee.ai": "in-south-1", "api.ibee.co.in": "in-south-2"}
RETENTION_MODES: typing.Tuple[str, ...] = ("GOVERNANCE", "COMPLIANCE")
S3_PERMISSION_TYPES: typing.Tuple[str, ...] = ("admin_rw", "admin_ro", "object_rw", "object_ro")
S3_BUCKET_SCOPES: typing.Tuple[str, ...] = ("all", "specific")
DEFAULT_S3_CREDENTIAL_NAME = "Default Key"
DEFAULT_S3_PERMISSION_TYPE = "admin_rw"
S3_SCOPE_ADMIN_MESSAGE = "bucket_scope and allowed_buckets apply only to object_rw/object_ro"
BUCKET_OBJECT_LOCK_MESSAGE = "Bucket cannot be deleted because Object Lock is enabled."
BUCKET_PRIVATE_SIDE_EFFECT = (
    "Making a bucket private disables its public URL and deletes any CDN distribution that uses it as origin."
)


def validate_bucket_name(name: typing.Any) -> str:
    """The portal's bucket-name rule for create (upper-case is rejected, not lower-cased)."""
    text = name.strip() if isinstance(name, str) else ""
    if not text:
        raise IbeeValidationError("Bucket name is required", code="invalid_bucket_name", field="name")
    if len(text) < 3:
        raise IbeeValidationError("Bucket name must be at least 3 characters", code="invalid_bucket_name", field="name")
    if len(text) > 63:
        raise IbeeValidationError("Bucket name must be less than 63 characters", code="invalid_bucket_name", field="name")
    if not BUCKET_NAME_PATTERN.fullmatch(text):
        raise IbeeValidationError(BUCKET_NAME_RULE_MESSAGE, code="invalid_bucket_name", field="name")
    return text


def validate_bucket_path_name(bucket_name: typing.Any, *, field: str = "bucket_name") -> str:
    """An existing bucket's name: non-blank (no pattern, so older names still resolve)."""
    return _required_text(bucket_name, field=field)


def resolve_object_storage_region(region: typing.Any, base_url: typing.Optional[str]) -> str:
    """``region`` when given; otherwise the portal's default for the API host."""
    if region is not None:
        return _required_text(region, field="region")
    host = (urlsplit(base_url or "").hostname or "").lower()
    default = OBJECT_STORAGE_REGION_BY_HOST.get(host)
    if default is None:
        raise IbeeValidationError("region is required for this base URL", code="invalid_region", field="region")
    return default


def validate_default_retention(default_retention: typing.Any) -> typing.Optional[typing.Dict[str, typing.Any]]:
    if default_retention is None:
        return None
    record: typing.Any = default_retention
    dump = getattr(record, "model_dump", None) or getattr(record, "dict", None)
    if not isinstance(record, typing.Mapping) and callable(dump):
        record = dump()
    if not isinstance(record, typing.Mapping):
        raise IbeeValidationError(
            "default_retention must be an object with mode and days or years.",
            code="invalid_default_retention",
            field="default_retention",
        )
    mode = getattr(record.get("mode"), "value", record.get("mode"))
    if mode not in RETENTION_MODES:
        raise IbeeValidationError(
            "default_retention.mode must be GOVERNANCE or COMPLIANCE.",
            code="invalid_default_retention",
            field="default_retention",
        )
    days, years = record.get("days"), record.get("years")
    if (days is None) == (years is None):
        raise IbeeValidationError(
            "default_retention needs exactly one of days or years.",
            code="invalid_default_retention",
            field="default_retention",
        )
    result: typing.Dict[str, typing.Any] = {"mode": mode}
    if days is not None:
        result["days"] = _int_value(days, field="default_retention.days", minimum=1, maximum=36500,
                                    message="Retention days must be a whole number between 1 and 36500.")
    else:
        result["years"] = _int_value(years, field="default_retention.years", minimum=1, maximum=100,
                                     message="Retention years must be a whole number between 1 and 100.")
    return result


def build_bucket_create_body(
    *,
    name: typing.Any,
    region: str,
    is_public: typing.Any = None,
    object_lock_enabled: typing.Any = None,
    default_retention: typing.Any = None,
    tags: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {"name": validate_bucket_name(name), "region": region}
    if is_public is not None:
        body["is_public"] = _bool(is_public, field="is_public")
    retention = validate_default_retention(default_retention)
    if object_lock_enabled is not None:
        body["object_lock_enabled"] = _bool(object_lock_enabled, field="object_lock_enabled")
    if retention is not None:
        if object_lock_enabled is False:
            raise IbeeValidationError(
                "object_lock_enabled must be true when default_retention is specified",
                code="invalid_object_lock_enabled",
                field="object_lock_enabled",
            )
        body["object_lock_enabled"] = True
        body["default_retention"] = retention
    if tags is not None:
        if isinstance(tags, str) or not isinstance(tags, typing.Iterable) or not all(isinstance(t, str) for t in tags):
            raise IbeeValidationError("tags must be a list of strings.", code="invalid_tags", field="tags")
        body["tags"] = list(tags)
    return body


def validate_bucket_list_params(limit: typing.Any = None, continuation_token: typing.Any = None) -> typing.Dict[str, typing.Any]:
    params: typing.Dict[str, typing.Any] = {}
    value = validate_limit(limit, maximum=1000)
    if value is not None:
        params["limit"] = value
    if continuation_token is not None:
        params["continuation_token"] = _required_text(continuation_token, field="continuation_token")
    return params


def check_bucket_deletable(bucket: typing.Any, *, skip_preflight: bool = False) -> None:
    """Portal delete checks: no Object Lock, and (unless skipped) no objects."""
    if record_get(bucket, "bucket_lock_enabled") is True:
        raise IbeeValidationError(BUCKET_OBJECT_LOCK_MESSAGE, code="bucket_object_lock", field="bucket_name")
    count = record_get(bucket, "object_count") or 0
    if not skip_preflight and _is_int(count) and count > 0:
        raise IbeeValidationError(
            f"Bucket is not empty ({count} objects). Delete all objects first.",
            code="bucket_not_empty",
            field="bucket_name",
            details={"object_count": count},
        )


def _normalize_bucket_list(values: typing.Any) -> typing.List[str]:
    if values is None:
        return []
    if isinstance(values, str) or not isinstance(values, typing.Iterable):
        raise IbeeValidationError("allowed_buckets must be a list of bucket names.", code="invalid_allowed_buckets", field="allowed_buckets")
    result: typing.List[str] = []
    for value in values:
        if not isinstance(value, str):
            raise IbeeValidationError("allowed_buckets must be a list of bucket names.", code="invalid_allowed_buckets", field="allowed_buckets")
        text = value.strip()
        if text and text not in result:
            result.append(text)
    return result


def build_s3_credential_body(
    *,
    name: typing.Any = None,
    permission_type: typing.Any = None,
    bucket_scope: typing.Any = None,
    allowed_buckets: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """The portal's S3 credential rules; ``permission_type`` defaults to ``admin_rw`` and is always sent."""
    if name is None:
        text = DEFAULT_S3_CREDENTIAL_NAME
    else:
        text = name.strip() if isinstance(name, str) else ""
        if not text:
            raise IbeeValidationError("Please enter a credential name", code="invalid_name", field="name")
    if len(text) > 100:
        raise IbeeValidationError("Credential name must be at most 100 characters.", code="invalid_name", field="name")
    permission = _choice(permission_type if permission_type is not None else DEFAULT_S3_PERMISSION_TYPE,
                         S3_PERMISSION_TYPES, field="permission_type")
    scope = _choice(bucket_scope, S3_BUCKET_SCOPES, field="bucket_scope") if bucket_scope is not None else None
    buckets = _normalize_bucket_list(allowed_buckets)
    if permission.startswith("admin_"):
        if scope == "specific" or buckets:
            raise IbeeValidationError(S3_SCOPE_ADMIN_MESSAGE, code="invalid_bucket_scope", field="bucket_scope")
        return {"name": text, "permission_type": permission, "bucket_scope": "all", "allowed_buckets": []}
    scope = scope or "all"
    if scope == "specific" and not buckets:
        raise IbeeValidationError("Please select at least one bucket", code="invalid_allowed_buckets", field="allowed_buckets")
    if scope == "all" and buckets:
        raise IbeeValidationError(
            "allowed_buckets must be empty when bucket_scope is 'all'.",
            code="invalid_allowed_buckets",
            field="allowed_buckets",
        )
    return {"name": text, "permission_type": permission, "bucket_scope": scope, "allowed_buckets": buckets}


def s3_endpoint_for_workspace(workspace_id: typing.Any) -> str:
    """The S3 endpoint the portal displays for a workspace (a display hint, never an API URL)."""
    return f"https://{workspace_id}.blob.ibeestorage.com"


def no_retry_request_options(request_options: typing.Optional[typing.Mapping[str, typing.Any]]) -> typing.Dict[str, typing.Any]:
    """``request_options`` with ``max_retries=0`` unless the caller set ``max_retries``."""
    options = dict(request_options or {})
    options.setdefault("max_retries", 0)
    return options


# ---------------------------------------------------------------------------
# CDN
# ---------------------------------------------------------------------------

CDN_CACHE_POLICIES: typing.Tuple[str, ...] = ("static-assets", "media", "short", "no-cache")
CDN_ORIGIN_TYPES: typing.Tuple[str, ...] = ("bucket", "custom")
CDN_METRICS_RANGES: typing.Tuple[str, ...] = ("24h", "7d", "30d")
CDN_PURGE_MODES: typing.Tuple[str, ...] = ("url", "hostname", "tag", "prefix", "all")
CDN_URL_DISPOSITIONS: typing.Tuple[str, ...] = ("inline", "attachment")
CDN_DOMAIN_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$")
CDN_PURGE_ALL_WARNING = "This will purge all cached data for every hostname of this distribution"
_PURGE_SELECTORS: typing.Dict[str, str] = {"url": "paths", "hostname": "hostnames", "tag": "tags", "prefix": "prefixes"}
_PURGE_LIMITS: typing.Dict[str, int] = {"paths": 30, "hostnames": 100, "tags": 100, "prefixes": 100}


def validate_cdn_distribution_name(name: typing.Any) -> str:
    text = _required_text(name, field="name", message="Please enter a name")
    if len(text) > 128:
        raise IbeeValidationError("name must be 1-128 characters.", code="invalid_name", field="name")
    return text


def validate_cdn_cache_policy(cache_policy: typing.Any) -> str:
    return _choice(cache_policy, CDN_CACHE_POLICIES, field="cache_policy")


def build_cdn_distribution_create_body(
    *, name: typing.Any, origin_id: typing.Any, origin_type: typing.Any = "bucket", cache_policy: typing.Any = "static-assets"
) -> typing.Dict[str, typing.Any]:
    return {
        "name": validate_cdn_distribution_name(name),
        "origin_type": _choice(origin_type if origin_type is not None else "bucket", CDN_ORIGIN_TYPES, field="origin_type"),
        "origin_id": _required_text(origin_id, field="origin_id", message="Please select a bucket"),
        "cache_policy": validate_cdn_cache_policy(cache_policy if cache_policy is not None else "static-assets"),
    }


def build_cdn_distribution_update_body(
    *, name: typing.Any = None, cache_policy: typing.Any = None, enabled: typing.Any = None
) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {}
    if name is not None:
        body["name"] = validate_cdn_distribution_name(name)
    if cache_policy is not None:
        body["cache_policy"] = validate_cdn_cache_policy(cache_policy)
    if enabled is not None:
        body["enabled"] = _bool(enabled, field="enabled")
    if not body:
        raise IbeeValidationError(
            "Provide at least one of name, cache_policy, enabled", code="empty_update", field=None
        )
    return body


def check_cdn_origin_public(bucket: typing.Any) -> None:
    if record_get(bucket, "is_public") is False:
        raise IbeeValidationError(
            "Only public buckets can be used as CDN origins", code="origin_not_public", field="origin_id"
        )


def validate_cdn_index_document(index_document: typing.Any) -> str:
    value = "index.html" if index_document is None else index_document
    text = _required_text(value, field="index_document")
    problem = None
    if len(text.encode("utf-8")) > 1024:
        problem = "must be at most 1024 bytes"
    elif text.startswith("/"):
        problem = "must not start with '/'"
    elif "\\" in text:
        problem = "must not contain a backslash"
    elif not all(0x20 <= ord(char) <= 0x7E for char in text):
        problem = "must contain printable ASCII characters only"
    elif any(segment in ("", ".", "..") for segment in text.split("/")):
        problem = "must not contain empty, '.' or '..' path segments"
    if problem:
        raise IbeeValidationError(f"index_document {problem}.", code="invalid_index_document", field="index_document")
    return text


def normalize_cdn_domain(domain: typing.Any, *, for_create: bool = False) -> str:
    """Lower-case and strip a custom domain; for create also check its length and syntax."""
    text = domain.strip().lower() if isinstance(domain, str) else ""
    if not text:
        raise IbeeValidationError("domain is required.", code="invalid_domain", field="domain")
    if not for_create:
        return text
    if not 3 <= len(text) <= 253 or not CDN_DOMAIN_PATTERN.fullmatch(text):
        raise IbeeValidationError(
            "Enter a valid domain name (for example cdn.example.com).", code="invalid_domain", field="domain"
        )
    if "." not in text:
        raise IbeeValidationError(
            "Domain must include a subdomain (e.g., cdn.example.com)", code="invalid_domain", field="domain"
        )
    return text


def _string_list(values: typing.Any, *, field: str) -> typing.List[str]:
    if isinstance(values, str):
        values = re.split(r"[,\n]", values)
    if not isinstance(values, typing.Iterable):
        raise IbeeValidationError(f"{field} must be a list of strings.", code=f"invalid_{field}", field=field)
    result: typing.List[str] = []
    for value in values:
        if not isinstance(value, str):
            raise IbeeValidationError(f"{field} must be a list of strings.", code=f"invalid_{field}", field=field)
        text = value.strip()
        if text:
            result.append(text)
    return result


def build_cdn_purge_body(
    mode: typing.Any,
    *,
    paths: typing.Any = None,
    hostnames: typing.Any = None,
    tags: typing.Any = None,
    prefixes: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """One purge body builder: only the selector matching ``mode`` is allowed, and it is normalised."""
    purge_mode = _choice(mode, CDN_PURGE_MODES, field="mode")
    given = {"paths": paths, "hostnames": hostnames, "tags": tags, "prefixes": prefixes}
    expected = _PURGE_SELECTORS.get(purge_mode)
    for field, value in given.items():
        if value is not None and field != expected:
            raise IbeeValidationError(
                f"{field} cannot be used with mode '{purge_mode}'.", code="invalid_purge_selector", field=field
            )
    if expected is None:
        return {"mode": purge_mode}
    items = _string_list(given[expected] if given[expected] is not None else [], field=expected)
    if expected == "paths":
        normalized = []
        for item in items:
            if "://" in item:
                lowered = item.lower()
                if not lowered.startswith("https://"):
                    raise IbeeValidationError("Purge URLs must use https://.", code="invalid_paths", field="paths")
                authority = item[len("https://"):].split("/", 1)[0]
                if "#" in item or "@" in authority:
                    raise IbeeValidationError(
                        "Purge URLs must not contain a fragment or credentials.", code="invalid_paths", field="paths"
                    )
                normalized.append(item)
            else:
                normalized.append(item if item.startswith("/") else f"/{item}")
        items = normalized
    elif expected == "hostnames":
        items = [item.lower() for item in items]
    elif expected == "prefixes":
        if any("?" in item or "#" in item for item in items):
            raise IbeeValidationError(
                "Purge prefixes must not contain a query string or fragment.", code="invalid_prefixes", field="prefixes"
            )
    limit = _PURGE_LIMITS[expected]
    if not 1 <= len(items) <= limit:
        raise IbeeValidationError(
            f"mode '{purge_mode}' needs 1-{limit} {expected}.", code=f"invalid_{expected}", field=expected
        )
    return {"mode": purge_mode, expected: items}


def validate_cdn_generate_url(
    *, bucket_name: typing.Any, object_key: typing.Any, expires_in: typing.Any = None, disposition: typing.Any = None
) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {
        "bucket_name": _required_text(bucket_name, field="bucket_name"),
        "object_key": object_key if isinstance(object_key, str) and object_key.strip() else None,
    }
    if body["object_key"] is None:
        raise IbeeValidationError("object_key is required.", code="invalid_object_key", field="object_key")
    if expires_in is not None:
        if not _is_int(expires_in) or expires_in < 1:
            raise IbeeValidationError("expires_in must be an integer >= 1.", code="invalid_expires_in", field="expires_in")
        body["expires_in"] = int(expires_in)
    if disposition is not None:
        body["disposition"] = _choice(disposition, CDN_URL_DISPOSITIONS, field="disposition")
    return body


def validate_cdn_metrics_range(value: typing.Any) -> str:
    return _choice("24h" if value is None else value, CDN_METRICS_RANGES, field="range")


__all__ = [
    "BLOCK_VOLUME_ATTACH_MODES",
    "BLOCK_VOLUME_CLASSES",
    "BLOCK_VOLUME_ID_PATTERN",
    "BLOCK_VOLUME_MAX_SIZE_GB",
    "BLOCK_VOLUME_MIN_SIZE_GB",
    "BLOCK_VOLUME_NAME_PATTERN",
    "BLOCK_VOLUME_TRANSIENT_STATES",
    "BLOCK_VOLUME_VM_STATES",
    "BLOCK_VOLUME_VM_TYPES",
    "BUCKET_NAME_PATTERN",
    "BUCKET_PRIVATE_SIDE_EFFECT",
    "CDN_CACHE_POLICIES",
    "CDN_METRICS_RANGES",
    "CDN_ORIGIN_TYPES",
    "CDN_PURGE_ALL_WARNING",
    "CDN_PURGE_MODES",
    "CDN_URL_DISPOSITIONS",
    "DEFAULT_S3_CREDENTIAL_NAME",
    "DEFAULT_S3_PERMISSION_TYPE",
    "DETACH_BEFORE_DELETE_MESSAGE",
    "NODE_LEVEL_ADVANCED_NOTE",
    "OBJECT_STORAGE_REGION_BY_HOST",
    "RETENTION_MODES",
    "S3_BUCKET_SCOPES",
    "S3_PERMISSION_TYPES",
    "VOLUME_OPERATION_FAILED_MESSAGE",
    "VOLUME_OPERATION_POLL_INTERVAL_SECONDS",
    "VOLUME_OPERATION_TIMEOUT_MESSAGE",
    "VOLUME_OPERATION_TIMEOUT_SECONDS",
    "assert_volume_attachable",
    "build_block_volume_create_body",
    "build_bucket_create_body",
    "build_cdn_distribution_create_body",
    "build_cdn_distribution_update_body",
    "build_cdn_purge_body",
    "build_s3_credential_body",
    "check_bucket_deletable",
    "check_cdn_origin_public",
    "check_volume_deletable",
    "check_volume_not_transient",
    "check_volume_resizable",
    "no_retry_request_options",
    "normalize_block_sku_code",
    "normalize_cdn_domain",
    "require_billing_catalog",
    "resolve_object_storage_region",
    "resolve_single_attachment",
    "resolve_volume_billing_catalog",
    "s3_endpoint_for_workspace",
    "suggest_block_volume_name",
    "validate_block_volume_id",
    "validate_block_volume_list_params",
    "validate_block_volume_name",
    "validate_block_volume_size",
    "validate_bucket_list_params",
    "validate_bucket_name",
    "validate_bucket_path_name",
    "validate_cdn_cache_policy",
    "validate_cdn_distribution_name",
    "validate_cdn_generate_url",
    "validate_cdn_index_document",
    "validate_cdn_metrics_range",
    "validate_default_retention",
    "validate_node_safe_detach",
    "validate_resize_request",
    "validate_vm_detach_confirmation",
    "validate_volume_attach_mode",
    "validate_volume_operations_limit",
    "validate_volume_vm_state",
    "validate_volume_vm_type",
    "volume_attachments",
    "volume_state",
    "volume_vm_type",
]
