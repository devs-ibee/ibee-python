"""0.4.0 operation wait helpers and auto-paging lists."""

from __future__ import annotations

import asyncio
import typing

import httpx
import pytest

import ibee.core.http_client as http_client_module
import ibee.operations as operations_module
from ibee import AsyncIbee, Ibee, IbeeValidationError, wait_for_compute_operation
from ibee.errors import NotFoundError, OperationFailedError, OperationTimeoutError, ServiceUnavailableError
from ibee.operations import poll_until
from ibee.pagination import paginate_pages

BASE = "https://api.example.test/v1"
WS = "710995"


class FakeTime:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: typing.List[float] = []

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds

    async def asleep(self, seconds: float) -> None:
        self.sleep(seconds)


@pytest.fixture(autouse=True)
def fake_time(monkeypatch: pytest.MonkeyPatch) -> FakeTime:
    fake = FakeTime()
    monkeypatch.setattr(operations_module, "_sleep", fake.sleep)
    monkeypatch.setattr(operations_module, "_asleep", fake.asleep)
    monkeypatch.setattr(operations_module, "_clock", fake.clock)
    monkeypatch.setattr(http_client_module, "retry_delay", lambda attempt, headers=None: 0.0)
    return fake


def _op(status: str, **extra: object) -> dict:
    return {
        "operation_id": "op-1",
        "vm_id": "vm-1",
        "action": "start",
        "status": status,
        "submitted_at": "2026-08-04T10:00:00Z",
        "updated_at": "2026-08-04T10:00:01Z",
        **extra,
    }


