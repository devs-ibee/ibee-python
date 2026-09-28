"""0.4.0 client-side validation: workspace ids, tokens, environments, keys, body size."""

from __future__ import annotations

import asyncio
import json
import math

import httpx
import pytest

from ibee import AsyncIbee, Ibee, IbeeEnvironment, IbeeValidationError
from ibee.errors import IbeeError
from ibee.idempotency import build_idempotency_key, build_stable_idempotency_key, fnv1a36
from ibee.validation import (
    check_billable_body_size,
    normalize_eligibility_operation,
    normalize_estimated_cost_minor,
    normalize_sku_code,
    resolve_base_url,
    validate_idempotency_key,
    validate_limit,
    validate_poll_interval,
    validate_vm_list_params,
    validate_wait_timeout,
    validate_workspace_id,
)

BASE = "https://api.example.test/v1"


def _client(handler, **kwargs) -> Ibee:
    kwargs.setdefault("token", "test-token")
    kwargs.setdefault("base_url", BASE)
    return Ibee(httpx_client=httpx.Client(transport=httpx.MockTransport(handler)), **kwargs)


def _ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"sites": [], "count": 0}, request=request)


# workspace_id -----------------------------------------------------------------


def test_workspace_id_error_is_typed_and_still_a_value_error() -> None:
    with pytest.raises(IbeeValidationError) as info:
        validate_workspace_id("0")
    assert isinstance(info.value, ValueError)
    assert isinstance(info.value, IbeeError)
    assert info.value.code == "invalid_workspace_id"
    assert info.value.field == "workspace_id"
    assert str(info.value) == "workspace_id must be a positive numeric string (for example, '710995')."


def test_positive_int_workspace_id_is_accepted_and_sent_as_string() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return _ok(request)

    _client(handler).compute_catalog.list_compute_sites(workspace_id=710995)  # type: ignore[arg-type]
    assert observed[0].url.params.get_list("workspace_id") == ["710995"]
    for bad in (True, 0, -3, 1.0):
        with pytest.raises(IbeeValidationError):
            validate_workspace_id(bad)


def test_tenancy_headers_are_never_sent() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return _ok(request)

    client = _client(handler, headers={"X-Organization-Id": "org-1", "X-Workspace-Id": "9"})
    client.compute_catalog.list_compute_sites(
        workspace_id="710995", request_options={"additional_headers": {"x-project-id": "p"}}
    )
    headers = {key.lower() for key in observed[0].headers}
    assert not headers & {"x-organization-id", "x-workspace-id", "x-project-id"}


# tokens and environments -------------------------------------------------------


@pytest.mark.parametrize(
    ("token", "environment"),
    [
        ("ibee_dev_key_abc.secret", IbeeEnvironment.PRODUCTION),
        ("ibee_prod_key_abc.secret", IbeeEnvironment.DEVELOPMENT),
    ],
)
def test_token_environment_mismatch_is_rejected_at_construction(token: str, environment: IbeeEnvironment) -> None:
    with pytest.raises(IbeeValidationError) as info:
        Ibee(token=token, environment=environment)
    assert info.value.code == "token_environment_mismatch"
    assert str(info.value) == "The API token environment does not match the configured IBEE endpoint."
    with pytest.raises(IbeeValidationError):
        AsyncIbee(token=token, environment=environment)


def test_matching_and_unprefixed_tokens_are_accepted() -> None:
    Ibee(token="ibee_prod_key_abc.secret")
    Ibee(token="ibee_dev_key_abc.secret", environment=IbeeEnvironment.DEVELOPMENT)
    Ibee(token="ibee_dev_key_abc.secret", base_url="https://API.IBEE.CO.IN./v1")
    Ibee(token="ibee_dev_key_abc.secret", base_url="http://localhost:8080/v1")
    Ibee(token="anything")


def test_prod_host_with_trailing_dot_is_still_checked() -> None:
    with pytest.raises(IbeeValidationError):
        Ibee(token="ibee_dev_key_abc.secret", base_url="https://api.ibee.ai./v1")


