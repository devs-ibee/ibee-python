"""Shared mock-transport helpers for the 0.4.0 compute tests."""

from __future__ import annotations

import json
import typing

import httpx

from ibee import AsyncIbee, Ibee

BASE = "https://api.example.test/v1"
WS = "710995"
VM = "0123456789abcdef01234567"
VM2 = "0123456789abcdef01234568"
OP = "op_0123456789abcdef01234567"
ACCEPTED = {"operation_id": OP, "vm_id": VM, "status": "accepted", "submitted_at": "2026-09-01T10:00:00Z"}

HOURLY = {"billing_interval": "HOURLY", "unit_price_minor": 250, "committed": False, "price_unit": "HOUR"}
MONTHLY = {
    "billing_interval": "MONTHLY",
    "unit_price_minor": 150000,
    "committed": True,
    "commitment_period": "MONTHLY",
    "commitment_months": 1,
    "committed_hours": 730,
    "discount_percent": 10,
    "price_unit": "MONTH",
}


def plan(plan_id: str = "plan-1", *, vm_type: str = "cloud", **overrides: typing.Any) -> typing.Dict[str, typing.Any]:
    record: typing.Dict[str, typing.Any] = {
        "plan_id": plan_id,
        "vm_type": vm_type,
        "name": "Standard 2x4",
        "code": "STD-2-4",
        "cpu": 2,
        "ram_mb": 4096,
        "disk_gb": 50,
        "gpu_count": 1 if vm_type == "gpu" else 0,
        "gpu_model": "L40S" if vm_type == "gpu" else None,
        "selectable": True,
        "pricing_status": "priced",
        "currency": "INR",
        "billing_interval": "HOURLY",
        "hourly_price_minor": 250,
        "monthly_price_minor": 150000,
        "site_id": "site-1",
        "billing_catalog": {
            "sku_id": 101,
            "sku_code": "vm-std-2-4",
            "product_code": "compute",
            "attached_skus": {"bandwidth": {"sku_id": 9, "sku_code": "BW-1TB"}},
            "billing_options": [HOURLY, MONTHLY],
        },
    }
    record.update(overrides)
    return record


def image(template_id: str = "tmpl-ubuntu", *, vm_type: str = "cloud", **overrides: typing.Any) -> typing.Dict[str, typing.Any]:
    record = {
        "template_id": template_id,
        "name": "Ubuntu 24.04",
        "os_distro": "ubuntu",
        "os_type": "linux",
        "architecture": "x86_64",
        "size_bytes": 1,
        "gpu_compatible": vm_type == "gpu",
        "compatible_vm_types": [vm_type],
        "site_ids": ["site-1"],
    }
    record.update(overrides)
    return record


def vm(**overrides: typing.Any) -> typing.Dict[str, typing.Any]:
    record = {
        "_id": VM,
        "name": "web-1",
        "status": "running",
        "os_type": "linux",
        "os_distro": "ubuntu",
        "site_id": "site-1",
        "plan_id": "plan-1",
        "cpu": 2,
        "ram_mb": 4096,
        "disk_gb": 50,
        "public_ip": "",
        "admin_username": "ubuntu",
        "ssh_keys": [],
    }
    record.update(overrides)
    return record


Responder = typing.Union[typing.Tuple[int, typing.Any], typing.Callable[[httpx.Request], httpx.Response]]


class Router:
    """Route ``(METHOD, path suffix)`` to queued responses; record every request."""

    def __init__(self, routes: typing.Optional[typing.Dict[typing.Tuple[str, str], typing.Any]] = None) -> None:
        self.routes: typing.Dict[typing.Tuple[str, str], typing.List[Responder]] = {}
        self.requests: typing.List[httpx.Request] = []
        for key, value in (routes or {}).items():
            self.add(key[0], key[1], value)

    def add(self, method: str, path: str, *responses: typing.Any) -> "Router":
        items = list(responses[0]) if len(responses) == 1 and isinstance(responses[0], list) else list(responses)
        self.routes.setdefault((method, path), []).extend(items)
        return self

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path
        key = (request.method, path[len("/v1/"):] if path.startswith("/v1/") else path)
        queue = self.routes.get(key)
        if not queue:
            return httpx.Response(599, json={"detail": f"unexpected {key}"}, request=request)
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if callable(item):
            return item(request)
        status, body = item
        return httpx.Response(status, json=body, request=request)

    # helpers
    def calls(self) -> typing.List[typing.Tuple[str, str]]:
        return [(r.method, r.url.path[len("/v1/"):]) for r in self.requests]

    def last(self, method: str, path: str) -> httpx.Request:
        for request in reversed(self.requests):
            if request.method == method and request.url.path == f"/v1/{path}":
                return request
        raise AssertionError(f"no {method} {path} in {self.calls()}")

    def body(self, method: str, path: str) -> typing.Any:
        return json.loads(self.last(method, path).content)


def sync_client(router: Router) -> Ibee:
    return Ibee(token="t", base_url=BASE, httpx_client=httpx.Client(transport=httpx.MockTransport(router)), max_retries=0)


def async_client(router: Router, http_client: httpx.AsyncClient) -> AsyncIbee:
    return AsyncIbee(token="t", base_url=BASE, httpx_client=http_client, max_retries=0)


def async_transport(router: Router) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(router))
