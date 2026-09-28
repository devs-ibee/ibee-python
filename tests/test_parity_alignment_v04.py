"""0.4.0 cross-client alignment with the TypeScript SDK (payment walls, backup restore, VPC delete,
CDN origin read, access pre-read and the canonical error codes)."""

from __future__ import annotations

import asyncio

import pytest

from _compute_fixtures import ACCEPTED, VM, WS, Router, async_client, async_transport, sync_client, vm
from ibee import IbeeValidationError
from ibee.errors import (
    IbeeError,
    OperationFailedError,
    error_from_response,
    is_payment_block_error,
)
from ibee.validation import (
    build_cdn_distribution_update_body,
    build_lb_body,
    build_node_attach_body,
    build_scope_update_body,
    build_store_update_body,
    resolve_backup_recovery_point_id,
)

V = "networking/vpcs/vpc-1"
RUNS = "compute/cloud-vm-backups/runs"
RESTORE = f"compute/cloud-vms/{VM}/backups/actions/restore"
RESTORE_RECORD = {
    "organization_id": "org",
    "workspace_id": WS,
    "restore_id": "restore-1",
    "source_vm_id": VM,
    "target_mode": "replace",
    "recovery_point_id": "rp-7",
    "status": "queued",
}


# 1. payment walls ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "error",
    [
        error_from_response(402, {"detail": "x"}),
        error_from_response(400, {"error": {"code": "INSUFFICIENT_FUNDS", "message": "x"}}),
        error_from_response(403, {"error": "forbidden", "billing_reason": "credit_limit_exceeded"}),
        error_from_response(409, {"detail": {"code": "conflict", "reason": "initial_topup_required"}}),
        error_from_response(403, {"detail": "Insufficient balance for this plan"}),
        error_from_response(400, {"detail": "Please top up your wallet"}),
        OperationFailedError({"status": "failed", "error_code": "insufficient_balance"}),
        {"code": "INSUFFICIENT_FUNDS"},
        {"status": 402},
        Exception("Add a payment method to continue"),
    ],
)
def test_payment_block_structured_first(error) -> None:
    assert is_payment_block_error(error)


@pytest.mark.parametrize(
    "error",
    [
        error_from_response(403, {"error": "insufficient_scope", "required_scope": "billing.read"}),
        {"code": "insufficient_scope", "message": "insufficient balance"},
        # A body with its own code is authoritative: no text heuristic.
        error_from_response(400, {"error": {"code": "quota_exceeded", "message": "payment required for more"}}),
        error_from_response(422, {"detail": [{"loc": ["body", "x"], "msg": "insufficient balance"}]}),
        # No bare "insufficient"/"balance" matches.
        error_from_response(409, {"detail": "Insufficient capacity in this site"}),
        error_from_response(400, {"detail": "load balancer not found"}),
        Exception("insufficient permissions"),
        error_from_response(502, {}),
        ValueError("nope"),
        None,
    ],
)
def test_payment_block_conservative_fallback(error) -> None:
    assert not is_payment_block_error(error)


# 2. backup restore resolves the recovery point ------------------------------------------


@pytest.mark.parametrize(
    "run, expected",
    [
        ({"recovery_point_id": " rp-1 "}, "rp-1"),
        ({"metadata": {"recovery_point_id": "rp-2"}}, "rp-2"),
        ({"metadata": {"recoveryPointId": "rp-3"}}, "rp-3"),
        ({"r2_prefix": "backups/org/vm/recovery-points/rp-4/"}, "rp-4"),
        ({"r2_prefix": "backups/org/vm/rp-5"}, "rp-5"),
        ({"metadata": {"r2_manifest_key": "x/recovery-points/rp-6/manifest.json"}}, "rp-6"),
        ({"metadata": {"r2_prefix": "x/recovery-points/rp-7"}}, "rp-7"),
    ],
)
def test_resolve_backup_recovery_point_id_follows_the_portal(run, expected) -> None:
    assert resolve_backup_recovery_point_id(run) == expected


