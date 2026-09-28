"""Billing SKU (``billing_catalog``) rules, ported from the IBEE portal.

Every billable compute request carries a ``billing_catalog`` object: the SKU
reference of the plan (or storage product) being bought, optionally with
``attached_skus`` for add-ons such as a Windows licence or a Reserved IP. These
helpers build and check that object exactly like the portal does, and raise
:class:`~ibee.validation.IbeeValidationError` before any HTTP call when it is
unusable.
"""

from __future__ import annotations

import math
import numbers
import typing

from . import IbeeValidationError

#: Components that are part of the VM plan and must never be billed separately.
ROOT_DISK_COMPONENTS = frozenset(
    {"rootdisk", "root_disk", "root_disk_storage", "rootvolume", "root_volume", "root_storage"}
)
#: Billing terms accepted by compute plans.
BILLING_TERMS: typing.Tuple[str, ...] = ("HOURLY", "MONTHLY", "YEARLY")

_ROOT_DISK_SKU_MESSAGE = "VM root disk is included in the VM plan and must not have a separate SKU"
_ROOT_DISK_ATTACHED_MESSAGE = "VM root disk is included in the VM plan and must not be sent as an attached SKU"


def _as_record(value: typing.Any) -> typing.Optional[typing.Dict[str, typing.Any]]:
    if isinstance(value, typing.Mapping):
        return dict(value)
    dump = getattr(value, "model_dump", None) or getattr(value, "dict", None)
    if callable(dump):
        try:
            result = dump()
        except Exception:
            return None
        return dict(result) if isinstance(result, typing.Mapping) else None
    return None


def _error(message: str, field: str) -> IbeeValidationError:
    return IbeeValidationError(message, code="invalid_billing_catalog", field=field)


def require_billing_sku(
    value: typing.Any, context: str = "billing_catalog", *, field: str = "billing_catalog"
) -> typing.Dict[str, typing.Any]:
    """Require an object with a non-blank ``sku_id`` and ``sku_code`` (upper-cased, not ``ROOTDISK-*``)."""
    record = _as_record(value)
    if record is None:
        raise _error(f"{context} is missing Billing catalog data", field)
    sku_id = record.get("sku_id")
    if sku_id is None:
        sku_id = record.get("skuId")
    if sku_id is None or isinstance(sku_id, bool) or str(sku_id).strip() == "":
        raise _error(f"{context} is missing Billing catalog sku_id", field)
    raw_code = record.get("sku_code")
    if raw_code is None:
        raw_code = record.get("skuCode")
    sku_code = str(raw_code if raw_code is not None else "").strip().upper()
    if not sku_code:
        raise _error(f"{context} is missing Billing catalog sku_code", field)
    if sku_code.startswith("ROOTDISK-"):
        raise _error(_ROOT_DISK_SKU_MESSAGE, field)
    record["sku_id"] = sku_id
    record["sku_code"] = sku_code
    return record


def normalize_component_key(component: typing.Any) -> str:
    """Lower-case an ``attached_skus`` key and replace ``-`` with ``_``."""
    return str(component).strip().lower().replace("-", "_")


def validate_billing_catalog(
    value: typing.Any,
    *,
    context: str = "billing_catalog",
    expected_product: typing.Optional[str] = None,
    field: str = "billing_catalog",
) -> typing.Dict[str, typing.Any]:
    """Check a ``billing_catalog`` object and return it normalised.

    ``sku_code`` is upper-cased, ``attached_skus`` keys are normalised and each
    attached SKU is checked. Root-disk SKUs are rejected. When ``expected_product``
    is given and the object carries ``product_code``, the two must match (for
    example ``snapshot_storage``, ``backup_storage`` or ``block_storage``).
    """
    primary = require_billing_sku(value, context, field=field)
    record = _as_record(value) or {}
    raw_attached = record.get("attached_skus")
    if raw_attached is None:
        raw_attached = record.get("attachedSkus")
    if raw_attached is not None and _as_record(raw_attached) is None:
        raise _error(f"{context} attached_skus must be an object", field)
    attached: typing.Dict[str, typing.Any] = {}
    for raw_component, sku in (_as_record(raw_attached) or {}).items():
        component = normalize_component_key(raw_component)
        if component in ROOT_DISK_COMPONENTS:
            raise _error(_ROOT_DISK_ATTACHED_MESSAGE, field)
        attached[component] = require_billing_sku(sku, f"{context} {component}", field=field)
    primary.pop("attachedSkus", None)
    primary["attached_skus"] = attached
    if expected_product is not None:
        product = primary.get("product_code")
        if product is not None and str(product).strip() and str(product).strip().lower() != expected_product:
            raise _error(
                f"{context} is for product '{product}', expected '{expected_product}'.",
                field,
            )
    return primary


