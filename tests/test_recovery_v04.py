"""0.4.0 portal-parity VM recovery (snapshots, backups, restores) and VM-side volumes."""

from __future__ import annotations

import asyncio
import datetime as dt

import pytest

import ibee.operations as operations_module
from _compute_fixtures import ACCEPTED, VM, WS, Router, async_client, async_transport, plan, sync_client, vm
from ibee import IbeeValidationError
from ibee.errors import BillingDeniedError, RecoveryFailedError, RecoveryRestoreFailedError

SNAP_SKU = {"sku_id": 5, "sku_code": "snapshot-std", "product_code": "snapshot_storage"}
BACKUP_SKU = {"sku_id": 6, "sku_code": "BACKUP-STD", "product_code": "backup_storage"}
CREATED = "2026-09-20T18:30:00Z"
MANIFEST = [
    {"source_volume_id": "root-1", "role": "root", "size_gb": 51, "display_size_gb": None},
    {"source_volume_id": "data-1", "role": "data", "source_volume_name": "logs", "size_gb": 20},
]


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(operations_module, "_sleep", lambda seconds: None)

    async def _asleep(seconds: float) -> None:
        return None

    monkeypatch.setattr(operations_module, "_asleep", _asleep)


def _snapshot(status: str = "succeeded", **overrides):
    record = {
        "organization_id": "org",
        "workspace_id": WS,
        "snapshot_set_id": "snap-1",
        "vm_id": VM,
        "vm_name": "web-1",
        "name": "nightly",
        "recovery_point_id": "rp-1",
        "status": status,
        "volume_manifest": MANIFEST,
        "created_at": CREATED,
        "updated_at": CREATED,
    }
    record.update(overrides)
    return record


def _run(status: str = "succeeded", **overrides):
    record = {
        "organization_id": "org",
        "workspace_id": WS,
        "run_id": "run-1",
        "vm_id": VM,
        "recovery_point_id": "rp-9",
        "trigger": "manual",
        "backup_type": "full",
        "status": status,
        "volume_manifest": MANIFEST,
        "created_at": CREATED,
    }
    record.update(overrides)
    return record


POLICY = {
    "organization_id": "org",
    "workspace_id": WS,
    "policy_id": "pol-1",
    "vm_id": VM,
    "enabled": True,
    "schedule": {"frequency": "daily", "hour": 12},
    "retention_days": 7,
    "full_backup_interval_days": 7,
    "incremental_enabled": True,
    "storage_backend": "s3",
    "created_at": CREATED,
    "updated_at": CREATED,
}


def _restore(status: str, **overrides):
    record = {
        "organization_id": "org",
        "workspace_id": WS,
        "restore_id": "restore-1",
        "source_vm_id": VM,
        "target_mode": "new_vm",
        "recovery_point_id": "rp-1",
        "status": status,
    }
    record.update(overrides)
    return record


# snapshots -------------------------------------------------------------------------


def test_snapshot_create_requires_a_valid_sku_and_mode_rules() -> None:
    router = Router()
    client = sync_client(router)
    for kwargs in (
        {"name": "n"},
        {"name": "n", "billing_catalog": {"sku_code": "SNAPSHOT-STD"}},
        {"name": "n", "billing_catalog": {**SNAP_SKU, "product_code": "backup_storage"}},
        {"name": "  ", "billing_catalog": SNAP_SKU},
        {"name": "x" * 256, "billing_catalog": SNAP_SKU},
        {"name": "n", "billing_catalog": SNAP_SKU, "mode": "selective"},
        {"name": "n", "billing_catalog": SNAP_SKU, "mode": "root_only", "selected_data_volume_ids": ["d"]},
        {"name": "n", "billing_catalog": SNAP_SKU, "mode": "everything"},
    ):
        with pytest.raises(IbeeValidationError):
            client.cloud_vms.create_cloud_vm_snapshot(VM, workspace_id=WS, **kwargs)
    assert router.requests == []


