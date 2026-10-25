# IBEE hand layer (listed in .fernignore).
"""Temporary client behaviours, kept until the server resolves its own SKU and defaults.

Each item is a decision that the server or the 0.4.1 contract does not make yet. They
work as in 0.4.x and go away one by one once the server owns them:

1. VM create (cloud and GPU): the plan and the image are looked up to fill ``cpu``,
   ``ram_mb``, ``disk_gb`` (and ``gpu_count``, ``gpu_model``), ``os_type`` and
   ``os_distro`` that you leave out. ``billing_catalog`` is the plan's catalog (or the
   one you pass) with the ``billing_term`` option merged in; cloud VMs default to
   HOURLY when the plan offers it. A ``windows_license`` SKU (per vCPU) and the
   Reserved IP's SKU are added under ``attached_skus``.
2. VM delete: ``public_ip_action="reserve"`` without a ``reserved_ip_label`` labels
   the address with the VM name. There is no default action: the request is sent as
   given, and the server answers 400 for a VM with an automatically assigned public
   IP until you choose ``release`` or ``reserve``.
3. ``billing_catalog`` on attach-volume (the volume's ``metadata.billing_catalog`` when
   you pass none; left out when the volume has none, so the server answers), on resize
   and resize-plan with ``plan_id``/``billing_term``/``billing_catalog`` (from the plan,
   default HOURLY), and, passed through as given, on backup policy update, Reserved IP
   reserve, VPC create (``nat_billing_catalog``), NAT gateway create and NAT gateway
   delete (with ``public_ip_action``). Root-disk resize takes ``billing_catalog`` from
   the contract (0.4.1).
4. Cloud VM, GPU VM and firewall group lists return every page when neither ``limit``
   nor ``offset`` is given.
5. Token environment check: a development token is not sent to production or a
   production token to development, and a token with a line break is refused.
6. Secret redaction is unchanged: the generated core redacts sensitive headers in
   debug logs, and errors never carry request headers.

The server answers everything else: no plan, image, network or state rules run here.
"""

import math
import typing
from urllib.parse import urlsplit

from .block_storage.client import AsyncBlockStorageClient, BlockStorageClient
from .cloud_vms.client import OMIT, AsyncCloudVmsClient, CloudVmsClient
from .compute_catalog.client import AsyncComputeCatalogClient, ComputeCatalogClient
from .firewalls.client import AsyncFirewallsClient, FirewallsClient
from .gpu_vms.client import AsyncGpuVmsClient, GpuVmsClient
from .reserved_ips.client import AsyncReservedIpsClient, ReservedIpsClient
from .vpcs.client import AsyncVpcsClient, VpcsClient

TERMS = ("HOURLY", "MONTHLY", "YEARLY")
PAGE_SIZE = 100
MAX_ITEMS = 10_000
_SHAPE = {"cloud": ("cpu", "ram_mb", "disk_gb"), "gpu": ("cpu", "ram_mb", "disk_gb", "gpu_count", "gpu_model")}
_Kw = typing.Dict[str, typing.Any]


# --- 5. token environment check ---------------------------------------------------


def check_token(token: typing.Any, base_url: str) -> str:
    from .client import IbeeValidationError

    if not isinstance(token, str) or not token.strip() or "\r" in token or "\n" in token:
        raise IbeeValidationError(
            "The API token must be a non-empty string without line breaks.", code="invalid_token", field="token"
        )
    host = (urlsplit(base_url).hostname or "").lower().rstrip(".")
    if (host == "api.ibee.ai" and token.startswith("ibee_dev_key_")) or (
        host == "api.ibee.co.in" and token.startswith("ibee_prod_key_")
    ):
        raise IbeeValidationError(
            "The API token environment does not match the configured IBEE endpoint.",
            code="token_environment_mismatch",
            field="token",
        )
    return token


def checked_token(token: typing.Any, base_url: str) -> typing.Any:
    if callable(token):
        return lambda: check_token(token(), base_url)
    return check_token(token, base_url)