def test_resolve_backup_recovery_point_id_missing() -> None:
    with pytest.raises(IbeeValidationError, match="missing recovery point id") as info:
        resolve_backup_recovery_point_id({"run_id": "run-1", "metadata": {"r2_prefix": "backups/x"}})
    assert info.value.code == "recovery_point_not_ready" and info.value.field == "recovery_point_id"


def test_restore_backup_sends_the_resolved_recovery_point_even_without_check_state() -> None:
    router = Router().add("GET", f"{RUNS}/run-1", (200, {"run_id": "run-1", "status": "succeeded", "metadata": {"recovery_point_id": "rp-7"}}))
    router.add("POST", RESTORE, (200, RESTORE_RECORD))
    sync_client(router).cloud_vms.restore_cloud_vm_backup(VM, workspace_id=WS, recovery_point_id="run-1", check_state=False)
    assert router.calls()[0] == ("GET", f"{RUNS}/run-1")
    assert router.body("POST", RESTORE) == {"recovery_point_id": "rp-7", "target_mode": "replace"}


def test_restore_backup_checks_success_before_the_recovery_point() -> None:
    failed = Router().add("GET", f"{RUNS}/run-1", (200, {"run_id": "run-1", "status": "failed"}))
    with pytest.raises(IbeeValidationError, match="Only successful backups"):
        sync_client(failed).cloud_vms.restore_cloud_vm_backup(VM, workspace_id=WS, recovery_point_id="run-1")
    missing = Router().add("GET", f"{RUNS}/run-1", (200, {"run_id": "run-1", "status": "succeeded"}))
    with pytest.raises(IbeeValidationError, match="missing recovery point id"):
        sync_client(missing).cloud_vms.restore_cloud_vm_backup(VM, workspace_id=WS, recovery_point_id="run-1")
    assert ("POST", RESTORE) not in missing.calls()


def test_restore_backup_async() -> None:
    router = Router().add("GET", f"{RUNS}/rp-7", (200, {"run_id": "run-1", "status": "succeeded", "recovery_point_id": "rp-7"}))
    router.add("POST", RESTORE, (200, RESTORE_RECORD))

    async def run() -> None:
        async with async_transport(router) as http_client:
            await async_client(router, http_client).cloud_vms.restore_cloud_vm_backup(VM, workspace_id=WS, recovery_point_id="rp-7")

    asyncio.run(run())
    assert router.body("POST", RESTORE)["recovery_point_id"] == "rp-7"


# 3 + 5. VPC delete dependency checks ---------------------------------------------------


def _vpc(**overrides):
    record = {"vpc_id": "vpc-1", "site_id": "site-1", "cidr": "10.20.0.0/24", "status": "available",
              "connectivity_type": "nat_gateway", "node_count": 0, "nat_gateways": []}
    record.update(overrides)
    return record


def test_delete_vpc_refuses_with_virtual_ips_by_default() -> None:
    router = Router().add("GET", V, (200, _vpc())).add("GET", f"{V}/virtual-ips", (200, [{"virtual_ip_id": "vip-1"}]))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).vpcs.delete_vpc("vpc-1", workspace_id=WS)
    assert info.value.code == "vpc_has_virtual_ips"
    assert ("DELETE", V) not in router.calls()


def test_delete_vpc_virtual_ip_check_skips_without_read_scope_unless_required() -> None:
    router = Router().add("GET", V, (200, _vpc())).add("GET", f"{V}/virtual-ips", (403, {"error": "insufficient_scope"}))
    router.add("DELETE", V, (204, None))
    sync_client(router).vpcs.delete_vpc("vpc-1", workspace_id=WS)
    assert router.calls()[-1] == ("DELETE", V)
    strict = Router().add("GET", V, (200, _vpc())).add("GET", f"{V}/virtual-ips", (403, {"error": "insufficient_scope"}))
    with pytest.raises(Exception) as info:
        sync_client(strict).vpcs.delete_vpc("vpc-1", workspace_id=WS, check_state=True)
    assert getattr(info.value, "status_code", None) == 403