def test_snapshot_create_selective_with_state_check_and_preflight() -> None:
    router = Router().add("GET", f"compute/gpu-vms/{VM}", (200, vm(data_volumes=[{"volume_id": "data-1"}])))
    router.add(
        "POST",
        "billing/resource-eligibility",
        (200, {"organization_id": "org", "allowed": True, "reason": "eligible", "sku_code": "SNAPSHOT-STD"}),
    )
    router.add("POST", f"compute/gpu-vms/{VM}/snapshots", (200, _snapshot("queued")))
    sync_client(router).gpu_vms.create_gpu_vm_snapshot(
        VM,
        workspace_id=WS,
        name="n",
        description="   ",
        mode="selective",
        selected_data_volume_ids=[" data-1 ", "data-1", ""],
        billing_catalog=SNAP_SKU,
        preflight_billing=True,
        check_state=True,
    )
    body = router.body("POST", f"compute/gpu-vms/{VM}/snapshots")
    assert body == {
        "name": "n",
        "mode": "selective",
        "selected_data_volume_ids": ["data-1"],
        "billing_catalog": {**SNAP_SKU, "sku_code": "SNAPSHOT-STD", "attached_skus": {}},
    }
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).gpu_vms.create_gpu_vm_snapshot(
            VM, workspace_id=WS, name="n", mode="selective", selected_data_volume_ids=["other"], billing_catalog=SNAP_SKU, check_state=True
        )
    assert info.value.code == "volume_not_attached"


def test_snapshot_preflight_denial() -> None:
    router = Router().add(
        "POST",
        f"compute/cloud-vms/{VM}/snapshots",
        (402, {"error": "billing_denied", "billing_reason": "initial_topup_required", "billing_sku_code": "SNAPSHOT-STD"}),
    )
    with pytest.raises(BillingDeniedError):
        sync_client(router).cloud_vms.create_cloud_vm_snapshot(
            VM, workspace_id=WS, name="n", billing_catalog=SNAP_SKU, preflight_billing=True
        )
    assert router.calls() == [("POST", f"compute/cloud-vms/{VM}/snapshots")]


def test_snapshot_list_limits_and_delete_guard() -> None:
    router = Router().add("GET", "compute/cloud-vm-snapshots/snap-1", (200, _snapshot("restoring")))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.list_cloud_vm_snapshots(VM, workspace_id=WS, limit=201)
    with pytest.raises(IbeeValidationError) as info:
        client.cloud_vms.delete_cloud_vm_snapshot("snap-1", workspace_id=WS, check_state=True)
    assert str(info.value) == "Cannot delete a snapshot while restore is in progress."
    assert router.calls() == [("GET", "compute/cloud-vm-snapshots/snap-1")]


def _snapshot_restore_router(snapshot=None, record=None, plans=None) -> Router:
    router = Router().add("GET", "compute/cloud-vm-snapshots/snap-1", (200, snapshot or _snapshot()))
    router.add("GET", f"compute/cloud-vms/{VM}", (200, record or vm()))
    router.add("GET", "compute/plans", (200, {"plans": plans or [plan(), plan("plan-small", disk_gb=40)]}))
    router.add("POST", "compute/cloud-vm-snapshots/snap-1/actions/restore", (200, _restore("queued")))
    return router


def test_snapshot_restore_new_vm_resolves_plan_and_default_names() -> None:
    router = _snapshot_restore_router()
    sync_client(router).cloud_vms.restore_cloud_vm_snapshot("snap-1", workspace_id=WS, vm_id=VM, target_mode="new_vm")
    request = router.last("POST", "compute/cloud-vm-snapshots/snap-1/actions/restore")
    assert request.url.params["vm_id"] == VM
    body = router.body("POST", "compute/cloud-vm-snapshots/snap-1/actions/restore")
    assert body["target_mode"] == "new_vm"
    assert body["target_vm_name"] == "web-1-snapshot-restored-20260920"
    assert body["target_volume_names"] == {"data-1": "logs-snapshot-restored-20260920"}
    assert (body["target_plan_id"], body["target_cpu"], body["target_ram_mb"], body["target_disk_gb"]) == ("plan-1", 2, 4096, 50)
    assert body["target_plan_hourly_rate"] == 2.5 and body["target_plan_monthly_rate"] == 1500
    assert body["target_billing_catalog"]["sku_code"] == "VM-STD-2-4"
    assert body["target_site_id"] == "site-1"
    assert body["auto_start"] is True
    assert "selected_volume_id" not in body