def checked_async_token(async_token: typing.Any, base_url: str) -> typing.Any:
    if async_token is None:
        return None

    async def token() -> str:
        return check_token(await async_token(), base_url)

    return token


# --- 1-3. billing_catalog composition (pure) ----------------------------------------


def _get(obj: typing.Any, key: str) -> typing.Any:
    if isinstance(obj, dict):
        return obj.get(key)
    value = getattr(obj, key, None)
    return getattr(value, "value", value)  # enums from the generated models


def _plain(obj: typing.Any) -> _Kw:
    if isinstance(obj, dict):
        return dict(obj)
    dump = getattr(obj, "model_dump", None) or getattr(obj, "dict", None)
    return dict(dump()) if callable(dump) else {}


def _number(value: typing.Any) -> typing.Any:
    try:
        number = float(value) if not isinstance(value, bool) else None
    except (TypeError, ValueError):
        return None
    if number is None or not math.isfinite(number):
        return None
    return int(number) if number.is_integer() else number


def billing_options(catalog: typing.Any) -> typing.List[_Kw]:
    """The priced HOURLY/MONTHLY/YEARLY options of a catalog, normalised like the portal."""
    options = []
    for raw in _get(catalog, "billing_options") or []:
        option, price = _plain(raw), _number(_get(raw, "unit_price_minor"))
        interval = option.get("billing_interval")
        if price is None or interval not in TERMS:
            continue
        option["committed"] = bool(option.get("committed"))
        if option.get("commitment_period") not in TERMS:
            option["commitment_period"] = interval
        for key in ("commitment_months", "committed_hours"):
            if _number(option.get(key)):
                option[key] = _number(option[key])
            else:
                option.pop(key, None)
        option["unit_price_minor"] = price
        options.append(option)
    return options


def with_term(catalog: typing.Any, term: typing.Optional[str], *, default: bool = False) -> _Kw:
    """The portal's ``billingCatalogForTerm``: the catalog with the ``term`` option merged in.

    ``default`` picks HOURLY when offered, else the first option. A term the catalog
    does not offer is sent as asked, and the server answers.
    """
    result, options = _plain(catalog), billing_options(catalog)
    result.pop("billing_options", None)
    if term is None and default and options:
        term = "HOURLY" if any(o["billing_interval"] == "HOURLY" for o in options) else options[0]["billing_interval"]
    if term is None:
        return result
    term = str(term).strip().upper()
    result["billing_interval"] = term
    option = next((o for o in options if o["billing_interval"] == term), None)
    if option is not None:
        result["committed"] = option["committed"]
        result["commitment_period"] = option.get("commitment_period")
        for key in ("commitment_months", "committed_hours", "price_unit"):
            if option.get(key):
                result[key] = option[key]
        if option.get("discount_percent") is not None:
            result["discount_percent"] = option["discount_percent"]
        result["unit_price_minor"] = option.get("unit_price_minor")
    return result


def vm_billing_catalog(
    catalog: typing.Any,
    *,
    term: typing.Optional[str] = None,
    default_term: bool = False,
    cpu: typing.Any = None,
    windows_license: typing.Any = None,
    reserved_ip_sku: typing.Any = None,
) -> _Kw:
    """A VM ``billing_catalog``: the term merged in, plus the Windows licence and Reserved IP SKUs."""
    result = with_term(catalog, term, default=default_term)
    attached = {str(k).strip().lower().replace("-", "_"): v for k, v in _plain(result.get("attached_skus")).items()}
    if windows_license is not None and "windows_license" not in attached:
        license_sku = with_term(windows_license, result.get("billing_interval"))
        license_sku.update(
            component_key="windows_license", os_type="windows", os_family="windows", quantity_basis="VCPU",
            quantity=max(1, int(cpu or 1)),
        )
        attached["windows_license"] = license_sku
    if reserved_ip_sku is not None:
        attached["reserved_ip"] = _plain(reserved_ip_sku)
    result["attached_skus"] = attached
    return result


