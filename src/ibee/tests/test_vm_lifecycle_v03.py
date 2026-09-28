from __future__ import annotations

import asyncio
import datetime as dt
import json
from dataclasses import dataclass, field
from typing import Any

import httpx
import pytest

from ibee import AsyncIbee, Ibee
from ibee.errors import UnauthorizedError


WORKSPACE_ID = "710995"


@dataclass(frozen=True)
class OperationCase:
    resource: str
    method_name: str
    http_method: str
    path: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    query: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] | None = None
    idempotency_key: str | None = None
    # (method, path) -> (status, json) for read-only pre-steps the SDK runs first (0.4.0).
    presteps: dict[tuple[str, str], tuple[int, Any]] = field(default_factory=dict)


SKU = {"sku_id": 5, "sku_code": "SNAPSHOT-STD"}
BACKUP_SKU = {"sku_id": 6, "sku_code": "BACKUP-STD"}
BLOCK_SKU = {"sku_id": 7, "sku_code": "BLOCK-STD"}
VM_IDS = {"cloud": "0123456789abcdef0123456a", "gpu": "0123456789abcdef0123456b"}


def _vm_cases(family: str) -> list[OperationCase]:
    resource = f"{family}_vms"
    method_prefix = f"{family}_vm"
    collection = f"/v1/compute/{family}-vms"
    snapshot_collection = f"/v1/compute/{family}-vm-snapshots"
    backup_collection = f"/v1/compute/{family}-vm-backups"
    vm_id = VM_IDS[family]
    vm_path = f"{collection}/{vm_id}"

    def case(
        method_name: str,
        http_method: str,
        path: str,
        *,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        presteps: dict[tuple[str, str], tuple[int, Any]] | None = None,
    ) -> OperationCase:
        return OperationCase(
            resource=resource,
            method_name=method_name,
            http_method=http_method,
            path=path,
            args=args,
            kwargs={"workspace_id": WORKSPACE_ID, **(kwargs or {})},
            query={"workspace_id": WORKSPACE_ID, **(query or {})},
            body=body,
            idempotency_key=idempotency_key,
            presteps=presteps or {},
        )

    return [
        case(
            f"update_{method_prefix}_access",
            "PATCH",
            f"{vm_path}/actions/access",
            args=(vm_id,),
            kwargs={"idempotency_key": f"{family}-access-1", "new_password": "example-only-password", "check_state": False},
            body={"new_password": "example-only-password"},
            idempotency_key=f"{family}-access-1",
        ),
        case(
            f"precheck_{method_prefix}_resize",
            "POST",
            f"{vm_path}/actions/resize/precheck",
            args=(vm_id,),
            kwargs={"cpu": 4},
            body={"cpu": 4},
        ),
        case(
            f"resize_{method_prefix}",
            "POST",
            f"{vm_path}/actions/resize",
            args=(vm_id,),
            kwargs={"idempotency_key": f"{family}-resize-1", "cpu": 4, "check_state": False},
            body={"cpu": 4},
            presteps={("POST", f"{vm_path}/actions/resize/precheck"): (200, {"decision": "in_place"})},
            idempotency_key=f"{family}-resize-1",
        ),
        case(
            f"resize_{method_prefix}_plan",
            "PATCH",
            f"{vm_path}/actions/resize-plan",
            args=(vm_id,),
            kwargs={"idempotency_key": f"{family}-plan-1", "cpu": 4, "ram_mb": 8192, "check_state": False},
            body={"cpu": 4, "ram_mb": 8192},
            idempotency_key=f"{family}-plan-1",
        ),
        case(
            f"resize_{method_prefix}_root_disk",
            "PATCH",
            f"{vm_path}/actions/resize-root-disk",
            args=(vm_id,),
            kwargs={"idempotency_key": f"{family}-disk-1", "new_size_gb": 160, "check_state": False},
            body={"new_size_gb": 160},
            idempotency_key=f"{family}-disk-1",
        ),
        case(
            f"attach_{method_prefix}_volume",
            "POST",
            f"{vm_path}/actions/attach-volume",
            args=(vm_id,),
            kwargs={"idempotency_key": f"{family}-attach-1", "volume_id": "volume-1", "billing_catalog": BLOCK_SKU, "check_state": False},
            body={"volume_id": "volume-1", "mode": "single-writer", "billing_catalog": {**BLOCK_SKU, "attached_skus": {}}},
            idempotency_key=f"{family}-attach-1",
        ),
        case(
            f"detach_{method_prefix}_volume",
            "POST",
            f"{vm_path}/actions/detach-volume",
            args=(vm_id,),
            kwargs={"idempotency_key": f"{family}-detach-1", "volume_id": "volume-1", "confirm_unmounted": True},
            body={"volume_id": "volume-1", "confirm_unmounted": True},
            idempotency_key=f"{family}-detach-1",
        ),
        case(
            f"acknowledge_{method_prefix}_mount_guidance",
            "POST",
            f"{vm_path}/mount-guidance/acknowledge",
            args=(vm_id,),
            kwargs={"volume_id": "volume-1"},
            body={"volume_id": "volume-1"},
        ),
        case(
            f"list_{method_prefix}_events",
            "GET",
            f"{vm_path}/events",
            args=(vm_id,),
            kwargs={"limit": 25},
            query={"limit": "25"},
        ),
        case(
            f"get_{method_prefix}_metrics_timeseries",
            "GET",
            f"{vm_path}/metrics/timeseries",
            args=(vm_id,),
            kwargs={"range": "24h"},
            query={"range": "24h"},
        ),
        case(
            f"get_{method_prefix}_bandwidth",
            "GET",
            f"{vm_path}/metrics/bandwidth",
            args=(vm_id,),
            kwargs={"month": "2026-08"},
            query={"month": "2026-08"},
        ),
        case(
            f"list_{method_prefix}_snapshots",
            "GET",
            f"{vm_path}/snapshots",
            args=(vm_id,),
            kwargs={"limit": 20, "offset": 5, "search": "nightly"},
            query={"limit": "20", "offset": "5", "search": "nightly"},
        ),
        case(
            f"create_{method_prefix}_snapshot",
            "POST",
            f"{vm_path}/snapshots",
            args=(vm_id,),
            kwargs={"name": " before-upgrade ", "mode": "root_only", "billing_catalog": SKU},
            body={
                "name": "before-upgrade",
                "mode": "root_only",
                "selected_data_volume_ids": [],
                "billing_catalog": {**SKU, "attached_skus": {}},
            },
        ),
        case(
            f"restore_{method_prefix}_snapshot",
            "POST",
            f"{snapshot_collection}/snapshot-1/actions/restore",
            args=("snapshot-1",),
            kwargs={"vm_id": vm_id, "target_mode": "replace", "check_state": False},
            query={"vm_id": vm_id},
            body={"target_mode": "replace", "auto_start": True},
        ),
        case(
            f"get_{method_prefix}_snapshot",
            "GET",
            f"{snapshot_collection}/snapshot-1",
            args=("snapshot-1",),
        ),
        case(
            f"delete_{method_prefix}_snapshot",
            "DELETE",
            f"{snapshot_collection}/snapshot-1",
            args=("snapshot-1",),
        ),
        case(
            f"get_{method_prefix}_snapshot_restore",
            "GET",
            f"{snapshot_collection}/restores/restore-1",
            args=("restore-1",),
        ),
        case(
            f"get_{method_prefix}_backup_policy",
            "GET",
            f"{vm_path}/backups/policy",
            args=(vm_id,),
        ),
        case(
            f"update_{method_prefix}_backup_policy",
            "PATCH",
            f"{vm_path}/backups/policy",
            args=(vm_id,),
            kwargs={"retention_days": 14, "check_state": False},
            body={"retention_days": 14},
        ),
        case(
            f"enable_{method_prefix}_backups",
            "POST",
            f"{vm_path}/backups/enable",
            args=(vm_id,),
            kwargs={"retention_days": 14, "billing_catalog": BACKUP_SKU},
            body={
                "schedule": {"frequency": "daily", "hour": 12, "minute": 0, "timezone": "UTC", "window_minutes": 30},
                "retention_days": 14,
                "full_backup_interval_days": 7,
                "incremental_enabled": True,
                "billing_catalog": {**BACKUP_SKU, "attached_skus": {}},
            },
            presteps={("GET", f"{vm_path}/backups/policy"): (404, {"detail": "Backup policy not found"})},
        ),
        case(
            f"disable_{method_prefix}_backups",
            "POST",
            f"{vm_path}/backups/disable",
            args=(vm_id,),
            kwargs={"requested_by": "user-1"},
            body={"requested_by": "user-1"},
        ),
        case(
            f"reschedule_{method_prefix}_backup",
            "PATCH",
            f"{vm_path}/backups/policy/next-run-at",
            args=(vm_id,),
            kwargs={"next_run_at": dt.datetime(2026, 8, 10, 2, 30, tzinfo=dt.timezone.utc)},
            body={"next_run_at": "2026-08-10T02:30:00Z"},
        ),
        case(
            f"list_{method_prefix}_backup_runs",
            "GET",
            f"{vm_path}/backups/runs",
            args=(vm_id,),
            kwargs={"limit": 20, "offset": 5, "search": "manual"},
            query={"limit": "20", "offset": "5", "search": "manual"},
        ),
        case(
            f"create_{method_prefix}_backup_run",
            "POST",
            f"{vm_path}/backups/runs",
            args=(vm_id,),
            kwargs={"reason": "before-upgrade", "billing_catalog": BACKUP_SKU},
            body={"reason": "before-upgrade", "billing_catalog": {**BACKUP_SKU, "attached_skus": {}}},
        ),
        case(
            f"restore_{method_prefix}_backup",
            "POST",
            f"{vm_path}/backups/actions/restore",
            args=(vm_id,),
            kwargs={"recovery_point_id": "recovery-point-1", "target_mode": "replace", "check_state": False},
            body={"recovery_point_id": "recovery-point-1", "target_mode": "replace"},
        ),
        case(
            f"get_{method_prefix}_backup_run",
            "GET",
            f"{backup_collection}/runs/run-1",
            args=("run-1",),
        ),
        case(
            f"get_{method_prefix}_backup_restore",
            "GET",
            f"{backup_collection}/restores/restore-1",
            args=("restore-1",),
        ),
    ]