def test_snapshot_restore_new_vm_rejects_small_plan_and_bad_names() -> None:
    with pytest.raises(IbeeValidationError) as info:
        sync_client(_snapshot_restore_router()).cloud_vms.restore_cloud_vm_snapshot(
            "snap-1", workspace_id=WS, vm_id=VM, target_mode="new_vm", target_plan_id="plan-small"
        )
    assert info.value.code == "restore_disk_too_small"
    assert info.value.details == {"eligible_plan_ids": ["plan-1"]}
    with pytest.raises(IbeeValidationError) as info:
        sync_client(_snapshot_restore_router()).cloud_vms.restore_cloud_vm_snapshot(
            "snap-1", workspace_id=WS, vm_id=VM, target_mode="new_vm", target_volume_names={"root-1": "x"}
        )
    assert info.value.code == "invalid_target_volume_names"
    with pytest.raises(IbeeValidationError):
        sync_client(_snapshot_restore_router(snapshot=_snapshot("running"))).cloud_vms.restore_cloud_vm_snapshot(
            "snap-1", workspace_id=WS, vm_id=VM, target_mode="new_vm"
        )


def test_snapshot_restore_mode_combinations_are_local() -> None:
    router = Router()
    client = sync_client(router)
    for kwargs in (
        {"target_mode": "replace", "target_vm_name": "x"},
        {"target_mode": "replace", "selected_volume_id": "data-1"},
        {"target_mode": "volume_only"},
        {"target_mode": "volume_only", "vpc_id": "vpc-1"},
        {"target_mode": "clone"},
    ):
        with pytest.raises(IbeeValidationError):
            client.cloud_vms.restore_cloud_vm_snapshot("snap-1", workspace_id=WS, vm_id=VM, **kwargs)
    assert router.requests == []


def test_snapshot_restore_volume_only_requires_an_attached_disk() -> None:
    router = _snapshot_restore_router(record=vm(data_volumes=[{"volume_id": "other"}]))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).cloud_vms.restore_cloud_vm_snapshot(
            "snap-1", workspace_id=WS, vm_id=VM, target_mode="volume_only", selected_volume_id="data-1"
        )
    assert info.value.code == "volume_not_attached"
    ok = _snapshot_restore_router(record=vm(data_volumes=[{"volume_id": "data-1"}]))
    sync_client(ok).cloud_vms.restore_cloud_vm_snapshot(
        "snap-1", workspace_id=WS, vm_id=VM, target_mode="volume_only", selected_volume_id="data-1"
    )
    assert ok.body("POST", "compute/cloud-vm-snapshots/snap-1/actions/restore") == {
        "target_mode": "volume_only",
        "selected_volume_id": "data-1",
        "auto_start": True,
    }


def test_snapshot_restore_replace_checks_vm_state() -> None:
    router = _snapshot_restore_router(record=vm(status="resizing"))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).cloud_vms.restore_cloud_vm_snapshot("snap-1", workspace_id=WS, vm_id=VM, check_state=True)
    assert str(info.value) == "Snapshot restore is unavailable while the VM is resizing"
    # The VM state check is opt-in (as in 0.3.0 and the TypeScript SDK): by default the VM is not read.
    default = _snapshot_restore_router(record=vm(status="resizing"))
    sync_client(default).cloud_vms.restore_cloud_vm_snapshot("snap-1", workspace_id=WS, vm_id=VM)
    assert ("GET", f"compute/cloud-vms/{VM}") not in [(r.method, r.url.path.split("/v1/", 1)[-1]) for r in default.requests]


def test_wait_for_restore_success_and_failure() -> None:
    router = Router().add(
        "GET", "compute/cloud-vm-snapshots/restores/restore-1", (200, _restore("running")), (200, _restore("succeeded"))
    )
    result = sync_client(router).cloud_vms.wait_for_cloud_vm_snapshot_restore("restore-1", workspace_id=WS)
    assert result.status == "succeeded" and len(router.requests) == 2
    failed = Router().add("GET", "compute/gpu-vm-backups/restores/restore-1", (200, _restore("failed", error_message="disk full")))
    with pytest.raises(RecoveryRestoreFailedError) as info:
        sync_client(failed).gpu_vms.wait_for_gpu_vm_backup_restore("restore-1", workspace_id=WS)
    assert "disk full" in str(info.value) and info.value.resource_id == "restore-1"