def test_delete_vpc_checks_virtual_ips_before_deleting_the_nat_gateway() -> None:
    gateway = {"nat_gateway_id": "nat-1", "status": "available", "public_ip_source": "automatic"}
    router = Router().add("GET", V, (200, _vpc(nat_gateways=[gateway])))
    router.add("GET", f"{V}/virtual-ips", (200, [{"virtual_ip_id": "vip-1"}]))
    with pytest.raises(IbeeValidationError, match="virtual IP"):
        sync_client(router).vpcs.delete_vpc("vpc-1", workspace_id=WS, delete_nat_gateway=True, check_state=False)
    assert ("DELETE", f"{V}/nat-gateways/nat-1") not in router.calls()


def test_delete_vpc_check_state_false_is_a_plain_delete() -> None:
    router = Router().add("DELETE", V, (204, None))
    sync_client(router).vpcs.delete_vpc("vpc-1", workspace_id=WS, check_state=False)
    assert router.calls() == [("DELETE", V)]


# 4. CDN origin read ---------------------------------------------------------------------


@pytest.mark.parametrize("status", [403, 404])
def test_cdn_origin_read_is_best_effort(status: int) -> None:
    router = Router().add("GET", "object-storage/buckets/assets", (status, {"error": "insufficient_scope"} if status == 403 else {"detail": "Bucket not found"}))
    router.add("POST", "cdn/distributions", (201, {"id": "d1"}))
    assert sync_client(router).cdn.create_cdn_distribution(
        workspace_id=WS, name="site", origin_id="assets", check_origin_public=True
    ) == {"id": "d1"}


# 6. access pre-read ---------------------------------------------------------------------


def test_access_update_reads_the_vm_by_default_and_can_opt_out() -> None:
    path = f"compute/gpu-vms/{VM}"
    router = Router().add("GET", path, (200, vm(os_type="windows")))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).gpu_vms.update_gpu_vm_access(VM, workspace_id=WS, new_password="Password-1")
    assert info.value.code == "vm_not_linux"
    opted_out = Router().add("PATCH", f"{path}/actions/access", (202, ACCEPTED))
    sync_client(opted_out).gpu_vms.update_gpu_vm_access(VM, workspace_id=WS, new_password="Password-1", check_state=False)
    assert opted_out.calls() == [("PATCH", f"{path}/actions/access")]


# 8. canonical codes ---------------------------------------------------------------------


def test_nothing_to_update_is_no_changes_everywhere() -> None:
    for build in (
        lambda: build_store_update_body(),
        lambda: build_scope_update_body(),
        lambda: build_cdn_distribution_update_body(),
    ):
        with pytest.raises(IbeeValidationError) as info:
            build()
        assert info.value.code == "no_changes"


def test_reserved_ip_codes_and_l4_field_codes() -> None:
    with pytest.raises(IbeeValidationError) as info:
        build_node_attach_body(vm_id=VM, subnet_id="subnet-1", connectivity="public_ip", vpc={"connectivity_type": "private"})
    assert (info.value.code, info.value.field) == ("reserved_ip_required", "reserved_public_ip_id")
    backends = [{"target": "svc", "port": 80}]
    with pytest.raises(IbeeValidationError) as info:
        build_lb_body(layer="l4", name="n", protocol="tcp", backends=backends, rules=[])
    assert (info.value.code, info.value.field) == ("invalid_rules", "rules")
    with pytest.raises(IbeeValidationError) as info:
        build_lb_body(layer="l4", name="n", protocol="tcp", backends=backends, custom_domain="a.example.com")
    assert (info.value.code, info.value.field) == ("invalid_custom_domain", "custom_domain")


def test_nat_gateway_deleting_is_not_a_validation_error() -> None:
    error = IbeeError("x", code="nat_gateway_deleting")
    assert not isinstance(error, (IbeeValidationError, ValueError))
