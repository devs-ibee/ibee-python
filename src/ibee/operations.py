"""Waiting for asynchronous compute operations.

VM creates, deletes, power actions, access updates, resizes and volume
attach/detach return an operation (``operation_id``). :func:`wait_for_compute_operation`
polls ``GET /compute/operations/{operation_id}`` until it reaches a terminal status:

* success: ``succeeded`` (``completed`` is accepted as a legacy alias);
* failure: ``failed``, ``cancelled`` or ``timed_out`` -> :class:`OperationFailedError`;
* anything else (``accepted``, ``running``, ``waiting``, ``compensating``, unknown
  values) keeps polling until the client-side ``timeout`` ->
  :class:`OperationTimeoutError`.

Up to two consecutive transient poll failures (HTTP 429/502/503/504 or a network
error) are tolerated; the third is raised. HTTP 404 and other errors are raised
immediately.
"""

from __future__ import annotations

import asyncio
import time
import typing

import httpx

from .core.api_error import ApiError
from .errors.operation_errors import OperationFailedError, OperationTimeoutError
from .validation import (
    DEFAULT_POLL_INTERVAL_SECONDS,
    DEFAULT_WAIT_TIMEOUT_SECONDS,
    validate_operation_id,
    validate_poll_interval,
    validate_wait_timeout,
    validate_workspace_id,
)

if typing.TYPE_CHECKING:
    from .core.request_options import RequestOptions
    from .types.operation_status import OperationStatus

T = typing.TypeVar("T")

SUCCESS_STATUSES = frozenset({"succeeded", "completed"})
FAILURE_STATUSES = frozenset({"failed", "cancelled", "timed_out"})
MAX_CONSECUTIVE_POLL_FAILURES = 3
_RETRYABLE_POLL_STATUSES = frozenset({429, 502, 503, 504})

# Indirections so tests can replace time without patching global modules.
_sleep: typing.Callable[[float], None] = time.sleep
_clock: typing.Callable[[], float] = time.monotonic


async def _asleep(seconds: float) -> None:
    await asyncio.sleep(seconds)


def is_transient_poll_error(error: BaseException) -> bool:
    """HTTP 429/502/503/504 or a network-level failure."""
    if isinstance(error, ApiError):
        return error.status_code in _RETRYABLE_POLL_STATUSES
    return isinstance(error, httpx.TransportError)


def _status_text(value: typing.Any) -> str:
    return str(value if value is not None else "").strip().lower()


def poll_until(
    fetch: typing.Callable[[], T],
    status_of: typing.Callable[[T], typing.Any],
    *,
    success: typing.AbstractSet[str] = SUCCESS_STATUSES,
    failure: typing.AbstractSet[str] = FAILURE_STATUSES,
    timeout: float = DEFAULT_WAIT_TIMEOUT_SECONDS,
    poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
    max_consecutive_failures: int = MAX_CONSECUTIVE_POLL_FAILURES,
    on_update: typing.Optional[typing.Callable[[T], None]] = None,
    sleep: typing.Optional[typing.Callable[[float], None]] = None,
    clock: typing.Optional[typing.Callable[[], float]] = None,
    operation_id: typing.Optional[str] = None,
    error_factory: typing.Optional[typing.Callable[[T], BaseException]] = None,
) -> T:
    """Call ``fetch`` until ``status_of(result)`` is terminal; the generic polling engine.

    Returns the result on success; raises :class:`OperationFailedError` (or the
    exception built by ``error_factory``) on failure and
    :class:`OperationTimeoutError` when ``timeout`` seconds pass first.
    """
    sleep = sleep or _sleep
    clock = clock or _clock
    deadline = clock() + timeout
    failures = 0
    last: typing.Optional[T] = None
    while True:
        try:
            current = fetch()
        except Exception as exc:
            if not is_transient_poll_error(exc):
                raise
            failures += 1
            if failures >= max_consecutive_failures:
                raise
        else:
            failures = 0
            last = current
            if on_update is not None:
                on_update(current)
            status = _status_text(status_of(current))
            if status in success:
                return current
            if status in failure:
                raise error_factory(current) if error_factory is not None else OperationFailedError(current)
        remaining = deadline - clock()
        if remaining <= 0:
            raise OperationTimeoutError(last, timeout=timeout, operation_id=operation_id)
        sleep(min(poll_interval, remaining))