def test_callable_token_is_checked_per_request() -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _ok(request)

    client = Ibee(
        token=lambda: "ibee_dev_key_abc.secret",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    with pytest.raises(IbeeValidationError) as info:
        client.compute_catalog.list_compute_sites(workspace_id="710995")
    assert info.value.code == "token_environment_mismatch"
    assert calls == []


def test_async_token_is_checked_per_request() -> None:
    async def token() -> str:
        return "ibee_dev_key_abc.secret"

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(_ok)) as http_client:
            client = AsyncIbee(token="placeholder", async_token=token, httpx_client=http_client)
            await client.compute_catalog.list_compute_sites(workspace_id="710995")

    with pytest.raises(IbeeValidationError):
        asyncio.run(run())


@pytest.mark.parametrize("token", ["", "   ", "abc\r\nX-Evil: 1", "abc\n"])
def test_invalid_tokens_are_rejected(token: str) -> None:
    with pytest.raises(IbeeValidationError) as info:
        Ibee(token=token)
    assert info.value.code == "invalid_token"


@pytest.mark.parametrize(
    "url",
    [
        "api.ibee.ai/v1",
        "ftp://api.ibee.ai/v1",
        "http://api.ibee.ai/v1",
        "https://user:pw@api.ibee.ai/v1",
        "https://api.ibee.ai/v1?x=1",
        "https://api.ibee.ai/v1#frag",
        "https://api.ibee.ai/../v1",
        "https:///v1",
    ],
)
def test_unsafe_base_urls_are_rejected(url: str) -> None:
    with pytest.raises(IbeeValidationError) as info:
        Ibee(token="t", base_url=url)
    assert info.value.code == "invalid_base_url"


def test_base_url_resolution() -> None:
    assert resolve_base_url() == "https://api.ibee.ai/v1"
    assert resolve_base_url(environment=IbeeEnvironment.DEVELOPMENT) == "https://api.ibee.co.in/v1"
    assert resolve_base_url("https://api.example.test/v1/", IbeeEnvironment.DEVELOPMENT) == BASE
    assert resolve_base_url("http://127.0.0.1:9000/v1") == "http://127.0.0.1:9000/v1"
    assert resolve_base_url("http://[::1]:9000/v1") == "http://[::1]:9000/v1"


def test_environment_from_name() -> None:
    assert IbeeEnvironment.from_name(" DEV ") is IbeeEnvironment.DEVELOPMENT
    assert IbeeEnvironment.from_name("development") is IbeeEnvironment.DEVELOPMENT
    assert IbeeEnvironment.from_name(None) is IbeeEnvironment.PRODUCTION
    assert IbeeEnvironment.from_name("Production") is IbeeEnvironment.PRODUCTION
    with pytest.raises(IbeeValidationError) as info:
        IbeeEnvironment.from_name("staging")
    assert str(info.value) == "Invalid IBEE_ENV: use dev, development, prod or production"


# idempotency keys --------------------------------------------------------------


def test_idempotency_key_validation() -> None:
    assert validate_idempotency_key("abc-123_!~") == "abc-123_!~"
    for bad in ("", "has space", "a" * 129, "line\nbreak", "café", None, 5):
        with pytest.raises(IbeeValidationError) as info:
            validate_idempotency_key(bad)
        assert info.value.code == "invalid_idempotency_key"


def test_build_idempotency_key_matches_portal_algorithm() -> None:
    # Values computed with the portal's JavaScript implementation.
    assert fnv1a36("") == "ztntfp"
    assert fnv1a36("vm-1") == "h4ghdy"
    assert fnv1a36("héllo \U0001F600") == "lmw5e8"
    assert build_stable_idempotency_key("cloud-vm-start", "vm-1") == "cloud-vm-start-vm-1-h4ghdy"
    assert build_stable_idempotency_key("") == "request-empty"
    key = build_idempotency_key("cloud-vm-start", "vm-1")
    assert key.startswith("cloud-vm-start-vm-1-h4ghdy-") and len(key) == len("cloud-vm-start-vm-1-h4ghdy-") + 16
    assert key != build_idempotency_key("cloud-vm-start", "vm-1")
    long_key = build_idempotency_key("s" * 80, "p" * 300, "q q")
    assert len(long_key) <= 128
    validate_idempotency_key(long_key)