def test_wait_for_snapshot_falls_back_to_the_vm_list_while_capturing() -> None:
    router = Router().add(
        "GET", "compute/cloud-vm-snapshots/snap-1", (404, {"detail": "not found"}), (200, _snapshot("succeeded"))
    )
    router.add("GET", f"compute/cloud-vms/{VM}/snapshots", (200, {"snapshots": [_snapshot("running")], "total": 1}))
    result = sync_client(router).cloud_vms.wait_for_cloud_vm_snapshot("snap-1", workspace_id=WS, vm_id=VM)
    assert result.status == "succeeded"
    assert router.requests[1].url.params["limit"] == "200"
    failed = Router().add("GET", "compute/cloud-vm-backups/runs/run-1", (200, _run("failed")))
    with pytest.raises(RecoveryFailedError):
        sync_client(failed).cloud_vms.wait_for_cloud_vm_backup_run("run-1", workspace_id=WS)


# backups ---------------------------------------------------------------------------


def test_enable_backups_uses_portal_defaults_or_the_saved_policy() -> None:
    router = Router().add("GET", f"compute/cloud-vms/{VM}/backups/policy", (404, {"detail": "Backup policy not found"}))
    router.add("POST", f"compute/cloud-vms/{VM}/backups/enable", (200, POLICY))
    client = sync_client(router)
    client.cloud_vms.enable_cloud_vm_backups(VM, workspace_id=WS, billing_catalog=BACKUP_SKU)
    body = router.body("POST", f"compute/cloud-vms/{VM}/backups/enable")
    assert body["schedule"] == {"frequency": "daily", "hour": 12, "minute": 0, "timezone": "UTC", "window_minutes": 30}
    assert (body["retention_days"], body["full_backup_interval_days"], body["incremental_enabled"]) == (7, 7, True)

    saved_schedule = {"frequency": "weekly", "day_of_week": 2, "hour": 3, "minute": 0, "timezone": "Asia/Kolkata", "window_minutes": 30}
    saved = {"policy_id": "pol-1", "enabled": False, "schedule": saved_schedule, "retention_days": 30,
             "full_backup_interval_days": 5, "incremental_enabled": False}

    def saved_router() -> Router:
        r = Router().add("GET", f"compute/cloud-vms/{VM}/backups/policy", (200, saved))
        return r.add("POST", f"compute/cloud-vms/{VM}/backups/enable", (200, POLICY))

    # Re-enable with nothing passed: the saved policy is re-sent unchanged (portal).
    router2 = saved_router()
    sync_client(router2).cloud_vms.enable_cloud_vm_backups(VM, workspace_id=WS, billing_catalog=BACKUP_SKU)
    body = router2.body("POST", f"compute/cloud-vms/{VM}/backups/enable")
    assert body["schedule"] == saved_schedule
    assert (body["retention_days"], body["full_backup_interval_days"], body["incremental_enabled"]) == (30, 5, False)

    # Any setting passed: the caller's values over the portal defaults (saved values not merged; same as TS).
    router3 = saved_router()
    sync_client(router3).cloud_vms.enable_cloud_vm_backups(VM, workspace_id=WS, billing_catalog=BACKUP_SKU, retention_days=14)
    body = router3.body("POST", f"compute/cloud-vms/{VM}/backups/enable")
    assert body["schedule"] == {"frequency": "daily", "hour": 12, "minute": 0, "timezone": "UTC", "window_minutes": 30}
    assert (body["retention_days"], body["full_backup_interval_days"], body["incremental_enabled"]) == (14, 7, True)

    # A saved 0.3.0 'hourly' policy can still be re-enabled.
    hourly = dict(saved, schedule={"frequency": "hourly", "hour": 0, "minute": 5})
    router4 = Router().add("GET", f"compute/cloud-vms/{VM}/backups/policy", (200, hourly))
    router4.add("POST", f"compute/cloud-vms/{VM}/backups/enable", (200, POLICY))
    sync_client(router4).cloud_vms.enable_cloud_vm_backups(VM, workspace_id=WS, billing_catalog=BACKUP_SKU)
    assert router4.body("POST", f"compute/cloud-vms/{VM}/backups/enable")["schedule"]["frequency"] == "hourly"


