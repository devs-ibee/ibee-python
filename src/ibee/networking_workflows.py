# Hand-written (listed in .fernignore).
"""Portal-equivalent request flows for VPCs, NAT gateways, virtual IPs, Reserved IPs, firewalls and load balancers.

Each flow is a generator of :class:`~ibee.compute_workflows.Call` steps (read-only
pre-steps, then the request the caller asked for) driven by
:func:`~ibee.compute_workflows.run_sync` or :func:`~ibee.compute_workflows.run_async`,
so the sync and async clients share one implementation. Every rule is checked
with :mod:`ibee.validation` before the request it guards.
"""

from __future__ import annotations

import typing
import warnings
from urllib.parse import quote

from .compute_workflows import RESPONSE, Call, Flow, Sleep, billing_preflight
from .errors.forbidden_error import ForbiddenError
from .errors.networking_errors import as_reserved_ip_target_error, is_vpc_allocation_required
from .errors.not_found_error import NotFoundError
from .types.firewall_group import FirewallGroup
from .types.firewall_group_summary import FirewallGroupSummary
from .types.load_balancer import LoadBalancer
from .types.nat_gateway import NatGateway
from .types.nat_port_forwarding_rule import NatPortForwardingRule
from .types.network_allocation import NetworkAllocation
from .types.networking_site import NetworkingSite
from .types.reserved_ip import ReservedIp
from .types.subnet import Subnet
from .types.vpc_detail import VpcDetail
from .types.vpc_summary import VpcSummary
from .types.vpc_virtual_ip import VpcVirtualIp
from .validation import (
    NAT_GATEWAY_SKU_CODE,
    RESERVED_IP_SKU_CODE,
    IbeeBillingWarning,
    IbeeValidationError,
    build_firewall_group_body,
    build_firewall_rule_body,
    build_lb_body,
    build_nat_create_body,
    build_nat_delete_body,
    build_node_attach_body,
    build_pf_create_body,
    build_pf_update_body,
    build_reserve_ip_body,
    build_reserved_ip_target_body,
    build_reserved_ip_update_body,
    build_subnet_create_body,
    build_subnet_update_body,
    build_virtual_ip_create_body,
    build_vpc_create_body,
    build_vpc_update_body,
    check_firewall_name_unique,
    check_gateway_available,
    check_nat_reserved_ip,
    check_nat_vpc,
    check_pf_duplicate,
    check_pf_vip_announcers,
    check_pf_vm_target,
    check_reserved_ip_attachable,
    check_reserved_ip_detachable,
    check_reserved_ip_movable,
    check_reserved_ip_releasable,
    check_reserved_ip_unattached,
    check_rule_not_system_managed,
    check_virtual_ip_deletable,
    check_vpc_deletable,
    find_pf_vip_target,
    record_get,
    validate_lb_list_params,
    validate_limit,
    validate_offset,
    validate_optional_site_filter,
    validate_reserved_ip_billing_catalog,
    validate_reserved_ip_label,
    validate_reserved_ip_site_id,
    validate_resource_id,
)

UNCONTRACTED = "Not yet part of the published API contract; behaviour may change."
NAT_DELETE_WAIT_ATTEMPTS = 20
NAT_DELETE_WAIT_INTERVAL = 0.5
FIREWALL_PAGE_SIZE = 100


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seg(value: str) -> str:
    return quote(value, safe="")


def _pid(value: typing.Any, field: str) -> str:
    """A path id: stripped and non-empty (URL-encoded when the path is built)."""
    text = value.strip() if isinstance(value, str) else ""
    if not text:
        raise IbeeValidationError(f"{field} is required.", code=f"invalid_{field}", field=field)
    return text


def _ws(workspace_id: str, **extra: typing.Any) -> typing.Dict[str, typing.Any]:
    params: typing.Dict[str, typing.Any] = {"workspace_id": workspace_id}
    params.update({key: value for key, value in extra.items() if value is not None})
    return params


def _given(value: typing.Any) -> bool:
    return value is not None and value is not ...


def vpc_path(vpc_id: str, *rest: str) -> str:
    return "/".join(["networking/vpcs", _seg(vpc_id), *(_seg(part) for part in rest)])


def reserved_ip_path(reserved_ip_id: str, *rest: str) -> str:
    return "/".join(["networking/reserved-ips", _seg(reserved_ip_id), *rest])


def firewall_path(firewall_group_id: str, *rest: str) -> str:
    return "/".join(["networking/firewall-groups", _seg(firewall_group_id), *(_seg(part) for part in rest)])


def _preflight(workspace_id: str, sku_code: str, resource_type: str) -> Flow[typing.Any]:
    """Billing preflight that explains a missing ``billing.read`` scope."""
    try:
        return (yield from billing_preflight(workspace_id, sku_code=sku_code, resource_type=resource_type))
    except ForbiddenError as exc:
        exc.message = (
            f"{exc.message} (the billing check needs the billing.read scope; pass the option that "
            "disables the billing check to skip it)"
        ).strip()
        raise


def get_vpc(workspace_id: str, vpc_id: str) -> Flow[typing.Dict[str, typing.Any]]:
    data = yield Call("GET", vpc_path(vpc_id), params=_ws(workspace_id))
    return data if isinstance(data, dict) else {}


def get_subnet(workspace_id: str, vpc_id: str, subnet_id: str) -> Flow[typing.Dict[str, typing.Any]]:
    data = yield Call("GET", vpc_path(vpc_id, "subnets", subnet_id), params=_ws(workspace_id))
    return data if isinstance(data, dict) else {}


def _list(data: typing.Any) -> typing.List[typing.Dict[str, typing.Any]]:
    return [item for item in data or [] if isinstance(item, dict)] if isinstance(data, list) else []