def _ops_client(*responses, max_retries: int = 0) -> typing.Tuple[Ibee, list]:
    observed: list[httpx.Request] = []
    queue = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, Exception):
            raise item
        status, body = item
        return httpx.Response(status, json=body, request=request)

    client = Ibee(
        token="t",
        base_url=BASE,
        max_retries=max_retries,
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    return client, observed


# waiting ---------------------------------------------------------------------


def test_wait_polls_until_succeeded(fake_time: FakeTime) -> None:
    client, observed = _ops_client((200, _op("accepted")), (200, _op("running")), (200, _op("succeeded")))
    updates: list = []
    result = client.cloud_vms.wait_for_compute_operation(
        " op-1 ", workspace_id=WS, poll_interval=2, on_update=updates.append
    )
    assert result.status == "succeeded"
    assert [u.status for u in updates] == ["accepted", "running", "succeeded"]
    assert fake_time.sleeps == [2.0, 2.0]
    assert all(request.url.path == "/v1/compute/operations/op-1" for request in observed)


def test_completed_is_a_legacy_success_alias() -> None:
    client, _ = _ops_client((200, _op("COMPLETED")))
    assert wait_for_compute_operation(client, "op-1", workspace_id=WS).status == "COMPLETED"


@pytest.mark.parametrize("status", ["failed", "cancelled", "timed_out"])
def test_terminal_failures_raise_or_return(status: str) -> None:
    client, _ = _ops_client((200, _op(status, error_code="E_CAPACITY", error_message="no capacity")))
    with pytest.raises(OperationFailedError) as info:
        client.gpu_vms.wait_for_compute_operation("op-1", workspace_id=WS)
    error = info.value
    assert (error.operation_id, error.vm_id, error.status, error.error_code) == ("op-1", "vm-1", status, "E_CAPACITY")
    assert error.code == "operation_failed"
    assert str(error) == f"start {status} for vm-1: E_CAPACITY: no capacity (operation op-1)"
    returned = client.gpu_vms.wait_for_compute_operation("op-1", workspace_id=WS, raise_on_failure=False)
    assert returned.status == status


def test_wait_times_out_on_the_client_deadline(fake_time: FakeTime) -> None:
    client, observed = _ops_client((200, _op("waiting")))
    with pytest.raises(OperationTimeoutError) as info:
        client.cloud_vms.wait_for_compute_operation("op-1", workspace_id=WS, timeout=12, poll_interval=5)
    assert isinstance(info.value, TimeoutError)
    assert info.value.last_status == "waiting"
    assert info.value.timeout == 12
    assert info.value.code == "operation_wait_timeout"
    assert fake_time.sleeps == [5.0, 5.0, 2.0]
    assert len(observed) == 4


def test_two_transient_failures_are_tolerated_and_the_third_raises() -> None:
    client, observed = _ops_client((503, {}), (502, {}), (200, _op("succeeded")))
    assert client.cloud_vms.wait_for_compute_operation("op-1", workspace_id=WS).status == "succeeded"
    assert len(observed) == 3

    client, observed = _ops_client((503, {}), httpx.ConnectError("down"), (504, {}), (200, _op("succeeded")))
    with pytest.raises(Exception) as info:
        client.cloud_vms.wait_for_compute_operation("op-1", workspace_id=WS)
    assert getattr(info.value, "status_code", None) == 504
    assert len(observed) == 3


def test_successful_poll_resets_failure_count() -> None:
    client, observed = _ops_client(
        (503, {}), (503, {}), (200, _op("running")), (503, {}), (503, {}), (200, _op("succeeded"))
    )
    assert client.cloud_vms.wait_for_compute_operation("op-1", workspace_id=WS).status == "succeeded"
    assert len(observed) == 6


def test_not_found_aborts_immediately() -> None:
    client, observed = _ops_client((404, {"detail": "Operation not found"}))
    with pytest.raises(NotFoundError):
        client.cloud_vms.wait_for_compute_operation("op-1", workspace_id=WS)
    assert len(observed) == 1


@pytest.mark.parametrize(
    ("kwargs", "code"),
    [
        ({"operation_id": "  "}, "invalid_operation_id"),
        ({"timeout": 0}, "invalid_timeout"),
        ({"timeout": 7201}, "invalid_timeout"),
        ({"poll_interval": 61}, "invalid_poll_interval"),
        ({"timeout": 5, "poll_interval": 10}, "invalid_poll_interval"),
        ({"workspace_id": "x"}, "invalid_workspace_id"),
    ],
)
def test_wait_validates_inputs(kwargs: dict, code: str) -> None:
    client, observed = _ops_client((200, _op("succeeded")))
    arguments = {"operation_id": "op-1", "workspace_id": WS, **kwargs}
    with pytest.raises(IbeeValidationError) as info:
        wait_for_compute_operation(client, **arguments)
    assert info.value.code == code
    assert observed == []


def test_get_compute_operation_rejects_blank_ids_and_gpu_alias_uses_same_route() -> None:
    client, observed = _ops_client((200, _op("running")))
    with pytest.raises(IbeeValidationError):
        client.cloud_vms.get_compute_operation(" ", workspace_id=WS)
    assert client.gpu_vms.get_compute_operation("op/1", workspace_id=WS).status == "running"
    assert observed[0].url.raw_path.startswith(b"/v1/compute/operations/op%2F1")


def test_async_wait_parity(fake_time: FakeTime) -> None:
    responses = [(200, _op("running")), (200, _op("succeeded"))]

    def handler(request: httpx.Request) -> httpx.Response:
        status, body = responses.pop(0)
        return httpx.Response(status, json=body, request=request)

    seen: list = []

    async def on_update(op) -> None:
        seen.append(op.status)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            client = AsyncIbee(token="t", base_url=BASE, httpx_client=http_client)
            return await client.gpu_vms.wait_for_compute_operation("op-1", workspace_id=WS, on_update=on_update)

    assert asyncio.run(run()).status == "succeeded"
    assert seen == ["running", "succeeded"]
    assert fake_time.sleeps == [5.0]


def test_poll_until_is_reusable_with_custom_statuses(fake_time: FakeTime) -> None:
    states = iter(["in-progress", "in-progress", "succeeded"])
    result = poll_until(lambda: {"status": next(states)}, lambda item: item["status"], success={"succeeded"},
                        failure={"failed"}, poll_interval=1, timeout=10)
    assert result == {"status": "succeeded"}
    with pytest.raises(OperationFailedError):
        poll_until(lambda: {"status": "failed"}, lambda item: item["status"], success={"succeeded"}, failure={"failed"})
    with pytest.raises(ServiceUnavailableError):
        from ibee.errors import error_from_response

        def fail():
            raise error_from_response(503, {})

        poll_until(fail, lambda item: item, poll_interval=1, timeout=100)


# pagination --------------------------------------------------------------------


def _vm(index: int) -> dict:
    return {"id": f"vm-{index}", "name": f"web-{index}", "status": "running"}


def _paged_client(items: typing.List[dict], observed: list, key: str = "id") -> Ibee:
    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        limit = int(request.url.params.get("limit", 10))
        offset = int(request.url.params.get("offset", 0))
        return httpx.Response(200, json=items[offset : offset + limit], request=request)

    return Ibee(token="t", base_url=BASE, httpx_client=httpx.Client(transport=httpx.MockTransport(handler)))


def test_list_cloud_vms_auto_pages_everything() -> None:
    observed: list[httpx.Request] = []
    vms = _paged_client([_vm(i) for i in range(250)], observed).cloud_vms.list_cloud_vms(workspace_id=WS)
    assert len(vms) == 250
    assert [(r.url.params["limit"], r.url.params["offset"]) for r in observed] == [
        ("100", "0"),
        ("100", "100"),
        ("100", "200"),
    ]


def test_list_with_limit_makes_one_request_with_all_params() -> None:
    observed: list[httpx.Request] = []
    vms = _paged_client([_vm(i) for i in range(50)], observed).gpu_vms.list_gpu_vms(
        workspace_id=WS, limit=5, offset=10, search=" web ", sort_by="name", sort_direction="asc"
    )
    assert [vm.id for vm in vms] == [f"vm-{i}" for i in range(10, 15)]
    assert len(observed) == 1
    assert dict(observed[0].url.params) == {
        "workspace_id": WS,
        "limit": "5",
        "offset": "10",
        "search": "web",
        "sort_by": "name",
        "sort_direction": "asc",
    }


def test_auto_paging_deduplicates_shifted_items() -> None:
    pages = {0: [_vm(i) for i in range(3)], 3: [_vm(2), _vm(3)]}
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json=pages.get(int(request.url.params["offset"]), []), request=request)

    client = Ibee(token="t", base_url=BASE, httpx_client=httpx.Client(transport=httpx.MockTransport(handler)))
    vms = list(client.cloud_vms.iter_cloud_vms(workspace_id=WS, page_size=3))
    assert [vm.id for vm in vms] == ["vm-0", "vm-1", "vm-2", "vm-3"]


