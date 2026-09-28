"""VPC, subnet, node, NAT gateway, port-forwarding and virtual-IP rules, ported from the IBEE portal.

Every function raises :class:`~ibee.validation.IbeeValidationError` before any HTTP
call. Functions that take a record (VPC, subnet, NAT gateway, allocation, virtual
IP) accept either the SDK model or a plain ``dict``.
"""

from __future__ import annotations

import numbers
import re
import typing

from . import IbeeValidationError
from .compute import as_plain, record_get

# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


class IbeeBillingWarning(UserWarning):
    """Emitted when a billable network resource is created without a billing catalog.

    The portal always sends the NAT-GATEWAY / RESERVED-IP catalog; the public API
    cannot list it yet, so the SDK warns instead of refusing.
    """


# ---------------------------------------------------------------------------
# IPv4 parsing
# ---------------------------------------------------------------------------

_OCTET = re.compile(r"^\d{1,3}$")
_CIDR = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})$")

RFC1918_BLOCKS: typing.Tuple[typing.Tuple[int, int], ...] = (
    (0x0A000000, 0x0AFFFFFF),  # 10.0.0.0/8
    (0xAC100000, 0xAC1FFFFF),  # 172.16.0.0/12
    (0xC0A80000, 0xC0A8FFFF),  # 192.168.0.0/16
)
RFC1918_MESSAGE = "Use private RFC1918 space: 10.0.0.0/8, 172.16.0.0/12, or 192.168.0.0/16."
VPC_PREFIX_RANGE = (22, 28)
SUBNET_MAX_PREFIX = 29
SUBNET_PREFIX_RANGE = (22, 29)
MAX_SUBNETS_PER_VPC = 10
DEFAULT_SUBNET_DNS: typing.Tuple[str, ...] = ("1.1.1.1", "8.8.8.8")


class Ipv4Cidr(typing.NamedTuple):
    """A parsed IPv4 CIDR. ``start``/``end`` are integer addresses (``end`` inclusive)."""

    address: int
    prefix: int
    size: int

    @property
    def start(self) -> int:
        return self.address - (self.address % self.size)

    @property
    def end(self) -> int:
        return self.start + self.size - 1

    @property
    def aligned(self) -> bool:
        return self.address % self.size == 0


def format_ipv4(value: int) -> str:
    """Dotted-quad text of an integer IPv4 address."""
    return ".".join(str((value >> shift) & 0xFF) for shift in (24, 16, 8, 0))


def parse_ipv4(value: typing.Any, *, field: str = "ip") -> int:
    """Strict dotted-quad IPv4 (4 decimal octets 0-255) as an integer."""
    text = value.strip() if isinstance(value, str) else None
    parts = text.split(".") if text else []
    if len(parts) != 4 or not all(_OCTET.fullmatch(part) and int(part) <= 255 for part in parts):
        raise IbeeValidationError(
            f"{field} must be an IPv4 address like 10.0.0.10.", code=f"invalid_{field}", field=field
        )
    result = 0
    for part in parts:
        result = (result << 8) | int(part)
    return result


def parse_ipv4_cidr(value: typing.Any, *, field: str = "cidr") -> Ipv4Cidr:
    """Parse ``A.B.C.D/P`` (octets 0-255, prefix 0-32). Alignment is reported separately."""
    text = value.strip() if isinstance(value, str) else ""
    match = _CIDR.fullmatch(text)
    if not match or any(int(octet) > 255 for octet in match.groups()[:4]) or int(match.group(5)) > 32:
        raise IbeeValidationError(
            f"{field} must be an IPv4 CIDR like 10.20.0.0/24.", code=f"invalid_{field}", field=field
        )
    address = parse_ipv4(text.split("/", 1)[0], field=field)
    prefix = int(match.group(5))
    return Ipv4Cidr(address, prefix, 2 ** (32 - prefix))


def is_rfc1918_range(start: int, end: int) -> bool:
    return any(low <= start and end <= high for low, high in RFC1918_BLOCKS)


def is_private_ipv4(value: int) -> bool:
    """RFC1918, loopback, link-local or shared/benchmark private space (Python ``is_private`` for IPv4)."""
    import ipaddress

    return ipaddress.IPv4Address(value).is_private


def cidr_contains(outer: Ipv4Cidr, inner: Ipv4Cidr) -> bool:
    return inner.start >= outer.start and inner.end <= outer.end


def cidr_overlaps(a: Ipv4Cidr, b: Ipv4Cidr) -> bool:
    return a.start <= b.end and b.start <= a.end


def validate_private_cidr(
    cidr: typing.Any, *, min_prefix: int = 0, max_prefix: int = 32, field: str = "cidr"
) -> str:
    """Strict RFC1918 IPv4 network with ``min_prefix <= prefix <= max_prefix``; returns ``A.B.C.D/P``."""
    parsed = parse_ipv4_cidr(cidr, field=field)
    if not min_prefix <= parsed.prefix <= max_prefix:
        if min_prefix > 0:
            message = f"{field} prefix must be between /{min_prefix} and /{max_prefix}."
        else:
            message = f"{field} prefix must be /{max_prefix} or larger (for example /24)."
        raise IbeeValidationError(message, code=f"invalid_{field}", field=field)
    if not parsed.aligned:
        suggestion = f"{format_ipv4(parsed.start)}/{parsed.prefix}"
        raise IbeeValidationError(
            f"{field} must start on a /{parsed.prefix} boundary. Did you mean {suggestion}?",
            code=f"invalid_{field}",
            field=field,
            details={"suggestion": suggestion},
        )
    if not is_rfc1918_range(parsed.start, parsed.end):
        raise IbeeValidationError(RFC1918_MESSAGE, code=f"invalid_{field}", field=field)
    return f"{format_ipv4(parsed.start)}/{parsed.prefix}"