def _find(items: typing.Any, key: str, value: typing.Any) -> typing.Any:
    return next((item for item in items or [] if str(_get(item, key)) == str(value)), None)


def needs_lookup(family: str, kw: _Kw) -> bool:
    shape = _SHAPE[family][:4] + ("os_type", "os_distro", "billing_catalog")
    return any(kw.get(key) is None for key in shape)


def create_kwargs(family: str, kw: _Kw, plan: typing.Any, image: typing.Any, reserved_ip: typing.Any) -> _Kw:
    kw = dict(kw)
    term, license_sku, caller = kw.pop("billing_term", None), kw.pop("windows_license", None), kw.get("billing_catalog")
    for key in _SHAPE[family] + ("os_type", "os_distro"):
        source = image if key.startswith("os_") else plan
        if kw.get(key) is None and _get(source, key) is not None:
            kw[key] = _get(source, key)
    catalog = caller if caller is not None else _get(plan, "billing_catalog")
    if catalog is not None:
        kw["billing_catalog"] = vm_billing_catalog(
            catalog, term=term, default_term=caller is None and family == "cloud", cpu=kw.get("cpu"),
            windows_license=license_sku, reserved_ip_sku=_get(reserved_ip, "billing_catalog"),
        )
    for key in ("cpu", "ram_mb", "os_type", "os_distro", "billing_catalog") + _SHAPE[family][3:]:
        kw.setdefault(key, None)  # required by the contract: the server answers a missing value
    return kw


def delete_kwargs(vm: typing.Any, kw: _Kw) -> _Kw:
    kw = dict(kw)
    if kw.get("public_ip_action") == "reserve" and kw.get("reserved_ip_label") is None and _get(vm, "name"):
        kw["reserved_ip_label"] = str(_get(vm, "name"))[:120]
    return kw


def _with_body(kw: _Kw, **extra: typing.Any) -> _Kw:
    """Send fields the 0.4.1 contract does not declare yet (``additional_body_parameters``)."""
    extra = {key: value for key, value in extra.items() if value is not None}
    if extra:
        options = dict(kw.get("request_options") or {})
        options["additional_body_parameters"] = {**(options.get("additional_body_parameters") or {}), **extra}
        kw = {**kw, "request_options": options}
    return kw


def resize_kwargs(
    keys: typing.Tuple[str, ...], kw: _Kw, plan: typing.Any, vm: typing.Any, held: _Kw, typed: bool = False
) -> _Kw:
    """``typed``: the operation declares ``billing_catalog`` (resize-plan); otherwise it is sent as an extra body field."""
    kw = dict(kw)
    for key in keys:
        if kw.get(key) is None and _get(plan, key) is not None:
            kw[key] = _get(plan, key)
    catalog = None
    if held.get("billing_catalog") is not None:
        catalog = vm_billing_catalog(held["billing_catalog"], term=held.get("billing_term"))
    elif plan is not None:
        windows = "windows" in f"{_get(vm, 'os_type') or ''} {_get(vm, 'os_distro') or ''}".lower()
        license_sku = held.get("windows_license")
        if windows and license_sku is None:
            license_sku = _get(_get(_get(vm, "billing_catalog"), "attached_skus"), "windows_license")
        catalog = vm_billing_catalog(
            _get(plan, "billing_catalog"), term=held.get("billing_term") or "HOURLY", cpu=kw.get("cpu") or _get(vm, "cpu"),
            windows_license=license_sku if windows else None,
        )
    if typed:
        return {**kw, "billing_catalog": catalog} if catalog is not None else kw
    return _with_body(kw, billing_catalog=catalog)