def test_list_validates_paging_params_before_sending() -> None:
    observed: list[httpx.Request] = []
    client = _paged_client([], observed)
    for kwargs in ({"limit": 101}, {"offset": -1}, {"sort_by": "cpu"}, {"search": "x" * 121}):
        with pytest.raises(IbeeValidationError):
            client.cloud_vms.list_cloud_vms(workspace_id=WS, **kwargs)
    with pytest.raises(IbeeValidationError):
        client.firewalls.list_firewall_groups(workspace_id=WS, limit=0)
    assert observed == []


def _group(index: int) -> dict:
    return {
        "firewall_group_id": f"fg-{index}",
        "organization_id": "org",
        "workspace_id": WS,
        "name": f"g{index}",
        "is_default": False,
        "status": "active",
        "rules": [],
        "created_at": "2026-08-04T10:00:00Z",
        "updated_at": "2026-08-04T10:00:00Z",
    }


def test_firewall_groups_auto_page_and_single_page() -> None:
    observed: list[httpx.Request] = []
    client = _paged_client([_group(i) for i in range(120)], observed)
    groups = client.firewalls.list_firewall_groups(workspace_id=WS)
    assert len(groups) == 120
    assert len(observed) == 2
    observed.clear()
    assert len(client.firewalls.list_firewall_groups(workspace_id=WS, limit=7)) == 7
    assert dict(observed[0].url.params) == {"workspace_id": WS, "limit": "7"}
    assert "summary" not in observed[0].url.params


def test_async_iter_and_list_parity() -> None:
    items = [_vm(i) for i in range(130)]
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        limit = int(request.url.params["limit"])
        offset = int(request.url.params["offset"])
        return httpx.Response(200, json=items[offset : offset + limit], request=request)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            client = AsyncIbee(token="t", base_url=BASE, httpx_client=http_client)
            listed = await client.cloud_vms.list_cloud_vms(workspace_id=WS)
            iterated = [vm async for vm in client.gpu_vms.iter_gpu_vms(workspace_id=WS, page_size=50)]
            return listed, iterated

    listed, iterated = asyncio.run(run())
    assert len(listed) == 130 and len(iterated) == 130


def test_paginate_pages_stops_on_total() -> None:
    calls: list = []

    def fetch(page: int, limit: int) -> dict:
        calls.append(page)
        start = (page - 1) * limit
        return {"stores": list(range(start, min(start + limit, 5))), "total": 5}

    assert list(paginate_pages(fetch, limit=2, items_key="stores")) == [0, 1, 2, 3, 4]
    assert calls == [1, 2, 3]