def validate_vpc_cidr(cidr: typing.Any, *, field: str = "cidr") -> str:
    """VPC CIDR: RFC1918, aligned, prefix /22-/28."""
    return validate_private_cidr(cidr, min_prefix=VPC_PREFIX_RANGE[0], max_prefix=VPC_PREFIX_RANGE[1], field=field)


def validate_subnet_cidr(
    cidr: typing.Any,
    *,
    vpc_cidr: typing.Optional[str] = None,
    existing_cidrs: typing.Iterable[str] = (),
    field: str = "cidr",
) -> str:
    """Subnet CIDR: RFC1918, aligned, prefix <= /29, inside ``vpc_cidr`` and not overlapping ``existing_cidrs``."""
    value = validate_private_cidr(cidr, max_prefix=SUBNET_MAX_PREFIX, field=field)
    parsed = parse_ipv4_cidr(value)
    if vpc_cidr:
        outer = parse_ipv4_cidr(vpc_cidr)
        if not cidr_contains(outer, parsed):
            raise IbeeValidationError(
                f"Subnet CIDR must be a sub-range of {vpc_cidr}.", code="subnet_outside_vpc", field=field
            )
    for other in existing_cidrs:
        try:
            other_cidr = parse_ipv4_cidr(other)
        except IbeeValidationError:
            continue
        if cidr_overlaps(parsed, other_cidr):
            raise IbeeValidationError(
                f"Subnet CIDR overlaps the existing subnet {other}.", code="subnet_overlap", field=field
            )
    return value


def validate_ipv4(value: typing.Any, *, field: str = "ip", private: bool = False) -> str:
    """Dotted-quad IPv4 (normalised); ``private=True`` also requires a private address."""
    number = parse_ipv4(value, field=field)
    if private and not is_private_ipv4(number):
        raise IbeeValidationError(
            f"{field} must be a private IPv4 address.", code=f"invalid_{field}", field=field
        )
    return format_ipv4(number)


def validate_host_in_subnet(
    ip: typing.Any, subnet_cidr: str, gateway: typing.Optional[str] = None, *, field: str = "ip"
) -> str:
    """A usable host in ``subnet_cidr``: not the network, broadcast or gateway address (portal wording)."""
    number = parse_ipv4(ip, field=field)
    subnet = parse_ipv4_cidr(subnet_cidr, field="subnet_cidr")
    if not subnet.start <= number <= subnet.end:
        raise IbeeValidationError(
            f"Address must be inside {subnet_cidr}.", code="address_outside_subnet", field=field
        )
    if number in (subnet.start, subnet.end):
        raise IbeeValidationError(
            "Choose a usable host address, not the network or broadcast address.",
            code="address_not_usable",
            field=field,
        )
    if gateway and str(gateway).strip() == format_ipv4(number):
        raise IbeeValidationError(
            "This address is reserved for the subnet gateway.", code="address_is_gateway", field=field
        )
    return format_ipv4(number)


# ---------------------------------------------------------------------------
# Text, ids, lists, ports
# ---------------------------------------------------------------------------


def validate_name(
    value: typing.Any, *, field: str = "name", max_length: int = 80, message: typing.Optional[str] = None
) -> str:
    """Strip; 1 <= len <= ``max_length``."""
    text = value.strip() if isinstance(value, str) else ""
    if not text:
        raise IbeeValidationError(message or f"{field} is required.", code=f"invalid_{field}", field=field)
    if len(text) > max_length:
        raise IbeeValidationError(
            f"{field} must be 1-{max_length} characters.", code=f"invalid_{field}", field=field
        )
    return text


def validate_text_max(value: typing.Any, *, field: str, max_length: int) -> str:
    """Strip; at most ``max_length`` characters (empty allowed)."""
    if value is None:
        return ""
    if not isinstance(value, str):
        raise IbeeValidationError(f"{field} must be a string.", code=f"invalid_{field}", field=field)
    text = value.strip()
    if len(text) > max_length:
        raise IbeeValidationError(
            f"{field} must be at most {max_length} characters.", code=f"invalid_{field}", field=field
        )
    return text


def validate_resource_id(value: typing.Any, *, field: str, max_length: int = 160) -> str:
    """Strip; non-empty; at most ``max_length`` characters."""
    text = value.strip() if isinstance(value, str) else ""
    if not text:
        raise IbeeValidationError(f"{field} is required.", code=f"invalid_{field}", field=field)
    if len(text) > max_length:
        raise IbeeValidationError(
            f"{field} must be at most {max_length} characters.", code=f"invalid_{field}", field=field
        )
    return text


def validate_bounded_id_list(
    values: typing.Any, *, field: str, max_items: int = 32, min_items: int = 0, label: str = "IDs"
) -> typing.List[str]:
    """Strip each id (blank rejected), de-duplicate keeping order, ``min_items <= len <= max_items``."""
    if values is None:
        values = []
    if isinstance(values, str) or not isinstance(values, typing.Iterable):
        raise IbeeValidationError(f"{field} must be a list of strings.", code=f"invalid_{field}", field=field)
    result: typing.List[str] = []
    for value in values:
        text = value.strip() if isinstance(value, str) else ""
        if not text:
            raise IbeeValidationError(f"{label} cannot be blank.", code=f"invalid_{field}", field=field)
        if text not in result:
            result.append(text)
    if len(result) > max_items:
        raise IbeeValidationError(
            f"{field} accepts at most {max_items} items.", code=f"invalid_{field}", field=field
        )
    if len(result) < min_items:
        raise IbeeValidationError(
            f"{field} needs at least {min_items} item(s).", code=f"invalid_{field}", field=field
        )
    return result


