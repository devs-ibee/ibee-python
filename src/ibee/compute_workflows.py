# Hand-written (listed in .fernignore).
"""Portal-equivalent request flows for cloud and GPU VMs, VM recovery and VM-side volumes.

Each flow is a generator that yields :class:`Call` objects (the HTTP requests it
needs, including read-only pre-steps such as resolving the plan) and receives the
parsed responses. :func:`run_sync` and :func:`run_async` drive a flow over the
sync or async transport, so ``Ibee`` and ``AsyncIbee`` share one implementation.

Every rule is checked with :mod:`ibee.validation` before the request it guards.
"""

from __future__ import annotations

import dataclasses
import typing

from .core.pydantic_utilities import parse_obj_as
from .core.request_options import RequestOptions
from .errors.forbidden_error import ForbiddenError
from .errors.not_found_error import NotFoundError
from .types.backup_policy import BackupPolicy
from .types.backup_run import BackupRun
from .types.backup_run_list import BackupRunList
from .types.mount_guidance_acknowledge import MountGuidanceAcknowledge
from .types.operation_accepted import OperationAccepted
from .types.recovery_restore import RecoveryRestore
from .types.snapshot_delete_result import SnapshotDeleteResult
from .types.snapshot_set import SnapshotSet
from .types.snapshot_set_list import SnapshotSetList
from .types.vm_console_session import VmConsoleSession
from .types.vm_resize_precheck import VmResizePrecheck
from .validation import (
    IbeeValidationError,
    apply_billing_term_to_catalog,
    assert_volume_attachable,
    assert_vm_action_allowed,
    resolve_backup_recovery_point_id,
    resolve_volume_billing_catalog,
    validate_block_volume_id,
    build_vm_billing_catalog,
    normalize_billing_term,
    normalize_id_list,
    normalize_ssh_public_keys,
    record_get,
    recovery_default_vm_name,
    recovery_min_root_disk_gb,
    recovery_target_volume_names,
    resolve_delete_public_ip_action,
    resolve_vm_shape,
    restore_target_from_plan,
    select_compute_image,
    select_compute_plan,
    select_restore_plan,
    validate_access_update,
    validate_attach_mode,
    validate_attach_preconditions,
    validate_backup_ready,
    validate_backup_reason,
    validate_backup_retention,
    validate_backup_schedule,
    check_backup_schedule_input,
    validate_backup_statuses,
    validate_billing_catalog,
    validate_console_target,
    validate_detach_confirmation,
    validate_firewall_group_ids,
    validate_network_request,
    validate_next_run_at,
    validate_optional_text,
    validate_recovery_list_params,
    validate_requested_by,
    validate_required_text,
    validate_resize_plan_change,
    validate_resize_target,
    validate_restore_mode,
    validate_restore_mode_combination,
    validate_restore_target,
    validate_restore_vm_state,
    validate_root_disk_growth,
    validate_snapshot_deletable,
    validate_snapshot_ready,
    validate_snapshot_request,
    validate_snapshot_volumes_attached,
    validate_target_volume_names,
    validate_vm_id,
    validate_vm_name,
    validate_vm_network_placement,
    validate_volume_only_selection,
    volume_billing_catalog,
)
from .validation.compute import is_windows_vm

if typing.TYPE_CHECKING:
    from .core.client_wrapper import AsyncClientWrapper, SyncClientWrapper

T = typing.TypeVar("T")

#: Parse modes for :class:`Call`.
JSON = "json"
RESPONSE = "response"


@dataclasses.dataclass(frozen=True)
class Call:
    """One HTTP request of a flow. ``main`` marks the request the caller asked for."""

    method: str
    path: str
    params: typing.Optional[typing.Dict[str, typing.Any]] = None
    json: typing.Any = None
    headers: typing.Optional[typing.Dict[str, typing.Any]] = None
    parse: typing.Any = JSON
    main: bool = False


@dataclasses.dataclass(frozen=True)
class Sleep:
    """A pause between polls (``time.sleep`` / ``asyncio.sleep`` depending on the runner)."""

    seconds: float


Flow = typing.Generator[typing.Union[Call, Sleep], typing.Any, T]

_PRESTEP_OPTION_KEYS = ("timeout_in_seconds", "max_retries", "additional_headers")


def _options_for(call: Call, request_options: typing.Optional[RequestOptions]) -> typing.Optional[RequestOptions]:
    if request_options is None or call.main:
        return request_options
    return typing.cast(
        RequestOptions, {key: request_options[key] for key in _PRESTEP_OPTION_KEYS if key in request_options}  # type: ignore[literal-required]
    )


def _parse(call: Call, response: typing.Any) -> typing.Any:
    if call.parse == RESPONSE:
        return response
    if call.parse is None:
        return None
    try:
        data = response.json()
    except Exception:
        data = None
    if call.parse == JSON:
        return data
    return parse_obj_as(type_=call.parse, object_=data)  # type: ignore[arg-type]


def _request_kwargs(call: Call, request_options: typing.Optional[RequestOptions]) -> typing.Dict[str, typing.Any]:
    headers = dict(call.headers or {})
    if call.json is not None:
        headers.setdefault("content-type", "application/json")
    return {
        "method": call.method,
        "params": call.params,
        "json": call.json,
        "headers": headers or None,
        "request_options": _options_for(call, request_options),
    }


def run_sync(
    client_wrapper: "SyncClientWrapper", flow: Flow[T], request_options: typing.Optional[RequestOptions] = None
) -> T:
    """Drive ``flow`` with the synchronous HTTP client."""
    value: typing.Any = None
    error: typing.Optional[BaseException] = None
    while True:
        try:
            call = flow.throw(error) if error is not None else flow.send(value)
        except StopIteration as stop:
            return typing.cast(T, stop.value)
        if isinstance(call, Sleep):
            import time

            time.sleep(max(call.seconds, 0.0))
            value, error = None, None
            continue
        try:
            response = client_wrapper.httpx_client.request(call.path, **_request_kwargs(call, request_options))
            value, error = _parse(call, response), None
        except Exception as exc:  # handed to the flow, which may handle it (e.g. 404 -> None)
            value, error = None, exc


async def run_async(
    client_wrapper: "AsyncClientWrapper", flow: Flow[T], request_options: typing.Optional[RequestOptions] = None
) -> T:
    """Drive ``flow`` with the asynchronous HTTP client."""
    value: typing.Any = None
    error: typing.Optional[BaseException] = None
    while True:
        try:
            call = flow.throw(error) if error is not None else flow.send(value)
        except StopIteration as stop:
            return typing.cast(T, stop.value)
        if isinstance(call, Sleep):
            import asyncio

            await asyncio.sleep(max(call.seconds, 0.0))
            value, error = None, None
            continue
        try:
            response = await client_wrapper.httpx_client.request(call.path, **_request_kwargs(call, request_options))
            value, error = _parse(call, response), None
        except Exception as exc:
            value, error = None, exc


def clean_kwargs(values: typing.Mapping[str, typing.Any]) -> typing.Dict[str, typing.Any]:
    """Method ``locals()`` minus ``self``/``request_options``, with the ``OMIT`` sentinel mapped to ``None``."""
    return {
        key: (None if value is ... else value)
        for key, value in values.items()
        if key not in ("self", "request_options", "__class__")
    }


# ---------------------------------------------------------------------------
# Paths and shared pre-steps
# ---------------------------------------------------------------------------

