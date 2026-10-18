"""ibee.client configuration and the held token environment check."""

import asyncio

import httpx
import pytest
from mockapi import Recorder, async_client, client

from ibee import AsyncIbee, Ibee, IbeeEnvironment
from ibee.client import IbeeValidationError, environment_from_name, resolve_base_url


def _base(api: object) -> str:
    return api._client_wrapper.get_base_url()  # type: ignore[attr-defined]


def test_token_from_argument_then_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    rec = Recorder((200, []))
    monkeypatch.setenv("IBEE_TOKEN", "from-ibee-token")
    client(rec, token=None, workspace_id="1").reserved_ips.list_reserved_ips()
    monkeypatch.setenv("IBEE_API_TOKEN", "from-api-token")
    client(rec, token=None, workspace_id="1").reserved_ips.list_reserved_ips()
    client(rec, token="explicit", workspace_id="1").reserved_ips.list_reserved_ips()
    assert [r.headers["authorization"] for r in rec.requests] == [
        "Bearer from-ibee-token",
        "Bearer from-api-token",
        "Bearer explicit",
    ]


def test_missing_token_is_a_configuration_error() -> None:
    with pytest.raises(IbeeValidationError) as info:
        Ibee()
    assert info.value.code == "missing_token" and isinstance(info.value, ValueError)


def test_endpoint_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _base(Ibee(token="t")) == "https://api.ibee.ai/v1"
    monkeypatch.setenv("IBEE_ENV", "dev")
    assert _base(Ibee(token="t")) == "https://api.ibee.co.in/v1"
    monkeypatch.setenv("IBEE_ENDPOINT", "https://endpoint.example.test/v1")
    assert _base(Ibee(token="t")) == "https://endpoint.example.test/v1"
    monkeypatch.setenv("IBEE_BASE_URL", "https://base.example.test/v1/")
    assert _base(Ibee(token="t")) == "https://base.example.test/v1"
    assert _base(Ibee(token="t", environment=IbeeEnvironment.PRODUCTION)) == "https://api.ibee.ai/v1"
    assert _base(Ibee(token="t", base_url="http://localhost:8080/v1")) == "http://localhost:8080/v1"


@pytest.mark.parametrize(
    "url",
    [
        "http://api.example.test/v1",
        "ftp://api.example.test",
        "https://user:pw@api.example.test/v1",
        "https://api.example.test/v1?x=1",
        "https://api.example.test/v1#frag",
        "https://api.example.test/../v1",
        "not a url",
    ],
)
def test_unsafe_base_urls_are_refused(url: str) -> None:
    with pytest.raises(IbeeValidationError) as info:
        resolve_base_url(url)
    assert info.value.code == "invalid_base_url"


def test_environment_names() -> None:
    assert environment_from_name("Development ") is IbeeEnvironment.DEVELOPMENT
    assert environment_from_name("") is IbeeEnvironment.PRODUCTION
    with pytest.raises(IbeeValidationError) as info:
        environment_from_name("staging")
    assert info.value.code == "invalid_environment"


# held: token environment check ---------------------------------------------------


@pytest.mark.parametrize(
    ("token", "env"),
    [("ibee_dev_key_abc", IbeeEnvironment.PRODUCTION), ("ibee_prod_key_abc", IbeeEnvironment.DEVELOPMENT)],
)
def test_token_for_the_other_environment_is_refused(token: str, env: IbeeEnvironment) -> None:
    with pytest.raises(IbeeValidationError) as info:
        Ibee(token=token, environment=env)
    assert info.value.code == "token_environment_mismatch"


def test_matching_tokens_and_other_hosts_are_accepted() -> None:
    Ibee(token="ibee_prod_key_abc")
    Ibee(token="ibee_dev_key_abc", environment=IbeeEnvironment.DEVELOPMENT)
    Ibee(token="ibee_dev_key_abc", base_url="https://mock.example.test/v1")


def test_token_with_a_line_break_is_refused() -> None:
    with pytest.raises(IbeeValidationError) as info:
        Ibee(token="abc\r\nX-Evil: 1")
    assert info.value.code == "invalid_token"


def test_callable_and_async_tokens_are_checked_per_request() -> None:
    rec = Recorder((200, []))
    api = client(rec, token=lambda: "ibee_dev_key_abc", base_url="https://api.ibee.ai/v1", workspace_id="1")
    with pytest.raises(IbeeValidationError):
        api.reserved_ips.list_reserved_ips()
    assert rec.requests == []

    async def bad_token() -> str:
        return "ibee_dev_key_abc"

    async def run() -> None:
        api = AsyncIbee(
            async_token=bad_token,
            base_url="https://api.ibee.ai/v1",
            workspace_id="1",
            httpx_client=httpx.AsyncClient(transport=httpx.MockTransport(rec)),
        )
        with pytest.raises(IbeeValidationError):
            await api.reserved_ips.list_reserved_ips()

    asyncio.run(run())
    assert rec.requests == []


def test_async_client_reads_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IBEE_API_TOKEN", "env-token")
    monkeypatch.setenv("IBEE_WORKSPACE_ID", "55")
    rec = Recorder((200, []))
    asyncio.run(async_client(rec, token=None).reserved_ips.list_reserved_ips())
    assert rec.requests[0].headers["authorization"] == "Bearer env-token"
    assert rec.requests[0].url.params["workspace_id"] == "55"
