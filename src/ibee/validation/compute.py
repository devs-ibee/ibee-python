"""Cloud and GPU VM rules, ported from the IBEE portal and the compute API.

All functions raise :class:`~ibee.validation.IbeeValidationError` before any HTTP
call. Functions that take a ``vm`` accept either a ``CloudVm``/``GpuVm`` model or a
plain ``dict`` as returned by ``GET /compute/{cloud-vms|gpu-vms}/{vm_id}``.
"""

from __future__ import annotations

import datetime as dt
import numbers
import re
import typing

from . import IbeeValidationError, validate_limit

# ---------------------------------------------------------------------------
# Record helpers
# ---------------------------------------------------------------------------


def record_get(record: typing.Any, name: str, default: typing.Any = None) -> typing.Any:
    """Read ``name`` from a dict or a pydantic model (including extra fields)."""
    if record is None:
        return default
    if isinstance(record, typing.Mapping):
        return record.get(name, default)
    value = getattr(record, name, None)
    if value is not None:
        return value
    extra = getattr(record, "model_extra", None) or getattr(record, "__pydantic_extra__", None)
    if isinstance(extra, typing.Mapping) and name in extra:
        return extra[name]
    return default


def as_plain(record: typing.Any) -> typing.Dict[str, typing.Any]:
    """A plain ``dict`` copy of a dict or pydantic model (extra fields kept)."""
    if record is None:
        return {}
    if isinstance(record, typing.Mapping):
        return dict(record)
    dump = getattr(record, "model_dump", None) or getattr(record, "dict", None)
    if callable(dump):
        try:
            result = dump()
        except Exception:
            result = None
        if isinstance(result, typing.Mapping):
            return dict(result)
    return {}


def _text(value: typing.Any) -> str:
    return str(value if value is not None else "").strip()