FAMILIES = ("cloud", "gpu")


def _family(family: str) -> str:
    if family not in FAMILIES:
        raise ValueError(f"unknown VM family {family!r}")
    return family


def vm_collection(family: str) -> str:
    return f"compute/{_family(family)}-vms"


def vm_path(family: str, vm_id: str) -> str:
    from urllib.parse import quote

    return f"{vm_collection(family)}/{quote(vm_id, safe='')}"


def _seg(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")


def _ws(workspace_id: str, **extra: typing.Any) -> typing.Dict[str, typing.Any]:
    params: typing.Dict[str, typing.Any] = {"workspace_id": workspace_id}
    params.update({key: value for key, value in extra.items() if value is not None})
    return params


def _compact(body: typing.Mapping[str, typing.Any]) -> typing.Dict[str, typing.Any]:
    return {key: value for key, value in body.items() if value is not None}


def _key_header(idempotency_key: typing.Optional[str]) -> typing.Optional[typing.Dict[str, str]]:
    return {"X-Idempotency-Key": idempotency_key} if idempotency_key is not None else None


def get_vm(family: str, workspace_id: str, vm_id: str) -> Flow[typing.Dict[str, typing.Any]]:
    """Pre-step: the VM record as a dict (``_id`` also exposed as ``id``)."""
    vm = yield Call("GET", vm_path(family, vm_id), params=_ws(workspace_id))
    vm = dict(vm) if isinstance(vm, dict) else {}
    if not vm.get("id") and vm.get("_id") is not None:
        vm["id"] = str(vm["_id"])
    return vm


def list_plans(workspace_id: str, vm_type: str, site_id: typing.Optional[str]) -> Flow[typing.List[typing.Dict[str, typing.Any]]]:
    data = yield Call("GET", "compute/plans", params=_ws(workspace_id, vm_type=vm_type, site_id=site_id))
    plans = data.get("plans") if isinstance(data, dict) else data
    return [plan for plan in plans or [] if isinstance(plan, dict)]


def list_images(workspace_id: str, vm_type: str, site_id: typing.Optional[str]) -> Flow[typing.List[typing.Dict[str, typing.Any]]]:
    data = yield Call("GET", "compute/images", params=_ws(workspace_id, vm_type=vm_type, site_id=site_id))
    images = data.get("images") if isinstance(data, dict) else data
    return [image for image in images or [] if isinstance(image, dict)]


def billing_preflight(
    workspace_id: str,
    *,
    sku_code: typing.Optional[str] = None,
    estimated_cost_minor: typing.Optional[int] = None,
    resource_type: str = "resource",
) -> Flow[typing.Any]:
    """Deprecated compatibility no-op shared by mutation workflows.

    Billing admission and pricing belong to the upstream mutation. Explicit
    diagnostics remain available through ``billing.check_resource_eligibility``.
    Keep this a generator so sync and async callers retain the same contract.
    """
    yield from ()


def _maybe_state(vm: typing.Any, action: str, check_state: typing.Optional[bool]) -> None:
    if check_state is not False and vm is not None:
        assert_vm_action_allowed(vm, action)


def _opt_in_state(vm: typing.Any, action: str, check_state: typing.Optional[bool]) -> None:
    """The portal state matrix, applied only with ``check_state=True`` (0.3.0 default kept)."""
    if check_state is True and vm is not None:
        assert_vm_action_allowed(vm, action)


# ---------------------------------------------------------------------------
# VM lifecycle
# ---------------------------------------------------------------------------


def create_vm(
    family: str,
    *,
    workspace_id: str,
    idempotency_key: typing.Optional[str] = None,
    name: typing.Any = None,
    site_id: typing.Any = None,
    plan_id: typing.Any = None,
    template_id: typing.Any = None,
    os_type: typing.Any = None,
    os_distro: typing.Any = None,
    cpu: typing.Any = None,
    ram_mb: typing.Any = None,
    disk_gb: typing.Any = None,
    gpu_count: typing.Any = None,
    gpu_model: typing.Any = None,
    billing_catalog: typing.Any = None,
    billing_term: typing.Any = None,
    windows_license: typing.Any = None,
    ssh_key_ids: typing.Any = None,
    ssh_keys: typing.Any = None,
    firewall_group_ids: typing.Any = None,
    vpc_id: typing.Any = None,
    subnet_id: typing.Any = None,
    network_connectivity: typing.Any = None,
    reserved_public_ip_id: typing.Any = None,
    tags: typing.Any = None,
    requested_by: typing.Any = None,
    preflight_billing: bool = False,
) -> Flow[OperationAccepted]:
    """Portal deploy: resolve plan and image, build ``billing_catalog`` for the term, then create."""
    vm_type = _family(family)
    name = validate_vm_name(name)
    site = validate_required_text(
        site_id,
        field="site_id",
        label="site_id (copy it from compute_catalog.list_compute_sites; the API needs it to place the VM)",
    )
    term = normalize_billing_term(billing_term)
    keys = normalize_ssh_public_keys(ssh_keys)
    key_ids = normalize_id_list(ssh_key_ids, field="ssh_key_ids")
    firewalls = validate_firewall_group_ids(firewall_group_ids)
    network = validate_network_request(
        vpc_id=vpc_id, subnet_id=subnet_id, network_connectivity=network_connectivity, reserved_public_ip_id=reserved_public_ip_id
    )
    requested = validate_requested_by(requested_by)
    validate_required_text(plan_id, field="plan_id")
    validate_required_text(template_id, field="template_id", max_length=255)

    explicit = billing_catalog is not None and all(
        value is not None for value in (cpu, ram_mb, disk_gb, os_type, os_distro, *((gpu_count,) if vm_type == "gpu" else ()))
    )
    if explicit:
        # Advanced single-request mode: the caller supplied the SKU and the whole shape.
        plan: typing.Dict[str, typing.Any] = {
            "plan_id": str(plan_id).strip(),
            "cpu": cpu,
            "ram_mb": ram_mb,
            "disk_gb": disk_gb,
            "gpu_count": gpu_count,
            "gpu_model": gpu_model,
        }
        image: typing.Dict[str, typing.Any] = {"template_id": str(template_id).strip(), "os_type": os_type, "os_distro": os_distro}
    else:
        plans = yield from list_plans(workspace_id, vm_type, site)
        plan = select_compute_plan(plans, plan_id, vm_type=vm_type)
        images = yield from list_images(workspace_id, vm_type, site)
        image = select_compute_image(images, template_id, vm_type=vm_type, site_id=site)
    shape = resolve_vm_shape(
        plan,
        image,
        vm_type=vm_type,
        cpu=None if explicit else cpu,
        ram_mb=None if explicit else ram_mb,
        disk_gb=None if explicit else disk_gb,
        os_type=None if explicit else os_type,
        os_distro=None if explicit else os_distro,
        gpu_count=None if explicit else gpu_count,
        gpu_model=None if explicit else gpu_model,
    )

    reserved_catalog = None
    if network:
        vpc = yield Call("GET", f"networking/vpcs/{_seg(network['vpc_id'])}", params=_ws(workspace_id))
        subnet = yield Call(
            "GET",
            f"networking/vpcs/{_seg(network['vpc_id'])}/subnets/{_seg(network['subnet_id'])}",
            params=_ws(workspace_id),
        )
        reserved = None
        if network.get("reserved_public_ip_id"):
            reserved = yield Call(
                "GET", f"networking/reserved-ips/{_seg(network['reserved_public_ip_id'])}", params=_ws(workspace_id)
            )
        reserved_catalog = validate_vm_network_placement(
            site_id=site, network=network, vpc=vpc, subnet=subnet, reserved_ip=reserved
        )

    if billing_catalog is not None:
        catalog = validate_billing_catalog(billing_catalog, context="billing_catalog")
        # The caller's catalog gets the chosen term too (the plan must offer it).
        catalog = apply_billing_term_to_catalog(catalog, term, label="billing_catalog")
        attached = catalog.get("attached_skus") or {}
        if shape["os_type"] == "windows":
            if "windows_license" not in attached:
                catalog = build_vm_billing_catalog(
                    catalog, term=term, apply_term=term is not None, os_type="windows", cpu=shape["cpu"],
                    windows_license=windows_license, context="billing_catalog",
                )
        elif "windows_license" in attached or windows_license is not None:
            raise IbeeValidationError(
                "windows_license is only allowed for Windows VMs.", code="windows_license_not_allowed", field="windows_license"
            )
        if reserved_catalog is not None:
            catalog = {**catalog, "attached_skus": {**(catalog.get("attached_skus") or {}), "reserved_ip": reserved_catalog}}
    else:
        catalog = build_vm_billing_catalog(
            plan.get("billing_catalog"),
            term=term,
            apply_term=vm_type == "cloud" or term is not None,
            os_type=shape["os_type"],
            cpu=shape["cpu"],
            windows_license=windows_license,
            reserved_ip_billing_catalog=reserved_catalog,
        )

    if preflight_billing:
        # Legacy flag: the shared helper performs no request or decision.
        yield from billing_preflight(
            workspace_id,
            resource_type="gpu_vm" if vm_type == "gpu" else "vm",
        )

    body: typing.Dict[str, typing.Any] = {
        "name": name,
        "site_id": site,
        "plan_id": str(plan.get("plan_id")),
        "template_id": str(image.get("template_id") or template_id).strip(),
        **shape,
        "billing_catalog": catalog,
    }
    if key_ids:
        body["ssh_key_ids"] = key_ids
    if keys:
        body["ssh_keys"] = keys
    if firewalls:
        body["firewall_group_id"] = firewalls[0]
        body["firewall_group_ids"] = firewalls
    body.update(network)
    if tags is not None:
        body["tags"] = list(tags)
    if requested is not None:
        body["requested_by"] = requested
    result = yield Call(
        "POST",
        vm_collection(vm_type),
        params=_ws(workspace_id),
        json=body,
        headers=_key_header(idempotency_key),
        parse=OperationAccepted,
        main=True,
    )
    return typing.cast(OperationAccepted, result)


def delete_vm(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    idempotency_key: typing.Optional[str] = None,
    public_ip_action: typing.Any = None,
    reserved_ip_label: typing.Any = None,
    reserved_ip_billing_catalog: typing.Any = None,
    requested_by: typing.Any = None,
    preflight_billing: bool = False,
    check_state: typing.Optional[bool] = None,
) -> Flow[OperationAccepted]:
    """Portal delete dialog: decide what happens to an auto-assigned public IP (default: release)."""
    vm_id = validate_vm_id(vm_id)
    requested = validate_requested_by(requested_by)
    action = None if public_ip_action is None else str(public_ip_action).strip().lower()
    vm = None
    if not (check_state is not True and action == "release"):
        vm = yield from get_vm(family, workspace_id, vm_id)
        _maybe_state(vm, "delete", check_state)
    body = resolve_delete_public_ip_action(
        vm,
        public_ip_action=public_ip_action,
        reserved_ip_label=reserved_ip_label,
        reserved_ip_billing_catalog=reserved_ip_billing_catalog,
    )
    if body and body.get("public_ip_action") == "reserve" and preflight_billing:
        yield from billing_preflight(
            workspace_id, sku_code=body["reserved_ip_billing_catalog"].get("sku_code"), resource_type="reserved_ip"
        )
    if requested is not None:
        body = {**(body or {}), "requested_by": requested}
    result = yield Call(
        "DELETE",
        vm_path(family, vm_id),
        params=_ws(workspace_id),
        json=body or None,
        headers=_key_header(idempotency_key),
        parse=OperationAccepted,
        main=True,
    )
    return typing.cast(OperationAccepted, result)


def power_action(
    family: str,
    action: str,
    *,
    workspace_id: str,
    vm_id: str,
    idempotency_key: typing.Optional[str] = None,
    force: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[OperationAccepted]:
    """Start / stop / reboot; with ``check_state=True`` the portal state rule is checked first."""
    vm_id = validate_vm_id(vm_id)
    if check_state:
        vm = yield from get_vm(family, workspace_id, vm_id)
        assert_vm_action_allowed(vm, action)
    result = yield Call(
        "POST",
        f"{vm_path(family, vm_id)}/actions/{action}",
        params=_ws(workspace_id),
        json=_compact({"force": force}) or None,
        headers=_key_header(idempotency_key),
        parse=OperationAccepted,
        main=True,
    )
    return typing.cast(OperationAccepted, result)


def update_access(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    idempotency_key: typing.Optional[str] = None,
    requested_by: typing.Any = None,
    admin_username: typing.Any = None,
    ssh_key_mode: typing.Any = None,
    ssh_keys: typing.Any = None,
    ssh_key_ids: typing.Any = None,
    ssh_key_secret_refs: typing.Any = None,
    new_password: typing.Any = None,
    password_auth_enabled: typing.Any = None,
    confirm_remove_last_ssh_key: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[OperationAccepted]:
    vm_id = validate_vm_id(vm_id)
    fields = dict(
        ssh_key_mode=ssh_key_mode,
        ssh_keys=ssh_keys,
        ssh_key_ids=ssh_key_ids,
        ssh_key_secret_refs=ssh_key_secret_refs,
        new_password=new_password,
        password_auth_enabled=password_auth_enabled,
        confirm_remove_last_ssh_key=confirm_remove_last_ssh_key,
    )
    body = validate_access_update(**fields)
    requested = validate_requested_by(requested_by)
    username = validate_optional_text(admin_username, field="admin_username", max_length=255)
    if check_state is not False:
        vm = yield from get_vm(family, workspace_id, vm_id)
        body = validate_access_update(**fields, vm=vm)
        if username is None and "new_password" in body:
            username = validate_optional_text(record_get(vm, "admin_username"), field="admin_username")
    body = _compact({"requested_by": requested, "admin_username": username, **body})
    result = yield Call(
        "PATCH",
        f"{vm_path(family, vm_id)}/actions/access",
        params=_ws(workspace_id),
        json=body,
        headers=_key_header(idempotency_key),
        parse=OperationAccepted,
        main=True,
    )
    return typing.cast(OperationAccepted, result)


def _plan_target(
    family: str, workspace_id: str, vm: typing.Mapping[str, typing.Any], plan_id: str
) -> Flow[typing.Dict[str, typing.Any]]:
    plans = yield from list_plans(workspace_id, family, record_get(vm, "site_id"))
    return select_compute_plan(plans, plan_id, vm_type=family)


def _explicit_or_plan(plan: typing.Optional[typing.Mapping[str, typing.Any]], **explicit: typing.Any) -> typing.Dict[str, typing.Any]:
    if plan is None:
        return explicit
    given = [key for key, value in explicit.items() if value is not None]
    if given:
        raise IbeeValidationError(
            f"Pass either plan_id or explicit {', '.join(given)}, not both.", code="invalid_resize_target", field=given[0]
        )
    return {key: plan.get(key) for key in explicit}


def _resize_billing_catalog(
    *,
    plan: typing.Optional[typing.Mapping[str, typing.Any]],
    vm: typing.Optional[typing.Mapping[str, typing.Any]],
    billing_catalog: typing.Any,
    billing_term: typing.Any,
    windows_license: typing.Any,
    cpu: typing.Optional[int],
) -> typing.Optional[typing.Dict[str, typing.Any]]:
    term = normalize_billing_term(billing_term)
    if billing_catalog is not None:
        catalog = validate_billing_catalog(billing_catalog, context="billing_catalog")
        return apply_billing_term_to_catalog(catalog, term, label="billing_catalog")
    if plan is None:
        if term is not None:
            raise IbeeValidationError(
                "billing_term needs plan_id (or an explicit billing_catalog).", code="invalid_billing_term", field="billing_term"
            )
        return None
    windows = vm is not None and is_windows_vm(vm)
    license_sku = windows_license
    if windows and license_sku is None:
        attached = record_get(record_get(vm, "billing_catalog") or {}, "attached_skus") or {}
        license_sku = record_get(attached, "windows_license")
    return build_vm_billing_catalog(
        plan.get("billing_catalog"),
        term=term or "HOURLY",
        apply_term=True,
        os_type="windows" if windows else "linux",
        cpu=cpu,
        windows_license=license_sku if windows else None,
    )


def precheck_resize(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    cpu: typing.Any = None,
    ram_mb: typing.Any = None,
    disk_gb: typing.Any = None,
    plan_id: typing.Any = None,
    requested_by: typing.Any = None,
) -> Flow[VmResizePrecheck]:
    vm_id = validate_vm_id(vm_id)
    plan = None
    if plan_id is not None:
        vm = yield from get_vm(family, workspace_id, vm_id)
        plan = yield from _plan_target(family, workspace_id, vm, validate_required_text(plan_id, field="plan_id"))
    target = validate_resize_target(**_explicit_or_plan(plan, cpu=cpu, ram_mb=ram_mb, disk_gb=disk_gb))
    result = yield Call(
        "POST",
        f"{vm_path(family, vm_id)}/actions/resize/precheck",
        params=_ws(workspace_id),
        json=_compact({**target, "requested_by": validate_requested_by(requested_by)}),
        parse=VmResizePrecheck,
        main=True,
    )
    return typing.cast(VmResizePrecheck, result)


_PRECHECK_MESSAGES = {
    "migration_required": "This downgrade requires migration. In-place disk shrink is blocked.",
    "blocked": "Resize is currently blocked.",
}


def resize(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    idempotency_key: typing.Optional[str] = None,
    requested_by: typing.Any = None,
    cpu: typing.Any = None,
    ram_mb: typing.Any = None,
    disk_gb: typing.Any = None,
    plan_id: typing.Any = None,
    billing_term: typing.Any = None,
    billing_catalog: typing.Any = None,
    windows_license: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[OperationAccepted]:
    """Portal resize: target from the plan, precheck must be ``in_place``, then resize with the new SKU."""
    vm_id = validate_vm_id(vm_id)
    requested = validate_requested_by(requested_by)
    vm = None
    plan = None
    if plan_id is not None or check_state is True:
        vm = yield from get_vm(family, workspace_id, vm_id)
        _opt_in_state(vm, "resize", check_state)
    if plan_id is not None:
        plan = yield from _plan_target(family, workspace_id, vm or {}, validate_required_text(plan_id, field="plan_id"))
    target = validate_resize_target(**_explicit_or_plan(plan, cpu=cpu, ram_mb=ram_mb, disk_gb=disk_gb))
    catalog = _resize_billing_catalog(
        plan=plan,
        vm=vm,
        billing_catalog=billing_catalog,
        billing_term=billing_term,
        windows_license=windows_license,
        cpu=target.get("cpu") or record_get(vm, "cpu"),
    )
    precheck = yield Call(
        "POST", f"{vm_path(family, vm_id)}/actions/resize/precheck", params=_ws(workspace_id), json=target
    )
    decision = str(record_get(precheck, "decision") or "").strip().lower()
    if decision != "in_place":
        raise IbeeValidationError(
            _PRECHECK_MESSAGES.get(decision, f"Resize precheck returned '{decision or 'unknown'}'; not resizing."),
            code="resize_not_in_place",
            field="cpu",
            details=precheck,
        )
    body = _compact({**target, "billing_catalog": catalog, "requested_by": requested})
    result = yield Call(
        "POST",
        f"{vm_path(family, vm_id)}/actions/resize",
        params=_ws(workspace_id),
        json=body,
        headers=_key_header(idempotency_key),
        parse=OperationAccepted,
        main=True,
    )
    return typing.cast(OperationAccepted, result)


def resize_plan(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    idempotency_key: typing.Optional[str] = None,
    cpu: typing.Any = None,
    ram_mb: typing.Any = None,
    allow_online: typing.Any = None,
    confirm_downgrade: typing.Any = None,
    requested_by: typing.Any = None,
    plan_id: typing.Any = None,
    billing_term: typing.Any = None,
    billing_catalog: typing.Any = None,
    windows_license: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[OperationAccepted]:
    vm_id = validate_vm_id(vm_id)
    requested = validate_requested_by(requested_by)
    vm = None
    plan = None
    if plan_id is not None or check_state is not False:
        # Required pre-step: the no-op / downgrade check needs the current shape.
        vm = yield from get_vm(family, workspace_id, vm_id)
        _opt_in_state(vm, "resize_plan", check_state)
    if plan_id is not None:
        plan = yield from _plan_target(family, workspace_id, vm or {}, validate_required_text(plan_id, field="plan_id"))
    shape = validate_resize_target(**_explicit_or_plan(plan, cpu=cpu, ram_mb=ram_mb), require_one=False)
    if "cpu" not in shape or "ram_mb" not in shape:
        raise IbeeValidationError("cpu and ram_mb are required (or pass plan_id).", code="invalid_resize_target", field="cpu")
    if vm is not None and check_state is not False:
        validate_resize_plan_change(vm, cpu=shape["cpu"], ram_mb=shape["ram_mb"], confirm_downgrade=confirm_downgrade)
    catalog = _resize_billing_catalog(
        plan=plan, vm=vm, billing_catalog=billing_catalog, billing_term=billing_term, windows_license=windows_license, cpu=shape["cpu"]
    )
    body = _compact(
        {
            **shape,
            "allow_online": allow_online,
            "confirm_downgrade": confirm_downgrade,
            "billing_catalog": catalog,
            "requested_by": requested,
        }
    )
    result = yield Call(
        "PATCH",
        f"{vm_path(family, vm_id)}/actions/resize-plan",
        params=_ws(workspace_id),
        json=body,
        headers=_key_header(idempotency_key),
        parse=OperationAccepted,
        main=True,
    )
    return typing.cast(OperationAccepted, result)


def resize_root_disk(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    new_size_gb: typing.Any,
    idempotency_key: typing.Optional[str] = None,
    allow_online: typing.Any = None,
    requested_by: typing.Any = None,
    billing_catalog: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[OperationAccepted]:
    vm_id = validate_vm_id(vm_id)
    requested = validate_requested_by(requested_by)
    size = validate_resize_target(disk_gb=new_size_gb)["disk_gb"]
    catalog = validate_billing_catalog(billing_catalog) if billing_catalog is not None else None
    if check_state is not False:
        # Required pre-step: the new size must exceed the current root disk.
        vm = yield from get_vm(family, workspace_id, vm_id)
        _opt_in_state(vm, "resize_root_disk", check_state)
        validate_root_disk_growth(vm, size)
    body = _compact(
        {"new_size_gb": size, "allow_online": allow_online, "billing_catalog": catalog, "requested_by": requested}
    )
    result = yield Call(
        "PATCH",
        f"{vm_path(family, vm_id)}/actions/resize-root-disk",
        params=_ws(workspace_id),
        json=body,
        headers=_key_header(idempotency_key),
        parse=OperationAccepted,
        main=True,
    )
    return typing.cast(OperationAccepted, result)


def create_console_session(
    *,
    workspace_id: str,
    vm_id: str,
    vm_type: typing.Any = None,
    console_type: typing.Any = None,
    requested_by: typing.Any = None,
    user_id: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[VmConsoleSession]:
    vm_id = validate_vm_id(vm_id)
    validate_console_target(vm_type, console_type)
    # Like the TypeScript SDK, API sessions are labelled "api" unless the caller names one.
    requested = validate_requested_by(requested_by) or "api"
    if check_state:
        vm = yield from get_vm("cloud", workspace_id, vm_id)
        assert_vm_action_allowed(vm, "console")
    body = _compact(
        {
            "vm_id": vm_id,
            "vm_type": getattr(vm_type, "value", vm_type),
            "console_type": getattr(console_type, "value", console_type),
            "requested_by": requested,
            "user_id": user_id,
        }
    )
    result = yield Call(
        "POST", "compute/console/sessions", params=_ws(workspace_id), json=body, parse=VmConsoleSession, main=True
    )
    return typing.cast(VmConsoleSession, result)


# ---------------------------------------------------------------------------
# VM-side volumes
# ---------------------------------------------------------------------------


def attach_volume(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    volume_id: typing.Any,
    idempotency_key: typing.Optional[str] = None,
    mode: typing.Any = None,
    billing_catalog: typing.Any = None,
    requested_by: typing.Any = None,
    check_state: typing.Optional[bool] = None,
    volume: typing.Any = None,
    skip_volume_read: bool = False,
) -> Flow[OperationAccepted]:
    """Portal attach: read the volume (SKU, state, VM type, site), check the VM's site, then attach.

    ``volume`` is an already-read volume record (used by the block-storage helper).
    Without ``block-storage.read`` the volume cannot be read and ``billing_catalog``
    must be passed; without ``vm.read`` the VM checks are skipped.
    """
    vm_id = validate_vm_id(vm_id)
    volume_id = validate_block_volume_id(volume_id)
    attach_mode = validate_attach_mode(mode)
    requested = validate_requested_by(requested_by)
    catalog = None
    if billing_catalog is not None:
        catalog = validate_billing_catalog(billing_catalog, expected_product="block_storage")
    if catalog is None or check_state is not False:
        if volume is None and not skip_volume_read:
            try:
                volume = yield Call("GET", f"block-storage/volumes/{_seg(volume_id)}", params=_ws(workspace_id))
            except ForbiddenError:
                if catalog is None:
                    raise IbeeValidationError(
                        "billing_catalog is required; grant block-storage.read or pass billing_catalog",
                        code="volume_unreadable",
                        field="billing_catalog",
                    )
                volume = None
        if volume is None and catalog is None:
            raise IbeeValidationError(
                "billing_catalog is required; grant block-storage.read or pass billing_catalog",
                code="volume_unreadable",
                field="billing_catalog",
            )
        vm = None
        if check_state is not False:
            try:
                vm = yield from get_vm(family, workspace_id, vm_id)
            except ForbiddenError:
                vm = None  # best effort: the API still checks the VM
            _opt_in_state(vm, "attach_volume", check_state)
        if volume is not None:
            validate_attach_preconditions(volume, vm)
            assert_volume_attachable(volume, family, vm)
            if catalog is None:
                catalog = resolve_volume_billing_catalog(volume)
    body = _compact({"volume_id": volume_id, "mode": attach_mode, "billing_catalog": catalog, "requested_by": requested})
    result = yield Call(
        "POST",
        f"{vm_path(family, vm_id)}/actions/attach-volume",
        params=_ws(workspace_id),
        json=body,
        headers=_key_header(idempotency_key),
        parse=OperationAccepted,
        main=True,
    )
    return typing.cast(OperationAccepted, result)


def detach_volume(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    volume_id: typing.Any,
    idempotency_key: typing.Optional[str] = None,
    confirm_unmounted: typing.Any = None,
    force: typing.Any = None,
    requested_by: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[OperationAccepted]:
    vm_id = validate_vm_id(vm_id)
    volume_id = validate_block_volume_id(volume_id)
    validate_detach_confirmation(confirm_unmounted, force)
    requested = validate_requested_by(requested_by)
    if check_state:
        try:
            volume = yield Call("GET", f"block-storage/volumes/{_seg(volume_id)}", params=_ws(workspace_id))
        except ForbiddenError:
            volume = None  # best effort without block-storage.read: the API still checks the attachment
        attachments = record_get(volume, "attachments") or []
        if volume is not None and not any(str(record_get(item, "vm_id") or "").strip() == vm_id for item in attachments):
            raise IbeeValidationError(
                "The volume is not attached to this VM.", code="volume_not_attached", field="volume_id"
            )
    body = _compact(
        {"volume_id": volume_id, "confirm_unmounted": confirm_unmounted, "force": force, "requested_by": requested}
    )
    result = yield Call(
        "POST",
        f"{vm_path(family, vm_id)}/actions/detach-volume",
        params=_ws(workspace_id),
        json=body,
        headers=_key_header(idempotency_key),
        parse=OperationAccepted,
        main=True,
    )
    return typing.cast(OperationAccepted, result)


def acknowledge_mount_guidance(
    family: str, *, workspace_id: str, vm_id: str, volume_id: typing.Any
) -> Flow[MountGuidanceAcknowledge]:
    vm_id = validate_vm_id(vm_id)
    volume_id = validate_required_text(volume_id, field="volume_id")
    result = yield Call(
        "POST",
        f"{vm_path(family, vm_id)}/mount-guidance/acknowledge",
        params=_ws(workspace_id),
        json={"volume_id": volume_id},
        parse=MountGuidanceAcknowledge,
        main=True,
    )
    return typing.cast(MountGuidanceAcknowledge, result)


# ---------------------------------------------------------------------------
# Snapshots
# ---------------------------------------------------------------------------

SNAPSHOT_SKU_HELP = (
    "billing_catalog (the snapshot_storage SKU, code SNAPSHOT-STD, with sku_id and sku_code) is required. "
    "The public API cannot list it yet; copy billing_catalog from an existing snapshot set of this workspace."
)
BACKUP_SKU_HELP = (
    "billing_catalog (the backup_storage SKU, code BACKUP-STD, with sku_id and sku_code) is required. "
    "The public API cannot list it yet; copy billing_catalog from an existing backup run of this workspace."
)


def snapshot_collection(family: str) -> str:
    return f"compute/{_family(family)}-vm-snapshots"


def backup_collection(family: str) -> str:
    return f"compute/{_family(family)}-vm-backups"


def _require_catalog(value: typing.Any, *, help_text: str, product: str) -> typing.Dict[str, typing.Any]:
    if value is None:
        raise IbeeValidationError(help_text, code="billing_catalog_required", field="billing_catalog")
    return validate_billing_catalog(value, expected_product=product)


def create_snapshot(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    name: typing.Any,
    description: typing.Any = None,
    mode: typing.Any = None,
    selected_data_volume_ids: typing.Any = None,
    billing_catalog: typing.Any = None,
    requested_by: typing.Any = None,
    preflight_billing: bool = False,
    check_state: typing.Optional[bool] = None,
) -> Flow[SnapshotSet]:
    vm_id = validate_vm_id(vm_id)
    body = validate_snapshot_request(
        name=name, description=description, mode=mode, selected_data_volume_ids=selected_data_volume_ids
    )
    body["billing_catalog"] = _require_catalog(billing_catalog, help_text=SNAPSHOT_SKU_HELP, product="snapshot_storage")
    requested = validate_requested_by(requested_by)
    if requested is not None:
        body["requested_by"] = requested
    if check_state:
        vm = yield from get_vm(family, workspace_id, vm_id)
        assert_vm_action_allowed(vm, "snapshot")
        if body["mode"] == "selective":
            validate_snapshot_volumes_attached(vm, body["selected_data_volume_ids"])
    if preflight_billing:
        yield from billing_preflight(workspace_id, sku_code=body["billing_catalog"].get("sku_code"), resource_type="snapshot")
    result = yield Call(
        "POST", f"{vm_path(family, vm_id)}/snapshots", params=_ws(workspace_id), json=body, parse=SnapshotSet, main=True
    )
    return typing.cast(SnapshotSet, result)


def list_snapshots(
    family: str, *, workspace_id: str, vm_id: str, limit: typing.Any = None, offset: typing.Any = None, search: typing.Any = None
) -> Flow[SnapshotSetList]:
    vm_id = validate_vm_id(vm_id)
    query = validate_recovery_list_params(limit=limit, offset=offset, search=search)
    result = yield Call(
        "GET", f"{vm_path(family, vm_id)}/snapshots", params=_ws(workspace_id, **query), parse=SnapshotSetList, main=True
    )
    return typing.cast(SnapshotSetList, result)


def delete_snapshot(
    family: str, *, workspace_id: str, snapshot_set_id: typing.Any, check_state: typing.Optional[bool] = None
) -> Flow[SnapshotDeleteResult]:
    snapshot_set_id = validate_required_text(snapshot_set_id, field="snapshot_set_id")
    path = f"{snapshot_collection(family)}/{_seg(snapshot_set_id)}"
    if check_state:
        snapshot = yield Call("GET", path, params=_ws(workspace_id))
        validate_snapshot_deletable(snapshot)
    result = yield Call("DELETE", path, params=_ws(workspace_id), parse=SnapshotDeleteResult, main=True)
    return typing.cast(SnapshotDeleteResult, result)


def _restore_new_vm_fields(
    family: str,
    workspace_id: str,
    *,
    kind: str,
    vm: typing.Mapping[str, typing.Any],
    recovery_point: typing.Mapping[str, typing.Any],
    fields: typing.Dict[str, typing.Any],
) -> Flow[typing.Dict[str, typing.Any]]:
    """Resolve the plan and default names for a new-VM restore (portal restore dialog)."""
    manifest = record_get(recovery_point, "volume_manifest") or []
    min_root = recovery_min_root_disk_gb(manifest)
    plan_id = fields.get("target_plan_id") or record_get(vm, "plan_id")
    if plan_id:
        site = fields.get("target_site_id") or record_get(vm, "site_id")
        plans = yield from list_plans(workspace_id, family, site)
        plan = select_restore_plan(plans, plan_id, min_root_disk_gb=min_root)
        for key, value in restore_target_from_plan(plan, vm=vm).items():
            if fields.get(key) is None:
                fields[key] = value
    elif min_root is not None and fields.get("target_disk_gb") is not None and fields["target_disk_gb"] < min_root:
        raise IbeeValidationError(
            f"Root disk must be at least {min_root:g} GB.", code="restore_disk_too_small", field="target_disk_gb"
        )
    if fields.get("target_vm_name") is None:
        fields["target_vm_name"] = recovery_default_vm_name(
            record_get(vm, "name") or record_get(recovery_point, "vm_name"), kind, record_get(recovery_point, "created_at")
        )
    else:
        fields["target_vm_name"] = str(fields["target_vm_name"]).strip()
    if fields.get("target_volume_names") is None:
        names = recovery_target_volume_names(manifest, kind, record_get(recovery_point, "created_at"))
        if names:
            fields["target_volume_names"] = names
    else:
        fields["target_volume_names"] = validate_target_volume_names(manifest, fields["target_volume_names"])
    if fields.get("target_billing_catalog") is not None:
        fields["target_billing_catalog"] = validate_billing_catalog(
            fields["target_billing_catalog"], context="Selected plan", field="target_billing_catalog"
        )
    validate_restore_target(fields)
    return fields


def _recovery_point_dict(value: typing.Any) -> typing.Dict[str, typing.Any]:
    return dict(value) if isinstance(value, dict) else {}


def restore_snapshot(
    family: str,
    *,
    workspace_id: str,
    snapshot_set_id: typing.Any,
    vm_id: typing.Any,
    target_mode: typing.Any = None,
    selected_volume_id: typing.Any = None,
    target_volume_names: typing.Any = None,
    target_billing_catalog: typing.Any = None,
    vpc_id: typing.Any = None,
    subnet_id: typing.Any = None,
    network_connectivity: typing.Any = None,
    ssh_key_ids: typing.Any = None,
    auto_start: typing.Any = None,
    requested_by: typing.Any = None,
    check_state: typing.Optional[bool] = None,
    **targets: typing.Any,
) -> Flow[RecoveryRestore]:
    """Portal snapshot restore (replace, new VM, or one volume)."""
    snapshot_set_id = validate_required_text(snapshot_set_id, field="snapshot_set_id")
    vm_id = validate_vm_id(vm_id)
    mode = validate_restore_mode(target_mode)
    requested = validate_requested_by(requested_by)
    fields: typing.Dict[str, typing.Any] = {key: value for key, value in targets.items() if value is not None}
    fields.update(
        _compact(
            {
                "target_volume_names": target_volume_names,
                "target_billing_catalog": target_billing_catalog,
                "vpc_id": vpc_id,
                "subnet_id": subnet_id,
                "network_connectivity": network_connectivity,
                "ssh_key_ids": ssh_key_ids,
                "selected_volume_id": selected_volume_id,
            }
        )
    )
    validate_restore_mode_combination(mode, fields)
    snapshot: typing.Dict[str, typing.Any] = {}
    vm: typing.Optional[typing.Dict[str, typing.Any]] = None
    if check_state is not False or mode != "replace":
        snapshot = _recovery_point_dict(
            (yield Call("GET", f"{snapshot_collection(family)}/{_seg(snapshot_set_id)}", params=_ws(workspace_id)))
        )
        validate_snapshot_ready(snapshot)
    if check_state is True or mode == "new_vm" or (mode == "volume_only" and check_state is not False):
        vm = yield from get_vm(family, workspace_id, vm_id)
        if check_state is True:
            validate_restore_vm_state(vm)
    body: typing.Dict[str, typing.Any] = {"target_mode": mode}
    if mode == "volume_only":
        selected = str(selected_volume_id).strip()
        validate_volume_only_selection(snapshot, vm if check_state is not False else None, selected)
        body["selected_volume_id"] = selected
    if mode == "new_vm":
        network = validate_network_request(vpc_id=vpc_id, subnet_id=subnet_id, network_connectivity=network_connectivity)
        fields.pop("vpc_id", None)
        fields.pop("subnet_id", None)
        fields.pop("network_connectivity", None)
        keys = normalize_id_list(ssh_key_ids, field="ssh_key_ids")
        fields.pop("ssh_key_ids", None)
        fields = yield from _restore_new_vm_fields(
            family, workspace_id, kind="snapshot", vm=vm or {}, recovery_point=snapshot, fields=fields
        )
        if network:
            network.setdefault("network_connectivity", "private")
            vpc = yield Call("GET", f"networking/vpcs/{_seg(network['vpc_id'])}", params=_ws(workspace_id))
            subnet = yield Call(
                "GET",
                f"networking/vpcs/{_seg(network['vpc_id'])}/subnets/{_seg(network['subnet_id'])}",
                params=_ws(workspace_id),
            )
            validate_vm_network_placement(
                site_id=str(fields.get("target_site_id") or record_get(vm, "site_id") or ""),
                network=network,
                vpc=vpc,
                subnet=subnet,
            )
            body.update(network)
        if keys:
            body["ssh_key_ids"] = keys
        body.update(fields)
    body["auto_start"] = True if auto_start is None else bool(auto_start)
    if requested is not None:
        body["requested_by"] = requested
    result = yield Call(
        "POST",
        f"{snapshot_collection(family)}/{_seg(snapshot_set_id)}/actions/restore",
        params=_ws(workspace_id, vm_id=vm_id),
        json=body,
        parse=RecoveryRestore,
        main=True,
    )
    return typing.cast(RecoveryRestore, result)


# ---------------------------------------------------------------------------
# Backups
# ---------------------------------------------------------------------------


def _get_policy(family: str, workspace_id: str, vm_id: str) -> Flow[typing.Optional[typing.Dict[str, typing.Any]]]:
    try:
        policy = yield Call("GET", f"{vm_path(family, vm_id)}/backups/policy", params=_ws(workspace_id))
    except NotFoundError:
        return None
    return dict(policy) if isinstance(policy, dict) else None


def enable_backups(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    schedule: typing.Any = None,
    retention_days: typing.Any = None,
    full_backup_interval_days: typing.Any = None,
    incremental_enabled: typing.Any = None,
    billing_catalog: typing.Any = None,
    requested_by: typing.Any = None,
    preflight_billing: bool = False,
) -> Flow[BackupPolicy]:
    """Portal enable.

    Re-enable with no settings passed re-sends the saved policy unchanged (portal
    "re-enable with existing policy"). Otherwise the caller's values are applied
    over the portal defaults (daily at 12:00 UTC, 30-minute window, 7-day
    retention, weekly full backup, incremental on), as the portal's save does.
    """
    vm_id = validate_vm_id(vm_id)
    catalog = _require_catalog(billing_catalog, help_text=BACKUP_SKU_HELP, product="backup_storage")
    requested = validate_requested_by(requested_by)
    validate_backup_retention(
        retention_days=retention_days, full_backup_interval_days=full_backup_interval_days, incremental_enabled=incremental_enabled
    )
    check_backup_schedule_input(schedule)
    no_settings = all(value is None for value in (schedule, retention_days, full_backup_interval_days, incremental_enabled))
    policy = yield from _get_policy(family, workspace_id, vm_id)
    body: typing.Dict[str, typing.Any]
    if policy is not None and policy.get("policy_id") and no_settings:
        saved_schedule = policy.get("schedule")
        body = {
            "schedule": dict(saved_schedule) if isinstance(saved_schedule, dict) else validate_backup_schedule(None),
            "retention_days": policy.get("retention_days") if policy.get("retention_days") is not None else 7,
            "full_backup_interval_days": policy.get("full_backup_interval_days")
            if policy.get("full_backup_interval_days") is not None
            else 7,
            "incremental_enabled": policy.get("incremental_enabled")
            if policy.get("incremental_enabled") is not None
            else True,
        }
    else:
        body = {
            "schedule": validate_backup_schedule(schedule),
            **validate_backup_retention(
                retention_days=7 if retention_days is None else retention_days,
                full_backup_interval_days=7 if full_backup_interval_days is None else full_backup_interval_days,
                incremental_enabled=True if incremental_enabled is None else incremental_enabled,
            ),
        }
    body["billing_catalog"] = catalog
    if requested is not None:
        body["requested_by"] = requested
    if preflight_billing:
        yield from billing_preflight(workspace_id, sku_code=catalog.get("sku_code"), resource_type="backup")
    result = yield Call(
        "POST", f"{vm_path(family, vm_id)}/backups/enable", params=_ws(workspace_id), json=body, parse=BackupPolicy, main=True
    )
    return typing.cast(BackupPolicy, result)


def update_backup_policy(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    schedule: typing.Any = None,
    retention_days: typing.Any = None,
    full_backup_interval_days: typing.Any = None,
    incremental_enabled: typing.Any = None,
    billing_catalog: typing.Any = None,
    requested_by: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[BackupPolicy]:
    vm_id = validate_vm_id(vm_id)
    requested = validate_requested_by(requested_by)
    body: typing.Dict[str, typing.Any] = validate_backup_retention(
        retention_days=retention_days, full_backup_interval_days=full_backup_interval_days, incremental_enabled=incremental_enabled
    )
    catalog = validate_billing_catalog(billing_catalog, expected_product="backup_storage") if billing_catalog is not None else None
    if schedule is None and not body and catalog is None:
        raise IbeeValidationError(
            "Provide at least one of schedule, retention_days, full_backup_interval_days, incremental_enabled or billing_catalog.",
            code="no_changes",
            field=None,
        )
    check_backup_schedule_input(schedule)
    saved_schedule = None
    if check_state is not False:
        policy = yield from _get_policy(family, workspace_id, vm_id)
        if policy is None or policy.get("enabled") is False:
            raise IbeeValidationError(
                "Backups are disabled for this VM; enable them first (enable_*_backups).",
                code="backups_disabled",
                field="vm_id",
            )
        saved_schedule = policy.get("schedule")
    if schedule is not None:
        body["schedule"] = validate_backup_schedule(schedule, base=saved_schedule)
    if catalog is not None:
        body["billing_catalog"] = catalog
    if requested is not None:
        body["requested_by"] = requested
    result = yield Call(
        "PATCH", f"{vm_path(family, vm_id)}/backups/policy", params=_ws(workspace_id), json=body, parse=BackupPolicy, main=True
    )
    return typing.cast(BackupPolicy, result)


def reschedule_backup(
    family: str, *, workspace_id: str, vm_id: str, next_run_at: typing.Any, requested_by: typing.Any = None
) -> Flow[BackupPolicy]:
    vm_id = validate_vm_id(vm_id)
    when = validate_next_run_at(next_run_at)
    requested = validate_requested_by(requested_by)
    body = _compact({"next_run_at": when, "requested_by": requested})
    result = yield Call(
        "PATCH",
        f"{vm_path(family, vm_id)}/backups/policy/next-run-at",
        params=_ws(workspace_id),
        json=body,
        parse=BackupPolicy,
        main=True,
    )
    return typing.cast(BackupPolicy, result)


def create_backup_run(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    reason: typing.Any = None,
    billing_catalog: typing.Any = None,
    requested_by: typing.Any = None,
    check_state: typing.Optional[bool] = None,
    preflight_billing: bool = False,
) -> Flow[BackupRun]:
    vm_id = validate_vm_id(vm_id)
    catalog = _require_catalog(billing_catalog, help_text=BACKUP_SKU_HELP, product="backup_storage")
    body = _compact(
        {"reason": validate_backup_reason(reason), "billing_catalog": catalog, "requested_by": validate_requested_by(requested_by)}
    )
    if check_state:
        policy = yield from _get_policy(family, workspace_id, vm_id)
        if policy is None or policy.get("enabled") is not True:
            raise IbeeValidationError(
                "Backup policy is disabled for this VM. Enable backups before creating a backup run.",
                code="backups_disabled",
                field="vm_id",
            )
    if preflight_billing:
        yield from billing_preflight(workspace_id, sku_code=catalog.get("sku_code"), resource_type="backup")
    result = yield Call(
        "POST", f"{vm_path(family, vm_id)}/backups/runs", params=_ws(workspace_id), json=body, parse=BackupRun, main=True
    )
    return typing.cast(BackupRun, result)


def list_backup_runs(
    family: str,
    *,
    workspace_id: str,
    vm_id: str,
    limit: typing.Any = None,
    offset: typing.Any = None,
    search: typing.Any = None,
    restorable_only: bool = False,
) -> Flow[BackupRunList]:
    vm_id = validate_vm_id(vm_id)
    query = validate_recovery_list_params(limit=limit, offset=offset, search=search)
    result = yield Call(
        "GET", f"{vm_path(family, vm_id)}/backups/runs", params=_ws(workspace_id, **query), parse=BackupRunList, main=True
    )
    return _restorable(typing.cast(BackupRunList, result)) if restorable_only else typing.cast(BackupRunList, result)


def _restorable(runs: BackupRunList) -> BackupRunList:
    kept = [run for run in runs.runs if str(getattr(run, "status", "")).lower() == "succeeded"]
    try:
        return runs.model_copy(update={"runs": kept})  # type: ignore[attr-defined]
    except AttributeError:  # pragma: no cover - pydantic v1
        return runs.copy(update={"runs": kept})


def list_all_backup_runs(
    family: str,
    *,
    workspace_id: str,
    vm_id: typing.Any = None,
    status: typing.Any = None,
    limit: typing.Any = None,
    offset: typing.Any = None,
    search: typing.Any = None,
) -> Flow[BackupRunList]:
    query = validate_recovery_list_params(limit=limit, offset=offset, search=search)
    # Portal Backups page default: succeeded runs. ``"all"`` (or an empty list) lists every status.
    if status is None:
        statuses: typing.Optional[typing.List[str]] = ["succeeded"]
    elif isinstance(status, str) and status.strip().lower() == "all":
        statuses = None
    else:
        statuses = validate_backup_statuses(status)
    vm = validate_optional_text(vm_id, field="vm_id")
    params = _ws(workspace_id, vm_type="cloud" if family == "cloud" else None, vm_id=vm, **query)
    if statuses:
        params["status"] = statuses
    result = yield Call("GET", f"{backup_collection(family)}/runs", params=params, parse=BackupRunList, main=True)
    return typing.cast(BackupRunList, result)


def delete_backup_run(
    family: str, *, workspace_id: str, run_id: typing.Any, check_state: typing.Optional[bool] = None
) -> Flow[typing.Dict[str, typing.Any]]:
    run_id = validate_required_text(run_id, field="run_id")
    path = f"{backup_collection(family)}/runs/{_seg(run_id)}"
    if check_state:
        run = yield Call("GET", path, params=_ws(workspace_id))
        if str(record_get(run, "status") or "").lower() != "succeeded":
            raise IbeeValidationError(
                "Only a completed backup can be deleted", code="backup_not_completed", field="run_id"
            )
    result = yield Call("DELETE", path, params=_ws(workspace_id), main=True)
    return typing.cast(typing.Dict[str, typing.Any], result if isinstance(result, dict) else {})


def restore_backup(
    family: str,
    *,
    workspace_id: str,
    vm_id: typing.Any,
    recovery_point_id: typing.Any,
    target_mode: typing.Any = None,
    selected_volume_id: typing.Any = None,
    target_volume_names: typing.Any = None,
    target_billing_catalog: typing.Any = None,
    auto_start: typing.Any = None,
    requested_by: typing.Any = None,
    check_state: typing.Optional[bool] = None,
    **targets: typing.Any,
) -> Flow[RecoveryRestore]:
    """Portal backup restore (replace, new VM, or one volume). ``auto_start`` is not sent (backups ignore it).

    The run is always read first to check it succeeded and to send the recovery point ID it reports
    (``check_state`` does not skip this read).
    """
    vm_id = validate_vm_id(vm_id)
    recovery_point_id = validate_required_text(recovery_point_id, field="recovery_point_id")
    mode = validate_restore_mode(target_mode)
    requested = validate_requested_by(requested_by)
    fields: typing.Dict[str, typing.Any] = {key: value for key, value in targets.items() if value is not None}
    fields.update(
        _compact(
            {
                "target_volume_names": target_volume_names,
                "target_billing_catalog": target_billing_catalog,
                "selected_volume_id": selected_volume_id,
            }
        )
    )
    validate_restore_mode_combination(mode, fields)
    # Always read the run (the lookup accepts a run ID or a recovery point ID): only a succeeded
    # backup can be restored, and the restore needs the recovery point ID the run reports, resolved
    # like the portal's restore dialog.
    run = _recovery_point_dict(
        (yield Call("GET", f"{backup_collection(family)}/runs/{_seg(recovery_point_id)}", params=_ws(workspace_id)))
    )
    validate_backup_ready(run)
    recovery_point_id = resolve_backup_recovery_point_id(run)
    body: typing.Dict[str, typing.Any] = {"recovery_point_id": recovery_point_id, "target_mode": mode}
    if mode == "volume_only":
        selected = str(selected_volume_id).strip()
        manifest_ids = {
            str(record_get(item, "source_volume_id") or "").strip() for item in record_get(run, "volume_manifest") or []
        }
        if manifest_ids and selected not in manifest_ids:
            raise IbeeValidationError(
                "selected_volume_id is not part of this backup.", code="volume_not_in_recovery_point", field="selected_volume_id"
            )
        body["selected_volume_id"] = selected
    if mode == "new_vm":
        vm = yield from get_vm(family, workspace_id, vm_id)
        fields = yield from _restore_new_vm_fields(
            family, workspace_id, kind="backup", vm=vm, recovery_point=run, fields=fields
        )
        body.update(fields)
    if requested is not None:
        body["requested_by"] = requested
    result = yield Call(
        "POST",
        f"{vm_path(family, vm_id)}/backups/actions/restore",
        params=_ws(workspace_id),
        json=body,
        parse=RecoveryRestore,
        main=True,
    )
    return typing.cast(RecoveryRestore, result)


__all__ = [
    "Call",
    "FAMILIES",
    "clean_kwargs",
    "run_async",
    "run_sync",
]
