"""VM recovery rules (snapshots, backups, restores) and VM-side volume rules, ported from the IBEE portal."""

from __future__ import annotations

import datetime as dt
import math
import numbers
import typing

from . import IbeeValidationError, validate_limit, validate_offset, validate_search
from .compute import (
    as_plain,
    normalize_id_list,
    record_get,
    validate_optional_text,
    validate_required_text,
)

# ---------------------------------------------------------------------------
# Snapshots
# ---------------------------------------------------------------------------

SNAPSHOT_MODES: typing.Tuple[str, ...] = ("root_only", "all_attached", "selective")


def validate_snapshot_request(
    *, name: typing.Any, description: typing.Any = None, mode: typing.Any = None, selected_data_volume_ids: typing.Any = None
) -> typing.Dict[str, typing.Any]:
    """Snapshot create rules; returns the body fields (without ``billing_catalog``).

    ``name`` 1-255 characters after trimming; ``description`` at most 1024 (blank is
    omitted); ``mode`` defaults to ``all_attached``; ``selective`` needs at least one
    data volume id, the other modes take none.
    """
    body: typing.Dict[str, typing.Any] = {
        "name": validate_required_text(name, field="name", max_length=255, label="Snapshot name")
    }
    text = validate_optional_text(description, field="description", max_length=1024)
    if text is not None:
        body["description"] = text
    snapshot_mode = str(getattr(mode, "value", mode) or "all_attached")
    if snapshot_mode not in SNAPSHOT_MODES:
        raise IbeeValidationError(
            "mode must be one of: root_only, all_attached, selective.", code="invalid_snapshot_mode", field="mode"
        )
    ids = normalize_id_list(selected_data_volume_ids, field="selected_data_volume_ids")
    if snapshot_mode == "selective" and not ids:
        raise IbeeValidationError(
            "Select at least one attached data volume for a selective snapshot.",
            code="invalid_selected_data_volume_ids",
            field="selected_data_volume_ids",
        )
    if snapshot_mode != "selective" and ids:
        raise IbeeValidationError(
            "selected_data_volume_ids is only used with mode='selective'.",
            code="invalid_selected_data_volume_ids",
            field="selected_data_volume_ids",
        )
    body["mode"] = snapshot_mode
    body["selected_data_volume_ids"] = ids
    return body


def validate_snapshot_volumes_attached(vm: typing.Any, ids: typing.Sequence[str]) -> None:
    """Selective snapshot volumes must be attached to the VM."""
    attached = {
        str(record_get(item, "volume_id") or "").strip() for item in record_get(vm, "data_volumes") or []
    }
    missing = [volume_id for volume_id in ids if volume_id not in attached]
    if missing:
        raise IbeeValidationError(
            "Selected data volume(s) are not attached to this VM: " + ", ".join(missing),
            code="volume_not_attached",
            field="selected_data_volume_ids",
        )


def validate_recovery_list_params(
    *, limit: typing.Any = None, offset: typing.Any = None, search: typing.Any = None
) -> typing.Dict[str, typing.Any]:
    """Snapshot / backup lists: limit 1-200, offset >= 0, search trimmed (blank omitted)."""
    values = {
        "limit": validate_limit(limit, maximum=200),
        "offset": validate_offset(offset),
        "search": validate_search(search, max_length=10_000),
    }
    return {key: value for key, value in values.items() if value is not None}


BACKUP_RUN_STATUSES: typing.Tuple[str, ...] = ("queued", "running", "succeeded", "failed", "cancelled")


def validate_backup_statuses(statuses: typing.Any) -> typing.Optional[typing.List[str]]:
    """Each status is one of queued, running, succeeded, failed, cancelled."""
    if statuses is None:
        return None
    values = [statuses] if isinstance(statuses, str) else list(statuses)
    result: typing.List[str] = []
    for value in values:
        text = str(getattr(value, "value", value)).strip().lower()
        if text not in BACKUP_RUN_STATUSES:
            raise IbeeValidationError(
                "status must be one of: " + ", ".join(BACKUP_RUN_STATUSES) + ".", code="invalid_status", field="status"
            )
        if text not in result:
            result.append(text)
    return result


