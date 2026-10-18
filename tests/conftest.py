"""Test isolation: no IBEE_* variables from the environment, no real sleeps between retries."""

import pytest

import ibee.transport


@pytest.fixture(autouse=True)
def _clean_env_and_no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("IBEE_API_TOKEN", "IBEE_TOKEN", "IBEE_WORKSPACE_ID", "IBEE_BASE_URL", "IBEE_ENDPOINT", "IBEE_ENV"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(ibee.transport, "_sleep", lambda seconds: None)

    async def _no_async_sleep(seconds: float) -> None:
        return None

    monkeypatch.setattr(ibee.transport, "_async_sleep", _no_async_sleep)