def with_attached_billing_skus(
    value: typing.Any,
    attachments: typing.Mapping[str, typing.Any],
    *,
    context: str = "Selected VM plan",
    field: str = "billing_catalog",
) -> typing.Dict[str, typing.Any]:
    """Validate ``value`` and merge ``attachments`` (skipping ``None``) into its ``attached_skus``."""
    primary = validate_billing_catalog(value, context=context, field=field)
    attached = dict(primary.get("attached_skus") or {})
    for raw_component, sku in attachments.items():
        if sku is None:
            continue
        component = normalize_component_key(raw_component)
        if component in ROOT_DISK_COMPONENTS:
            raise _error(_ROOT_DISK_ATTACHED_MESSAGE, field)
        attached[component] = require_billing_sku(sku, f"{context} {component}", field=field)
    primary["attached_skus"] = attached
    return primary


# ---------------------------------------------------------------------------
# Billing terms
# ---------------------------------------------------------------------------


def normalize_billing_term(term: typing.Any, *, field: str = "billing_term") -> typing.Optional[str]:
    """``None``, or one of ``HOURLY``/``MONTHLY``/``YEARLY`` (case-insensitive)."""
    if term is None:
        return None
    if isinstance(term, str) and term.strip().upper() in BILLING_TERMS:
        return term.strip().upper()
    raise IbeeValidationError(
        "billing_term must be one of: HOURLY, MONTHLY, YEARLY.", code="invalid_billing_term", field=field
    )


def _finite_number(value: typing.Any) -> typing.Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, numbers.Real):
        number = float(value)
    else:
        try:
            number = float(str(value))
        except (TypeError, ValueError):
            return None
    return number if math.isfinite(number) else None


def normalize_billing_options(options: typing.Any) -> typing.List[typing.Dict[str, typing.Any]]:
    """Portal ``normalizeBillingOptions``: keep priced HOURLY/MONTHLY/YEARLY options, normalised."""
    result: typing.List[typing.Dict[str, typing.Any]] = []
    for raw in options if isinstance(options, (list, tuple)) else []:
        option = _as_record(raw)
        if option is None:
            continue
        interval = option.get("billing_interval")
        price = _finite_number(option.get("unit_price_minor"))
        if price is None or interval not in BILLING_TERMS:
            continue
        period = option.get("commitment_period")
        normalized = dict(option)
        normalized["committed"] = bool(option.get("committed"))
        normalized["commitment_period"] = period if period in BILLING_TERMS else interval
        for key in ("commitment_months", "committed_hours"):
            number = _finite_number(option.get(key))
            if number:
                normalized[key] = int(number) if float(number).is_integer() else number
            else:
                normalized.pop(key, None)
        normalized["unit_price_minor"] = int(price) if float(price).is_integer() else price
        result.append(normalized)
    return result


def billing_options_of(catalog: typing.Any) -> typing.List[typing.Dict[str, typing.Any]]:
    """The normalised ``billing_options`` carried by a billing catalog (or a plan)."""
    record = _as_record(catalog) or {}
    options = record.get("billing_options")
    if options is None and _as_record(record.get("billing_catalog")) is not None:
        options = (_as_record(record.get("billing_catalog")) or {}).get("billing_options")
    return normalize_billing_options(options)


def default_billing_term(catalog: typing.Any) -> typing.Optional[str]:
    """``HOURLY`` when offered, else the first option's term; ``None`` when there are no options."""
    options = billing_options_of(catalog)
    if not options:
        return None
    for option in options:
        if option["billing_interval"] == "HOURLY":
            return "HOURLY"
    return str(options[0]["billing_interval"])


def select_billing_option(
    catalog: typing.Any, term: str, *, label: str = "Selected plan", field: str = "billing_term"
) -> typing.Dict[str, typing.Any]:
    """Portal ``billingOptionForInterval``; raises ``'<label> does not support <term> billing'``."""
    for option in billing_options_of(catalog):
        if option["billing_interval"] == term:
            return option
    raise IbeeValidationError(
        f"{label} does not support {term.lower()} billing", code="unsupported_billing_term", field=field
    )


def billing_catalog_for_term(catalog: typing.Any, option: typing.Mapping[str, typing.Any]) -> typing.Dict[str, typing.Any]:
    """Exact port of the portal ``billingCatalogForTerm``."""
    result = dict(_as_record(catalog) or {})
    result["billing_interval"] = option.get("billing_interval")
    result["committed"] = bool(option.get("committed"))
    result["commitment_period"] = option.get("commitment_period")
    if option.get("commitment_months"):
        result["commitment_months"] = option.get("commitment_months")
    if option.get("committed_hours"):
        result["committed_hours"] = option.get("committed_hours")
    if option.get("discount_percent") is not None:
        result["discount_percent"] = option.get("discount_percent")
    if option.get("price_unit"):
        result["price_unit"] = option.get("price_unit")
    result["unit_price_minor"] = option.get("unit_price_minor")
    return result