# ---------------------------------------------------------------------------
# Backup policies
# ---------------------------------------------------------------------------

BACKUP_FREQUENCIES: typing.Tuple[str, ...] = ("daily", "weekly")
DEFAULT_BACKUP_SCHEDULE: typing.Dict[str, typing.Any] = {
    "frequency": "daily",
    "hour": 12,
    "minute": 0,
    "window_minutes": 30,
    "timezone": "UTC",
}
DEFAULT_BACKUP_RETENTION: typing.Dict[str, typing.Any] = {
    "retention_days": 7,
    "full_backup_interval_days": 7,
    "incremental_enabled": True,
}


def _int_in(value: typing.Any, low: int, high: int, field: str) -> int:
    result = validate_limit(value, minimum=low, maximum=high, field=field)
    if result is None:
        raise IbeeValidationError(f"{field} must be an integer between {low} and {high}.", code=f"invalid_{field}", field=field)
    return result


def validate_timezone(timezone: typing.Any) -> str:
    """1-128 characters and a valid IANA time zone (the server silently falls back to UTC otherwise)."""
    if not isinstance(timezone, str) or not 1 <= len(timezone.strip()) <= 128:
        raise IbeeValidationError("timezone must be 1-128 characters.", code="invalid_timezone", field="timezone")
    value = timezone.strip()
    try:
        from zoneinfo import ZoneInfo

        ZoneInfo(value)
    except Exception:
        if value.upper() != "UTC":
            raise IbeeValidationError(
                f"timezone '{value}' is not a valid IANA time zone (for example 'Asia/Kolkata').",
                code="invalid_timezone",
                field="timezone",
            )
    return value


def validate_backup_schedule(
    schedule: typing.Any, *, base: typing.Optional[typing.Mapping[str, typing.Any]] = None
) -> typing.Dict[str, typing.Any]:
    """Full backup schedule object, as the portal sends it.

    Missing fields come from ``base`` (for example the saved policy) and then from
    the portal defaults (daily at 12:00 UTC, 30-minute window). A saved frequency
    other than daily/weekly (such as ``hourly``) is replaced by the default. ``frequency`` is
    ``daily`` or ``weekly``; ``day_of_week`` (0=Monday .. 6=Sunday) is required for
    weekly schedules and dropped for daily ones.
    """
    merged: typing.Dict[str, typing.Any] = dict(DEFAULT_BACKUP_SCHEDULE)
    saved = dict(as_plain(base))
    saved_frequency = getattr(saved.get("frequency"), "value", saved.get("frequency"))
    if saved_frequency is not None and str(saved_frequency).strip().lower() not in BACKUP_FREQUENCIES:
        # A saved frequency the portal cannot show (e.g. 'hourly' from 0.3.0) falls back to the
        # portal default ('daily') instead of failing a call that did not pass a frequency.
        saved.pop("frequency", None)
        saved.pop("day_of_week", None)
    for source in (saved, schedule):
        for key, value in as_plain(source).items():
            if value is not None:
                merged[key] = getattr(value, "value", value)
    frequency = str(merged.get("frequency") or "").strip().lower()
    if frequency not in BACKUP_FREQUENCIES:
        raise IbeeValidationError(
            "frequency must be 'daily' or 'weekly'.", code="invalid_frequency", field="frequency"
        )
    result: typing.Dict[str, typing.Any] = {
        "frequency": frequency,
        "hour": _int_in(merged.get("hour"), 0, 23, "hour"),
        "minute": _int_in(merged.get("minute"), 0, 59, "minute"),
        "timezone": validate_timezone(merged.get("timezone")),
        "window_minutes": _int_in(merged.get("window_minutes"), 5, 180, "window_minutes"),
    }
    explicit_day = as_plain(schedule).get("day_of_week")
    if frequency == "weekly":
        day = explicit_day if explicit_day is not None else merged.get("day_of_week")
        if day is None:
            raise IbeeValidationError(
                "day_of_week (0=Monday .. 6=Sunday) is required when frequency is weekly.",
                code="invalid_day_of_week",
                field="day_of_week",
            )
        result["day_of_week"] = _int_in(day, 0, 6, "day_of_week")
    elif explicit_day is not None:
        raise IbeeValidationError(
            "day_of_week is only used with frequency='weekly'.", code="invalid_day_of_week", field="day_of_week"
        )
    return result