def volume_catalog(volume: typing.Any) -> typing.Any:
    """The volume's ``metadata.billing_catalog`` as sent, or ``OMIT`` (the field is left out) when it has none."""
    catalog = _get(_get(volume, "metadata"), "billing_catalog")
    if catalog is None:
        return OMIT
    sent = catalog.dict() if hasattr(catalog, "dict") else dict(catalog)  # the fields the server sent
    # The generated model reads a numeric sku_id/product_id as a float: send 31, not 31.0.
    return {key: int(value) if isinstance(value, float) and value.is_integer() else value for key, value in sent.items()}


def _held_resize(kw: _Kw) -> typing.Tuple[_Kw, _Kw]:
    held = {key: kw.pop(key) for key in ("plan_id", "billing_term", "billing_catalog", "windows_license") if key in kw}
    return kw, held


def _id(item: typing.Any) -> typing.Any:
    return _get(item, "id") or _get(item, "firewall_group_id")


class _Pager:
    """Collects every page of an offset/limit list, skipping items already seen."""

    def __init__(self) -> None:
        self.items: typing.List[typing.Any] = []
        self.seen: typing.Set[typing.Any] = set()
        self.offset, self.done = 0, False

    def add(self, page: typing.Any) -> None:
        page = list(page or [])
        for item in page:
            if _id(item) is None or _id(item) not in self.seen:
                self.seen.add(_id(item))
                self.items.append(item)
        self.offset += len(page)
        self.done = len(page) < PAGE_SIZE or len(self.items) >= MAX_ITEMS


def _all_pages_wanted(kw: _Kw) -> bool:
    return kw.get("limit") is None and kw.get("offset") is None


# --- sync and async lookups ---------------------------------------------------------


class _Sync:
    def __init__(self, *, client_wrapper: typing.Any) -> None:
        super().__init__(client_wrapper=client_wrapper)  # type: ignore[call-arg]
        self._wrapper = client_wrapper

    def _all(self, fetch: typing.Callable[..., typing.Any], kw: _Kw) -> typing.Any:
        if not _all_pages_wanted(kw):
            return fetch(**kw)
        pager = _Pager()
        while not pager.done:
            pager.add(fetch(**{**kw, "limit": PAGE_SIZE, "offset": pager.offset}))
        return pager.items

    def _create(self, family: str, kw: _Kw) -> _Kw:
        plan = image = reserved = None
        ws, site = kw.get("workspace_id"), kw.get("site_id")
        if needs_lookup(family, kw):
            catalog = ComputeCatalogClient(client_wrapper=self._wrapper)
            plan = _find(catalog.list_compute_plans(workspace_id=ws, vm_type=family, site_id=site).plans, "plan_id", kw.get("plan_id"))
            image = _find(catalog.list_compute_images(workspace_id=ws, vm_type=family, site_id=site).images, "template_id", kw.get("template_id"))
        if kw.get("reserved_public_ip_id"):
            reserved = ReservedIpsClient(client_wrapper=self._wrapper).get_reserved_ip(kw["reserved_public_ip_id"], workspace_id=ws)
        return create_kwargs(family, kw, plan, image, reserved)

    def _delete(self, get_vm: typing.Callable[..., typing.Any], vm_id: str, kw: _Kw) -> _Kw:
        # The VM is read only to label a reserved address; public_ip_action has no default.
        if kw.get("public_ip_action") == "reserve" and kw.get("reserved_ip_label") is None:
            return delete_kwargs(get_vm(vm_id, workspace_id=kw.get("workspace_id")), kw)
        return kw

    def _attach(self, kw: _Kw) -> _Kw:
        if kw.get("billing_catalog") is None and kw.get("volume_id"):
            volume = BlockStorageClient(client_wrapper=self._wrapper).get_block_volume(kw["volume_id"], workspace_id=kw.get("workspace_id"))
            kw = {**kw, "billing_catalog": volume_catalog(volume)}
        return kw

    def _resize(self, family: str, keys: typing.Tuple[str, ...], get_vm: typing.Any, vm_id: str, kw: _Kw, typed: bool = False) -> _Kw:
        kw, held = _held_resize(dict(kw))
        vm = plan = None
        if held.get("plan_id") is not None:
            vm = get_vm(vm_id, workspace_id=kw.get("workspace_id"))
            plans = ComputeCatalogClient(client_wrapper=self._wrapper).list_compute_plans(
                workspace_id=kw.get("workspace_id"), vm_type=family, site_id=_get(vm, "site_id")
            ).plans
            plan = _find(plans, "plan_id", held["plan_id"])
        return resize_kwargs(keys, kw, plan, vm, held, typed)