async def apoll_until(
    fetch: typing.Callable[[], typing.Awaitable[T]],
    status_of: typing.Callable[[T], typing.Any],
    *,
    success: typing.AbstractSet[str] = SUCCESS_STATUSES,
    failure: typing.AbstractSet[str] = FAILURE_STATUSES,
    timeout: float = DEFAULT_WAIT_TIMEOUT_SECONDS,
    poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
    max_consecutive_failures: int = MAX_CONSECUTIVE_POLL_FAILURES,
    on_update: typing.Optional[typing.Callable[[T], typing.Any]] = None,
    sleep: typing.Optional[typing.Callable[[float], typing.Awaitable[None]]] = None,
    clock: typing.Optional[typing.Callable[[], float]] = None,
    operation_id: typing.Optional[str] = None,
    error_factory: typing.Optional[typing.Callable[[T], BaseException]] = None,
) -> T:
    """Async variant of :func:`poll_until`. ``on_update`` may be sync or async."""
    sleep = sleep or _asleep
    clock = clock or _clock
    deadline = clock() + timeout
    failures = 0
    last: typing.Optional[T] = None
    while True:
        try:
            current = await fetch()
        except Exception as exc:
            if not is_transient_poll_error(exc):
                raise
            failures += 1
            if failures >= max_consecutive_failures:
                raise
        else:
            failures = 0
            last = current
            if on_update is not None:
                result = on_update(current)
                if asyncio.iscoroutine(result):
                    await result
            status = _status_text(status_of(current))
            if status in success:
                return current
            if status in failure:
                raise error_factory(current) if error_factory is not None else OperationFailedError(current)
        remaining = deadline - clock()
        if remaining <= 0:
            raise OperationTimeoutError(last, timeout=timeout, operation_id=operation_id)
        await sleep(min(poll_interval, remaining))


def _operation_getter(client: typing.Any) -> typing.Callable[..., typing.Any]:
    getter = getattr(client, "get_compute_operation", None)
    if getter is None:
        cloud_vms = getattr(client, "cloud_vms", None)
        getter = getattr(cloud_vms, "get_compute_operation", None)
    if getter is None:
        raise TypeError("client must be an Ibee/AsyncIbee client or its cloud_vms/gpu_vms client")
    return getter


def _status_of(operation: typing.Any) -> typing.Any:
    if isinstance(operation, typing.Mapping):
        return operation.get("status")
    return getattr(operation, "status", None)


def _validated(
    operation_id: typing.Any, workspace_id: typing.Any, timeout: typing.Any, poll_interval: typing.Any
) -> typing.Tuple[str, str, float, float]:
    op_id = validate_operation_id(operation_id)
    workspace = validate_workspace_id(workspace_id)
    wait_timeout = validate_wait_timeout(timeout)
    interval = validate_poll_interval(poll_interval, wait_timeout)
    return op_id, workspace, wait_timeout, interval


def wait_for_compute_operation(
    client: typing.Any,
    operation_id: str,
    *,
    workspace_id: str,
    timeout: float = DEFAULT_WAIT_TIMEOUT_SECONDS,
    poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
    raise_on_failure: bool = True,
    on_update: typing.Optional[typing.Callable[["OperationStatus"], None]] = None,
    request_options: typing.Optional["RequestOptions"] = None,
) -> "OperationStatus":
    """Poll a compute operation until it finishes.

    Parameters
    ----------
    client
        An ``Ibee`` client, or its ``cloud_vms``/``gpu_vms`` client.
    operation_id : str
        ``operation_id`` returned by the create/delete/action call.
    workspace_id : str
        The workspace the operation belongs to.
    timeout : float
        Seconds to wait (1-7200, default 1200).
    poll_interval : float
        Seconds between polls (1-60, default 5, and not more than ``timeout``).
    raise_on_failure : bool
        When ``False``, a ``failed``/``cancelled``/``timed_out`` operation is
        returned instead of raising ``OperationFailedError``.
    on_update
        Called with each polled status.

    Raises
    ------
    OperationFailedError
        The operation failed, was cancelled, or timed out on the server.
    OperationTimeoutError
        ``timeout`` elapsed first; the operation may still finish.
    NotFoundError
        The operation does not exist in this workspace.
    """
    op_id, workspace, wait_timeout, interval = _validated(operation_id, workspace_id, timeout, poll_interval)
    getter = _operation_getter(client)
    try:
        return poll_until(
            lambda: getter(op_id, workspace_id=workspace, request_options=request_options),
            _status_of,
            timeout=wait_timeout,
            poll_interval=interval,
            on_update=on_update,
            operation_id=op_id,
        )
    except OperationFailedError as exc:
        if raise_on_failure:
            raise
        return exc.operation


async def wait_for_compute_operation_async(
    client: typing.Any,
    operation_id: str,
    *,
    workspace_id: str,
    timeout: float = DEFAULT_WAIT_TIMEOUT_SECONDS,
    poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
    raise_on_failure: bool = True,
    on_update: typing.Optional[typing.Callable[["OperationStatus"], typing.Any]] = None,
    request_options: typing.Optional["RequestOptions"] = None,
) -> "OperationStatus":
    """Async variant of :func:`wait_for_compute_operation` for ``AsyncIbee`` clients."""
    op_id, workspace, wait_timeout, interval = _validated(operation_id, workspace_id, timeout, poll_interval)
    getter = _operation_getter(client)
    try:
        return await apoll_until(
            lambda: getter(op_id, workspace_id=workspace, request_options=request_options),
            _status_of,
            timeout=wait_timeout,
            poll_interval=interval,
            on_update=on_update,
            operation_id=op_id,
        )
    except OperationFailedError as exc:
        if raise_on_failure:
            raise
        return exc.operation


__all__ = [
    "FAILURE_STATUSES",
    "MAX_CONSECUTIVE_POLL_FAILURES",
    "SUCCESS_STATUSES",
    "apoll_until",
    "is_transient_poll_error",
    "poll_until",
    "wait_for_compute_operation",
    "wait_for_compute_operation_async",
]
