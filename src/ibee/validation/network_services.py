"""Reserved IP, firewall and load-balancer rules, ported from the IBEE portal and the networking API.

Every function raises :class:`~ibee.validation.IbeeValidationError` before any HTTP
call. Records (Reserved IPs, firewall groups) may be SDK models or plain dicts.
"""

from __future__ import annotations

import ipaddress
import numbers
import re
import typing

from . import IbeeValidationError
from .compute import as_plain, record_get
from .networking import (
    validate_name,
    validate_network_billing_catalog,
    validate_resource_id,
    validate_text_max,
)


def _given(value: typing.Any) -> bool:
    return value is not None and value is not ...


def _int_in(value: typing.Any, low: int, high: typing.Optional[int], *, field: str, message: typing.Optional[str] = None) -> int:
    if (
        not isinstance(value, numbers.Integral)
        or isinstance(value, bool)
        or int(value) < low
        or (high is not None and int(value) > high)
    ):
        bound = f"between {low} and {high}" if high is not None else f">= {low}"
        raise IbeeValidationError(message or f"{field} must be an integer {bound}.", code=f"invalid_{field.split('.')[-1]}", field=field)
    return int(value)


# ---------------------------------------------------------------------------
# Reserved IPs
# ---------------------------------------------------------------------------

_DNS_LABEL = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def validate_reserved_ip_site_id(site_id: typing.Any) -> str:
    text = site_id.strip() if isinstance(site_id, str) else ""
    if not text or len(text) > 120:
        raise IbeeValidationError(
            "Choose a location for the Reserved IP.", code="invalid_site_id", field="site_id"
        )
    return text


def validate_optional_site_filter(site_id: typing.Any) -> typing.Optional[str]:
    """An optional ``site_id`` list filter: non-empty after trim, at most 120 characters."""
    if site_id is None:
        return None
    return validate_resource_id(site_id, field="site_id", max_length=120)


def validate_reserved_ip_label(label: typing.Any) -> str:
    return validate_text_max(label, field="label", max_length=120)


def validate_reverse_dns(value: typing.Any) -> str:
    """Empty clears it; otherwise a hostname of at most 253 characters (IDNA allowed, optional trailing dot)."""
    if not isinstance(value, str):
        raise IbeeValidationError("reverse_dns must be a string.", code="invalid_reverse_dns", field="reverse_dns")
    text = value.strip()
    if not text:
        return ""
    host = text[:-1] if text.endswith(".") else text
    error = IbeeValidationError(
        "Enter a valid FQDN (for example host.example.com), or leave blank to clear.",
        code="invalid_reverse_dns",
        field="reverse_dns",
    )
    try:
        encoded = host.encode("idna").decode("ascii")
    except (UnicodeError, ValueError):
        raise error from None
    if not encoded or len(encoded) > 253 or not all(_DNS_LABEL.fullmatch(label) for label in encoded.split(".")):
        raise error
    return text


def validate_reserved_ip_billing_catalog(value: typing.Any) -> typing.Dict[str, typing.Any]:
    """RESERVED-IP catalog: ``sku_code`` and ``sku_id`` required; only the portal keys are sent."""
    from .networking import NETWORK_BILLING_CATALOG_KEYS

    record = validate_network_billing_catalog(value, require_sku_id=True)
    return {key: record[key] for key in NETWORK_BILLING_CATALOG_KEYS if key in record}


def build_reserve_ip_body(
    *, site_id: typing.Any, label: typing.Any = None, billing_catalog: typing.Any = None
) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {"site_id": validate_reserved_ip_site_id(site_id)}
    if _given(label):
        body["label"] = validate_reserved_ip_label(label)
    if _given(billing_catalog):
        body["billing_catalog"] = validate_reserved_ip_billing_catalog(billing_catalog)
    return body


def build_reserved_ip_update_body(*, label: typing.Any = None, reverse_dns: typing.Any = None) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {}
    if _given(label):
        body["label"] = validate_reserved_ip_label(label)
    if _given(reverse_dns):
        body["reverse_dns"] = validate_reverse_dns(reverse_dns)
    if not body:
        raise IbeeValidationError("At least one Reserved IP field must be provided.", code="no_changes")
    return body


def build_reserved_ip_target_body(
    *, vm_id: typing.Any, vpc_id: typing.Any = None, subnet_id: typing.Any = None
) -> typing.Dict[str, typing.Any]:
    body: typing.Dict[str, typing.Any] = {"vm_id": validate_resource_id(vm_id, field="vm_id")}
    if _given(vpc_id):
        body["vpc_id"] = validate_resource_id(vpc_id, field="vpc_id")
    if _given(subnet_id):
        body["subnet_id"] = validate_resource_id(subnet_id, field="subnet_id")
    return body