class _Async(_Sync):
    async def _all(self, fetch: typing.Callable[..., typing.Any], kw: _Kw) -> typing.Any:  # type: ignore[override]
        if not _all_pages_wanted(kw):
            return await fetch(**kw)
        pager = _Pager()
        while not pager.done:
            pager.add(await fetch(**{**kw, "limit": PAGE_SIZE, "offset": pager.offset}))
        return pager.items

    async def _create(self, family: str, kw: _Kw) -> _Kw:  # type: ignore[override]
        plan = image = reserved = None
        ws, site = kw.get("workspace_id"), kw.get("site_id")
        if needs_lookup(family, kw):
            catalog = AsyncComputeCatalogClient(client_wrapper=self._wrapper)
            plan = _find((await catalog.list_compute_plans(workspace_id=ws, vm_type=family, site_id=site)).plans, "plan_id", kw.get("plan_id"))
            image = _find((await catalog.list_compute_images(workspace_id=ws, vm_type=family, site_id=site)).images, "template_id", kw.get("template_id"))
        if kw.get("reserved_public_ip_id"):
            reserved = await AsyncReservedIpsClient(client_wrapper=self._wrapper).get_reserved_ip(kw["reserved_public_ip_id"], workspace_id=ws)
        return create_kwargs(family, kw, plan, image, reserved)

    async def _delete(self, get_vm: typing.Any, vm_id: str, kw: _Kw) -> _Kw:  # type: ignore[override]
        if kw.get("public_ip_action") == "reserve" and kw.get("reserved_ip_label") is None:
            return delete_kwargs(await get_vm(vm_id, workspace_id=kw.get("workspace_id")), kw)
        return kw

    async def _attach(self, kw: _Kw) -> _Kw:  # type: ignore[override]
        if kw.get("billing_catalog") is None and kw.get("volume_id"):
            volume = await AsyncBlockStorageClient(client_wrapper=self._wrapper).get_block_volume(kw["volume_id"], workspace_id=kw.get("workspace_id"))
            kw = {**kw, "billing_catalog": volume_catalog(volume)}
        return kw

    async def _resize(self, family: str, keys: typing.Tuple[str, ...], get_vm: typing.Any, vm_id: str, kw: _Kw, typed: bool = False) -> _Kw:  # type: ignore[override]
        kw, held = _held_resize(dict(kw))
        vm = plan = None
        if held.get("plan_id") is not None:
            vm = await get_vm(vm_id, workspace_id=kw.get("workspace_id"))
            plans = (await AsyncComputeCatalogClient(client_wrapper=self._wrapper).list_compute_plans(
                workspace_id=kw.get("workspace_id"), vm_type=family, site_id=_get(vm, "site_id")
            )).plans
            plan = _find(plans, "plan_id", held["plan_id"])
        return resize_kwargs(keys, kw, plan, vm, held, typed)


# --- the resource clients that carry held behaviour ----------------------------------