PORT_MESSAGE = "Ports must be whole numbers from 1 to 65535."


def validate_port(value: typing.Any, *, field: str = "port") -> int:
    """Integer (not bool/float) 1-65535."""
    if not isinstance(value, numbers.Integral) or isinstance(value, bool) or not 1 <= int(value) <= 65535:
        raise IbeeValidationError(PORT_MESSAGE, code="invalid_port", field=field)
    return int(value)


def validate_dns_list(values: typing.Any, *, field: str = "dns") -> typing.List[str]:
    """At least one IPv4 address."""
    if isinstance(values, str) or not isinstance(values, typing.Iterable):
        raise IbeeValidationError(f"{field} must be a list of IPv4 addresses.", code=f"invalid_{field}", field=field)
    result = [validate_ipv4(item, field=field) for item in values]
    if not result:
        raise IbeeValidationError(f"{field} needs at least one server.", code=f"invalid_{field}", field=field)
    return result


def _given(value: typing.Any) -> bool:
    return value is not None and value is not ...


def require_changes(body: typing.Mapping[str, typing.Any], message: str) -> None:
    """PATCH bodies must carry at least one field."""
    if not body:
        raise IbeeValidationError(message, code="no_changes")


# ---------------------------------------------------------------------------
# Billing catalogs for network resources
# ---------------------------------------------------------------------------

NAT_GATEWAY_SKU_CODE = "NAT-GATEWAY"
RESERVED_IP_SKU_CODE = "RESERVED-IP"
NETWORK_BILLING_CATALOG_KEYS: typing.Tuple[str, ...] = (
    "source",
    "product_id",
    "product_code",
    "sku_id",
    "sku_code",
    "display_name",
    "plan_id",
    "plan_version",
    "unit_price_minor",
    "price_currency",
    "billing_interval",
    "billing_period_hours",
)


def network_billing_catalog(price: typing.Any) -> typing.Dict[str, typing.Any]:
    """Build the catalog object the portal sends from a network price record (``{}`` for ``None``).

    Accepts snake_case or camelCase keys (``skuId``/``sku_id``).
    """
    record = as_plain(price)
    if not record:
        return {}
    result: typing.Dict[str, typing.Any] = {}
    for key in NETWORK_BILLING_CATALOG_KEYS:
        camel = re.sub(r"_([a-z])", lambda m: m.group(1).upper(), key)
        value = record.get(key, record.get(camel))
        if value is not None:
            result[key] = value
    return result


def validate_network_billing_catalog(
    value: typing.Any, *, field: str = "billing_catalog", require_sku_id: bool = False
) -> typing.Dict[str, typing.Any]:
    """A dict with a non-empty string ``sku_code`` (or ``code``); ``unit_price_minor`` >= 0 when present."""
    record = as_plain(value)
    if not record:
        raise IbeeValidationError(
            f"{field} must be an object with a sku_code.", code="invalid_billing_catalog", field=field
        )
    code = record.get("sku_code", record.get("code"))
    if not isinstance(code, str) or not code.strip():
        raise IbeeValidationError(
            f"{field} must include a non-empty sku_code.", code="invalid_billing_catalog", field=field
        )
    if require_sku_id:
        sku_id = record.get("sku_id")
        if sku_id is None or isinstance(sku_id, bool) or str(sku_id).strip() == "":
            raise IbeeValidationError(
                f"{field} must include a non-empty sku_id.", code="invalid_billing_catalog", field=field
            )
    price = record.get("unit_price_minor")
    if price is not None and (
        not isinstance(price, numbers.Integral) or isinstance(price, bool) or int(price) < 0
    ):
        raise IbeeValidationError(
            f"{field}.unit_price_minor must be an integer >= 0.", code="invalid_billing_catalog", field=field
        )
    return record


# ---------------------------------------------------------------------------
# VPCs
# ---------------------------------------------------------------------------

VPC_CONNECTIVITY_TYPES: typing.Tuple[str, ...] = ("private", "nat_gateway", "public")


def _enum_text(value: typing.Any) -> typing.Any:
    """Enum inputs are matched trimmed and case-insensitively (like the TypeScript SDK)."""
    value = getattr(value, "value", value)
    return value.strip().lower() if isinstance(value, str) else value


def validate_vpc_connectivity_type(value: typing.Any) -> typing.Optional[str]:
    if not _given(value):
        return None
    value = _enum_text(value)
    if value not in VPC_CONNECTIVITY_TYPES:
        raise IbeeValidationError(
            "connectivity_type must be one of: private, nat_gateway, public.",
            code="invalid_connectivity_type",
            field="connectivity_type",
        )
    return typing.cast(str, value)