def test_update_backup_policy_with_a_saved_hourly_schedule_uses_the_default_frequency() -> None:
    hourly = dict(POLICY, schedule={"frequency": "hourly", "hour": 0, "minute": 5, "timezone": "UTC", "window_minutes": 30})
    router = Router().add("GET", f"compute/gpu-vms/{VM}/backups/policy", (200, hourly))
    router.add("PATCH", f"compute/gpu-vms/{VM}/backups/policy", (200, POLICY))
    sync_client(router).gpu_vms.update_gpu_vm_backup_policy(VM, workspace_id=WS, schedule={"hour": 3})
    schedule = router.body("PATCH", f"compute/gpu-vms/{VM}/backups/policy")["schedule"]
    assert (schedule["frequency"], schedule["hour"], schedule["minute"]) == ("daily", 3, 5)
    assert "day_of_week" not in schedule


def test_backup_enable_and_run_preflight_billing() -> None:
    denied = {"organization_id": "org", "allowed": False, "reason": "initial_topup_required", "sku_code": "BACKUP-STD"}
    for call in ("enable", "run"):
        router = Router().add("GET", f"compute/cloud-vms/{VM}/backups/policy", (404, {"detail": "not found"}))
        mutation = f"compute/cloud-vms/{VM}/backups/" + ("enable" if call == "enable" else "runs")
        router.add("POST", mutation, (402, {"error": "billing_denied", "billing_reason": "initial_topup_required"}))
        client = sync_client(router)
        with pytest.raises(BillingDeniedError):
            if call == "enable":
                client.cloud_vms.enable_cloud_vm_backups(VM, workspace_id=WS, billing_catalog=BACKUP_SKU, preflight_billing=True)
            else:
                client.cloud_vms.create_cloud_vm_backup_run(VM, workspace_id=WS, billing_catalog=BACKUP_SKU, preflight_billing=True)
        assert ("POST", "billing/resource-eligibility") not in router.calls()
        assert ("POST", mutation) in router.calls()

    async def main() -> None:
        router = Router().add(
            "POST", "billing/resource-eligibility", (200, {"organization_id": "org", "allowed": True, "reason": "eligible", "sku_code": "BACKUP-STD"})
        )
        router.add("POST", f"compute/gpu-vms/{VM}/backups/runs", (202, _run("queued")))
        async with async_transport(router) as http:
            await async_client(router, http).gpu_vms.create_gpu_vm_backup_run(
                VM, workspace_id=WS, billing_catalog=BACKUP_SKU, preflight_billing=True
            )
        assert router.calls() == [("POST", f"compute/gpu-vms/{VM}/backups/runs")]

    asyncio.run(main())


def test_backup_schedule_rules_are_local() -> None:
    router = Router()
    client = sync_client(router)
    for schedule in (
        {"frequency": "hourly"},
        {"frequency": "daily", "day_of_week": 3},
        {"hour": 24},
        {"minute": 60},
        {"window_minutes": 4},
        {"timezone": "Mars/Base"},
    ):
        with pytest.raises(IbeeValidationError):
            client.cloud_vms.enable_cloud_vm_backups(VM, workspace_id=WS, schedule=schedule, billing_catalog=BACKUP_SKU)
    for kwargs in ({"retention_days": 0}, {"full_backup_interval_days": 31}, {}):
        with pytest.raises(IbeeValidationError):
            client.cloud_vms.enable_cloud_vm_backups(VM, workspace_id=WS, **({"billing_catalog": BACKUP_SKU} if kwargs else {}), **kwargs)
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.reschedule_cloud_vm_backup(VM, workspace_id=WS, next_run_at=dt.datetime(2026, 10, 1, 2, 30))
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.create_cloud_vm_backup_run(VM, workspace_id=WS, reason="x")
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.update_cloud_vm_backup_policy(VM, workspace_id=WS)
    assert router.requests == []


def test_weekly_schedule_needs_a_day() -> None:
    router = Router().add("GET", f"compute/cloud-vms/{VM}/backups/policy", (404, {"detail": "Backup policy not found"}))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).cloud_vms.enable_cloud_vm_backups(
            VM, workspace_id=WS, schedule={"frequency": "weekly"}, billing_catalog=BACKUP_SKU
        )
    assert info.value.field == "day_of_week"
    assert router.calls() == [("GET", f"compute/cloud-vms/{VM}/backups/policy")]