def reserved_ip_attachment_kind(reserved_ip: typing.Any) -> str:
    """Classify a Reserved IP like the portal: none, nat_gateway, vpc_virtual_ip, direct, converted_active or vpc."""
    if not record_get(reserved_ip, "attached_resource_id"):
        return "none"
    kind = record_get(reserved_ip, "attached_resource_type") or ""
    if kind in ("nat_gateway", "vpc_virtual_ip"):
        return kind
    allocation = record_get(reserved_ip, "attached_allocation_id")
    network = record_get(reserved_ip, "attached_network_id")
    if kind in ("vm", "") and network and not allocation and not record_get(reserved_ip, "attached_vpc_id"):
        return "direct"
    if record_get(reserved_ip, "allocation_method") == "converted" and not allocation and not network:
        return "converted_active"
    return "vpc"


def check_reserved_ip_releasable(reserved_ip: typing.Any) -> None:
    if record_get(reserved_ip, "attached_resource_id"):
        if record_get(reserved_ip, "attached_resource_type") == "nat_gateway":
            message = "Change or delete the NAT Gateway before releasing this IP."
        else:
            message = "Detach this IP before releasing it."
        raise IbeeValidationError(message, code="reserved_ip_attached", field="reserved_ip_id")


def check_reserved_ip_attachable(reserved_ip: typing.Any, *, detach_from_service: bool = False) -> bool:
    """Return ``True`` when the IP must be detached from a NAT gateway / VIP first."""
    kind = reserved_ip_attachment_kind(reserved_ip)
    if kind == "none":
        return False
    if kind in ("nat_gateway", "vpc_virtual_ip"):
        if not detach_from_service:
            label = "a NAT gateway" if kind == "nat_gateway" else "a virtual IP"
            raise IbeeValidationError(
                f"Reserved IP is attached to {label}; pass detach_from_service=True to move it.",
                code="reserved_ip_attached_to_service",
                field="reserved_ip_id",
            )
        return True
    raise IbeeValidationError(
        "Reserved IP is already attached; use move_reserved_ip.", code="reserved_ip_attached", field="reserved_ip_id"
    )


def check_reserved_ip_movable(reserved_ip: typing.Any, target_vm_id: str) -> None:
    kind = reserved_ip_attachment_kind(reserved_ip)
    if kind == "none":
        raise IbeeValidationError(
            "Reserved IP is not attached; use attach_reserved_ip.", code="reserved_ip_not_attached", field="reserved_ip_id"
        )
    if kind in ("nat_gateway", "vpc_virtual_ip"):
        raise IbeeValidationError(
            "Detach from the NAT gateway/VIP first or use attach_reserved_ip(detach_from_service=True).",
            code="reserved_ip_attached_to_service",
            field="reserved_ip_id",
        )
    if kind in ("direct", "converted_active"):
        raise IbeeValidationError(
            "Moving a converted or provider-network Reserved IP is not supported; detach first.",
            code="reserved_ip_not_movable",
            field="reserved_ip_id",
        )
    if record_get(reserved_ip, "attached_resource_id") == target_vm_id:
        raise IbeeValidationError(
            "The Reserved IP is already attached to that VM.", code="reserved_ip_same_target", field="vm_id"
        )


def check_reserved_ip_detachable(reserved_ip: typing.Any) -> bool:
    """``False`` when the IP is not attached (detach is then a no-op)."""
    kind = reserved_ip_attachment_kind(reserved_ip)
    if kind == "none":
        return False
    if kind == "converted_active" and record_get(reserved_ip, "attached_resource_type") == "vm":
        raise IbeeValidationError(
            "This converted address is still the VM's active public IP; the VM network must be torn down before detaching.",
            code="reserved_ip_converted_active",
            field="reserved_ip_id",
        )
    return True


def check_reserved_ip_unattached(reserved_ip: typing.Any) -> None:
    if record_get(reserved_ip, "attached_resource_id"):
        raise IbeeValidationError(
            "That Reserved IP is not available; choose an unattached address.",
            code="reserved_ip_attached",
            field="reserved_ip_id",
        )


# ---------------------------------------------------------------------------
# Firewalls
# ---------------------------------------------------------------------------