def build_vpc_create_body(
    *,
    name: typing.Any,
    site_id: typing.Any,
    description: typing.Any = None,
    region: typing.Any = None,
    cidr: typing.Any = None,
    auto_cidr: typing.Any = None,
    create_default_subnet: typing.Any = None,
    default_subnet_cidr: typing.Any = None,
    is_default: typing.Any = None,
    connectivity_type: typing.Any = None,
    nat_billing_catalog: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """Validate and assemble a VPC create body the way the portal does."""
    body: typing.Dict[str, typing.Any] = {
        "name": validate_name(name, message="Name and location are required."),
        "site_id": validate_resource_id(site_id, field="site_id", max_length=120),
    }
    if _given(description):
        text = validate_text_max(description, field="description", max_length=500)
        if text:
            body["description"] = text
    if _given(region):
        text = validate_text_max(region, field="region", max_length=120)
        if text:
            body["region"] = text
    connectivity = validate_vpc_connectivity_type(connectivity_type)
    if connectivity is not None:
        body["connectivity_type"] = connectivity
    if _given(cidr):
        if auto_cidr is True:
            raise IbeeValidationError("cidr requires auto_cidr=false.", code="invalid_auto_cidr", field="auto_cidr")
        body["cidr"] = validate_vpc_cidr(cidr)
        body["auto_cidr"] = False
    elif auto_cidr is False:
        raise IbeeValidationError(
            "cidr is required when auto_cidr is false.", code="cidr_required", field="cidr"
        )
    elif _given(auto_cidr):
        body["auto_cidr"] = bool(auto_cidr)
    if _given(create_default_subnet):
        body["create_default_subnet"] = bool(create_default_subnet)
    if _given(default_subnet_cidr):
        if create_default_subnet is False:
            raise IbeeValidationError(
                "default_subnet_cidr requires create_default_subnet=true.",
                code="invalid_default_subnet_cidr",
                field="default_subnet_cidr",
            )
        subnet = validate_vpc_cidr(default_subnet_cidr, field="default_subnet_cidr")
        if "cidr" in body and not cidr_contains(parse_ipv4_cidr(body["cidr"]), parse_ipv4_cidr(subnet)):
            raise IbeeValidationError(
                f"default_subnet_cidr must be a sub-range of {body['cidr']}.",
                code="invalid_default_subnet_cidr",
                field="default_subnet_cidr",
            )
        body["default_subnet_cidr"] = subnet
    if _given(is_default):
        body["is_default"] = bool(is_default)
    if _given(nat_billing_catalog):
        if connectivity != "nat_gateway":
            raise IbeeValidationError(
                "nat_billing_catalog is only allowed with connectivity_type='nat_gateway'.",
                code="invalid_nat_billing_catalog",
                field="nat_billing_catalog",
            )
        body["nat_billing_catalog"] = validate_network_billing_catalog(
            nat_billing_catalog, field="nat_billing_catalog"
        )
    return body


def build_vpc_update_body(*, name: typing.Any = None, description: typing.Any = None) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {}
    if _given(name):
        body["name"] = validate_name(name)
    if _given(description):
        body["description"] = validate_text_max(description, field="description", max_length=500)
    require_changes(body, "At least one VPC field must be provided.")
    return body


def vpc_node_count(vpc: typing.Any) -> int:
    count = record_get(vpc, "node_count")
    nodes = record_get(vpc, "attached_nodes") or []
    try:
        count = int(count or 0)
    except (TypeError, ValueError):
        count = 0
    return max(count, len(nodes))


def check_vpc_deletable(vpc: typing.Any, *, deleting_nat_gateway: bool = False) -> None:
    """Portal delete checks: no attached nodes; no NAT gateway unless it is being deleted first."""
    nodes = vpc_node_count(vpc)
    if nodes > 0:
        raise IbeeValidationError(
            f"Detach {nodes} attached node(s) before deleting this VPC.", code="vpc_has_nodes", field="vpc_id"
        )
    if record_get(vpc, "nat_gateways") and not deleting_nat_gateway:
        raise IbeeValidationError(
            "Delete the NAT gateway first (pass delete_nat_gateway=True).",
            code="vpc_has_nat_gateway",
            field="vpc_id",
        )


# ---------------------------------------------------------------------------
# Subnets
# ---------------------------------------------------------------------------


def build_subnet_create_body(
    *,
    name: typing.Any,
    cidr: typing.Any = None,
    auto_cidr: typing.Any = None,
    prefix_length: typing.Any = None,
    dns: typing.Any = None,
    vpc: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """Validate a subnet create body; with ``vpc`` (its detail) also check containment, overlap and quota."""
    body: typing.Dict[str, typing.Any] = {"name": validate_name(name)}
    vpc_cidr = record_get(vpc, "cidr") if vpc is not None else None
    subnets = list(record_get(vpc, "subnets") or []) if vpc is not None else []
    if vpc is not None and len(subnets) >= MAX_SUBNETS_PER_VPC:
        raise IbeeValidationError(
            f"Subnet quota exceeded; limit is {MAX_SUBNETS_PER_VPC} per VPC.", code="subnet_quota_exceeded"
        )
    if _given(cidr):
        if _given(prefix_length):
            raise IbeeValidationError(
                "prefix_length is only valid with automatic CIDR allocation.",
                code="invalid_prefix_length",
                field="prefix_length",
            )
        if auto_cidr is True:
            raise IbeeValidationError("cidr requires auto_cidr=false.", code="invalid_auto_cidr", field="auto_cidr")
        body["cidr"] = validate_subnet_cidr(
            cidr,
            vpc_cidr=vpc_cidr,
            existing_cidrs=[str(record_get(s, "cidr") or "") for s in subnets],
        )
        body["auto_cidr"] = False
    else:
        if auto_cidr is False:
            raise IbeeValidationError(
                "cidr is required when auto_cidr is false.", code="cidr_required", field="cidr"
            )
        if _given(auto_cidr):
            body["auto_cidr"] = True
        if _given(prefix_length):
            low, high = SUBNET_PREFIX_RANGE
            if (
                not isinstance(prefix_length, numbers.Integral)
                or isinstance(prefix_length, bool)
                or not low <= int(prefix_length) <= high
            ):
                raise IbeeValidationError(
                    f"prefix_length must be an integer between {low} and {high}.",
                    code="invalid_prefix_length",
                    field="prefix_length",
                )
            if vpc_cidr:
                vpc_prefix = parse_ipv4_cidr(vpc_cidr).prefix
                if int(prefix_length) < vpc_prefix:
                    raise IbeeValidationError(
                        f"prefix_length must be /{vpc_prefix} or smaller (the VPC is {vpc_cidr}).",
                        code="invalid_prefix_length",
                        field="prefix_length",
                    )
            body["prefix_length"] = int(prefix_length)
    if _given(dns):
        body["dns"] = validate_dns_list(dns)
    return body


def build_subnet_update_body(*, name: typing.Any = None, dns: typing.Any = None) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {}
    if _given(name):
        body["name"] = validate_name(name)
    if _given(dns):
        body["dns"] = validate_dns_list(dns)
    require_changes(body, "At least one subnet field must be provided.")
    return body


# ---------------------------------------------------------------------------
# Nodes (network allocations)
# ---------------------------------------------------------------------------

NODE_CONNECTIVITY: typing.Tuple[str, ...] = ("private", "nat", "public_ip")
_INACTIVE_NODE_STATES = frozenset({"deleting", "deleted", "error", "failed"})


def available_nat_gateway(vpc: typing.Any) -> typing.Any:
    """The first NAT gateway of ``vpc`` whose status is ``available`` (or ``None``)."""
    for gateway in record_get(vpc, "nat_gateways") or []:
        if str(record_get(gateway, "status") or "").lower() == "available":
            return gateway
    return None


def resolve_node_connectivity(
    vpc_connectivity_type: typing.Any,
    nat_gateway_available: bool,
    has_primary_network: bool = False,
    use_vpc_for_internet: bool = True,
) -> str:
    """Portal default connectivity for a node attach: ``nat`` in a NAT VPC with an available gateway, else ``private``."""
    if vpc_connectivity_type == "nat_gateway" and nat_gateway_available and (
        not has_primary_network or use_vpc_for_internet
    ):
        return "nat"
    return "private"


def build_node_attach_body(
    *,
    vm_id: typing.Any,
    subnet_id: typing.Any,
    connectivity: typing.Any = None,
    reserved_public_ip_id: typing.Any = None,
    requested_private_ip: typing.Any = None,
    subnet: typing.Any = None,
    vpc: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """Validate a node attach; ``subnet`` checks ``requested_private_ip``, ``vpc`` checks connectivity."""
    body: typing.Dict[str, typing.Any] = {
        "vm_id": validate_resource_id(vm_id, field="vm_id"),
        "subnet_id": validate_resource_id(subnet_id, field="subnet_id"),
    }
    if _given(connectivity):
        connectivity = _enum_text(connectivity)
        if connectivity not in NODE_CONNECTIVITY:
            raise IbeeValidationError(
                "connectivity must be one of: private, nat, public_ip.",
                code="invalid_connectivity",
                field="connectivity",
            )
        body["connectivity"] = connectivity
    if _given(reserved_public_ip_id):
        if connectivity != "public_ip":
            raise IbeeValidationError(
                "reserved_public_ip_id is only valid with connectivity='public_ip'.",
                code="invalid_reserved_public_ip_id",
                field="reserved_public_ip_id",
            )
        body["reserved_public_ip_id"] = validate_resource_id(reserved_public_ip_id, field="reserved_public_ip_id")
    if _given(requested_private_ip) and isinstance(requested_private_ip, str) and requested_private_ip.strip():
        if subnet is not None:
            body["requested_private_ip"] = validate_host_in_subnet(
                requested_private_ip,
                str(record_get(subnet, "cidr") or ""),
                record_get(subnet, "gateway"),
                field="requested_private_ip",
            )
        else:
            body["requested_private_ip"] = validate_ipv4(requested_private_ip, field="requested_private_ip")
    elif _given(requested_private_ip) and not isinstance(requested_private_ip, str):
        raise IbeeValidationError(
            "requested_private_ip must be a string.", code="invalid_requested_private_ip", field="requested_private_ip"
        )
    if vpc is not None:
        vpc_type = record_get(vpc, "connectivity_type")
        chosen = body.get("connectivity")
        if chosen == "nat":
            if vpc_type != "nat_gateway":
                raise IbeeValidationError(
                    "NAT connectivity needs a nat_gateway VPC.", code="invalid_connectivity", field="connectivity"
                )
            if available_nat_gateway(vpc) is None:
                raise IbeeValidationError(
                    "NAT connectivity needs an available NAT gateway in this VPC.",
                    code="nat_gateway_unavailable",
                    field="connectivity",
                )
        if chosen == "public_ip":
            if vpc_type == "nat_gateway":
                raise IbeeValidationError(
                    "Dedicated public IPs are not available for nat_gateway VPCs.",
                    code="invalid_connectivity",
                    field="connectivity",
                )
            if vpc_type == "private" and "reserved_public_ip_id" not in body:
                raise IbeeValidationError(
                    "public_ip connectivity in a private VPC needs reserved_public_ip_id.",
                    code="reserved_ip_required",
                    field="reserved_public_ip_id",
                )
    return body


# ---------------------------------------------------------------------------
# NAT gateways
# ---------------------------------------------------------------------------

NAT_PUBLIC_IP_ACTIONS: typing.Tuple[str, ...] = ("reserve", "release")


def check_nat_vpc(vpc: typing.Any) -> None:
    if record_get(vpc, "connectivity_type") != "nat_gateway":
        raise IbeeValidationError(
            "NAT gateways can only be created for nat_gateway VPCs.", code="vpc_not_nat_gateway", field="vpc_id"
        )


def check_nat_reserved_ip(reserved_ip: typing.Any, vpc_site_id: typing.Any, *, field: str = "reserved_public_ip_id") -> None:
    """Portal eligibility for a NAT gateway Reserved IP: same site, unattached, ``reserved``, customer-owned."""
    site = record_get(reserved_ip, "site_id")
    if site and vpc_site_id and site != vpc_site_id:
        raise IbeeValidationError(
            "The Reserved IP must be in the same site as the VPC.", code="reserved_ip_site_mismatch", field=field
        )
    if record_get(reserved_ip, "attached_resource_id") or record_get(reserved_ip, "attached_resource_type"):
        raise IbeeValidationError(
            "That Reserved IP is already attached; choose an unattached address.",
            code="reserved_ip_attached",
            field=field,
        )
    status = str(record_get(reserved_ip, "status") or "").lower()
    if status and status != "reserved":
        raise IbeeValidationError(
            f"That Reserved IP is {status}; choose a reserved address.", code="reserved_ip_unavailable", field=field
        )
    kind = record_get(reserved_ip, "reservation_type")
    if kind and kind != "user_reserved":
        raise IbeeValidationError(
            "Only customer Reserved IPs can be used.", code="reserved_ip_not_user_reserved", field=field
        )


def build_nat_create_body(
    *,
    name: typing.Any = None,
    subnet_id: typing.Any = None,
    reserved_public_ip_id: typing.Any = None,
    billing_catalog: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {}
    if _given(subnet_id):
        body["subnet_id"] = validate_resource_id(subnet_id, field="subnet_id")
    if _given(reserved_public_ip_id):
        body["reserved_public_ip_id"] = validate_resource_id(reserved_public_ip_id, field="reserved_public_ip_id")
    if _given(name):
        body["name"] = validate_name(name)
    if _given(billing_catalog):
        body["billing_catalog"] = validate_network_billing_catalog(billing_catalog)
    return body


def default_nat_delete_ip_action(
    gateway: typing.Any, has_reserved_ip_catalog: bool = False, *, uses_reserved_ip: typing.Optional[bool] = None
) -> str:
    """Portal default for ``public_ip_action`` on NAT delete.

    ``uses_reserved_ip`` is the portal ``natGatewayUsesReservedIp`` result when known (legacy gateways without
    ``public_ip_source`` are Reserved-IP backed when their ``public_ip_id`` is a Reserved IP attached to them);
    otherwise ``public_ip_source == 'reserved'`` decides.
    """
    reserved = uses_reserved_ip if uses_reserved_ip is not None else record_get(gateway, "public_ip_source") == "reserved"
    if reserved or has_reserved_ip_catalog:
        return "reserve"
    return "release"


def build_nat_delete_body(
    *,
    public_ip_action: typing.Any = None,
    billing_catalog: typing.Any = None,
    gateway: typing.Any = None,
    uses_reserved_ip: typing.Optional[bool] = None,
) -> typing.Optional[typing.Dict[str, typing.Any]]:
    """Body for NAT delete (``None`` means send no body, like the portal list page).

    Reserving without ``billing_catalog`` is allowed only for a Reserved-IP-backed gateway:
    ``uses_reserved_ip`` when given, else ``gateway.public_ip_source == 'reserved'``.
    """
    if not _given(public_ip_action):
        if _given(billing_catalog):
            raise IbeeValidationError(
                "billing_catalog is only allowed with public_ip_action='reserve'.",
                code="invalid_billing_catalog",
                field="billing_catalog",
            )
        return None
    if public_ip_action not in NAT_PUBLIC_IP_ACTIONS:
        raise IbeeValidationError(
            "public_ip_action must be 'reserve' or 'release'.", code="invalid_public_ip_action", field="public_ip_action"
        )
    body: typing.Dict[str, typing.Any] = {"public_ip_action": public_ip_action}
    if _given(billing_catalog):
        if public_ip_action != "reserve":
            raise IbeeValidationError(
                "billing_catalog is only allowed with public_ip_action='reserve'.",
                code="invalid_billing_catalog",
                field="billing_catalog",
            )
        body["billing_catalog"] = validate_network_billing_catalog(billing_catalog)
    elif (
        public_ip_action == "reserve"
        and gateway is not None
        and not (
            uses_reserved_ip if uses_reserved_ip is not None else record_get(gateway, "public_ip_source") == "reserved"
        )
    ):
        raise IbeeValidationError(
            "Reserving a platform NAT IP requires the RESERVED-IP billing_catalog.",
            code="billing_catalog_required",
            field="billing_catalog",
        )
    return body


# ---------------------------------------------------------------------------
# Port forwarding
# ---------------------------------------------------------------------------

PF_PROTOCOLS: typing.Tuple[str, ...] = ("tcp", "udp")
PF_TARGET_TYPES: typing.Tuple[str, ...] = ("vm", "vip")


def validate_pf_protocol(value: typing.Any) -> str:
    text = value.strip().lower() if isinstance(value, str) else None
    if text not in PF_PROTOCOLS:
        raise IbeeValidationError("protocol must be 'tcp' or 'udp'.", code="invalid_protocol", field="protocol")
    return typing.cast(str, text)


def validate_pf_target_type(value: typing.Any) -> str:
    value = _enum_text(value)
    if value not in PF_TARGET_TYPES:
        raise IbeeValidationError("target_type must be 'vm' or 'vip'.", code="invalid_target_type", field="target_type")
    return typing.cast(str, value)


def check_pf_duplicate(
    rules: typing.Iterable[typing.Any],
    protocol: str,
    external_port: int,
    *,
    exclude_rule_id: typing.Optional[str] = None,
) -> None:
    """No other rule on the gateway may use the same protocol and external port."""
    for rule in rules:
        rule_id = record_get(rule, "port_forward_rule_id") or record_get(rule, "port_forwarding_rule_id")
        if exclude_rule_id is not None and rule_id == exclude_rule_id:
            continue
        if str(record_get(rule, "protocol") or "tcp").lower() == protocol and record_get(rule, "external_port") == external_port:
            raise IbeeValidationError(
                f"{protocol.upper()} external port {external_port} already exists on this NAT gateway.",
                code="duplicate_external_port",
                field="external_port",
            )


def check_gateway_available(gateways: typing.Iterable[typing.Any], nat_gateway_id: str) -> typing.Any:
    for gateway in gateways:
        if record_get(gateway, "nat_gateway_id") == nat_gateway_id:
            if str(record_get(gateway, "status") or "").lower() != "available":
                raise IbeeValidationError(
                    "An active NAT gateway is required.", code="nat_gateway_unavailable", field="nat_gateway_id"
                )
            return gateway
    raise IbeeValidationError(
        "An active NAT gateway is required.", code="nat_gateway_unavailable", field="nat_gateway_id"
    )


def check_pf_vm_target(nodes: typing.Iterable[typing.Any], internal_ip: str, nat_gateway_id: str) -> None:
    for node in nodes:
        if (
            record_get(node, "connectivity") == "nat"
            and record_get(node, "private_ip") == internal_ip
            and record_get(node, "nat_gateway_id") in (None, "", nat_gateway_id)
        ):
            return
    raise IbeeValidationError(
        "internal_ip must be the private IP of a NAT-connected node on this NAT gateway.",
        code="invalid_internal_ip",
        field="internal_ip",
    )


def find_pf_vip_target(virtual_ips: typing.Iterable[typing.Any], internal_ip: str) -> typing.Any:
    for vip in virtual_ips:
        if (
            record_get(vip, "private_ip") == internal_ip
            and record_get(vip, "purpose") == "metallb"
            and str(record_get(vip, "status") or "").lower() == "available"
            and record_get(vip, "announcer_vm_ids")
        ):
            return vip
    raise IbeeValidationError(
        "internal_ip must match an available MetalLB virtual IP in this VPC.",
        code="invalid_internal_ip",
        field="internal_ip",
    )


def check_pf_vip_announcers(target_vm_ids: typing.List[str], vip: typing.Any) -> None:
    announcers = set(record_get(vip, "announcer_vm_ids") or [])
    if set(target_vm_ids) != announcers:
        raise IbeeValidationError(
            "target_vm_ids must match the virtual IP's announcer VMs.",
            code="invalid_target_vm_ids",
            field="target_vm_ids",
        )


def validate_pf_target_vm_ids(target_type: str, values: typing.Any) -> typing.List[str]:
    ids = validate_bounded_id_list(values, field="target_vm_ids", label="VIP announcer VM IDs")
    if target_type == "vm" and ids:
        raise IbeeValidationError(
            "target_vm_ids is only supported for VIP targets.", code="invalid_target_vm_ids", field="target_vm_ids"
        )
    if target_type == "vip" and _given(values) and not ids:
        raise IbeeValidationError(
            "Select at least one MetalLB announcer node.", code="invalid_target_vm_ids", field="target_vm_ids"
        )
    return ids


def build_pf_create_body(
    *,
    name: typing.Any,
    external_port: typing.Any,
    internal_ip: typing.Any,
    internal_port: typing.Any,
    protocol: typing.Any = None,
    target_type: typing.Any = None,
    target_vm_ids: typing.Any = None,
    note: typing.Any = None,
    enabled: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """Validate a port-forwarding rule create body (context checks happen separately)."""
    if not (isinstance(name, str) and name.strip()) or not (isinstance(internal_ip, str) and internal_ip.strip()):
        raise IbeeValidationError(
            "Rule name and internal IP are required.",
            code="invalid_rule",
            field="name" if not (isinstance(name, str) and name.strip()) else "internal_ip",
        )
    kind = validate_pf_target_type(target_type if _given(target_type) else "vm")
    body: typing.Dict[str, typing.Any] = {
        "name": validate_name(name),
        "protocol": validate_pf_protocol(protocol if _given(protocol) else "tcp"),
        "external_port": validate_port(external_port, field="external_port"),
        "internal_ip": validate_ipv4(internal_ip, field="internal_ip", private=True),
        "internal_port": validate_port(internal_port, field="internal_port"),
        "target_type": kind,
        "target_vm_ids": validate_pf_target_vm_ids(kind, target_vm_ids),
        "note": validate_text_max(note, field="note", max_length=500),
        "enabled": True if not _given(enabled) else bool(enabled),
    }
    return body


def build_pf_update_body(
    *,
    name: typing.Any = None,
    protocol: typing.Any = None,
    external_port: typing.Any = None,
    internal_ip: typing.Any = None,
    internal_port: typing.Any = None,
    target_type: typing.Any = None,
    target_vm_ids: typing.Any = None,
    note: typing.Any = None,
    enabled: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {}
    if _given(name):
        body["name"] = validate_name(name)
    if _given(protocol):
        body["protocol"] = validate_pf_protocol(protocol)
    if _given(external_port):
        body["external_port"] = validate_port(external_port, field="external_port")
    if _given(internal_ip):
        body["internal_ip"] = validate_ipv4(internal_ip, field="internal_ip", private=True)
    if _given(internal_port):
        body["internal_port"] = validate_port(internal_port, field="internal_port")
    if _given(target_vm_ids) and not _given(target_type):
        raise IbeeValidationError(
            "target_vm_ids requires target_type in the same update.", code="invalid_target_vm_ids", field="target_vm_ids"
        )
    if _given(target_type):
        kind = validate_pf_target_type(target_type)
        body["target_type"] = kind
        if kind == "vm":
            body["target_vm_ids"] = validate_pf_target_vm_ids(kind, target_vm_ids)
        elif _given(target_vm_ids):
            body["target_vm_ids"] = validate_pf_target_vm_ids(kind, target_vm_ids)
    if _given(note):
        body["note"] = validate_text_max(note, field="note", max_length=500)
    if _given(enabled):
        body["enabled"] = bool(enabled)
    require_changes(body, "At least one port forwarding field must be provided.")
    return body


# ---------------------------------------------------------------------------
# Virtual IPs
# ---------------------------------------------------------------------------

VIRTUAL_IP_PURPOSES: typing.Tuple[str, ...] = ("metallb", "custom")


def eligible_announcer_ids(nodes: typing.Iterable[typing.Any], subnet_id: str) -> typing.List[str]:
    """VM ids that can announce a virtual IP in ``subnet_id``: NAT-connected, same subnet, not failed/deleting."""
    result: typing.List[str] = []
    for node in nodes:
        if (
            record_get(node, "connectivity") == "nat"
            and record_get(node, "subnet_id") == subnet_id
            and str(record_get(node, "status") or "").lower() not in _INACTIVE_NODE_STATES
        ):
            vm_id = record_get(node, "vm_id")
            if vm_id:
                result.append(str(vm_id))
    return result


def build_virtual_ip_create_body(
    *,
    subnet_id: typing.Any,
    private_ip: typing.Any,
    purpose: typing.Any = None,
    announcer_vm_ids: typing.Any = None,
    subnet: typing.Any = None,
    nodes: typing.Optional[typing.Iterable[typing.Any]] = None,
) -> typing.Dict[str, typing.Any]:
    subnet_value = validate_resource_id(subnet_id, field="subnet_id")
    kind = _enum_text(purpose) if _given(purpose) else "metallb"
    if kind not in VIRTUAL_IP_PURPOSES:
        raise IbeeValidationError("purpose must be 'metallb' or 'custom'.", code="invalid_purpose", field="purpose")
    if subnet is not None:
        ip = validate_host_in_subnet(
            private_ip, str(record_get(subnet, "cidr") or ""), record_get(subnet, "gateway"), field="private_ip"
        )
        ip = validate_ipv4(ip, field="private_ip", private=True)
    else:
        ip = validate_ipv4(private_ip, field="private_ip", private=True)
    announcers = validate_bounded_id_list(
        announcer_vm_ids, field="announcer_vm_ids", label="Virtual IP announcer VM IDs"
    )
    if kind == "metallb" and not announcers:
        raise IbeeValidationError(
            "Select at least one NAT-connected announcer node.",
            code="invalid_announcer_vm_ids",
            field="announcer_vm_ids",
        )
    if nodes is not None and announcers:
        eligible = set(eligible_announcer_ids(nodes, subnet_value))
        missing = [vm for vm in announcers if vm not in eligible]
        if missing:
            raise IbeeValidationError(
                "Announcer VMs must be NAT-connected nodes in the same subnet: " + ", ".join(missing),
                code="invalid_announcer_vm_ids",
                field="announcer_vm_ids",
            )
    return {"subnet_id": subnet_value, "private_ip": ip, "purpose": kind, "announcer_vm_ids": announcers}


def check_virtual_ip_deletable(vip: typing.Any) -> None:
    if record_get(vip, "public_ip_id"):
        raise IbeeValidationError(
            "Detach the Reserved IP before deleting this reservation.",
            code="virtual_ip_has_reserved_ip",
            field="virtual_ip_id",
        )


__all__ = [
    "DEFAULT_SUBNET_DNS",
    "IbeeBillingWarning",
    "Ipv4Cidr",
    "MAX_SUBNETS_PER_VPC",
    "NAT_GATEWAY_SKU_CODE",
    "NAT_PUBLIC_IP_ACTIONS",
    "NETWORK_BILLING_CATALOG_KEYS",
    "NODE_CONNECTIVITY",
    "PF_PROTOCOLS",
    "PF_TARGET_TYPES",
    "PORT_MESSAGE",
    "RESERVED_IP_SKU_CODE",
    "RFC1918_MESSAGE",
    "VIRTUAL_IP_PURPOSES",
    "VPC_CONNECTIVITY_TYPES",
    "available_nat_gateway",
    "build_nat_create_body",
    "build_nat_delete_body",
    "build_node_attach_body",
    "build_pf_create_body",
    "build_pf_update_body",
    "build_subnet_create_body",
    "build_subnet_update_body",
    "build_virtual_ip_create_body",
    "build_vpc_create_body",
    "build_vpc_update_body",
    "check_gateway_available",
    "check_nat_reserved_ip",
    "check_nat_vpc",
    "check_pf_duplicate",
    "check_pf_vip_announcers",
    "check_pf_vm_target",
    "check_virtual_ip_deletable",
    "check_vpc_deletable",
    "cidr_contains",
    "cidr_overlaps",
    "default_nat_delete_ip_action",
    "eligible_announcer_ids",
    "find_pf_vip_target",
    "format_ipv4",
    "is_private_ipv4",
    "is_rfc1918_range",
    "network_billing_catalog",
    "parse_ipv4",
    "parse_ipv4_cidr",
    "require_changes",
    "resolve_node_connectivity",
    "validate_bounded_id_list",
    "validate_dns_list",
    "validate_host_in_subnet",
    "validate_ipv4",
    "validate_name",
    "validate_network_billing_catalog",
    "validate_pf_protocol",
    "validate_pf_target_type",
    "validate_pf_target_vm_ids",
    "validate_port",
    "validate_private_cidr",
    "validate_resource_id",
    "validate_subnet_cidr",
    "validate_text_max",
    "validate_vpc_cidr",
    "validate_vpc_connectivity_type",
    "vpc_node_count",
]