def test_update_policy_requires_enabled_backups_and_merges_the_schedule() -> None:
    router = Router().add("GET", f"compute/gpu-vms/{VM}/backups/policy", (200, {"enabled": False}))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(router).gpu_vms.update_gpu_vm_backup_policy(VM, workspace_id=WS, retention_days=10)
    assert info.value.code == "backups_disabled"
    saved = {"enabled": True, "schedule": {"frequency": "daily", "hour": 20, "minute": 15, "timezone": "UTC", "window_minutes": 60}}
    router = Router().add("GET", f"compute/gpu-vms/{VM}/backups/policy", (200, saved))
    router.add("PATCH", f"compute/gpu-vms/{VM}/backups/policy", (200, POLICY))
    sync_client(router).gpu_vms.update_gpu_vm_backup_policy(VM, workspace_id=WS, schedule={"hour": 4})
    assert router.body("PATCH", f"compute/gpu-vms/{VM}/backups/policy") == {
        "schedule": {"frequency": "daily", "hour": 4, "minute": 15, "timezone": "UTC", "window_minutes": 60}
    }


def test_workspace_backup_list_and_delete_run() -> None:
    router = Router().add("GET", "compute/cloud-vm-backups/runs", (200, {"runs": [], "total": 0}))
    router.add("GET", "compute/gpu-vm-backups/runs", (200, {"runs": [], "total": 0}))
    router.add("DELETE", "compute/gpu-vm-backups/runs/run-1", (200, {"status": "deleted", "run_id": "run-1"}))
    client = sync_client(router)
    client.cloud_vms.list_all_cloud_vm_backup_runs(workspace_id=WS, status=["succeeded", "failed"], limit=20, search=" ")
    assert router.requests[0].url.params.get_list("status") == ["succeeded", "failed"]
    assert dict(router.requests[0].url.params) | {"status": "x"} == {"workspace_id": WS, "vm_type": "cloud", "limit": "20", "status": "x"}
    client.gpu_vms.list_all_gpu_vm_backup_runs(workspace_id=WS, vm_id=VM)
    assert "vm_type" not in router.requests[1].url.params and router.requests[1].url.params["vm_id"] == VM
    assert client.gpu_vms.delete_gpu_vm_backup_run("run-1", workspace_id=WS) == {"status": "deleted", "run_id": "run-1"}
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.list_all_cloud_vm_backup_runs(workspace_id=WS, status=["done"])


def test_backup_runs_restorable_filter() -> None:
    router = Router().add("GET", f"compute/cloud-vms/{VM}/backups/runs", (200, {"runs": [_run("succeeded"), _run("failed", run_id="run-2")], "total": 2}))
    result = sync_client(router).cloud_vms.list_cloud_vm_backup_runs(VM, workspace_id=WS, restorable_only=True)
    assert [run.run_id for run in result.runs] == ["run-1"]


def test_backup_restore_new_vm_and_readiness() -> None:
    router = Router().add("GET", "compute/cloud-vm-backups/runs/rp-9", (200, _run()))
    router.add("GET", f"compute/cloud-vms/{VM}", (200, vm()))
    router.add("GET", "compute/plans", (200, {"plans": [plan()]}))
    router.add("POST", f"compute/cloud-vms/{VM}/backups/actions/restore", (200, _restore("queued")))
    sync_client(router).cloud_vms.restore_cloud_vm_backup(
        VM, workspace_id=WS, recovery_point_id="rp-9", target_mode="new_vm", target_vm_name=" copy-1 ", auto_start=False
    )
    body = router.body("POST", f"compute/cloud-vms/{VM}/backups/actions/restore")
    assert body["recovery_point_id"] == "rp-9" and body["target_vm_name"] == "copy-1"
    assert body["target_volume_names"] == {"data-1": "logs-backup-restored-20260920"}
    assert "auto_start" not in body and "vpc_id" not in body
    failed = Router().add("GET", "compute/cloud-vm-backups/runs/rp-9", (200, _run("failed")))
    with pytest.raises(IbeeValidationError) as info:
        sync_client(failed).cloud_vms.restore_cloud_vm_backup(VM, workspace_id=WS, recovery_point_id="rp-9")
    assert str(info.value) == "Only successful backups can be restored."


