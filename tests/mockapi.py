"""A mock IBEE API and clients wired to it (no network, no real token)."""

import json
import typing

import httpx

from ibee import AsyncIbee, Ibee

BASE = "https://api.example.test/v1"
WS = "710995"
VM = "0123456789abcdef01234567"
ACCEPTED = {"operation_id": "op_1", "vm_id": VM, "status": "accepted", "submitted_at": "2026-01-01T00:00:00Z"}


class Recorder:
    """Answers requests from a queue (the last answer repeats) and records them."""

    def __init__(self, *answers: typing.Any) -> None:
        self.answers = list(answers) or [(200, {})]
        self.requests: typing.List[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        answer = self.answers.pop(0) if len(self.answers) > 1 else self.answers[0]
        if callable(answer):
            return answer(request)
        if isinstance(answer, Exception):
            raise answer
        status, body, *headers = answer
        if isinstance(body, str):
            return httpx.Response(status, text=body, headers=(headers or [None])[0])
        return httpx.Response(status, json=body, headers=(headers or [None])[0])

    def body(self, index: int = -1) -> typing.Any:
        content = self.requests[index].content
        return json.loads(content) if content else None


def client(handler: typing.Callable[[httpx.Request], httpx.Response], **kwargs: typing.Any) -> Ibee:
    kwargs.setdefault("token", "t")
    kwargs.setdefault("base_url", BASE)
    return Ibee(httpx_client=httpx.Client(transport=httpx.MockTransport(handler)), **kwargs)


def async_client(handler: typing.Callable[[httpx.Request], httpx.Response], **kwargs: typing.Any) -> AsyncIbee:
    kwargs.setdefault("token", "t")
    kwargs.setdefault("base_url", BASE)
    return AsyncIbee(httpx_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)), **kwargs)