class CloudVms(_Sync, CloudVmsClient):
    def list_cloud_vms(self, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return self._all(super().list_cloud_vms, kw)

    def create_cloud_vm(self, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().create_cloud_vm(**self._create("cloud", kw))

    def delete_cloud_vm(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().delete_cloud_vm(vm_id, **self._delete(self.get_cloud_vm, vm_id, kw))

    def attach_cloud_vm_volume(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().attach_cloud_vm_volume(vm_id, **self._attach(kw))

    def resize_cloud_vm(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().resize_cloud_vm(vm_id, **self._resize("cloud", ("cpu", "ram_mb", "disk_gb"), self.get_cloud_vm, vm_id, kw))

    def resize_cloud_vm_plan(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        kw = self._resize("cloud", ("cpu", "ram_mb"), self.get_cloud_vm, vm_id, kw, typed=True)
        return super().resize_cloud_vm_plan(vm_id, **{"cpu": None, "ram_mb": None, **kw})


    def update_cloud_vm_backup_policy(self, vm_id: str, *, billing_catalog: typing.Any = None, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().update_cloud_vm_backup_policy(vm_id, **_with_body(kw, billing_catalog=billing_catalog))


class GpuVms(_Sync, GpuVmsClient):
    def list_gpu_vms(self, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return self._all(super().list_gpu_vms, kw)

    def create_gpu_vm(self, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().create_gpu_vm(**self._create("gpu", kw))

    def delete_gpu_vm(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().delete_gpu_vm(vm_id, **self._delete(self.get_gpu_vm, vm_id, kw))

    def attach_gpu_vm_volume(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().attach_gpu_vm_volume(vm_id, **self._attach(kw))

    def resize_gpu_vm(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().resize_gpu_vm(vm_id, **self._resize("gpu", ("cpu", "ram_mb", "disk_gb"), self.get_gpu_vm, vm_id, kw))

    def resize_gpu_vm_plan(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        kw = self._resize("gpu", ("cpu", "ram_mb"), self.get_gpu_vm, vm_id, kw, typed=True)
        return super().resize_gpu_vm_plan(vm_id, **{"cpu": None, "ram_mb": None, **kw})


    def update_gpu_vm_backup_policy(self, vm_id: str, *, billing_catalog: typing.Any = None, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().update_gpu_vm_backup_policy(vm_id, **_with_body(kw, billing_catalog=billing_catalog))


class Firewalls(_Sync, FirewallsClient):
    def list_firewall_groups(self, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return self._all(super().list_firewall_groups, kw)


class Vpcs(VpcsClient):
    def create_vpc(self, *, nat_billing_catalog: typing.Any = None, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().create_vpc(**_with_body(kw, nat_billing_catalog=nat_billing_catalog))

    def create_nat_gateway(self, vpc_id: str, *, billing_catalog: typing.Any = None, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().create_nat_gateway(vpc_id, **_with_body(kw, billing_catalog=billing_catalog))

    def delete_nat_gateway(  # type: ignore[override]
        self, vpc_id: str, nat_gateway_id: str, *, public_ip_action: typing.Any = None, billing_catalog: typing.Any = None, **kw: typing.Any
    ) -> typing.Any:
        kw = _with_body(kw, public_ip_action=public_ip_action, billing_catalog=billing_catalog)
        return super().delete_nat_gateway(vpc_id, nat_gateway_id, **kw)



class ReservedIps(ReservedIpsClient):
    def reserve_ip(self, *, billing_catalog: typing.Any = None, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return super().reserve_ip(**_with_body(kw, billing_catalog=billing_catalog))

class AsyncCloudVms(_Async, AsyncCloudVmsClient):
    async def list_cloud_vms(self, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await self._all(super().list_cloud_vms, kw)

    async def create_cloud_vm(self, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().create_cloud_vm(**(await self._create("cloud", kw)))

    async def delete_cloud_vm(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().delete_cloud_vm(vm_id, **(await self._delete(self.get_cloud_vm, vm_id, kw)))

    async def attach_cloud_vm_volume(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().attach_cloud_vm_volume(vm_id, **(await self._attach(kw)))

    async def resize_cloud_vm(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        kw = await self._resize("cloud", ("cpu", "ram_mb", "disk_gb"), self.get_cloud_vm, vm_id, kw)
        return await super().resize_cloud_vm(vm_id, **kw)

    async def resize_cloud_vm_plan(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        kw = await self._resize("cloud", ("cpu", "ram_mb"), self.get_cloud_vm, vm_id, kw, typed=True)
        return await super().resize_cloud_vm_plan(vm_id, **{"cpu": None, "ram_mb": None, **kw})


    async def update_cloud_vm_backup_policy(self, vm_id: str, *, billing_catalog: typing.Any = None, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().update_cloud_vm_backup_policy(vm_id, **_with_body(kw, billing_catalog=billing_catalog))


class AsyncGpuVms(_Async, AsyncGpuVmsClient):
    async def list_gpu_vms(self, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await self._all(super().list_gpu_vms, kw)

    async def create_gpu_vm(self, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().create_gpu_vm(**(await self._create("gpu", kw)))

    async def delete_gpu_vm(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().delete_gpu_vm(vm_id, **(await self._delete(self.get_gpu_vm, vm_id, kw)))

    async def attach_gpu_vm_volume(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().attach_gpu_vm_volume(vm_id, **(await self._attach(kw)))

    async def resize_gpu_vm(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        kw = await self._resize("gpu", ("cpu", "ram_mb", "disk_gb"), self.get_gpu_vm, vm_id, kw)
        return await super().resize_gpu_vm(vm_id, **kw)

    async def resize_gpu_vm_plan(self, vm_id: str, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        kw = await self._resize("gpu", ("cpu", "ram_mb"), self.get_gpu_vm, vm_id, kw, typed=True)
        return await super().resize_gpu_vm_plan(vm_id, **{"cpu": None, "ram_mb": None, **kw})


    async def update_gpu_vm_backup_policy(self, vm_id: str, *, billing_catalog: typing.Any = None, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().update_gpu_vm_backup_policy(vm_id, **_with_body(kw, billing_catalog=billing_catalog))


class AsyncFirewalls(_Async, AsyncFirewallsClient):
    async def list_firewall_groups(self, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await self._all(super().list_firewall_groups, kw)


class AsyncVpcs(AsyncVpcsClient):
    async def create_vpc(self, *, nat_billing_catalog: typing.Any = None, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().create_vpc(**_with_body(kw, nat_billing_catalog=nat_billing_catalog))

    async def create_nat_gateway(self, vpc_id: str, *, billing_catalog: typing.Any = None, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().create_nat_gateway(vpc_id, **_with_body(kw, billing_catalog=billing_catalog))

    async def delete_nat_gateway(  # type: ignore[override]
        self, vpc_id: str, nat_gateway_id: str, *, public_ip_action: typing.Any = None, billing_catalog: typing.Any = None, **kw: typing.Any
    ) -> typing.Any:
        kw = _with_body(kw, public_ip_action=public_ip_action, billing_catalog=billing_catalog)
        return await super().delete_nat_gateway(vpc_id, nat_gateway_id, **kw)



class AsyncReservedIps(AsyncReservedIpsClient):
    async def reserve_ip(self, *, billing_catalog: typing.Any = None, **kw: typing.Any) -> typing.Any:  # type: ignore[override]
        return await super().reserve_ip(**_with_body(kw, billing_catalog=billing_catalog))

_CLIENTS = {
    "_cloud_vms": (CloudVms, AsyncCloudVms),
    "_gpu_vms": (GpuVms, AsyncGpuVms),
    "_firewalls": (Firewalls, AsyncFirewalls),
    "_vpcs": (Vpcs, AsyncVpcs),
    "_reserved_ips": (ReservedIps, AsyncReservedIps),
}


def install(client: typing.Any) -> None:
    """Give ``client`` the resource clients above in place of the generated ones."""
    from .base_client import AsyncBaseIbee

    index = 1 if isinstance(client, AsyncBaseIbee) else 0
    for attr, classes in _CLIENTS.items():
        setattr(client, attr, classes[index](client_wrapper=client._client_wrapper))