def list_nodes_raw(workspace_id: str, vpc_id: str) -> Flow[typing.List[typing.Dict[str, typing.Any]]]:
    return _list((yield Call("GET", vpc_path(vpc_id, "nodes"), params=_ws(workspace_id))))


def list_gateways_raw(workspace_id: str, vpc_id: str) -> Flow[typing.List[typing.Dict[str, typing.Any]]]:
    return _list((yield Call("GET", vpc_path(vpc_id, "nat-gateways"), params=_ws(workspace_id))))


def list_rules_raw(workspace_id: str, vpc_id: str, nat_gateway_id: str) -> Flow[typing.List[typing.Dict[str, typing.Any]]]:
    path = vpc_path(vpc_id, "nat-gateways", nat_gateway_id, "port-forwarding-rules")
    return _list((yield Call("GET", path, params=_ws(workspace_id))))


def list_virtual_ips_raw(workspace_id: str, vpc_id: str) -> Flow[typing.List[typing.Dict[str, typing.Any]]]:
    return _list((yield Call("GET", vpc_path(vpc_id, "virtual-ips"), params=_ws(workspace_id))))


def get_reserved_ip_raw(workspace_id: str, reserved_ip_id: str) -> Flow[typing.Dict[str, typing.Any]]:
    data = yield Call("GET", reserved_ip_path(reserved_ip_id), params=_ws(workspace_id))
    return data if isinstance(data, dict) else {}


# ---------------------------------------------------------------------------
# Sites and VPCs
# ---------------------------------------------------------------------------


def list_networking_sites(*, workspace_id: str, available_only: bool = False) -> Flow[typing.List[NetworkingSite]]:
    sites = yield Call("GET", "networking/sites", params=_ws(workspace_id), parse=typing.List[NetworkingSite], main=True)
    if available_only:
        sites = [site for site in sites if site.available is True]
    return sites


def list_vpcs(*, workspace_id: str, site_id: typing.Any = None) -> Flow[typing.List[VpcSummary]]:
    site = validate_optional_site_filter(site_id)
    return (
        yield Call("GET", "networking/vpcs", params=_ws(workspace_id, site_id=site), parse=typing.List[VpcSummary], main=True)
    )


def create_vpc(
    *,
    workspace_id: str,
    name: typing.Any = None,
    site_id: typing.Any = None,
    description: typing.Any = None,
    region: typing.Any = None,
    cidr: typing.Any = None,
    auto_cidr: typing.Any = None,
    create_default_subnet: typing.Any = None,
    default_subnet_cidr: typing.Any = None,
    is_default: typing.Any = None,
    connectivity_type: typing.Any = None,
    nat_billing_catalog: typing.Any = None,
    check_site: bool = False,
) -> Flow[VpcDetail]:
    """Portal VPC create: validate CIDR, connectivity and NAT catalog; optionally check the site first."""
    body = build_vpc_create_body(
        name=name,
        site_id=site_id,
        description=description,
        region=region,
        cidr=cidr,
        auto_cidr=auto_cidr,
        create_default_subnet=create_default_subnet,
        default_subnet_cidr=default_subnet_cidr,
        is_default=is_default,
        connectivity_type=connectivity_type,
        nat_billing_catalog=nat_billing_catalog,
    )
    if body.get("connectivity_type") == "public":
        warnings.warn(
            "connectivity_type='public' is deprecated: the portal creates 'private' or 'nat_gateway' VPCs.",
            DeprecationWarning,
            stacklevel=4,
        )
    if body.get("connectivity_type") == "nat_gateway" and "nat_billing_catalog" not in body:
        warnings.warn(
            "The managed NAT gateway will be created without a billing catalog (nat_billing_catalog). "
            "The portal always sends the NAT-GATEWAY catalog.",
            IbeeBillingWarning,
            stacklevel=4,
        )
    if check_site:
        sites = _list((yield Call("GET", "networking/sites", params=_ws(workspace_id))))
        match = next((site for site in sites if site.get("site_id") == body["site_id"]), None)
        if match is None or match.get("available") is not True:
            message = (match or {}).get("message") or "This site does not support VPCs; choose a site where available is true."
            raise IbeeValidationError(str(message), code="site_unavailable", field="site_id")
    return (
        yield Call("POST", "networking/vpcs", params=_ws(workspace_id), json=body, parse=VpcDetail, main=True)
    )


def update_vpc(*, workspace_id: str, vpc_id: str, name: typing.Any = None, description: typing.Any = None) -> Flow[VpcDetail]:
    vpc_id = _pid(vpc_id, "vpc_id")
    body = build_vpc_update_body(name=name, description=description)
    return (yield Call("PATCH", vpc_path(vpc_id), params=_ws(workspace_id), json=body, parse=VpcDetail, main=True))


def wait_for_nat_gateway_absent(
    *,
    workspace_id: str,
    vpc_id: str,
    nat_gateway_id: str,
    attempts: int = NAT_DELETE_WAIT_ATTEMPTS,
    interval: float = NAT_DELETE_WAIT_INTERVAL,
) -> Flow[bool]:
    """Poll the VPC until ``nat_gateway_id`` is gone (a 404 counts as gone); ``False`` after ``attempts``."""
    vpc_id = _pid(vpc_id, "vpc_id")
    nat_gateway_id = _pid(nat_gateway_id, "nat_gateway_id")
    attempts = validate_limit(attempts, maximum=1000, field="attempts") or NAT_DELETE_WAIT_ATTEMPTS
    for attempt in range(attempts):
        try:
            vpc = yield from get_vpc(workspace_id, vpc_id)
        except NotFoundError:
            return True
        if not any(record_get(g, "nat_gateway_id") == nat_gateway_id for g in vpc.get("nat_gateways") or []):
            return True
        if attempt < attempts - 1:
            yield Sleep(interval)
    return False