CASES = [
    *_vm_cases("cloud"),
    *_vm_cases("gpu"),
    OperationCase(
        resource="vm_console",
        method_name="create_vm_console_session",
        http_method="POST",
        path="/v1/compute/console/sessions",
        kwargs={"workspace_id": WORKSPACE_ID, "vm_id": VM_IDS["cloud"], "vm_type": "cloud"},
        query={"workspace_id": WORKSPACE_ID},
        body={"vm_id": VM_IDS["cloud"], "vm_type": "cloud"},
    ),
    OperationCase(
        resource="vm_console",
        method_name="get_vm_console_session",
        http_method="GET",
        path="/v1/compute/console/sessions/session-1",
        args=("session-1",),
        kwargs={"workspace_id": WORKSPACE_ID},
        query={"workspace_id": WORKSPACE_ID},
    ),
    OperationCase(
        resource="vm_console",
        method_name="close_vm_console_session",
        http_method="DELETE",
        path="/v1/compute/console/sessions/session-1",
        args=("session-1",),
        kwargs={"workspace_id": WORKSPACE_ID, "reason": "finished"},
        query={"workspace_id": WORKSPACE_ID, "reason": "finished"},
    ),
]


def _assert_request(case: OperationCase, request: httpx.Request) -> None:
    assert request.method == case.http_method
    assert request.url.path == case.path
    assert dict(request.url.params) == case.query
    assert request.headers["authorization"] == "Bearer test-token"
    if case.body is None:
        assert request.content == b""
    else:
        assert json.loads(request.content) == case.body
        assert request.headers["content-type"] == "application/json"
    if case.idempotency_key is None:
        assert "x-idempotency-key" not in request.headers
    else:
        assert request.headers["x-idempotency-key"] == case.idempotency_key