def check_backup_schedule_input(schedule: typing.Any) -> None:
    """Check the schedule fields the caller passed, before any saved policy is read."""
    given = {key: getattr(value, "value", value) for key, value in as_plain(schedule).items() if value is not None}
    if "frequency" in given and str(given["frequency"]).strip().lower() not in BACKUP_FREQUENCIES:
        raise IbeeValidationError(
            "frequency must be 'daily' or 'weekly'.", code="invalid_frequency", field="frequency"
        )
    for key, low, high in (("hour", 0, 23), ("minute", 0, 59), ("window_minutes", 5, 180), ("day_of_week", 0, 6)):
        if key in given:
            _int_in(given[key], low, high, key)
    if "timezone" in given:
        validate_timezone(given["timezone"])
    if str(given.get("frequency") or "").strip().lower() == "daily" and "day_of_week" in given:
        raise IbeeValidationError(
            "day_of_week is only used with frequency='weekly'.", code="invalid_day_of_week", field="day_of_week"
        )


def validate_backup_retention(
    *, retention_days: typing.Any = None, full_backup_interval_days: typing.Any = None, incremental_enabled: typing.Any = None
) -> typing.Dict[str, typing.Any]:
    """retention_days 1-365, full_backup_interval_days 1-30, incremental_enabled bool."""
    result: typing.Dict[str, typing.Any] = {}
    if retention_days is not None:
        result["retention_days"] = _int_in(retention_days, 1, 365, "retention_days")
    if full_backup_interval_days is not None:
        result["full_backup_interval_days"] = _int_in(full_backup_interval_days, 1, 30, "full_backup_interval_days")
    if incremental_enabled is not None:
        if not isinstance(incremental_enabled, bool):
            raise IbeeValidationError(
                "incremental_enabled must be a boolean.", code="invalid_incremental_enabled", field="incremental_enabled"
            )
        result["incremental_enabled"] = incremental_enabled
    return result