# eligibility inputs ------------------------------------------------------------


def test_eligibility_input_normalisation() -> None:
    assert normalize_sku_code("  vm.std  ") == "vm.std"
    assert normalize_sku_code("   ") is None
    assert normalize_sku_code(None) is None
    with pytest.raises(IbeeValidationError) as info:
        normalize_sku_code("x" * 65)
    assert info.value.code == "invalid_sku_code"

    assert normalize_estimated_cost_minor(0) == 0
    assert normalize_estimated_cost_minor(12.5) == 13
    assert normalize_estimated_cost_minor(2.5) == 3
    assert normalize_estimated_cost_minor(2.4) == 2
    for bad in (-1, -0.5, math.nan, math.inf, True, "5"):
        with pytest.raises(IbeeValidationError) as info:
            normalize_estimated_cost_minor(bad)
        assert info.value.code == "invalid_estimated_cost_minor"

    assert normalize_eligibility_operation(" read_resource ") == "READ_RESOURCE"
    assert normalize_eligibility_operation(None) is None
    with pytest.raises(IbeeValidationError) as info:
        normalize_eligibility_operation("BOGUS")
    assert info.value.code == "invalid_operation"


# waits and paging --------------------------------------------------------------


def test_wait_bounds() -> None:
    assert validate_wait_timeout(1) == 1.0
    assert validate_wait_timeout(7200) == 7200.0
    for bad in (0, 0.5, 7201, math.nan, True, "10"):
        with pytest.raises(IbeeValidationError) as info:
            validate_wait_timeout(bad)
        assert info.value.code == "invalid_timeout"
    assert validate_poll_interval(5, 1200.0) == 5.0
    for bad, timeout in ((0.5, 100.0), (61, 100.0), (10, 5.0)):
        with pytest.raises(IbeeValidationError) as info:
            validate_poll_interval(bad, timeout)
        assert info.value.code == "invalid_poll_interval"


def test_vm_list_params() -> None:
    assert validate_vm_list_params(limit=100, offset=0, search="  web ", sort_by="name", sort_direction="asc") == {
        "limit": 100,
        "offset": 0,
        "search": "web",
        "sort_by": "name",
        "sort_direction": "asc",
    }
    assert validate_vm_list_params(search="   ") == {}
    for kwargs, code in (
        ({"limit": 0}, "invalid_limit"),
        ({"limit": 101}, "invalid_limit"),
        ({"offset": -1}, "invalid_offset"),
        ({"search": "x" * 121}, "invalid_search"),
        ({"sort_by": "cpu"}, "invalid_sort_by"),
        ({"sort_direction": "DESC"}, "invalid_sort_direction"),
    ):
        with pytest.raises(IbeeValidationError) as info:
            validate_vm_list_params(**kwargs)
        assert info.value.code == code
    assert validate_limit(None, maximum=10) is None


# billable body size ------------------------------------------------------------


def test_billable_create_body_limit_is_enforced_before_sending() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(201, json={}, request=request)

    client = _client(handler)
    with pytest.raises(IbeeValidationError) as info:
        client.secret_store.create_secret_store(workspace_id="710995", name="n", description="x" * 70_000)
    assert info.value.code == "request_body_too_large"
    assert observed == []

    check_billable_body_size("POST", "compute/cloud-vms", {"name": "x" * 1000})
    check_billable_body_size("PATCH", "compute/cloud-vms/vm-1", {"name": "x" * 70_000})
    with pytest.raises(IbeeValidationError):
        check_billable_body_size("POST", "/v1/cdn/distributions/d-1/custom-domains", {"d": "x" * 70_000})


def test_billable_create_without_body_sends_json_object() -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(200, json={}, request=request)

    client = _client(handler)
    client._client_wrapper.httpx_client.request(
        "networking/reserved-ips", method="POST", params={"workspace_id": "710995"}
    )
    assert json.loads(observed[0].content) == {}
    assert observed[0].headers["content-type"] == "application/json"