FIREWALL_PROTOCOLS: typing.Tuple[str, ...] = ("tcp", "udp", "icmp", "any")
FIREWALL_DIRECTIONS: typing.Tuple[str, ...] = ("ingress", "egress")
FIREWALL_ACTIONS: typing.Tuple[str, ...] = ("allow", "drop")
FIREWALL_PROTOCOL_MESSAGE = "The current firewall API supports Any, TCP, UDP, and ICMP rules only."
_PORT_INPUT = re.compile(r"^\s*(\d{1,5})\s*(?:-\s*(\d{1,5})\s*)?$")


def validate_firewall_group_name(name: typing.Any) -> str:
    text = name.strip() if isinstance(name, str) else ""
    if not text:
        raise IbeeValidationError("Firewall name is required.", code="invalid_name", field="name")
    if len(text) > 120:
        raise IbeeValidationError(
            "Firewall name must be 120 characters or fewer.", code="invalid_name", field="name"
        )
    return text


def check_firewall_name_unique(name: str, groups: typing.Iterable[typing.Any]) -> None:
    wanted = name.strip().lower()
    for group in groups:
        if str(record_get(group, "name") or "").strip().lower() == wanted:
            raise IbeeValidationError(
                "A firewall group with this name already exists.", code="duplicate_name", field="name"
            )


def build_firewall_group_body(*, name: typing.Any, description: typing.Any = None, is_default: typing.Any = None) -> typing.Dict[str, typing.Any]:
    if is_default is True:
        raise IbeeValidationError(
            "is_default groups are platform-managed and cannot be created by customers.",
            code="invalid_is_default",
            field="is_default",
        )
    body: typing.Dict[str, typing.Any] = {"name": validate_firewall_group_name(name)}
    if _given(description):
        if not isinstance(description, str):
            raise IbeeValidationError("description must be a string.", code="invalid_description", field="description")
        if description.strip():
            body["description"] = description.strip()
    return body


def parse_port_range(value: typing.Any) -> typing.Tuple[int, int]:
    """Parse ``'22'`` or ``'8000-8080'`` into ``(start, end)`` (portal port input)."""
    match = _PORT_INPUT.fullmatch(str(value if value is not None else ""))
    if not match:
        raise IbeeValidationError(
            "Use a single port like 22 or a range like 8000-8080.", code="invalid_port", field="port"
        )
    start = int(match.group(1))
    end = int(match.group(2)) if match.group(2) else start
    for number in (start, end):
        if not 1 <= number <= 65535:
            raise IbeeValidationError("Port must be between 1 and 65535.", code="invalid_port", field="port")
    if end < start:
        raise IbeeValidationError(
            "Port range end must be greater than or equal to the start.", code="invalid_port", field="port"
        )
    return start, end


def normalize_ipv4_remote_targets(values: typing.Any) -> typing.List[str]:
    """Each item an IPv4 address (-> /32) or IPv4 CIDR (-> its network); de-duplicated."""
    if isinstance(values, str):
        values = [part for part in values.split(",")]
    if not isinstance(values, typing.Iterable):
        raise IbeeValidationError(
            "remote_targets must be a list of IPv4 addresses or CIDRs.", code="invalid_remote_targets", field="remote_targets"
        )
    result: typing.List[str] = []
    for raw in values:
        text = raw.strip() if isinstance(raw, str) else ""
        if not text:
            raise IbeeValidationError(
                "Enter at least one CIDR or IP address for the selected source.",
                code="invalid_remote_targets",
                field="remote_targets",
            )
        try:
            if "/" in text:
                network = ipaddress.ip_network(text, strict=False)
                version = network.version
                normalized = str(network)
            else:
                address = ipaddress.ip_address(text)
                version = address.version
                normalized = f"{address}/32"
        except ValueError:
            raise IbeeValidationError(
                f"{text} is not a valid IPv4 address or CIDR.", code="invalid_remote_targets", field="remote_targets"
            ) from None
        if version != 4:
            raise IbeeValidationError(
                "Only IPv4 remote targets are supported.", code="invalid_remote_targets", field="remote_targets"
            )
        if normalized not in result:
            result.append(normalized)
    if not result:
        raise IbeeValidationError(
            "Enter at least one CIDR or IP address for the selected source.",
            code="invalid_remote_targets",
            field="remote_targets",
        )
    return result