def _apply_term(
    catalog: typing.Dict[str, typing.Any], term: str, *, label: str, required: bool
) -> typing.Dict[str, typing.Any]:
    if billing_options_of(catalog):
        return billing_catalog_for_term(catalog, select_billing_option(catalog, term, label=label))
    interval = str(catalog.get("billing_interval") or "").strip().upper()
    if required and interval and interval != term:
        raise IbeeValidationError(
            f"{label} does not support {term.lower()} billing", code="unsupported_billing_term", field="billing_term"
        )
    return catalog


def build_windows_license_sku(
    windows_license: typing.Any, *, term: typing.Optional[str], cpu: int
) -> typing.Dict[str, typing.Any]:
    """Price the Windows licence add-on for the VM like the portal (per vCPU, same billing term)."""
    record = _as_record(windows_license)
    if record is None:
        raise IbeeValidationError(
            "windows_license must be a billing SKU object with sku_id and sku_code.",
            code="invalid_windows_license",
            field="windows_license",
        )
    for key in ("os_type", "os_family"):
        value = record.get(key)
        if value is not None and str(value).strip() and str(value).strip().lower() != "windows":
            raise IbeeValidationError(
                f"windows_license {key} must be 'windows'.", code="invalid_windows_license", field="windows_license"
            )
    priced = _apply_term(record, term, label="Windows licence", required=True) if term else record
    priced.pop("billing_options", None)
    priced.update(
        {
            "component_key": "windows_license",
            "os_type": "windows",
            "os_family": "windows",
            "quantity_basis": "VCPU",
            "quantity": max(1, int(cpu)),
        }
    )
    return require_billing_sku(priced, "Windows licence", field="windows_license")


def build_vm_billing_catalog(
    plan_catalog: typing.Any,
    *,
    term: typing.Optional[str],
    apply_term: bool = True,
    os_type: typing.Optional[str] = None,
    cpu: typing.Optional[int] = None,
    windows_license: typing.Any = None,
    reserved_ip_billing_catalog: typing.Any = None,
    context: str = "Selected VM plan",
) -> typing.Dict[str, typing.Any]:
    """Build the ``billing_catalog`` for a VM create or resize exactly like the portal.

    * the plan SKU with the chosen billing term applied (``billingCatalogForTerm``);
      without ``term`` the plan's default term is used (``HOURLY`` when offered),
      and a plan that lists no billing options is sent unmodified (billed hourly);
    * ``attached_skus.windows_license`` when ``os_type`` is ``windows`` (required),
      priced per vCPU for the same term; rejected for any other OS;
    * ``attached_skus.reserved_ip`` when a Reserved IP is used for the public IP.
    """
    if _as_record(plan_catalog) is None:
        raise _error(f"{context} is missing Billing catalog data", "billing_catalog")
    base = validate_billing_catalog(plan_catalog, context=context)
    effective_term = term
    if apply_term:
        effective_term = term or default_billing_term(base)
        if effective_term is not None:
            base = _apply_term(base, effective_term, label="Selected plan", required=term is not None)
    base.pop("billing_options", None)
    is_windows = str(os_type or "").strip().lower() == "windows"
    license_sku = None
    if is_windows:
        if windows_license is None:
            raise IbeeValidationError(
                "Windows VMs require a Windows licence SKU: pass windows_license (a billing SKU object with "
                "sku_id and sku_code). The public API does not list licence add-ons yet.",
                code="windows_license_required",
                field="windows_license",
            )
        license_sku = build_windows_license_sku(
            windows_license, term=effective_term or base.get("billing_interval"), cpu=int(cpu or 1)
        )
    elif windows_license is not None:
        raise IbeeValidationError(
            "windows_license is only allowed for Windows VMs.", code="windows_license_not_allowed", field="windows_license"
        )
    reserved_ip = None
    if reserved_ip_billing_catalog is not None:
        reserved_ip = require_billing_sku(reserved_ip_billing_catalog, "Selected Reserved IP", field="reserved_public_ip_id")
    return with_attached_billing_skus(
        base, {"windows_license": license_sku, "reserved_ip": reserved_ip}, context=context
    )


__all__ = [
    "BILLING_TERMS",
    "ROOT_DISK_COMPONENTS",
    "billing_catalog_for_term",
    "billing_options_of",
    "build_vm_billing_catalog",
    "build_windows_license_sku",
    "default_billing_term",
    "normalize_billing_options",
    "normalize_billing_term",
    "normalize_component_key",
    "require_billing_sku",
    "select_billing_option",
    "validate_billing_catalog",
    "with_attached_billing_skus",
]