# volumes -----------------------------------------------------------------------------


def _volume(**overrides):
    record = {
        "volume_id": "64b0000000000000000000b1",
        "name": "data",
        "state": "available",
        "site_id": "site-1",
        "site_name": "Chennai",
        "attachments": [],
        "metadata": {"billing_catalog": {"sku_id": 12, "sku_code": "block-std", "product_code": "block_storage"}},
    }
    record.update(overrides)
    return record


def test_attach_reads_the_volume_sku_and_checks_site() -> None:
    router = Router().add("GET", "block-storage/volumes/64b0000000000000000000b1", (200, _volume()))
    router.add("GET", f"compute/cloud-vms/{VM}", (200, vm()))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/attach-volume", (202, ACCEPTED))
    sync_client(router).cloud_vms.attach_cloud_vm_volume(VM, workspace_id=WS, volume_id="64b0000000000000000000b1")
    body = router.body("POST", f"compute/cloud-vms/{VM}/actions/attach-volume")
    assert body == {
        "volume_id": "64b0000000000000000000b1",
        "mode": "single-writer",
        "billing_catalog": {"sku_id": 12, "sku_code": "BLOCK-STD", "product_code": "block_storage", "attached_skus": {}},
    }
    assert router.last("POST", f"compute/cloud-vms/{VM}/actions/attach-volume").headers["x-idempotency-key"]

    for volume, code in (
        (_volume(attachments=[{"vm_id": VM2}]), "volume_attached"),
        (_volume(state="resizing"), "volume_busy"),
        (_volume(site_id="site-9"), "site_mismatch"),
        (_volume(metadata={}), "invalid_billing_catalog"),
    ):
        bad = Router().add("GET", "block-storage/volumes/64b0000000000000000000b1", (200, volume)).add("GET", f"compute/cloud-vms/{VM}", (200, vm()))
        with pytest.raises(IbeeValidationError) as info:
            sync_client(bad).cloud_vms.attach_cloud_vm_volume(VM, workspace_id=WS, volume_id="64b0000000000000000000b1")
        assert info.value.code == code


def test_detach_requires_unmount_confirmation_or_force() -> None:
    router = Router().add("POST", f"compute/gpu-vms/{VM}/actions/detach-volume", (202, ACCEPTED))
    client = sync_client(router)
    with pytest.raises(IbeeValidationError):
        client.gpu_vms.detach_gpu_vm_volume(VM, workspace_id=WS, volume_id="64b0000000000000000000b1")
    client.gpu_vms.detach_gpu_vm_volume(VM, workspace_id=WS, volume_id="64b0000000000000000000b1", force=True)
    assert router.body("POST", f"compute/gpu-vms/{VM}/actions/detach-volume") == {"volume_id": "64b0000000000000000000b1", "force": True}


def test_async_recovery_parity() -> None:
    router = _snapshot_restore_router()
    router.add("GET", "compute/cloud-vm-snapshots/restores/restore-1", (200, _restore("succeeded")))
    router.add("GET", "block-storage/volumes/64b0000000000000000000b1", (200, _volume()))
    router.add("POST", f"compute/cloud-vms/{VM}/actions/attach-volume", (202, ACCEPTED))

    async def run() -> None:
        async with async_transport(router) as http_client:
            client = async_client(router, http_client)
            restore = await client.cloud_vms.restore_cloud_vm_snapshot("snap-1", workspace_id=WS, vm_id=VM, target_mode="new_vm")
            done = await client.cloud_vms.wait_for_cloud_vm_snapshot_restore(restore.restore_id, workspace_id=WS)
            assert done.status == "succeeded"
            await client.cloud_vms.attach_cloud_vm_volume(VM, workspace_id=WS, volume_id="64b0000000000000000000b1")
            with pytest.raises(IbeeValidationError):
                await client.cloud_vms.create_cloud_vm_snapshot(VM, workspace_id=WS, name="n")

    asyncio.run(run())
    assert router.body("POST", "compute/cloud-vm-snapshots/snap-1/actions/restore")["target_vm_name"] == "web-1-snapshot-restored-20260920"
    assert router.body("POST", f"compute/cloud-vms/{VM}/actions/attach-volume")["billing_catalog"]["sku_code"] == "BLOCK-STD"


VM2 = "0123456789abcdef01234568"