def _unauthorized(request: httpx.Request) -> httpx.Response:
    return httpx.Response(401, json={"detail": "unauthorized"}, request=request)


def test_lifecycle_matrix_is_complete_and_has_unique_client_methods() -> None:
    assert len(CASES) == 57
    assert len({(case.resource, case.method_name) for case in CASES}) == 57


def _handler(case: OperationCase, observed: list[httpx.Request]):
    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        prestep = case.presteps.get((request.method, request.url.path))
        if prestep is not None:
            status, body = prestep
            return httpx.Response(status, json=body, request=request)
        return _unauthorized(request)

    return handler


def _check(case: OperationCase, observed: list[httpx.Request]) -> None:
    assert len(observed) == 1 + len(case.presteps)
    assert [(request.method, request.url.path) for request in observed[:-1]] == list(case.presteps)
    _assert_request(case, observed[-1])


@pytest.mark.parametrize("case", CASES, ids=lambda case: f"{case.resource}.{case.method_name}")
def test_sync_vm_lifecycle_request_contract(case: OperationCase) -> None:
    observed: list[httpx.Request] = []
    client = Ibee(
        token="test-token",
        base_url="https://api.example.test/v1",
        httpx_client=httpx.Client(transport=httpx.MockTransport(_handler(case, observed))),
    )
    method = getattr(getattr(client, case.resource), case.method_name)

    with pytest.raises(UnauthorizedError):
        method(*case.args, **case.kwargs)

    _check(case, observed)


@pytest.mark.parametrize("case", CASES, ids=lambda case: f"{case.resource}.{case.method_name}")
def test_async_vm_lifecycle_request_contract(case: OperationCase) -> None:
    observed: list[httpx.Request] = []

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(_handler(case, observed))) as http_client:
            client = AsyncIbee(
                token="test-token",
                base_url="https://api.example.test/v1",
                httpx_client=http_client,
            )
            method = getattr(getattr(client, case.resource), case.method_name)
            with pytest.raises(UnauthorizedError):
                await method(*case.args, **case.kwargs)

    asyncio.run(run())

    _check(case, observed)