def delete_vpc(
    *,
    workspace_id: str,
    vpc_id: str,
    check_state: typing.Optional[bool] = None,
    delete_nat_gateway: bool = False,
    nat_public_ip_action: typing.Any = None,
    nat_billing_catalog: typing.Any = None,
    wait_attempts: int = NAT_DELETE_WAIT_ATTEMPTS,
    wait_interval: float = NAT_DELETE_WAIT_INTERVAL,
) -> Flow[None]:
    """Portal VPC delete: refuse while nodes are attached; optionally delete the NAT gateway first."""
    vpc_id = _pid(vpc_id, "vpc_id")
    build_nat_delete_body(public_ip_action=nat_public_ip_action, billing_catalog=nat_billing_catalog)
    if check_state is not False or delete_nat_gateway:
        vpc = yield from get_vpc(workspace_id, vpc_id)
        check_vpc_deletable(vpc, deleting_nat_gateway=delete_nat_gateway)
        gateways = (vpc.get("nat_gateways") or []) if delete_nat_gateway else []
        for gateway in gateways:
            gateway_id = str(record_get(gateway, "nat_gateway_id") or "")
            body = build_nat_delete_body(
                public_ip_action=nat_public_ip_action, billing_catalog=nat_billing_catalog, gateway=gateway
            )
            yield Call("DELETE", vpc_path(vpc_id, "nat-gateways", gateway_id), params=_ws(workspace_id), json=body, parse=None)
            gone = yield from wait_for_nat_gateway_absent(
                workspace_id=workspace_id,
                vpc_id=vpc_id,
                nat_gateway_id=gateway_id,
                attempts=wait_attempts,
                interval=wait_interval,
            )
            if not gone:
                raise IbeeValidationError(
                    "The NAT gateway deletion is still reconciling; retry deleting the VPC shortly.",
                    code="nat_gateway_deleting",
                    field="vpc_id",
                )
    yield Call("DELETE", vpc_path(vpc_id), params=_ws(workspace_id), parse=None, main=True)
    return None


# ---------------------------------------------------------------------------
# Subnets and nodes
# ---------------------------------------------------------------------------