def build_firewall_rule_body(
    *,
    update: bool = False,
    protocol: typing.Any = None,
    port_start: typing.Any = None,
    port_end: typing.Any = None,
    remote_targets: typing.Any = None,
    action: typing.Any = None,
    direction: typing.Any = None,
    description: typing.Any = None,
    priority: typing.Any = None,
    enabled: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """Validate a firewall rule create (``update=False``) or partial update body."""
    body: typing.Dict[str, typing.Any] = {}
    if _given(protocol) or not update:
        value = _enum_text(protocol) if _given(protocol) else "tcp"
        if value not in FIREWALL_PROTOCOLS:
            raise IbeeValidationError(FIREWALL_PROTOCOL_MESSAGE, code="invalid_protocol", field="protocol")
        body["protocol"] = value
    proto = body.get("protocol")
    if proto in ("icmp", "any"):
        if _given(port_start) or _given(port_end):
            raise IbeeValidationError(
                f"Ports are not used by {proto} rules; omit port_start and port_end.",
                code="invalid_port",
                field="port_start",
            )
    else:
        if _given(port_start):
            body["port_start"] = _int_in(port_start, 1, 65535, field="port_start", message="Port must be between 1 and 65535.")
        elif proto in ("tcp", "udp"):
            raise IbeeValidationError("Port is required for TCP and UDP rules.", code="invalid_port", field="port_start")
        if _given(port_end):
            body["port_end"] = _int_in(port_end, 1, 65535, field="port_end", message="Port must be between 1 and 65535.")
        elif "port_start" in body and proto in ("tcp", "udp"):
            body["port_end"] = body["port_start"]
        if "port_start" in body and "port_end" in body and body["port_end"] < body["port_start"]:
            raise IbeeValidationError(
                "Port range end must be greater than or equal to the start.", code="invalid_port", field="port_end"
            )
    if _given(remote_targets):
        body["remote_targets"] = normalize_ipv4_remote_targets(remote_targets)
    elif not update:
        body["remote_targets"] = ["0.0.0.0/0"]
    if _given(action) or not update:
        value = _enum_text(action) if _given(action) else "allow"
        if value not in FIREWALL_ACTIONS:
            raise IbeeValidationError("action must be 'allow' or 'drop'.", code="invalid_action", field="action")
        body["action"] = value
    if _given(direction) or not update:
        value = _enum_text(direction) if _given(direction) else "ingress"
        if value not in FIREWALL_DIRECTIONS:
            raise IbeeValidationError(
                "direction must be 'ingress' or 'egress'.", code="invalid_direction", field="direction"
            )
        body["direction"] = value
    if _given(description):
        if not isinstance(description, str):
            raise IbeeValidationError("description must be a string.", code="invalid_description", field="description")
        if description.strip():  # blank is omitted on create and update (portal)
            body["description"] = description.strip()
    if _given(priority):
        if not isinstance(priority, numbers.Integral) or isinstance(priority, bool):
            raise IbeeValidationError("priority must be an integer.", code="invalid_priority", field="priority")
        body["priority"] = int(priority)
    if _given(enabled):
        body["enabled"] = bool(enabled)
    if update and not body:
        raise IbeeValidationError("At least one firewall rule field must be provided.", code="no_changes")
    return body


def find_firewall_rule(group: typing.Any, rule_id: str) -> typing.Any:
    for rule in record_get(group, "rules") or []:
        if record_get(rule, "rule_id") == rule_id or record_get(rule, "firewall_rule_id") == rule_id:
            return rule
    return None


def check_rule_not_system_managed(group: typing.Any, rule_id: str, *, deleting: bool = False) -> None:
    rule = find_firewall_rule(group, rule_id)
    if rule is not None and record_get(rule, "system_managed"):
        raise IbeeValidationError(
            "System-managed rules cannot be removed." if deleting else "System-managed firewall rules cannot be updated.",
            code="system_managed_rule",
            field="firewall_rule_id",
        )


# ---------------------------------------------------------------------------
# Load balancers
# ---------------------------------------------------------------------------

LB_STATUSES: typing.Tuple[str, ...] = ("provisioning", "active", "failed", "deleting", "deleted")
LB_LAYERS: typing.Tuple[str, ...] = ("l4", "l7")
LB_PROTOCOLS_BY_LAYER: typing.Dict[str, typing.Tuple[str, ...]] = {"l4": ("tcp", "tls_passthrough"), "l7": ("http", "https")}
LB_ALGORITHMS: typing.Tuple[str, ...] = ("round_robin", "least_request", "random", "consistent_hash")
LB_BACKEND_TYPES: typing.Tuple[str, ...] = ("service", "ip", "hostname")
LB_HEALTH_CHECK_TYPES: typing.Tuple[str, ...] = ("http", "https", "tcp")
DEFAULT_RETRY_ON: typing.Tuple[str, ...] = ("5xx", "reset", "connect-failure")
#: The portal's health-check form defaults (not sent automatically).
PORTAL_HEALTH_CHECK_DEFAULT: typing.Dict[str, typing.Any] = {
    "active": {"type": "http", "path": "/health", "interval_ms": 10000, "timeout_ms": 2000, "healthy_threshold": 2, "unhealthy_threshold": 3}
}


def _plain(value: typing.Any, field: str) -> typing.Dict[str, typing.Any]:
    record = as_plain(value)
    if not record and not isinstance(value, typing.Mapping):
        raise IbeeValidationError(f"{field} must be an object.", code=f"invalid_{field.split('.')[-1]}", field=field)
    return {key: item for key, item in record.items() if item is not None}


def _enum_text(value: typing.Any) -> typing.Any:
    """Enum inputs are matched trimmed and case-insensitively (like the TypeScript SDK)."""
    value = getattr(value, "value", value)
    return value.strip().lower() if isinstance(value, str) else value


def _choice(value: typing.Any, choices: typing.Sequence[str], field: str) -> str:
    text = _enum_text(value)
    if text not in choices:
        raise IbeeValidationError(
            f"{field} must be one of: {', '.join(choices)}.", code=f"invalid_{field.split('.')[-1]}", field=field
        )
    return typing.cast(str, text)


def _bool(value: typing.Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise IbeeValidationError(f"{field} must be true or false.", code=f"invalid_{field.split('.')[-1]}", field=field)
    return value


def validate_lb_name(name: typing.Any) -> str:
    text = name.strip() if isinstance(name, str) else ""
    if not text:
        raise IbeeValidationError("Name is required.", code="invalid_name", field="name")
    if len(text) > 128:
        raise IbeeValidationError("Name must be 1-128 characters.", code="invalid_name", field="name")
    return text


def validate_lb_backend(value: typing.Any, *, field: str = "backends") -> typing.Dict[str, typing.Any]:
    record = _plain(value, field)
    kind = _choice(record.get("type", "service"), LB_BACKEND_TYPES, f"{field}.type")
    target = record.get("target")
    target = target.strip() if isinstance(target, str) else ""
    if not target:
        raise IbeeValidationError("Each backend target is required.", code="invalid_backend", field=field)
    if kind == "ip":
        try:
            ipaddress.ip_address(target)
        except ValueError:
            raise IbeeValidationError(
                "IP backends must use a valid IP address.", code="invalid_backend", field=field
            ) from None
    elif kind == "hostname":
        if "." not in target or target.startswith(".") or target.endswith("."):
            raise IbeeValidationError(
                "Hostname backends must use a valid fully qualified hostname.", code="invalid_backend", field=field
            )
    elif "/" in target or ":" in target:
        raise IbeeValidationError(
            "Service backends must use a Kubernetes service name without a slash or port.",
            code="invalid_backend",
            field=field,
        )
    result: typing.Dict[str, typing.Any] = {
        "type": kind,
        "target": target,
        "port": _int_in(record.get("port"), 1, 65535, field=f"{field}.port"),
        "weight": _int_in(record.get("weight", 100), 1, 1000, field=f"{field}.weight"),
        "tls": _bool(record.get("tls", False), f"{field}.tls"),
    }
    return result


def validate_lb_backends(values: typing.Any, *, field: str = "backends") -> typing.List[typing.Dict[str, typing.Any]]:
    if isinstance(values, (str, bytes)) or not isinstance(values, typing.Iterable):
        raise IbeeValidationError(f"{field} must be a list.", code="invalid_backends", field=field)
    items = [validate_lb_backend(item, field=field) for item in values]
    if not items:
        raise IbeeValidationError("Add at least one backend.", code="invalid_backends", field=field)
    return items


def validate_lb_routing(value: typing.Any, *, layer: str) -> typing.Dict[str, typing.Any]:
    record = _plain(value, "routing")
    result: typing.Dict[str, typing.Any] = {}
    if "algorithm" in record:
        result["algorithm"] = _choice(record["algorithm"], LB_ALGORITHMS, "routing.algorithm")
    if "sticky_header" in record:
        if layer != "l7":
            raise IbeeValidationError(
                "Sticky sessions (sticky_header) are only available on L7 load balancers.",
                code="invalid_sticky_header",
                field="routing.sticky_header",
            )
        header = record["sticky_header"]
        header = header.strip() if isinstance(header, str) else ""
        if not header:
            raise IbeeValidationError("Sticky header name is required.", code="invalid_sticky_header", field="routing.sticky_header")
        result["sticky_header"] = header
    unknown = set(record) - {"algorithm", "sticky_header"}
    if unknown:
        raise IbeeValidationError(
            f"Unknown routing field(s): {', '.join(sorted(unknown))}.", code="invalid_routing", field="routing"
        )
    return result


def validate_lb_policy(value: typing.Any) -> typing.Dict[str, typing.Any]:
    record = _plain(value, "policy")
    unknown = set(record) - {"timeout_ms", "retries", "proxy_protocol_enabled"}
    if unknown:
        raise IbeeValidationError(
            f"Unknown policy field(s): {', '.join(sorted(unknown))}.", code="invalid_policy", field="policy"
        )
    result: typing.Dict[str, typing.Any] = {}
    if "timeout_ms" in record:
        result["timeout_ms"] = _int_in(record["timeout_ms"], 100, 300000, field="policy.timeout_ms")
    if "retries" in record:
        retries = _plain(record["retries"], "policy.retries")
        extra = set(retries) - {"attempts", "on", "per_retry_timeout_ms"}
        if extra:
            raise IbeeValidationError(
                f"Unknown retries field(s): {', '.join(sorted(extra))}.", code="invalid_retries", field="policy.retries"
            )
        out: typing.Dict[str, typing.Any] = {
            "attempts": _int_in(retries.get("attempts", 3), 1, 10, field="policy.retries.attempts"),
            "per_retry_timeout_ms": _int_in(
                retries.get("per_retry_timeout_ms", 5000), 100, 120000, field="policy.retries.per_retry_timeout_ms"
            ),
        }
        on = retries.get("on", list(DEFAULT_RETRY_ON))
        if isinstance(on, str) or not isinstance(on, typing.Iterable):
            raise IbeeValidationError("policy.retries.on must be a list of strings.", code="invalid_retries", field="policy.retries.on")
        on_list = [item.strip() for item in on if isinstance(item, str) and item.strip()]
        if not on_list or len(on_list) != len(list(on)):
            raise IbeeValidationError(
                "policy.retries.on must be a non-empty list of non-empty strings.", code="invalid_retries", field="policy.retries.on"
            )
        out["on"] = on_list
        result["retries"] = out
    if "proxy_protocol_enabled" in record:
        result["proxy_protocol_enabled"] = _bool(record["proxy_protocol_enabled"], "policy.proxy_protocol_enabled")
    return result


def validate_lb_health_check(value: typing.Any) -> typing.Dict[str, typing.Any]:
    record = _plain(value, "health_check")
    unknown = set(record) - {"active", "passive"}
    if unknown:
        raise IbeeValidationError(
            f"Unknown health_check field(s): {', '.join(sorted(unknown))}.", code="invalid_health_check", field="health_check"
        )
    result: typing.Dict[str, typing.Any] = {}
    if "active" in record:
        active = _plain(record["active"], "health_check.active")
        out: typing.Dict[str, typing.Any] = {"type": _choice(active.get("type", "http"), LB_HEALTH_CHECK_TYPES, "health_check.active.type")}
        path = active.get("path")
        if path is not None:
            if not isinstance(path, str):
                raise IbeeValidationError("health_check.active.path must be a string.", code="invalid_health_check", field="health_check.active.path")
            path = path.strip()
            if path and out["type"] == "tcp":
                raise IbeeValidationError(
                    "path is not supported for tcp active health checks.", code="invalid_health_check", field="health_check.active.path"
                )
            if path:
                out["path"] = path
        for key, low, high in (
            ("interval_ms", 100, 120000),
            ("timeout_ms", 100, 120000),
            ("healthy_threshold", 1, 20),
            ("unhealthy_threshold", 1, 20),
        ):
            if key in active:
                out[key] = _int_in(active[key], low, high, field=f"health_check.active.{key}")
        result["active"] = out
    if "passive" in record:
        passive = _plain(record["passive"], "health_check.passive")
        out = {}
        if "enabled" in passive:
            out["enabled"] = _bool(passive["enabled"], "health_check.passive.enabled")
        for key, low, high in (
            ("consecutive_5xx", 1, 100),
            ("interval_ms", 100, 120000),
            ("base_ejection_time_ms", 1000, 600000),
        ):
            if key in passive:
                out[key] = _int_in(passive[key], low, high, field=f"health_check.passive.{key}")
        result["passive"] = out
    return result


def validate_lb_observability(value: typing.Any) -> typing.Dict[str, typing.Any]:
    record = _plain(value, "observability")
    if set(record) - {"logs_enabled"}:
        raise IbeeValidationError("observability accepts only logs_enabled.", code="invalid_observability", field="observability")
    return {"logs_enabled": _bool(record.get("logs_enabled", False), "observability.logs_enabled")}


def default_lb_tls(protocol: str) -> typing.Optional[typing.Dict[str, str]]:
    if protocol == "https":
        return {"mode": "terminate", "certificate_source": "managed"}
    if protocol == "tls_passthrough":
        return {"mode": "passthrough", "certificate_source": "managed"}
    return None


def validate_lb_tls(value: typing.Any, *, protocol: typing.Optional[str], layer: str) -> typing.Dict[str, typing.Any]:
    if protocol in ("tcp", "http"):
        raise IbeeValidationError(f"tls is not supported for {protocol} load balancers.", code="invalid_tls", field="tls")
    record = _plain(value, "tls")
    expected = "passthrough" if layer == "l4" else "terminate"
    mode = getattr(record.get("mode", expected), "value", record.get("mode", expected))
    if mode != expected:
        raise IbeeValidationError(f"tls.mode must be '{expected}' for this load balancer.", code="invalid_tls", field="tls.mode")
    source = record.get("certificate_source", "managed")
    if source != "managed" or record.get("cert_pem") or record.get("key_pem"):
        raise IbeeValidationError(
            "Custom certificates are not supported; use certificate_source=managed.", code="invalid_tls", field="tls.certificate_source"
        )
    return {"mode": expected, "certificate_source": "managed"}


def validate_lb_rules(values: typing.Any) -> typing.List[typing.Dict[str, typing.Any]]:
    if isinstance(values, (str, bytes)) or not isinstance(values, typing.Iterable):
        raise IbeeValidationError("rules must be a list.", code="invalid_rules", field="rules")
    result: typing.List[typing.Dict[str, typing.Any]] = []
    for item in values:
        record = _plain(item, "rules")
        rule: typing.Dict[str, typing.Any] = {
            "priority": _int_in(
                record.get("priority", 1), 1, None, field="rules.priority", message="Each L7 rule priority must be a positive number."
            )
        }
        path = record.get("path_prefix", "/")
        path = path.strip() if isinstance(path, str) else ""
        path = path or "/"
        if not path.startswith("/"):
            raise IbeeValidationError("path_prefix must start with '/'.", code="invalid_rules", field="rules.path_prefix")
        rule["path_prefix"] = path
        headers = record.get("headers")
        if headers:
            if not isinstance(headers, typing.Mapping):
                raise IbeeValidationError("rules.headers must be an object.", code="invalid_rules", field="rules.headers")
            clean: typing.Dict[str, str] = {}
            for key, val in headers.items():
                name = key.strip() if isinstance(key, str) else ""
                text = val.strip() if isinstance(val, str) else ""
                if not name or not text:
                    raise IbeeValidationError(
                        "Rule header names and values must be non-empty.", code="invalid_rules", field="rules.headers"
                    )
                clean[name] = text
            rule["headers"] = clean
        if record.get("backends") is not None:
            rule["backends"] = validate_lb_backends(record["backends"], field="rules.backends")
        result.append(rule)
    return result


def validate_lb_custom_domain(value: typing.Any, *, protocol: typing.Optional[str]) -> typing.Dict[str, str]:
    if protocol is not None and protocol != "https":
        raise IbeeValidationError(
            "custom_domain is only supported for l7 https load balancers.", code="invalid_custom_domain", field="custom_domain"
        )
    record = _plain(value, "custom_domain") if not isinstance(value, str) else {"hostname": value}
    hostname = record.get("hostname")
    host = hostname.strip().lower().rstrip(".") if isinstance(hostname, str) else ""
    if not 1 <= len(host) <= 253 or "." not in host or host.startswith("."):
        raise IbeeValidationError(
            "custom_domain.hostname must be a valid FQDN.", code="invalid_custom_domain", field="custom_domain.hostname"
        )
    return {"hostname": host}


def build_lb_body(
    *,
    layer: str,
    update: bool = False,
    name: typing.Any = None,
    protocol: typing.Any = None,
    backends: typing.Any = None,
    routing: typing.Any = None,
    policy: typing.Any = None,
    health_check: typing.Any = None,
    tls: typing.Any = None,
    rules: typing.Any = None,
    custom_domain: typing.Any = ...,
    observability: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    """Validate and assemble an L4/L7 create or update body with the portal's defaults.

    ``custom_domain=None`` on an L7 update clears the domain (sent as JSON ``null``);
    ``...`` (the default) leaves it out.
    """
    body: typing.Dict[str, typing.Any] = {}
    proto: typing.Optional[str] = None
    if not update or _given(name):
        body["name"] = validate_lb_name(name)
    if not update:
        proto = _choice(protocol, LB_PROTOCOLS_BY_LAYER[layer], "protocol")
        body["protocol"] = proto
    if not update or _given(backends):
        body["backends"] = validate_lb_backends(backends)
    if _given(routing):
        body["routing"] = validate_lb_routing(routing, layer=layer)
    if _given(policy):
        body["policy"] = validate_lb_policy(policy)
    if _given(health_check):
        body["health_check"] = validate_lb_health_check(health_check)
    if _given(tls):
        body["tls"] = validate_lb_tls(tls, protocol=proto, layer=layer)
    elif not update and proto is not None:
        default = default_lb_tls(proto)
        if default is not None:
            body["tls"] = default
    if _given(observability):
        body["observability"] = validate_lb_observability(observability)
    if layer == "l4":
        if _given(rules) or (custom_domain is not ... and custom_domain is not None):
            raise IbeeValidationError(
                "custom_domain and rules are only available on L7 load balancers.", code="invalid_field", field="rules"
            )
    else:
        if _given(rules):
            body["rules"] = validate_lb_rules(rules)
        if custom_domain is None and update:
            body["custom_domain"] = None
        elif custom_domain is not ... and custom_domain is not None:
            body["custom_domain"] = validate_lb_custom_domain(custom_domain, protocol=proto)
    if update and not body:
        raise IbeeValidationError("At least one load balancer field must be provided.", code="no_changes")
    return body


def validate_lb_list_params(
    *,
    status: typing.Any = None,
    layer: typing.Any = None,
    protocol: typing.Any = None,
    include_deleted: typing.Any = None,
    limit: typing.Any = None,
    skip: typing.Any = None,
) -> typing.Dict[str, typing.Any]:
    params: typing.Dict[str, typing.Any] = {}
    if status is not None:
        params["status"] = _choice(status, LB_STATUSES, "status")
    if layer is not None:
        params["layer"] = _choice(layer, LB_LAYERS, "layer")
    if protocol is not None:
        allowed = LB_PROTOCOLS_BY_LAYER[params["layer"]] if "layer" in params else ("http", "https", "tcp", "tls_passthrough")
        params["protocol"] = _choice(protocol, allowed, "protocol")
    if include_deleted is not None:
        params["include_deleted"] = _bool(include_deleted, "include_deleted")
    if params.get("status") == "deleted":
        params["include_deleted"] = True
    if limit is not None:
        params["limit"] = _int_in(limit, 1, 500, field="limit")
    if skip is not None:
        params["skip"] = _int_in(skip, 0, None, field="skip")
    return params


__all__ = [
    "DEFAULT_RETRY_ON",
    "FIREWALL_ACTIONS",
    "FIREWALL_DIRECTIONS",
    "FIREWALL_PROTOCOLS",
    "FIREWALL_PROTOCOL_MESSAGE",
    "LB_ALGORITHMS",
    "LB_BACKEND_TYPES",
    "LB_HEALTH_CHECK_TYPES",
    "LB_LAYERS",
    "LB_PROTOCOLS_BY_LAYER",
    "LB_STATUSES",
    "PORTAL_HEALTH_CHECK_DEFAULT",
    "build_firewall_group_body",
    "build_firewall_rule_body",
    "build_lb_body",
    "build_reserve_ip_body",
    "build_reserved_ip_target_body",
    "build_reserved_ip_update_body",
    "check_firewall_name_unique",
    "check_reserved_ip_attachable",
    "check_reserved_ip_detachable",
    "check_reserved_ip_movable",
    "check_reserved_ip_releasable",
    "check_reserved_ip_unattached",
    "check_rule_not_system_managed",
    "default_lb_tls",
    "find_firewall_rule",
    "normalize_ipv4_remote_targets",
    "parse_port_range",
    "reserved_ip_attachment_kind",
    "validate_firewall_group_name",
    "validate_lb_backend",
    "validate_lb_backends",
    "validate_lb_custom_domain",
    "validate_lb_health_check",
    "validate_lb_list_params",
    "validate_lb_name",
    "validate_lb_observability",
    "validate_lb_policy",
    "validate_lb_routing",
    "validate_lb_rules",
    "validate_lb_tls",
    "validate_optional_site_filter",
    "validate_reserved_ip_billing_catalog",
    "validate_reserved_ip_label",
    "validate_reserved_ip_site_id",
    "validate_reverse_dns",
]