def normalize_vm_record(vm: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
    """The compute API returns ``_id``; copy it to ``id`` when ``id`` is missing."""
    if isinstance(vm, dict) and not vm.get("id") and vm.get("_id") is not None:
        vm = {**vm, "id": str(vm["_id"])}
    return vm


# ---------------------------------------------------------------------------
# Identifiers
# ---------------------------------------------------------------------------

VM_ID_PATTERN = re.compile(r"^[0-9a-fA-F]{24}$")
COMPUTE_OPERATION_ID_PATTERN = re.compile(r"^op_[0-9a-fA-F]{24}$")


def validate_vm_id(vm_id: typing.Any, *, field: str = "vm_id") -> str:
    """A VM id is a 24-character hexadecimal id (as returned by list/create)."""
    value = vm_id.strip() if isinstance(vm_id, str) else vm_id
    if not isinstance(value, str) or VM_ID_PATTERN.fullmatch(value) is None:
        raise IbeeValidationError(
            f"{field} must be a 24-character hexadecimal VM id.", code="invalid_vm_id", field=field
        )
    return value


def validate_compute_operation_id(operation_id: typing.Any) -> str:
    """A compute operation id looks like ``op_`` followed by 24 hexadecimal characters."""
    value = operation_id.strip() if isinstance(operation_id, str) else operation_id
    if not isinstance(value, str) or COMPUTE_OPERATION_ID_PATTERN.fullmatch(value) is None:
        raise IbeeValidationError(
            "operation_id must look like 'op_' followed by 24 hexadecimal characters.",
            code="invalid_operation_id",
            field="operation_id",
        )
    return value


def validate_required_text(
    value: typing.Any, *, field: str, max_length: typing.Optional[int] = None, label: typing.Optional[str] = None
) -> str:
    """Strip; must be non-empty (and at most ``max_length`` characters)."""
    text = value.strip() if isinstance(value, str) else None
    if not text:
        raise IbeeValidationError(f"{label or field} is required.", code=f"invalid_{field}", field=field)
    if max_length is not None and len(text) > max_length:
        raise IbeeValidationError(
            f"{label or field} must be at most {max_length} characters.", code=f"invalid_{field}", field=field
        )
    return text


def validate_optional_text(
    value: typing.Any, *, field: str, max_length: typing.Optional[int] = None
) -> typing.Optional[str]:
    """``None``/blank means omit; otherwise stripped and at most ``max_length`` characters."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise IbeeValidationError(f"{field} must be a string.", code=f"invalid_{field}", field=field)
    text = value.strip()
    if not text:
        return None
    if max_length is not None and len(text) > max_length:
        raise IbeeValidationError(
            f"{field} must be at most {max_length} characters.", code=f"invalid_{field}", field=field
        )
    return text


def validate_requested_by(requested_by: typing.Any) -> typing.Optional[str]:
    """Optional audit label: 1-128 characters when given."""
    if requested_by is None:
        return None
    if not isinstance(requested_by, str) or not 1 <= len(requested_by.strip()) <= 128:
        raise IbeeValidationError(
            "requested_by must be 1-128 characters.", code="invalid_requested_by", field="requested_by"
        )
    return requested_by.strip()


def normalize_id_list(values: typing.Any, *, field: str) -> typing.List[str]:
    """Strip each id, drop blanks and remove duplicates (order kept)."""
    if values is None:
        return []
    if isinstance(values, str) or not isinstance(values, typing.Iterable):
        raise IbeeValidationError(f"{field} must be a list of strings.", code=f"invalid_{field}", field=field)
    result: typing.List[str] = []
    for value in values:
        if not isinstance(value, str):
            raise IbeeValidationError(f"{field} must be a list of strings.", code=f"invalid_{field}", field=field)
        text = value.strip()
        if text and text not in result:
            result.append(text)
    return result


# ---------------------------------------------------------------------------
# Names
# ---------------------------------------------------------------------------

VM_NAME_PATTERN = re.compile(r"^[A-Za-z0-9-]+$")
MAX_BATCH_VMS = 5


def validate_vm_name(name: typing.Any, *, field: str = "name") -> str:
    """Hostname rule: trimmed, non-empty, letters, digits and hyphens only."""
    text = name.strip() if isinstance(name, str) else ""
    if not text:
        raise IbeeValidationError("Please enter a valid hostname", code="invalid_vm_name", field=field)
    if VM_NAME_PATTERN.fullmatch(text) is None:
        raise IbeeValidationError(
            "VM names may contain only letters, digits and hyphens.", code="invalid_vm_name", field=field
        )
    return text


def expand_batch_names(
    base: str,
    count: int,
    overrides: typing.Optional[typing.Sequence[str]] = None,
    *,
    reserved_ip: bool = False,
) -> typing.List[str]:
    """Names for a batch create: ``base`` for one VM, else ``base-1`` .. ``base-N`` (1-5).

    ``overrides`` replaces names by position. Names must be unique (case-insensitive).
    A Reserved IP can be used for one VM only.
    """
    base = validate_vm_name(base)
    if isinstance(count, bool) or not isinstance(count, numbers.Integral) or not 1 <= int(count) <= MAX_BATCH_VMS:
        raise IbeeValidationError(
            f"count must be between 1 and {MAX_BATCH_VMS}.", code="invalid_count", field="count"
        )
    count = int(count)
    if reserved_ip and count != 1:
        raise IbeeValidationError(
            "A Reserved IP can be used for a single VM only.", code="invalid_count", field="count"
        )
    names = [base] if count == 1 else [f"{base}-{index}" for index in range(1, count + 1)]
    for index, override in enumerate(overrides or []):
        if index < count and override is not None and str(override).strip():
            names[index] = validate_vm_name(override)
    if len({name.lower() for name in names}) != len(names):
        raise IbeeValidationError(
            "Each instance needs a unique hostname", code="duplicate_vm_names", field="name"
        )
    return names


# ---------------------------------------------------------------------------
# SSH keys and access
# ---------------------------------------------------------------------------

SSH_KEY_TYPES: typing.Tuple[str, ...] = (
    "ssh-rsa",
    "ssh-ed25519",
    "ecdsa-sha2-nistp256",
    "ecdsa-sha2-nistp384",
    "ecdsa-sha2-nistp521",
    "sk-ssh-ed25519@openssh.com",
    "sk-ecdsa-sha2-nistp256@openssh.com",
)
_SSH_KEY_DATA = re.compile(r"^[A-Za-z0-9+/=]+$")


def validate_ssh_public_key(key: typing.Any, *, field: str = "ssh_keys") -> str:
    """One OpenSSH public key on a single line, of a supported type; never a private key."""
    if not isinstance(key, str):
        raise IbeeValidationError("SSH keys must be strings.", code="invalid_ssh_key", field=field)
    text = key.strip()
    if "\r" in text or "\n" in text or "PRIVATE KEY" in text.upper():
        raise IbeeValidationError(
            "Only single-line public SSH keys are accepted", code="invalid_ssh_key", field=field
        )
    parts = text.split(None, 2)
    if len(parts) < 2 or parts[0] not in SSH_KEY_TYPES or _SSH_KEY_DATA.fullmatch(parts[1]) is None:
        raise IbeeValidationError(
            "Invalid SSH public key format (supported types: " + ", ".join(SSH_KEY_TYPES) + ").",
            code="invalid_ssh_key",
            field=field,
        )
    return text


def normalize_ssh_public_keys(keys: typing.Any, *, field: str = "ssh_keys") -> typing.List[str]:
    """Validate each key, drop blanks and duplicates."""
    if keys is None:
        return []
    if isinstance(keys, str) or not isinstance(keys, typing.Iterable):
        raise IbeeValidationError(f"{field} must be a list of strings.", code="invalid_ssh_key", field=field)
    result: typing.List[str] = []
    for key in keys:
        if isinstance(key, str) and not key.strip():
            continue
        text = validate_ssh_public_key(key, field=field)
        if text not in result:
            result.append(text)
    return result


SSH_KEY_MODES: typing.Tuple[str, ...] = ("add", "remove")
MIN_VM_PASSWORD_LENGTH = 8


def _secret_ref_marker(ref: typing.Any) -> typing.Tuple[str, str, str]:
    return (
        _text(record_get(ref, "ssh_key_id")),
        _text(record_get(ref, "store_key")),
        _text(record_get(ref, "secret_name")),
    )


def normalize_ssh_key_secret_refs(refs: typing.Any) -> typing.List[typing.Dict[str, typing.Any]]:
    """Each ref needs ``ssh_key_id`` or ``secret_name``; ``store_key`` defaults to ``ssh-keys``."""
    if refs is None:
        return []
    if isinstance(refs, (str, bytes)) or not isinstance(refs, typing.Iterable):
        raise IbeeValidationError(
            "ssh_key_secret_refs must be a list.", code="invalid_ssh_key_secret_refs", field="ssh_key_secret_refs"
        )
    result: typing.List[typing.Dict[str, typing.Any]] = []
    for ref in refs:
        plain = {key: value for key, value in as_plain(ref).items() if value is not None}
        if not _text(plain.get("ssh_key_id")) and not _text(plain.get("secret_name")):
            raise IbeeValidationError(
                "Each ssh_key_secret_refs entry needs ssh_key_id or secret_name.",
                code="invalid_ssh_key_secret_refs",
                field="ssh_key_secret_refs",
            )
        plain.setdefault("store_key", "ssh-keys")
        result.append(plain)
    return result


def _tracked_after(vm: typing.Any, mode: str, keys: typing.List[str], ids: typing.List[str], refs: typing.List[typing.Any]) -> bool:
    existing_keys = [k for k in (_text(v) for v in record_get(vm, "ssh_keys") or []) if k]
    existing_ids = [k for k in (_text(v) for v in record_get(vm, "ssh_key_ids") or []) if k]
    existing_refs = [ref for ref in record_get(vm, "ssh_key_secret_refs") or [] if ref]
    if mode == "add":
        return bool(existing_keys or existing_ids or existing_refs or keys or ids or refs)
    if mode == "remove":
        remove_markers = {_secret_ref_marker(ref) for ref in refs}
        remove_ref_ids = {value for ref in refs for value in (_secret_ref_marker(ref)[0], _secret_ref_marker(ref)[2]) if value}
        existing_keys = [k for k in existing_keys if k not in set(keys)]
        existing_ids = [k for k in existing_ids if k not in set(ids)]
        existing_refs = [
            ref
            for ref in existing_refs
            if _secret_ref_marker(ref) not in remove_markers
            and _secret_ref_marker(ref)[0] not in set(ids) | remove_ref_ids
            and _secret_ref_marker(ref)[2] not in set(ids) | remove_ref_ids
        ]
    return bool(existing_keys or existing_ids or existing_refs)


def _password_auth_enabled(vm: typing.Any) -> typing.Optional[bool]:
    value = record_get(vm, "ssh_password_auth_enabled")
    if value is None:
        return None
    return bool(value)


def is_windows_vm(vm: typing.Any) -> bool:
    """Whether the VM runs Windows (``os_type`` or ``os_distro`` mentions windows)."""
    return "windows" in _text(record_get(vm, "os_type")).lower() or "windows" in _text(
        record_get(vm, "os_distro")
    ).lower()


def validate_access_update(
    *,
    ssh_key_mode: typing.Any = None,
    ssh_keys: typing.Any = None,
    ssh_key_ids: typing.Any = None,
    ssh_key_secret_refs: typing.Any = None,
    new_password: typing.Any = None,
    password_auth_enabled: typing.Any = None,
    confirm_remove_last_ssh_key: typing.Any = None,
    vm: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """Access-update rules; returns the normalised body fields.

    * ``ssh_key_mode`` (``add``/``remove``) is required exactly when keys are given;
    * at least one change: keys, ``new_password`` or ``password_auth_enabled``;
    * ``new_password``: at least 8 characters after trimming, no line breaks;
    * with ``vm``: Linux only, ``running`` only, password login can only be disabled
      while a tracked SSH key remains, and removing the last key while password
      login is off needs ``confirm_remove_last_ssh_key=True``.
    """
    keys = normalize_ssh_public_keys(ssh_keys)
    ids = normalize_id_list(ssh_key_ids, field="ssh_key_ids")
    refs = normalize_ssh_key_secret_refs(ssh_key_secret_refs)
    mode = None
    if ssh_key_mode is not None:
        mode = str(getattr(ssh_key_mode, "value", ssh_key_mode)).strip().lower()
        if mode not in SSH_KEY_MODES:
            raise IbeeValidationError(
                "ssh_key_mode must be 'add' or 'remove'.", code="invalid_ssh_key_mode", field="ssh_key_mode"
            )
    has_keys = bool(keys or ids or refs)
    if has_keys and mode is None:
        raise IbeeValidationError(
            "ssh_key_mode ('add' or 'remove') is required when SSH keys are given.",
            code="invalid_ssh_key_mode",
            field="ssh_key_mode",
        )
    if mode is not None and not has_keys:
        raise IbeeValidationError(
            "ssh_key_mode needs at least one of ssh_keys, ssh_key_ids or ssh_key_secret_refs.",
            code="invalid_ssh_key_mode",
            field="ssh_key_mode",
        )
    password = None
    if new_password is not None:
        if not isinstance(new_password, str):
            raise IbeeValidationError("new_password must be a string.", code="invalid_password", field="new_password")
        if "\r" in new_password or "\n" in new_password:
            raise IbeeValidationError(
                "new_password must not contain line breaks.", code="invalid_password", field="new_password"
            )
        if len(new_password.strip()) < MIN_VM_PASSWORD_LENGTH:
            raise IbeeValidationError(
                "Password must be at least 8 characters.", code="invalid_password", field="new_password"
            )
        password = new_password
    if password_auth_enabled is not None and not isinstance(password_auth_enabled, bool):
        raise IbeeValidationError(
            "password_auth_enabled must be a boolean.", code="invalid_password_auth_enabled", field="password_auth_enabled"
        )
    if not has_keys and password is None and password_auth_enabled is None:
        raise IbeeValidationError(
            "Nothing to update: pass SSH keys with ssh_key_mode, new_password or password_auth_enabled.",
            code="no_changes",
            field=None,
        )
    if vm is not None:
        if is_windows_vm(vm):
            raise IbeeValidationError(
                "Post-create SSH key/password-login settings are supported for Linux VMs only",
                code="vm_not_linux",
                field="vm_id",
            )
        assert_vm_action_allowed(vm, "access")
        remaining = _tracked_after(vm, mode or "", keys, ids, refs)
        if password_auth_enabled is False and not remaining:
            raise IbeeValidationError(
                "Cannot disable SSH password login without at least one tracked SSH key",
                code="ssh_key_required",
                field="password_auth_enabled",
            )
        current = _password_auth_enabled(vm)
        final = password_auth_enabled if password_auth_enabled is not None else current
        if mode == "remove" and not remaining and final is False and confirm_remove_last_ssh_key is not True:
            raise IbeeValidationError(
                "Removing the last tracked SSH key while password SSH login is disabled requires confirmation "
                "(confirm_remove_last_ssh_key=True).",
                code="confirmation_required",
                field="confirm_remove_last_ssh_key",
            )
    body: typing.Dict[str, typing.Any] = {}
    if mode is not None:
        body["ssh_key_mode"] = mode
    if keys:
        body["ssh_keys"] = keys
    if ids:
        body["ssh_key_ids"] = ids
    if refs:
        body["ssh_key_secret_refs"] = refs
    if password is not None:
        body["new_password"] = password
    if password_auth_enabled is not None:
        body["password_auth_enabled"] = password_auth_enabled
    if confirm_remove_last_ssh_key is not None:
        body["confirm_remove_last_ssh_key"] = bool(confirm_remove_last_ssh_key)
    return body


# ---------------------------------------------------------------------------
# VM state matrix
# ---------------------------------------------------------------------------

VM_ACTIONS: typing.Tuple[str, ...] = (
    "start",
    "stop",
    "reboot",
    "delete",
    "access",
    "resize",
    "resize_plan",
    "resize_root_disk",
    "attach_volume",
    "detach_volume",
    "console",
    "snapshot",
)
_SNAPSHOT_LOCKED_STATES = frozenset(
    {"pending", "provisioning", "configuring", "starting", "stopping", "rebooting", "resizing", "deleting", "restoring"}
)
_RESIZE_STATES = frozenset({"running", "stopped", "error"})


def vm_status(vm: typing.Any) -> str:
    status = record_get(vm, "status")
    return _text(getattr(status, "value", status)).lower()


def assert_vm_action_allowed(vm: typing.Any, action: str) -> None:
    """Portal state matrix for VM actions.

    ``start`` needs ``stopped``; ``stop``/``reboot``/``access``/``console`` need
    ``running``; ``delete`` is refused while ``deleting``/``deleted`` (the API
    answers 409 while a resize runs); resizes and volume attach/detach need ``running``, ``stopped`` or
    ``error``; snapshots are refused while the VM is changing state.
    """
    status = vm_status(vm)
    allowed = True
    if action == "start":
        allowed = status == "stopped"
    elif action in ("stop", "reboot", "access", "console"):
        allowed = status == "running"
    elif action == "delete":
        allowed = status not in {"deleting", "deleted"}
    elif action in ("resize", "resize_plan", "resize_root_disk", "attach_volume", "detach_volume"):
        allowed = status in _RESIZE_STATES
    elif action == "snapshot":
        allowed = status not in _SNAPSHOT_LOCKED_STATES
    if not allowed:
        label = action.replace("_", " ")
        raise IbeeValidationError(
            f"Cannot {label} the VM while its status is '{status or 'unknown'}'.",
            code="invalid_vm_state",
            field="vm_id",
            details={"status": status, "action": action},
        )


# ---------------------------------------------------------------------------
# Delete: public IP reserve/release choice
# ---------------------------------------------------------------------------

PUBLIC_IP_ACTIONS: typing.Tuple[str, ...] = ("reserve", "release")


def has_auto_assigned_public_ip(vm: typing.Any) -> bool:
    """The VM has a public IP that is not a Reserved IP."""
    return bool(_text(record_get(vm, "public_ip"))) and not (
        _text(record_get(vm, "reserved_public_ip_id")) or _text(record_get(vm, "retained_reserved_public_ip_id"))
    )


def resolve_delete_public_ip_action(
    vm: typing.Any,
    *,
    public_ip_action: typing.Any = None,
    reserved_ip_label: typing.Any = None,
    reserved_ip_billing_catalog: typing.Any = None,
) -> typing.Optional[typing.Dict[str, typing.Any]]:
    """Portal delete dialog: decide what happens to the VM's public IP.

    With an auto-assigned public IP the choice is required and defaults to
    ``release``. ``reserve`` keeps the address as a billed Reserved IP and needs the
    VM's site and ``reserved_ip_billing_catalog`` (the Reserved IP SKU); the label
    defaults to the VM name. Returns the delete body, or ``None`` when there is
    nothing to send.
    """
    action = None
    if public_ip_action is not None:
        action = str(public_ip_action).strip().lower()
        if action not in PUBLIC_IP_ACTIONS:
            raise IbeeValidationError(
                "public_ip_action must be 'reserve' or 'release'.", code="invalid_public_ip_action", field="public_ip_action"
            )
    needs_choice = has_auto_assigned_public_ip(vm) if vm is not None else action is not None
    if vm is not None and not needs_choice:
        if action == "reserve":
            raise IbeeValidationError(
                "This VM does not have an auto-assigned public IP to reserve",
                code="invalid_public_ip_action",
                field="public_ip_action",
            )
        return None
    if action is None:
        action = "release"
    body: typing.Dict[str, typing.Any] = {"public_ip_action": action}
    if action == "reserve":
        if vm is not None and not _text(record_get(vm, "site_id")):
            raise IbeeValidationError(
                "The VM location is unavailable, so its public IP cannot be reserved yet.",
                code="vm_site_unavailable",
                field="public_ip_action",
            )
        from .billing_catalog import require_billing_sku

        if reserved_ip_billing_catalog is None:
            raise IbeeValidationError(
                "reserved_ip_billing_catalog (the Reserved IP SKU with sku_id and sku_code) is required to reserve "
                "the public IP. Copy billing_catalog from an existing Reserved IP in the same site.",
                code="reserved_ip_billing_catalog_required",
                field="reserved_ip_billing_catalog",
            )
        body["reserved_ip_billing_catalog"] = require_billing_sku(
            reserved_ip_billing_catalog, "Reserved IP", field="reserved_ip_billing_catalog"
        )
        label = validate_optional_text(reserved_ip_label, field="reserved_ip_label", max_length=120)
        if label is None and vm is not None:
            label = _text(record_get(vm, "name"))[:120] or None
        if label:
            body["reserved_ip_label"] = label
    return body


# ---------------------------------------------------------------------------
# Resize
# ---------------------------------------------------------------------------

CPU_RANGE = (1, 256)
RAM_MB_RANGE = (257, 2097152)
DISK_GB_RANGE = (1, 10000)


def _ranged(value: typing.Any, bounds: typing.Tuple[int, int], field: str) -> typing.Optional[int]:
    return validate_limit(value, minimum=bounds[0], maximum=bounds[1], field=field)


def validate_resize_target(
    *, cpu: typing.Any = None, ram_mb: typing.Any = None, disk_gb: typing.Any = None, require_one: bool = True
) -> typing.Dict[str, int]:
    """cpu 1-256, ram_mb 257-2097152, disk_gb 1-10000; at least one when ``require_one``."""
    values = {
        "cpu": _ranged(cpu, CPU_RANGE, "cpu"),
        "ram_mb": _ranged(ram_mb, RAM_MB_RANGE, "ram_mb"),
        "disk_gb": _ranged(disk_gb, DISK_GB_RANGE, "disk_gb"),
    }
    result = {key: value for key, value in values.items() if value is not None}
    if require_one and not result:
        raise IbeeValidationError(
            "Provide at least one of cpu, ram_mb or disk_gb (or plan_id).", code="no_changes", field=None
        )
    return result


def validate_resize_plan_change(
    vm: typing.Any, *, cpu: int, ram_mb: int, confirm_downgrade: typing.Any
) -> None:
    """The shape must change; a smaller CPU or RAM needs ``confirm_downgrade=True``."""
    current_cpu = record_get(vm, "cpu")
    current_ram = record_get(vm, "ram_mb")
    if current_cpu == cpu and current_ram == ram_mb:
        raise IbeeValidationError(
            "The VM already has this CPU and RAM shape; nothing to change.", code="no_changes", field="cpu"
        )
    downgrade = (isinstance(current_cpu, int) and cpu < current_cpu) or (
        isinstance(current_ram, int) and ram_mb < current_ram
    )
    if downgrade and confirm_downgrade is not True:
        raise IbeeValidationError(
            "Downgrade requested. confirm_downgrade=True is required.",
            code="confirmation_required",
            field="confirm_downgrade",
        )


def validate_root_disk_growth(vm: typing.Any, new_size_gb: int) -> None:
    """Root disks only grow: ``new_size_gb`` must be larger than the current size."""
    current = record_get(vm, "disk_gb")
    if isinstance(current, (int, float)) and not isinstance(current, bool) and new_size_gb <= current:
        raise IbeeValidationError(
            f"Root disk shrink is not supported: new_size_gb must be greater than the current {current} GB.",
            code="root_disk_grow_only",
            field="new_size_gb",
        )


# ---------------------------------------------------------------------------
# Metrics and events
# ---------------------------------------------------------------------------

METRICS_RANGES: typing.Tuple[str, ...] = ("30m", "1h", "6h", "24h", "7d")
BANDWIDTH_MONTH_PATTERN = re.compile(r"^[0-9]{4}-(0[1-9]|1[0-2])$")


def validate_metrics_range(value: typing.Any) -> typing.Optional[str]:
    if value is None:
        return None
    value = getattr(value, "value", value)
    if value not in METRICS_RANGES:
        raise IbeeValidationError(
            "range must be one of: " + ", ".join(METRICS_RANGES) + ".", code="invalid_range", field="range"
        )
    return str(value)


def validate_bandwidth_month(month: typing.Any) -> str:
    if not isinstance(month, str) or BANDWIDTH_MONTH_PATTERN.fullmatch(month.strip()) is None:
        raise IbeeValidationError("month must look like YYYY-MM (for example 2026-08).", code="invalid_month", field="month")
    return month.strip()


def current_bandwidth_month(now: typing.Optional[dt.datetime] = None) -> str:
    """The current UTC month as ``YYYY-MM`` (the portal's default)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    return f"{now.year:04d}-{now.month:02d}"


def validate_events_limit(limit: typing.Any) -> typing.Optional[int]:
    return validate_limit(limit, maximum=500)


# ---------------------------------------------------------------------------
# Console
# ---------------------------------------------------------------------------


def validate_console_target(vm_type: typing.Any, console_type: typing.Any) -> None:
    """Graphical console sessions exist for cloud VMs only."""
    if vm_type is not None and str(getattr(vm_type, "value", vm_type)) != "cloud":
        raise IbeeValidationError(
            "Socket-based console sessions are currently available only for cloud VMs",
            code="console_not_supported",
            field="vm_type",
        )
    if console_type is not None and str(getattr(console_type, "value", console_type)) != "graphical":
        raise IbeeValidationError(
            "console_type must be 'graphical'.", code="invalid_console_type", field="console_type"
        )


# ---------------------------------------------------------------------------
# Create: plans, images, shape and network placement
# ---------------------------------------------------------------------------


def _plan_id(plan: typing.Any) -> str:
    return _text(record_get(plan, "plan_id") or record_get(plan, "id") or record_get(plan, "_id"))


def select_compute_plan(
    plans: typing.Sequence[typing.Any], plan_id: typing.Any, *, vm_type: str, field: str = "plan_id"
) -> typing.Dict[str, typing.Any]:
    """Find ``plan_id`` in a plan list; it must be selectable, priced and carry a billing SKU."""
    wanted = validate_required_text(plan_id, field=field)
    for plan in plans:
        if _plan_id(plan) == wanted:
            plain = as_plain(plan)
            if record_get(plain, "selectable") is not True or _text(record_get(plain, "pricing_status")).lower() != "priced":
                raise IbeeValidationError(
                    f"Plan '{wanted}' is not available for new {vm_type} VMs (not selectable or not priced).",
                    code="plan_not_selectable",
                    field=field,
                )
            return plain
    raise IbeeValidationError(
        f"Plan '{wanted}' is not offered for {vm_type} VMs in this site. List plans with "
        f"compute_catalog.list_compute_plans(vm_type='{vm_type}', site_id=...).",
        code="plan_not_found",
        field=field,
        details={"plan_ids": [_plan_id(plan) for plan in plans]},
    )


def select_compute_image(
    images: typing.Sequence[typing.Any], template_id: typing.Any, *, vm_type: str, site_id: str
) -> typing.Dict[str, typing.Any]:
    """Find ``template_id`` in an image list, compatible with the VM type and site."""
    wanted = validate_required_text(template_id, field="template_id", max_length=255)
    for image in images:
        plain = as_plain(image)
        if _text(plain.get("template_id") or plain.get("id")) != wanted:
            continue
        types = [str(getattr(t, "value", t)) for t in plain.get("compatible_vm_types") or []]
        sites = [str(s) for s in plain.get("site_ids") or []]
        if types and vm_type not in types:
            raise IbeeValidationError(
                f"Image '{wanted}' cannot be used for {vm_type} VMs.", code="image_not_compatible", field="template_id"
            )
        if sites and site_id not in sites:
            raise IbeeValidationError(
                f"Image '{wanted}' is not available in site '{site_id}'.", code="image_not_compatible", field="template_id"
            )
        return plain
    raise IbeeValidationError(
        f"Image '{wanted}' is not offered for {vm_type} VMs in this site. List images with "
        f"compute_catalog.list_compute_images(vm_type='{vm_type}', site_id=...).",
        code="image_not_found",
        field="template_id",
    )


def _match(field: str, supplied: typing.Any, expected: typing.Any, *, label: str) -> typing.Any:
    if supplied is None:
        return expected
    if expected is not None and supplied != expected:
        raise IbeeValidationError(
            f"{field} must match the {label} ({expected}); omit it to use the {label} value.",
            code="shape_mismatch",
            field=field,
        )
    return supplied


def resolve_vm_shape(
    plan: typing.Mapping[str, typing.Any],
    image: typing.Mapping[str, typing.Any],
    *,
    vm_type: str,
    cpu: typing.Any = None,
    ram_mb: typing.Any = None,
    disk_gb: typing.Any = None,
    os_type: typing.Any = None,
    os_distro: typing.Any = None,
    gpu_count: typing.Any = None,
    gpu_model: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """Take cpu/ram/disk (and GPU fields) from the plan and os fields from the image.

    Values passed by the caller must equal the plan/image values.
    """
    image_os_type = _text(getattr(image.get("os_type"), "value", image.get("os_type"))).lower() or None
    supplied_os_type = None if os_type is None else _text(getattr(os_type, "value", os_type)).lower()
    shape: typing.Dict[str, typing.Any] = {
        "cpu": _match("cpu", cpu, plan.get("cpu"), label="plan"),
        "ram_mb": _match("ram_mb", ram_mb, plan.get("ram_mb"), label="plan"),
        "disk_gb": _match("disk_gb", disk_gb, plan.get("disk_gb"), label="plan"),
        "os_type": _match("os_type", supplied_os_type, image_os_type, label="image"),
        "os_distro": _text(os_distro) or _text(image.get("os_distro")) or None,
    }
    if not isinstance(shape["cpu"], int) or shape["cpu"] < 1:
        raise IbeeValidationError("The plan has no valid cpu count.", code="invalid_plan", field="plan_id")
    if not isinstance(shape["ram_mb"], int) or shape["ram_mb"] < 512:
        raise IbeeValidationError("The plan has no valid ram_mb.", code="invalid_plan", field="plan_id")
    if not isinstance(shape["disk_gb"], int) or shape["disk_gb"] < 10:
        raise IbeeValidationError("The plan has no valid disk_gb.", code="invalid_plan", field="plan_id")
    if shape["os_type"] not in ("linux", "windows"):
        raise IbeeValidationError("os_type must be 'linux' or 'windows'.", code="invalid_os_type", field="os_type")
    if not shape["os_distro"]:
        raise IbeeValidationError("os_distro is required.", code="invalid_os_distro", field="os_distro")
    if vm_type == "gpu":
        if shape["os_type"] != "linux":
            raise IbeeValidationError(
                "GPU VMs created through the public API must use a Linux image.", code="invalid_os_type", field="os_type"
            )
        count = _match("gpu_count", gpu_count, plan.get("gpu_count"), label="plan")
        if not isinstance(count, int) or count < 1:
            raise IbeeValidationError("The GPU plan has no GPUs (gpu_count >= 1).", code="invalid_plan", field="gpu_count")
        shape["gpu_count"] = count
        plan_model = _text(plan.get("gpu_model")) or None
        supplied_model = _text(gpu_model) or None
        if plan_model and supplied_model and plan_model.lower() != supplied_model.lower():
            raise IbeeValidationError(
                f"gpu_model must match the plan ({plan_model}); omit it to use the plan value.",
                code="shape_mismatch",
                field="gpu_model",
            )
        model = plan_model or supplied_model
        if model:
            shape["gpu_model"] = model
    return shape


NETWORK_CONNECTIVITY: typing.Tuple[str, ...] = ("private", "nat", "public_ip")
_UNUSABLE_VPC_STATES = frozenset({"deleting", "deleted", "error", "failed"})


def normalize_vpc_connectivity_type(value: typing.Any) -> str:
    """``nat``/``nat_gateway`` -> ``nat_gateway``; ``private`` -> ``private``; anything else -> ``public``."""
    text = _text(getattr(value, "value", value)).lower()
    if text in ("nat", "nat_gateway"):
        return "nat_gateway"
    return "private" if text == "private" else "public"


def validate_network_request(
    *,
    vpc_id: typing.Any = None,
    subnet_id: typing.Any = None,
    network_connectivity: typing.Any = None,
    reserved_public_ip_id: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """Local VPC placement rules; returns the body fields (``vpc_attachment_mode`` is always ``primary``)."""
    vpc = validate_optional_text(vpc_id, field="vpc_id")
    subnet = validate_optional_text(subnet_id, field="subnet_id")
    reserved = validate_optional_text(reserved_public_ip_id, field="reserved_public_ip_id")
    connectivity = None
    if network_connectivity is not None:
        connectivity = _text(getattr(network_connectivity, "value", network_connectivity)).lower()
        if connectivity not in NETWORK_CONNECTIVITY:
            raise IbeeValidationError(
                "network_connectivity must be one of: private, nat, public_ip.",
                code="invalid_network_connectivity",
                field="network_connectivity",
            )
    if connectivity in ("nat", "private") and not vpc:
        raise IbeeValidationError(
            "Select a NAT Gateway VPC" if connectivity == "nat" else "Select a VPC for private networking",
            code="vpc_required",
            field="vpc_id",
        )
    if connectivity is not None and not vpc:
        raise IbeeValidationError(
            "network_connectivity requires vpc_id and subnet_id.", code="vpc_required", field="vpc_id"
        )
    if vpc and not subnet:
        raise IbeeValidationError("Select a subnet for this VPC", code="subnet_required", field="subnet_id")
    if subnet and not vpc:
        raise IbeeValidationError("subnet_id requires vpc_id.", code="vpc_required", field="vpc_id")
    if reserved and (not vpc or connectivity != "public_ip"):
        raise IbeeValidationError(
            "A reserved public IP can only be used with Public IP connectivity",
            code="invalid_network_connectivity",
            field="reserved_public_ip_id",
        )
    if not vpc:
        return {}
    body: typing.Dict[str, typing.Any] = {"vpc_id": vpc, "subnet_id": subnet, "vpc_attachment_mode": "primary"}
    if connectivity is not None:
        body["network_connectivity"] = connectivity
    if reserved:
        body["reserved_public_ip_id"] = reserved
    return body


def validate_vm_network_placement(
    *,
    site_id: str,
    network: typing.Mapping[str, typing.Any],
    vpc: typing.Any,
    subnet: typing.Any = None,
    reserved_ip: typing.Any = None,
) -> typing.Optional[typing.Dict[str, typing.Any]]:
    """Check fetched VPC/subnet/Reserved IP records; returns the Reserved IP SKU to attach."""
    vpc_site = _text(record_get(vpc, "site_id"))
    if vpc_site and vpc_site != site_id:
        raise IbeeValidationError(
            "The selected VPC is in a different site than the VM.", code="vpc_site_mismatch", field="vpc_id"
        )
    if _text(record_get(vpc, "status")).lower() in _UNUSABLE_VPC_STATES:
        raise IbeeValidationError("The selected VPC is not available.", code="vpc_unavailable", field="vpc_id")
    if subnet is not None:
        subnet_vpc = _text(record_get(subnet, "vpc_id"))
        if subnet_vpc and subnet_vpc != network.get("vpc_id"):
            raise IbeeValidationError(
                "The subnet does not belong to the selected VPC.", code="subnet_mismatch", field="subnet_id"
            )
    connectivity = network.get("network_connectivity") or "private"
    vpc_type = normalize_vpc_connectivity_type(record_get(vpc, "connectivity_type") or record_get(vpc, "connectivity"))
    if connectivity == "nat" and vpc_type != "nat_gateway":
        raise IbeeValidationError(
            "Select a NAT Gateway VPC for managed outbound internet",
            code="vpc_connectivity_mismatch",
            field="network_connectivity",
        )
    if connectivity == "public_ip" and vpc_type not in ("public", "private"):
        raise IbeeValidationError(
            "Select a Public (Instance IP) VPC for this network mode",
            code="vpc_connectivity_mismatch",
            field="network_connectivity",
        )
    if connectivity == "public_ip" and vpc_type == "private" and not network.get("reserved_public_ip_id"):
        raise IbeeValidationError(
            "Select an available Reserved IP for Public IP connectivity on a private VPC",
            code="reserved_ip_required",
            field="reserved_public_ip_id",
        )
    if reserved_ip is None:
        return None
    reserved_site = _text(record_get(reserved_ip, "site_id"))
    if reserved_site and reserved_site != site_id:
        raise IbeeValidationError(
            "The Reserved IP is in a different site than the VM.", code="reserved_ip_site_mismatch", field="reserved_public_ip_id"
        )
    for key in ("attached_resource_id", "attached_to", "nat_gateway_id", "vm_id"):
        if _text(record_get(reserved_ip, key)):
            raise IbeeValidationError(
                "The Reserved IP is already attached to another resource.",
                code="reserved_ip_attached",
                field="reserved_public_ip_id",
            )
    from .billing_catalog import require_billing_sku

    return require_billing_sku(record_get(reserved_ip, "billing_catalog"), "Selected Reserved IP", field="reserved_public_ip_id")


def validate_firewall_group_ids(ids: typing.Any) -> typing.List[str]:
    """At most one firewall group (the portal is single-select)."""
    values = normalize_id_list(ids, field="firewall_group_ids")
    if len(values) > 1:
        raise IbeeValidationError(
            "Select at most one firewall group.", code="invalid_firewall_group_ids", field="firewall_group_ids"
        )
    return values


__all__ = [
    "BANDWIDTH_MONTH_PATTERN",
    "COMPUTE_OPERATION_ID_PATTERN",
    "CPU_RANGE",
    "DISK_GB_RANGE",
    "MAX_BATCH_VMS",
    "METRICS_RANGES",
    "NETWORK_CONNECTIVITY",
    "PUBLIC_IP_ACTIONS",
    "RAM_MB_RANGE",
    "SSH_KEY_MODES",
    "SSH_KEY_TYPES",
    "VM_ACTIONS",
    "VM_ID_PATTERN",
    "VM_NAME_PATTERN",
    "as_plain",
    "assert_vm_action_allowed",
    "current_bandwidth_month",
    "expand_batch_names",
    "has_auto_assigned_public_ip",
    "is_windows_vm",
    "normalize_id_list",
    "normalize_ssh_key_secret_refs",
    "normalize_ssh_public_keys",
    "normalize_vm_record",
    "normalize_vpc_connectivity_type",
    "record_get",
    "resolve_delete_public_ip_action",
    "resolve_vm_shape",
    "select_compute_image",
    "select_compute_plan",
    "validate_access_update",
    "validate_bandwidth_month",
    "validate_compute_operation_id",
    "validate_console_target",
    "validate_events_limit",
    "validate_firewall_group_ids",
    "validate_metrics_range",
    "validate_network_request",
    "validate_optional_text",
    "validate_requested_by",
    "validate_required_text",
    "validate_resize_plan_change",
    "validate_resize_target",
    "validate_root_disk_growth",
    "validate_ssh_public_key",
    "validate_vm_id",
    "validate_vm_name",
    "validate_vm_network_placement",
    "vm_status",
]