def validate_next_run_at(next_run_at: typing.Any) -> dt.datetime:
    """``next_run_at`` must be timezone-aware (a naive time would be read as UTC)."""
    value = next_run_at
    if isinstance(value, str):
        try:
            value = dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            value = None
    if not isinstance(value, dt.datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise IbeeValidationError(
            "next_run_at must be a timezone-aware datetime (for example 2026-10-01T02:30:00+05:30).",
            code="invalid_next_run_at",
            field="next_run_at",
        )
    return value


def validate_backup_reason(reason: typing.Any) -> typing.Optional[str]:
    return validate_optional_text(reason, field="reason", max_length=512)


# ---------------------------------------------------------------------------
# Restores
# ---------------------------------------------------------------------------

RESTORE_TARGET_MODES: typing.Tuple[str, ...] = ("replace", "new_vm", "volume_only")
NEW_VM_ONLY_FIELDS: typing.Tuple[str, ...] = (
    "target_vm_name",
    "target_cpu",
    "target_ram_mb",
    "target_disk_gb",
    "target_plan_id",
    "target_plan_name",
    "target_plan_code",
    "target_plan_type",
    "target_performance_category",
    "target_plan_monthly_rate",
    "target_plan_hourly_rate",
    "target_bandwidth_tb",
    "target_bandwidth_display",
    "target_network_bandwidth",
    "target_compute_node_id",
    "target_gpu_type",
    "target_gpu_model",
    "target_gpu_count",
    "target_gpu_memory_gb",
    "target_gpu_memory_display",
    "target_site_id",
    "target_site_name",
    "target_billing_catalog",
    "target_volume_names",
    "vpc_id",
    "subnet_id",
    "network_connectivity",
    "ssh_key_ids",
)


def validate_restore_mode(target_mode: typing.Any) -> str:
    mode = str(getattr(target_mode, "value", target_mode) or "replace")
    if mode not in RESTORE_TARGET_MODES:
        raise IbeeValidationError(
            "target_mode must be one of: replace, new_vm, volume_only.", code="invalid_target_mode", field="target_mode"
        )
    return mode


def validate_restore_mode_combination(mode: str, fields: typing.Mapping[str, typing.Any]) -> None:
    """Fields allowed per restore mode (``new_vm`` targets, ``volume_only`` volume)."""
    present = [key for key in NEW_VM_ONLY_FIELDS if fields.get(key) is not None]
    if mode != "new_vm" and present:
        raise IbeeValidationError(
            f"{present[0]} is only used with target_mode='new_vm'.", code="invalid_restore_request", field=present[0]
        )
    selected = fields.get("selected_volume_id")
    if mode == "volume_only":
        validate_required_text(selected, field="selected_volume_id", label="selected_volume_id")
    elif selected is not None:
        raise IbeeValidationError(
            "selected_volume_id is only used with target_mode='volume_only'.",
            code="invalid_restore_request",
            field="selected_volume_id",
        )


def validate_restore_target(fields: typing.Mapping[str, typing.Any]) -> None:
    """New-VM restore target ranges (after plan resolution)."""
    name = fields.get("target_vm_name")
    if not isinstance(name, str) or not name.strip():
        raise IbeeValidationError("Enter a name for the restored VM", code="invalid_target_vm_name", field="target_vm_name")
    if len(name.strip()) > 255:
        raise IbeeValidationError(
            "target_vm_name must be at most 255 characters.", code="invalid_target_vm_name", field="target_vm_name"
        )
    for field, low, high in (
        ("target_cpu", 1, 256),
        ("target_ram_mb", 512, 2097152),
        ("target_disk_gb", 10, 10000),
    ):
        value = fields.get(field)
        if value is None or validate_limit(value, minimum=low, maximum=high, field=field) is None:
            raise IbeeValidationError(
                "Select a valid compute plan for the restored VM", code="invalid_restore_plan", field=field
            )
    if fields.get("target_gpu_count") is not None:
        validate_limit(fields.get("target_gpu_count"), minimum=0, maximum=16, field="target_gpu_count")
    if fields.get("target_billing_catalog") is None:
        raise IbeeValidationError(
            "Selected plan is missing Billing catalog data", code="invalid_billing_catalog", field="target_billing_catalog"
        )


def _positive(value: typing.Any) -> typing.Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def _trim_root_headroom(value: typing.Optional[float]) -> typing.Optional[float]:
    if value is None:
        return None
    provisioned = math.ceil(value)
    if provisioned > 1 and provisioned % 10 == 1:
        return float(provisioned - 1)
    return value


def _manifest(recovery_point: typing.Any) -> typing.List[typing.Dict[str, typing.Any]]:
    manifest = record_get(recovery_point, "volume_manifest") or []
    return [as_plain(item) for item in manifest if item is not None]


def _role(item: typing.Mapping[str, typing.Any]) -> str:
    role = item.get("role")
    return str(getattr(role, "value", role) or "").strip().lower()


def recovery_min_root_disk_gb(manifest: typing.Sequence[typing.Any]) -> typing.Optional[float]:
    """Smallest plan disk (GB, plan display scale) that can hold the captured root disk."""
    items = [as_plain(item) for item in manifest]
    if not items:
        return None
    root = next((item for item in items if _role(item) == "root"), items[0])
    value = _positive(root.get("display_size_gb"))
    if value is None:
        value = _positive(root.get("size_gb"))
    return _trim_root_headroom(value)


def _date_token(created_at: typing.Any) -> str:
    value = created_at
    if isinstance(value, str):
        try:
            value = dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            value = None
    if not isinstance(value, dt.datetime):
        value = dt.datetime.now(dt.timezone.utc)
    if value.tzinfo is not None:
        value = value.astimezone(dt.timezone.utc)
    return value.strftime("%Y%m%d")


def recovery_default_vm_name(vm_name: typing.Any, kind: str, created_at: typing.Any) -> str:
    """``<vm name>-<snapshot|backup>-restored-YYYYMMDD`` (date in UTC)."""
    base = str(vm_name or "").strip() or "vm"
    return f"{base}-{kind}-restored-{_date_token(created_at)}"


def captured_data_volumes(manifest: typing.Sequence[typing.Any]) -> typing.List[typing.Dict[str, typing.Any]]:
    """Data volumes of a recovery point (``role == data``, or position > 0 without a role)."""
    result = []
    for index, raw in enumerate(manifest):
        item = as_plain(raw)
        role = _role(item)
        if (role and role != "data") or (not role and index == 0):
            continue
        if str(item.get("source_volume_id") or item.get("volume_id") or item.get("id") or "").strip():
            result.append(item)
    return result


def _volume_id(item: typing.Mapping[str, typing.Any]) -> str:
    return str(item.get("source_volume_id") or item.get("volume_id") or item.get("id") or "").strip()


def recovery_target_volume_names(
    manifest: typing.Sequence[typing.Any], kind: str, created_at: typing.Any
) -> typing.Dict[str, str]:
    """Portal default names for restored data volumes."""
    suffix = f"{kind}-restored-{_date_token(created_at)}"
    names: typing.Dict[str, str] = {}
    for item in captured_data_volumes(manifest):
        volume_id = _volume_id(item)
        display = next(
            (
                str(item.get(key)).strip()
                for key in ("source_volume_name", "display_name", "resource_name", "volume_name")
                if item.get(key) is not None and str(item.get(key)).strip()
            ),
            volume_id,
        )
        names[volume_id] = f"{display}-{suffix}"
    return names


def validate_target_volume_names(
    manifest: typing.Sequence[typing.Any], names: typing.Any
) -> typing.Dict[str, str]:
    """Keys must be exactly the captured data volume ids; values 1-255 characters after trimming."""
    if not isinstance(names, typing.Mapping):
        raise IbeeValidationError(
            "target_volume_names must map source volume ids to names.", code="invalid_target_volume_names", field="target_volume_names"
        )
    captured = {_volume_id(item) for item in captured_data_volumes(manifest)}
    result: typing.Dict[str, str] = {}
    for key, value in names.items():
        volume_id = str(key).strip()
        if volume_id not in captured:
            raise IbeeValidationError(
                f"target_volume_names references volume '{volume_id}', which is not a captured data volume.",
                code="invalid_target_volume_names",
                field="target_volume_names",
            )
        result[volume_id] = validate_required_text(value, field="target_volume_names", max_length=255, label="Volume name")
    missing = [volume_id for volume_id in sorted(captured) if volume_id and volume_id not in result]
    if missing:
        raise IbeeValidationError(
            f"target_volume_names is missing a name for: {', '.join(missing)}.",
            code="invalid_target_volume_names",
            field="target_volume_names",
        )
    return result


def restore_target_from_plan(plan: typing.Mapping[str, typing.Any], *, vm: typing.Any = None) -> typing.Dict[str, typing.Any]:
    """Map a public compute plan to the ``target_*`` fields of a new-VM restore (portal mapping)."""
    catalog = plan.get("billing_catalog")
    if not isinstance(catalog, typing.Mapping):
        raise IbeeValidationError(
            "Selected plan is missing Billing catalog data", code="invalid_billing_catalog", field="target_plan_id"
        )
    fields: typing.Dict[str, typing.Any] = {
        "target_plan_id": plan.get("plan_id"),
        "target_plan_name": plan.get("name"),
        "target_plan_code": plan.get("code"),
        "target_cpu": plan.get("cpu"),
        "target_ram_mb": plan.get("ram_mb"),
        "target_disk_gb": plan.get("disk_gb"),
        "target_billing_catalog": dict(catalog),
        "target_site_id": plan.get("site_id") or record_get(vm, "site_id"),
    }
    if (plan.get("gpu_count") or 0) > 0:
        fields["target_gpu_count"] = plan.get("gpu_count")
        fields["target_gpu_model"] = plan.get("gpu_model")
        fields["target_gpu_memory_gb"] = plan.get("gpu_memory_gb")
    for source, target in (("monthly_price_minor", "target_plan_monthly_rate"), ("hourly_price_minor", "target_plan_hourly_rate")):
        value = plan.get(source)
        if isinstance(value, numbers.Real) and not isinstance(value, bool):
            fields[target] = value / 100
    return {key: value for key, value in fields.items() if value is not None}


def select_restore_plan(
    plans: typing.Sequence[typing.Any], plan_id: typing.Any, *, min_root_disk_gb: typing.Optional[float]
) -> typing.Dict[str, typing.Any]:
    """The restore plan must be listed, selectable and at least as large as the captured root disk."""
    wanted = str(plan_id or "").strip()
    eligible = [
        str(record_get(plan, "plan_id"))
        for plan in plans
        if record_get(plan, "selectable") is True
        and (min_root_disk_gb is None or (record_get(plan, "disk_gb") or 0) >= min_root_disk_gb)
    ]
    for plan in plans:
        if str(record_get(plan, "plan_id") or "").strip() != wanted:
            continue
        plain = as_plain(plan)
        if plain.get("selectable") is not True:
            raise IbeeValidationError(
                "Select a valid compute plan for the restored VM",
                code="invalid_restore_plan",
                field="target_plan_id",
                details={"eligible_plan_ids": eligible},
            )
        if min_root_disk_gb is not None and (plain.get("disk_gb") or 0) < min_root_disk_gb:
            raise IbeeValidationError(
                f"Root disk must be at least {min_root_disk_gb:g} GB. Eligible plans: {', '.join(eligible) or 'none'}.",
                code="restore_disk_too_small",
                field="target_plan_id",
                details={"eligible_plan_ids": eligible},
            )
        return plain
    raise IbeeValidationError(
        f"Select a valid compute plan for the restored VM (plan '{wanted}' is not listed). "
        f"Eligible plans: {', '.join(eligible) or 'none'}.",
        code="invalid_restore_plan",
        field="target_plan_id",
        details={"eligible_plan_ids": eligible},
    )


def validate_snapshot_ready(snapshot: typing.Any) -> None:
    status = str(record_get(snapshot, "status") or "").strip().lower()
    if status not in ("succeeded", "available"):
        raise IbeeValidationError(
            "Only ready snapshot sets can be restored.", code="recovery_point_not_ready", field="snapshot_set_id"
        )


def validate_backup_ready(run: typing.Any) -> None:
    status = str(getattr(record_get(run, "status"), "value", record_get(run, "status")) or "").strip().lower()
    if status != "succeeded":
        raise IbeeValidationError(
            "Only successful backups can be restored.", code="recovery_point_not_ready", field="recovery_point_id"
        )


def validate_restore_vm_state(vm: typing.Any) -> None:
    status = str(getattr(record_get(vm, "status"), "value", record_get(vm, "status")) or "").strip().lower()
    if status not in ("running", "stopped"):
        raise IbeeValidationError(
            f"Snapshot restore is unavailable while the VM is {status or 'unknown'}",
            code="invalid_vm_state",
            field="vm_id",
        )


def validate_snapshot_deletable(snapshot: typing.Any) -> None:
    status = str(record_get(snapshot, "status") or "").strip().lower()
    if status in ("running", "restoring"):
        raise IbeeValidationError(
            "Cannot delete a snapshot while restore is in progress.", code="snapshot_busy", field="snapshot_set_id"
        )


def validate_volume_only_selection(snapshot: typing.Any, vm: typing.Any, selected_volume_id: str) -> None:
    """The volume must be in the snapshot and still attached to the VM."""
    items = _manifest(snapshot)
    item = next((entry for entry in items if _volume_id(entry) == selected_volume_id), None)
    if item is None:
        raise IbeeValidationError(
            "selected_volume_id is not part of this snapshot set.", code="volume_not_in_recovery_point", field="selected_volume_id"
        )
    if vm is None:
        return
    if _role(item) == "root" or (not _role(item) and items and items[0] is item):
        attached = {
            str(record_get(vm, key) or "").strip()
            for key in ("root_volume_active_id", "root_volume_clone_id", "root_volume_full_id", "volume_id")
        }
    else:
        attached = {str(record_get(entry, "volume_id") or "").strip() for entry in record_get(vm, "data_volumes") or []}
    if selected_volume_id not in attached:
        raise IbeeValidationError(
            "The selected snapshot disk is no longer attached to this VM. Use Create New VM to restore the captured "
            "topology, or select a currently attached disk.",
            code="volume_not_attached",
            field="selected_volume_id",
        )


# ---------------------------------------------------------------------------
# VM-side volumes
# ---------------------------------------------------------------------------

ATTACH_MODES: typing.Tuple[str, ...] = ("single-writer", "multi-writer")
_BUSY_VOLUME_STATES = frozenset({"creating", "attaching", "detaching", "resizing", "deleting"})


def validate_detach_confirmation(confirm_unmounted: typing.Any, force: typing.Any) -> None:
    if confirm_unmounted is not True and force is not True:
        raise IbeeValidationError(
            "Confirm the volume is unmounted in the guest (confirm_unmounted=True) or pass force=True.",
            code="confirmation_required",
            field="confirm_unmounted",
        )


def validate_attach_mode(mode: typing.Any) -> str:
    value = str(getattr(mode, "value", mode) or "single-writer")
    if value not in ATTACH_MODES:
        raise IbeeValidationError(
            "mode must be 'single-writer' or 'multi-writer'.", code="invalid_attach_mode", field="mode"
        )
    return value


def validate_attach_preconditions(volume: typing.Any, vm: typing.Any = None) -> None:
    """Portal attach checks on the block volume (and the VM's site when known)."""
    if record_get(volume, "attachments"):
        raise IbeeValidationError("Volume is already attached", code="volume_attached", field="volume_id")
    state = str(record_get(volume, "state") or record_get(volume, "status") or "").strip().lower()
    if state in _BUSY_VOLUME_STATES:
        raise IbeeValidationError(
            f"Volume is currently {state}. Retry attach once workflow completes.", code="volume_busy", field="volume_id"
        )
    volume_site = str(record_get(volume, "site_id") or "").strip()
    vm_site = str(record_get(vm, "site_id") or "").strip() if vm is not None else ""
    if volume_site and vm_site and volume_site != vm_site:
        site_name = record_get(volume, "site_name") or volume_site
        raise IbeeValidationError(f"Select a server in {site_name}", code="site_mismatch", field="vm_id")


def volume_billing_catalog(volume: typing.Any) -> typing.Any:
    """The volume's SKU: ``billing_catalog`` or ``metadata.billing_catalog``."""
    catalog = record_get(volume, "billing_catalog")
    if catalog is None:
        metadata = record_get(volume, "metadata")
        catalog = record_get(metadata, "billing_catalog") if metadata is not None else None
    return catalog


__all__ = [
    "ATTACH_MODES",
    "BACKUP_FREQUENCIES",
    "BACKUP_RUN_STATUSES",
    "DEFAULT_BACKUP_RETENTION",
    "DEFAULT_BACKUP_SCHEDULE",
    "NEW_VM_ONLY_FIELDS",
    "RESTORE_TARGET_MODES",
    "SNAPSHOT_MODES",
    "captured_data_volumes",
    "recovery_default_vm_name",
    "recovery_min_root_disk_gb",
    "recovery_target_volume_names",
    "restore_target_from_plan",
    "select_restore_plan",
    "validate_attach_mode",
    "validate_attach_preconditions",
    "validate_backup_ready",
    "validate_backup_reason",
    "validate_backup_retention",
    "validate_backup_schedule",
    "check_backup_schedule_input",
    "validate_backup_statuses",
    "validate_detach_confirmation",
    "validate_next_run_at",
    "validate_recovery_list_params",
    "validate_restore_mode",
    "validate_restore_mode_combination",
    "validate_restore_target",
    "validate_restore_vm_state",
    "validate_snapshot_deletable",
    "validate_snapshot_ready",
    "validate_snapshot_request",
    "validate_snapshot_volumes_attached",
    "validate_target_volume_names",
    "validate_timezone",
    "validate_volume_only_selection",
    "volume_billing_catalog",
]