def create_vpc_subnet(
    *,
    workspace_id: str,
    vpc_id: str,
    name: typing.Any = None,
    cidr: typing.Any = None,
    auto_cidr: typing.Any = None,
    prefix_length: typing.Any = None,
    dns: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[Subnet]:
    vpc_id = _pid(vpc_id, "vpc_id")
    build_subnet_create_body(name=name, cidr=cidr, auto_cidr=auto_cidr, prefix_length=prefix_length, dns=dns)
    vpc = None
    if check_state is not False:
        vpc = yield from get_vpc(workspace_id, vpc_id)
    body = build_subnet_create_body(
        name=name, cidr=cidr, auto_cidr=auto_cidr, prefix_length=prefix_length, dns=dns, vpc=vpc
    )
    return (
        yield Call("POST", vpc_path(vpc_id, "subnets"), params=_ws(workspace_id), json=body, parse=Subnet, main=True)
    )


def update_vpc_subnet(
    *, workspace_id: str, vpc_id: str, subnet_id: str, name: typing.Any = None, dns: typing.Any = None
) -> Flow[Subnet]:
    vpc_id = _pid(vpc_id, "vpc_id")
    subnet_id = _pid(subnet_id, "subnet_id")
    body = build_subnet_update_body(name=name, dns=dns)
    path = vpc_path(vpc_id, "subnets", subnet_id)
    return (yield Call("PATCH", path, params=_ws(workspace_id), json=body, parse=Subnet, main=True))


def attach_vpc_node(
    *,
    workspace_id: str,
    vpc_id: str,
    vm_id: typing.Any = None,
    subnet_id: typing.Any = None,
    connectivity: typing.Any = None,
    reserved_public_ip_id: typing.Any = None,
    requested_private_ip: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[NetworkAllocation]:
    vpc_id = _pid(vpc_id, "vpc_id")
    body = build_node_attach_body(
        vm_id=vm_id,
        subnet_id=subnet_id,
        connectivity=connectivity,
        reserved_public_ip_id=reserved_public_ip_id,
        requested_private_ip=requested_private_ip,
    )
    subnet = vpc = None
    if "requested_private_ip" in body and check_state is not False:
        subnet = yield from get_subnet(workspace_id, vpc_id, body["subnet_id"])
    if check_state is True:
        vpc = yield from get_vpc(workspace_id, vpc_id)
    if subnet is not None or vpc is not None:
        body = build_node_attach_body(
            vm_id=vm_id,
            subnet_id=subnet_id,
            connectivity=connectivity,
            reserved_public_ip_id=reserved_public_ip_id,
            requested_private_ip=requested_private_ip,
            subnet=subnet,
            vpc=vpc,
        )
    return (
        yield Call("POST", vpc_path(vpc_id, "nodes"), params=_ws(workspace_id), json=body, parse=NetworkAllocation, main=True)
    )


# ---------------------------------------------------------------------------
# NAT gateways
# ---------------------------------------------------------------------------


def create_nat_gateway(
    *,
    workspace_id: str,
    vpc_id: str,
    subnet_id: typing.Any = None,
    reserved_public_ip_id: typing.Any = None,
    name: typing.Any = None,
    billing_catalog: typing.Any = None,
    preflight_billing: bool = False,
    check_state: typing.Optional[bool] = None,
) -> Flow[NatGateway]:
    """Portal NAT create: only in nat_gateway VPCs; Reserved IP eligibility; optional billing preflight."""
    vpc_id = _pid(vpc_id, "vpc_id")
    body = build_nat_create_body(
        name=name, subnet_id=subnet_id, reserved_public_ip_id=reserved_public_ip_id, billing_catalog=billing_catalog
    )
    if check_state is not False:
        vpc = yield from get_vpc(workspace_id, vpc_id)
        check_nat_vpc(vpc)
        if "reserved_public_ip_id" in body and not vpc.get("nat_gateways"):
            reserved_ip = yield from get_reserved_ip_raw(workspace_id, body["reserved_public_ip_id"])
            check_nat_reserved_ip(reserved_ip, vpc.get("site_id"))
    if "billing_catalog" not in body:
        warnings.warn(
            "The NAT gateway will be created without a billing catalog and will not be metered. "
            "The portal always sends the NAT-GATEWAY catalog.",
            IbeeBillingWarning,
            stacklevel=4,
        )
    if preflight_billing:
        yield from _preflight(workspace_id, NAT_GATEWAY_SKU_CODE, "nat_gateway")
    return (
        yield Call("POST", vpc_path(vpc_id, "nat-gateways"), params=_ws(workspace_id), json=body, parse=NatGateway, main=True)
    )


def delete_nat_gateway(
    *,
    workspace_id: str,
    vpc_id: str,
    nat_gateway_id: str,
    public_ip_action: typing.Any = None,
    billing_catalog: typing.Any = None,
    check_state: typing.Optional[bool] = None,
    wait: bool = False,
    wait_attempts: int = NAT_DELETE_WAIT_ATTEMPTS,
    wait_interval: float = NAT_DELETE_WAIT_INTERVAL,
) -> Flow[typing.Optional[bool]]:
    vpc_id = _pid(vpc_id, "vpc_id")
    nat_gateway_id = _pid(nat_gateway_id, "nat_gateway_id")
    body = build_nat_delete_body(public_ip_action=public_ip_action, billing_catalog=billing_catalog)
    needs_gateway = body is not None and body["public_ip_action"] == "reserve" and "billing_catalog" not in body
    if check_state is True or (needs_gateway and check_state is not False):
        gateways = yield from list_gateways_raw(workspace_id, vpc_id)
        gateway = next((g for g in gateways if g.get("nat_gateway_id") == nat_gateway_id), None)
        if gateway is None:
            raise IbeeValidationError(
                f"NAT gateway {nat_gateway_id} was not found in this VPC.",
                code="nat_gateway_not_found",
                field="nat_gateway_id",
            )
        body = build_nat_delete_body(public_ip_action=public_ip_action, billing_catalog=billing_catalog, gateway=gateway)
        if check_state is True:
            virtual_ips = yield from list_virtual_ips_raw(workspace_id, vpc_id)
            if any(vip.get("public_ip_id") for vip in virtual_ips):
                raise IbeeValidationError(
                    "Detach virtual-IP Reserved Public IPs before deleting the NAT gateway.",
                    code="virtual_ip_has_reserved_ip",
                    field="nat_gateway_id",
                )
    path = vpc_path(vpc_id, "nat-gateways", nat_gateway_id)
    yield Call("DELETE", path, params=_ws(workspace_id), json=body, parse=None, main=True)
    if not wait:
        return None
    return (
        yield from wait_for_nat_gateway_absent(
            workspace_id=workspace_id,
            vpc_id=vpc_id,
            nat_gateway_id=nat_gateway_id,
            attempts=wait_attempts,
            interval=wait_interval,
        )
    )


def replace_nat_gateway_public_ip(
    *,
    workspace_id: str,
    vpc_id: str,
    nat_gateway_id: str,
    reserved_public_ip_id: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[NatGateway]:
    vpc_id = _pid(vpc_id, "vpc_id")
    nat_gateway_id = _pid(nat_gateway_id, "nat_gateway_id")
    reserved = validate_resource_id(reserved_public_ip_id, field="reserved_public_ip_id", max_length=10_000)
    if check_state is True:
        vpc = yield from get_vpc(workspace_id, vpc_id)
        check_gateway_available(vpc.get("nat_gateways") or [], nat_gateway_id)
        reserved_ip = yield from get_reserved_ip_raw(workspace_id, reserved)
        check_nat_reserved_ip(reserved_ip, vpc.get("site_id"))
    path = vpc_path(vpc_id, "nat-gateways", nat_gateway_id, "public-ip")
    return (
        yield Call(
            "PUT", path, params=_ws(workspace_id), json={"reserved_public_ip_id": reserved}, parse=NatGateway, main=True
        )
    )


# ---------------------------------------------------------------------------
# Port forwarding
# ---------------------------------------------------------------------------


def create_nat_port_forwarding_rule(
    *,
    workspace_id: str,
    vpc_id: str,
    nat_gateway_id: str,
    name: typing.Any = None,
    external_port: typing.Any = None,
    internal_ip: typing.Any = None,
    internal_port: typing.Any = None,
    protocol: typing.Any = None,
    target_type: typing.Any = None,
    target_vm_ids: typing.Any = None,
    note: typing.Any = None,
    enabled: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[NatPortForwardingRule]:
    """Portal rule create: gateway available, no duplicate protocol/port, target is a NAT node or MetalLB VIP."""
    vpc_id = _pid(vpc_id, "vpc_id")
    nat_gateway_id = _pid(nat_gateway_id, "nat_gateway_id")
    body = build_pf_create_body(
        name=name,
        external_port=external_port,
        internal_ip=internal_ip,
        internal_port=internal_port,
        protocol=protocol,
        target_type=target_type,
        target_vm_ids=target_vm_ids,
        note=note,
        enabled=enabled,
    )
    if check_state is not False:
        gateways = yield from list_gateways_raw(workspace_id, vpc_id)
        check_gateway_available(gateways, nat_gateway_id)
        rules = yield from list_rules_raw(workspace_id, vpc_id, nat_gateway_id)
        check_pf_duplicate(rules, body["protocol"], body["external_port"])
        if body["target_type"] == "vm":
            nodes = yield from list_nodes_raw(workspace_id, vpc_id)
            check_pf_vm_target(nodes, body["internal_ip"], nat_gateway_id)
        else:
            virtual_ips = yield from list_virtual_ips_raw(workspace_id, vpc_id)
            vip = find_pf_vip_target(virtual_ips, body["internal_ip"])
            if not body["target_vm_ids"]:
                body["target_vm_ids"] = list(vip.get("announcer_vm_ids") or [])
            check_pf_vip_announcers(body["target_vm_ids"], vip)
    if body["target_type"] == "vip" and not body["target_vm_ids"]:
        raise IbeeValidationError(
            "Select at least one MetalLB announcer node.", code="invalid_target_vm_ids", field="target_vm_ids"
        )
    path = vpc_path(vpc_id, "nat-gateways", nat_gateway_id, "port-forwarding-rules")
    return (
        yield Call("POST", path, params=_ws(workspace_id), json=body, parse=NatPortForwardingRule, main=True)
    )


def update_nat_port_forwarding_rule(
    *,
    workspace_id: str,
    vpc_id: str,
    nat_gateway_id: str,
    port_forwarding_rule_id: str,
    name: typing.Any = None,
    protocol: typing.Any = None,
    external_port: typing.Any = None,
    internal_ip: typing.Any = None,
    internal_port: typing.Any = None,
    target_type: typing.Any = None,
    target_vm_ids: typing.Any = None,
    note: typing.Any = None,
    enabled: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[NatPortForwardingRule]:
    vpc_id = _pid(vpc_id, "vpc_id")
    nat_gateway_id = _pid(nat_gateway_id, "nat_gateway_id")
    rule_id = _pid(port_forwarding_rule_id, "port_forwarding_rule_id")
    body = build_pf_update_body(
        name=name,
        protocol=protocol,
        external_port=external_port,
        internal_ip=internal_ip,
        internal_port=internal_port,
        target_type=target_type,
        target_vm_ids=target_vm_ids,
        note=note,
        enabled=enabled,
    )
    if check_state is not False:
        if body.get("enabled") is True:
            gateways = yield from list_gateways_raw(workspace_id, vpc_id)
            check_gateway_available(gateways, nat_gateway_id)
        if "external_port" in body or "protocol" in body:
            rules = yield from list_rules_raw(workspace_id, vpc_id, nat_gateway_id)
            current = next((r for r in rules if r.get("port_forward_rule_id") == rule_id), {})
            check_pf_duplicate(
                rules,
                body.get("protocol") or str(current.get("protocol") or "tcp").lower(),
                body.get("external_port", current.get("external_port")),
                exclude_rule_id=rule_id,
            )
    path = vpc_path(vpc_id, "nat-gateways", nat_gateway_id, "port-forwarding-rules", rule_id)
    return (
        yield Call("PATCH", path, params=_ws(workspace_id), json=body, parse=NatPortForwardingRule, main=True)
    )


# ---------------------------------------------------------------------------
# Virtual IPs (not yet part of the published API contract)
# ---------------------------------------------------------------------------


def list_vpc_virtual_ips(*, workspace_id: str, vpc_id: str) -> Flow[typing.List[VpcVirtualIp]]:
    vpc_id = _pid(vpc_id, "vpc_id")
    return (
        yield Call("GET", vpc_path(vpc_id, "virtual-ips"), params=_ws(workspace_id), parse=typing.List[VpcVirtualIp], main=True)
    )


def get_vpc_virtual_ip(*, workspace_id: str, vpc_id: str, virtual_ip_id: str) -> Flow[VpcVirtualIp]:
    """There is no single-VIP route: list the VPC's virtual IPs and pick one (404 when absent)."""
    virtual_ip_id = _pid(virtual_ip_id, "virtual_ip_id")
    items = yield from list_vpc_virtual_ips(workspace_id=workspace_id, vpc_id=vpc_id)
    for item in items:
        if item.virtual_ip_id == virtual_ip_id:
            return item
    raise NotFoundError(body={"detail": f"Virtual IP {virtual_ip_id} was not found"})


def create_vpc_virtual_ip(
    *,
    workspace_id: str,
    vpc_id: str,
    subnet_id: typing.Any = None,
    private_ip: typing.Any = None,
    purpose: typing.Any = None,
    announcer_vm_ids: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[VpcVirtualIp]:
    vpc_id = _pid(vpc_id, "vpc_id")
    build_virtual_ip_create_body(subnet_id=subnet_id, private_ip=private_ip, purpose=purpose, announcer_vm_ids=announcer_vm_ids)
    subnet = nodes = None
    if check_state is not False:
        subnet = yield from get_subnet(workspace_id, vpc_id, validate_resource_id(subnet_id, field="subnet_id"))
        nodes = yield from list_nodes_raw(workspace_id, vpc_id)
    body = build_virtual_ip_create_body(
        subnet_id=subnet_id,
        private_ip=private_ip,
        purpose=purpose,
        announcer_vm_ids=announcer_vm_ids,
        subnet=subnet,
        nodes=nodes,
    )
    return (
        yield Call("POST", vpc_path(vpc_id, "virtual-ips"), params=_ws(workspace_id), json=body, parse=VpcVirtualIp, main=True)
    )


def delete_vpc_virtual_ip(
    *, workspace_id: str, vpc_id: str, virtual_ip_id: str, check_state: typing.Optional[bool] = None
) -> Flow[None]:
    vpc_id = _pid(vpc_id, "vpc_id")
    virtual_ip_id = _pid(virtual_ip_id, "virtual_ip_id")
    if check_state is not False:
        vip = yield from get_vpc_virtual_ip(workspace_id=workspace_id, vpc_id=vpc_id, virtual_ip_id=virtual_ip_id)
        check_virtual_ip_deletable(vip)
    yield Call("DELETE", vpc_path(vpc_id, "virtual-ips", virtual_ip_id), params=_ws(workspace_id), parse=None, main=True)
    return None


# ---------------------------------------------------------------------------
# Reserved IPs
# ---------------------------------------------------------------------------


def list_reserved_ips(*, workspace_id: str, site_id: typing.Any = None) -> Flow[typing.List[ReservedIp]]:
    site = validate_optional_site_filter(site_id)
    return (
        yield Call(
            "GET", "networking/reserved-ips", params=_ws(workspace_id, site_id=site), parse=typing.List[ReservedIp], main=True
        )
    )


def reserve_ip(
    *,
    workspace_id: str,
    site_id: typing.Any = None,
    label: typing.Any = None,
    billing_catalog: typing.Any = None,
    check_billing: bool = False,
) -> Flow[ReservedIp]:
    body = build_reserve_ip_body(site_id=site_id, label=label, billing_catalog=billing_catalog)
    if check_billing:
        yield from _preflight(workspace_id, RESERVED_IP_SKU_CODE, "reserved_ip")
    return (
        yield Call("POST", "networking/reserved-ips", params=_ws(workspace_id), json=body, parse=ReservedIp, main=True)
    )


def update_reserved_ip(
    *, workspace_id: str, reserved_ip_id: str, label: typing.Any = None, reverse_dns: typing.Any = None
) -> Flow[ReservedIp]:
    reserved_ip_id = _pid(reserved_ip_id, "reserved_ip_id")
    body = build_reserved_ip_update_body(label=label, reverse_dns=reverse_dns)
    return (
        yield Call("PATCH", reserved_ip_path(reserved_ip_id), params=_ws(workspace_id), json=body, parse=ReservedIp, main=True)
    )


def release_reserved_ip(*, workspace_id: str, reserved_ip_id: str, check_state: typing.Optional[bool] = None) -> Flow[None]:
    reserved_ip_id = _pid(reserved_ip_id, "reserved_ip_id")
    if check_state is not False:
        current = yield from get_reserved_ip_raw(workspace_id, reserved_ip_id)
        check_reserved_ip_releasable(current)
    yield Call("DELETE", reserved_ip_path(reserved_ip_id), params=_ws(workspace_id), parse=None, main=True)
    return None


def _target_call(workspace_id: str, reserved_ip_id: str, action: str, body: typing.Dict[str, typing.Any]) -> Flow[ReservedIp]:
    try:
        return (
            yield Call(
                "POST", reserved_ip_path(reserved_ip_id, action), params=_ws(workspace_id), json=body, parse=ReservedIp, main=True
            )
        )
    except NotFoundError as exc:
        if is_vpc_allocation_required(exc):
            raise as_reserved_ip_target_error(exc) from exc
        raise


def attach_reserved_ip(
    *,
    workspace_id: str,
    reserved_ip_id: str,
    vm_id: typing.Any = None,
    vpc_id: typing.Any = None,
    subnet_id: typing.Any = None,
    detach_from_service: bool = False,
    check_state: typing.Optional[bool] = None,
) -> Flow[ReservedIp]:
    reserved_ip_id = _pid(reserved_ip_id, "reserved_ip_id")
    body = build_reserved_ip_target_body(vm_id=vm_id, vpc_id=vpc_id, subnet_id=subnet_id)
    if check_state is not False or detach_from_service:
        current = yield from get_reserved_ip_raw(workspace_id, reserved_ip_id)
        if check_reserved_ip_attachable(current, detach_from_service=detach_from_service):
            yield Call("POST", reserved_ip_path(reserved_ip_id, "detach"), params=_ws(workspace_id), parse=None)
    return (yield from _target_call(workspace_id, reserved_ip_id, "attach", body))


def move_reserved_ip(
    *,
    workspace_id: str,
    reserved_ip_id: str,
    vm_id: typing.Any = None,
    vpc_id: typing.Any = None,
    subnet_id: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[ReservedIp]:
    reserved_ip_id = _pid(reserved_ip_id, "reserved_ip_id")
    body = build_reserved_ip_target_body(vm_id=vm_id, vpc_id=vpc_id, subnet_id=subnet_id)
    if check_state is not False:
        current = yield from get_reserved_ip_raw(workspace_id, reserved_ip_id)
        check_reserved_ip_movable(current, body["vm_id"])
    return (yield from _target_call(workspace_id, reserved_ip_id, "move", body))


def detach_reserved_ip(*, workspace_id: str, reserved_ip_id: str, check_state: typing.Optional[bool] = None) -> Flow[ReservedIp]:
    reserved_ip_id = _pid(reserved_ip_id, "reserved_ip_id")
    if check_state is not False:
        current = yield from get_reserved_ip_raw(workspace_id, reserved_ip_id)
        if not check_reserved_ip_detachable(current):
            from .core.pydantic_utilities import parse_obj_as

            return typing.cast(ReservedIp, parse_obj_as(type_=ReservedIp, object_=current))  # type: ignore[arg-type]
    return (
        yield Call("POST", reserved_ip_path(reserved_ip_id, "detach"), params=_ws(workspace_id), parse=ReservedIp, main=True)
    )


def convert_vm_public_ip_to_reserved_ip(
    *,
    workspace_id: str,
    vm_id: typing.Any = None,
    site_id: typing.Any = None,
    label: typing.Any = None,
    billing_catalog: typing.Any = None,
    billing_check: bool = True,
) -> Flow[ReservedIp]:
    body: typing.Dict[str, typing.Any] = {
        "vm_id": validate_resource_id(vm_id, field="vm_id"),
        "site_id": validate_reserved_ip_site_id(site_id),
    }
    if _given(label):
        body["label"] = validate_reserved_ip_label(label)
    if _given(billing_catalog):
        body["billing_catalog"] = validate_reserved_ip_billing_catalog(billing_catalog)
    if billing_check:
        yield from _preflight(workspace_id, RESERVED_IP_SKU_CODE, "reserved_ip")
    return (
        yield Call("POST", "networking/reserved-ips/convert", params=_ws(workspace_id), json=body, parse=ReservedIp, main=True)
    )


def attach_reserved_ip_to_virtual_ip(
    *,
    workspace_id: str,
    reserved_ip_id: str,
    virtual_ip_id: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[ReservedIp]:
    reserved_ip_id = _pid(reserved_ip_id, "reserved_ip_id")
    body = {"virtual_ip_id": validate_resource_id(virtual_ip_id, field="virtual_ip_id")}
    if check_state is not False:
        current = yield from get_reserved_ip_raw(workspace_id, reserved_ip_id)
        check_reserved_ip_unattached(current)
    return (
        yield Call(
            "POST", reserved_ip_path(reserved_ip_id, "attach-virtual-ip"), params=_ws(workspace_id), json=body, parse=ReservedIp, main=True
        )
    )


# ---------------------------------------------------------------------------
# Firewalls
# ---------------------------------------------------------------------------


def _summary_page(workspace_id: str, limit: int, offset: int, *, main: bool = False) -> Flow[typing.List[typing.Dict[str, typing.Any]]]:
    data = yield Call(
        "GET", "networking/firewall-groups", params=_ws(workspace_id, summary="true", limit=limit, offset=offset), main=main
    )
    if isinstance(data, dict):  # tolerate a wrapped list
        data = data.get("items") or data.get("firewall_groups") or []
    return _list(data)


def _all_summaries(workspace_id: str, *, main: bool = False) -> Flow[typing.List[typing.Dict[str, typing.Any]]]:
    result: typing.List[typing.Dict[str, typing.Any]] = []
    seen: typing.Set[str] = set()
    offset = 0
    while True:
        page = yield from _summary_page(workspace_id, FIREWALL_PAGE_SIZE, offset, main=main)
        for item in page:
            key = str(item.get("firewall_group_id") or id(item))
            if key not in seen:
                seen.add(key)
                result.append(item)
        if len(page) < FIREWALL_PAGE_SIZE:
            return result
        offset += FIREWALL_PAGE_SIZE


def list_firewall_group_summaries(
    *, workspace_id: str, limit: typing.Any = None, offset: typing.Any = None
) -> Flow[typing.List[FirewallGroupSummary]]:
    from .core.pydantic_utilities import parse_obj_as

    page_limit = validate_limit(limit, maximum=100)
    page_offset = validate_offset(offset)
    if page_limit is None and page_offset is None:
        items = yield from _all_summaries(workspace_id, main=True)
    else:
        items = yield from _summary_page(workspace_id, page_limit or 10, page_offset or 0, main=True)
    return typing.cast(
        typing.List[FirewallGroupSummary], parse_obj_as(type_=typing.List[FirewallGroupSummary], object_=items)  # type: ignore[arg-type]
    )


def create_firewall_group(
    *,
    workspace_id: str,
    name: typing.Any = None,
    description: typing.Any = None,
    is_default: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[FirewallGroup]:
    body = build_firewall_group_body(name=name, description=description, is_default=is_default)
    if check_state is not False:
        groups = yield from _all_summaries(workspace_id)
        check_firewall_name_unique(body["name"], groups)
    return (
        yield Call("POST", "networking/firewall-groups", params=_ws(workspace_id), json=body, parse=FirewallGroup, main=True)
    )


def create_firewall_rule(
    *,
    workspace_id: str,
    firewall_group_id: str,
    description: typing.Any = None,
    direction: typing.Any = None,
    protocol: typing.Any = None,
    port_start: typing.Any = None,
    port_end: typing.Any = None,
    remote_targets: typing.Any = None,
    action: typing.Any = None,
    priority: typing.Any = None,
) -> Flow[FirewallGroup]:
    group_id = _pid(firewall_group_id, "firewall_group_id")
    body = build_firewall_rule_body(
        protocol=protocol,
        port_start=port_start,
        port_end=port_end,
        remote_targets=remote_targets,
        action=action,
        direction=direction,
        description=description,
        priority=priority,
    )
    return (
        yield Call("POST", firewall_path(group_id, "rules"), params=_ws(workspace_id), json=body, parse=FirewallGroup, main=True)
    )


def update_firewall_rule(
    *,
    workspace_id: str,
    firewall_group_id: str,
    firewall_rule_id: str,
    enabled: typing.Any = None,
    description: typing.Any = None,
    direction: typing.Any = None,
    protocol: typing.Any = None,
    port_start: typing.Any = None,
    port_end: typing.Any = None,
    remote_targets: typing.Any = None,
    action: typing.Any = None,
    priority: typing.Any = None,
    check_state: typing.Optional[bool] = None,
) -> Flow[FirewallGroup]:
    group_id = _pid(firewall_group_id, "firewall_group_id")
    rule_id = _pid(firewall_rule_id, "firewall_rule_id")
    body = build_firewall_rule_body(
        update=True,
        protocol=protocol,
        port_start=port_start,
        port_end=port_end,
        remote_targets=remote_targets,
        action=action,
        direction=direction,
        description=description,
        priority=priority,
        enabled=enabled,
    )
    if check_state is not False:
        group = yield Call("GET", firewall_path(group_id), params=_ws(workspace_id))
        check_rule_not_system_managed(group, rule_id)
    return (
        yield Call("PATCH", firewall_path(group_id, "rules", rule_id), params=_ws(workspace_id), json=body, parse=FirewallGroup, main=True)
    )


def delete_firewall_rule(
    *, workspace_id: str, firewall_group_id: str, firewall_rule_id: str, check_state: typing.Optional[bool] = None
) -> Flow[FirewallGroup]:
    group_id = _pid(firewall_group_id, "firewall_group_id")
    rule_id = _pid(firewall_rule_id, "firewall_rule_id")
    if check_state is not False:
        group = yield Call("GET", firewall_path(group_id), params=_ws(workspace_id))
        check_rule_not_system_managed(group, rule_id, deleting=True)
    return (
        yield Call("DELETE", firewall_path(group_id, "rules", rule_id), params=_ws(workspace_id), parse=FirewallGroup, main=True)
    )


def attach_firewall_group(*, workspace_id: str, firewall_group_id: str, vm_id: typing.Any = None) -> Flow[FirewallGroup]:
    group_id = _pid(firewall_group_id, "firewall_group_id")
    body = {"vm_id": _pid(vm_id, "vm_id")}
    return (
        yield Call("POST", firewall_path(group_id, "attachments"), params=_ws(workspace_id), json=body, parse=FirewallGroup, main=True)
    )


# ---------------------------------------------------------------------------
# Load balancers
# ---------------------------------------------------------------------------

LOAD_BALANCER_SKU_CODE = "LOADBALA-STD"


def list_load_balancers(
    *,
    workspace_id: str,
    status: typing.Any = None,
    layer: typing.Any = None,
    protocol: typing.Any = None,
    include_deleted: typing.Any = None,
    limit: typing.Any = None,
    skip: typing.Any = None,
) -> Flow[typing.List[LoadBalancer]]:
    params = validate_lb_list_params(
        status=status, layer=layer, protocol=protocol, include_deleted=include_deleted, limit=limit, skip=skip
    )
    if "include_deleted" in params:
        params["include_deleted"] = "true" if params["include_deleted"] else "false"
    return (
        yield Call("GET", "networking/load-balancers", params=_ws(workspace_id, **params), parse=typing.List[LoadBalancer], main=True)
    )


def get_load_balancer(*, workspace_id: str, load_balancer_id: str, include_deleted: typing.Any = None) -> Flow[LoadBalancer]:
    lb_id = _pid(load_balancer_id, "load_balancer_id")
    params = _ws(workspace_id)
    if include_deleted is not None:
        if not isinstance(include_deleted, bool):
            raise IbeeValidationError("include_deleted must be true or false.", code="invalid_include_deleted", field="include_deleted")
        params["include_deleted"] = "true" if include_deleted else "false"
    return (yield Call("GET", f"networking/load-balancers/{_seg(lb_id)}", params=params, parse=LoadBalancer, main=True))


def create_load_balancer(
    layer: str,
    *,
    workspace_id: str,
    name: typing.Any = None,
    protocol: typing.Any = None,
    backends: typing.Any = None,
    routing: typing.Any = None,
    tls: typing.Any = None,
    policy: typing.Any = None,
    health_check: typing.Any = None,
    observability: typing.Any = None,
    custom_domain: typing.Any = None,
    rules: typing.Any = None,
    check_billing: bool = False,
) -> Flow[LoadBalancer]:
    body = build_lb_body(
        layer=layer,
        name=name,
        protocol=protocol,
        backends=backends,
        routing=routing,
        policy=policy,
        health_check=health_check,
        tls=tls,
        rules=rules,
        custom_domain=custom_domain if custom_domain is not None else ...,
        observability=observability,
    )
    if check_billing:
        yield from _preflight(workspace_id, LOAD_BALANCER_SKU_CODE, "load_balancer")
    return (
        yield Call("POST", f"networking/load-balancers/{layer}", params=_ws(workspace_id), json=body, parse=LoadBalancer, main=True)
    )


def update_load_balancer(
    layer: str,
    *,
    workspace_id: str,
    load_balancer_id: str,
    name: typing.Any = None,
    backends: typing.Any = None,
    routing: typing.Any = None,
    tls: typing.Any = None,
    policy: typing.Any = None,
    health_check: typing.Any = None,
    observability: typing.Any = None,
    custom_domain: typing.Any = ...,
    rules: typing.Any = None,
) -> Flow[LoadBalancer]:
    lb_id = _pid(load_balancer_id, "load_balancer_id")
    body = build_lb_body(
        layer=layer,
        update=True,
        name=name,
        backends=backends,
        routing=routing,
        policy=policy,
        health_check=health_check,
        tls=tls,
        rules=rules,
        custom_domain=custom_domain,
        observability=observability,
    )
    return (
        yield Call("PATCH", f"networking/load-balancers/{layer}/{_seg(lb_id)}", params=_ws(workspace_id), json=body, parse=LoadBalancer, main=True)
    )


__all__ = [
    "LOAD_BALANCER_SKU_CODE",
    "NAT_DELETE_WAIT_ATTEMPTS",
    "NAT_DELETE_WAIT_INTERVAL",
    "UNCONTRACTED",
    "attach_firewall_group",
    "attach_reserved_ip",
    "attach_reserved_ip_to_virtual_ip",
    "attach_vpc_node",
    "convert_vm_public_ip_to_reserved_ip",
    "create_firewall_group",
    "create_firewall_rule",
    "create_load_balancer",
    "create_nat_gateway",
    "create_nat_port_forwarding_rule",
    "create_vpc",
    "create_vpc_subnet",
    "create_vpc_virtual_ip",
    "delete_firewall_rule",
    "delete_nat_gateway",
    "delete_vpc",
    "delete_vpc_virtual_ip",
    "detach_reserved_ip",
    "get_load_balancer",
    "get_vpc_virtual_ip",
    "list_firewall_group_summaries",
    "list_load_balancers",
    "list_networking_sites",
    "list_reserved_ips",
    "list_vpc_virtual_ips",
    "list_vpcs",
    "move_reserved_ip",
    "release_reserved_ip",
    "replace_nat_gateway_public_ip",
    "reserve_ip",
    "update_firewall_rule",
    "update_load_balancer",
    "update_nat_port_forwarding_rule",
    "update_reserved_ip",
    "update_vpc",
    "update_vpc_subnet",
    "wait_for_nat_gateway_absent",
]
