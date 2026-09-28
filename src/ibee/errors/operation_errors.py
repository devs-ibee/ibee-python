# Hand-written (listed in .fernignore).
"""Errors raised while waiting for asynchronous compute operations."""

from __future__ import annotations

import typing

from .ibee_error import IbeeError


def _attr(operation: typing.Any, name: str) -> typing.Any:
    if operation is None:
        return None
    if isinstance(operation, typing.Mapping):
        return operation.get(name)
    return getattr(operation, name, None)


class OperationFailedError(IbeeError):
    """The operation ended ``failed``, ``cancelled`` or ``timed_out`` on the server."""

    code = "operation_failed"

    def __init__(self, operation: typing.Any) -> None:
        self.operation = operation
        self.operation_id: typing.Optional[str] = _attr(operation, "operation_id")
        self.vm_id: typing.Optional[str] = _attr(operation, "vm_id")
        self.action: typing.Optional[str] = _attr(operation, "action")
        self.status: typing.Optional[str] = _attr(operation, "status")
        self.error_code: typing.Optional[str] = _attr(operation, "error_code")
        self.error_message: typing.Optional[str] = _attr(operation, "error_message")
        detail = ": ".join(str(part) for part in (self.error_code, self.error_message) if part)
        message = f"{self.action or 'operation'} {self.status} for {self.vm_id or 'resource'}"
        if detail:
            message += f": {detail}"
        message += f" (operation {self.operation_id})"
        super().__init__(message)


class OperationTimeoutError(IbeeError, TimeoutError):
    """The client stopped waiting before the operation reached a terminal status.

    This is different from the server-side ``timed_out`` status (which raises
    ``OperationFailedError``). The operation may still complete; resume waiting
    with the same ``operation_id``.
    """

    code = "operation_wait_timeout"

    def __init__(
        self,
        operation: typing.Any,
        *,
        timeout: float,
        operation_id: typing.Optional[str] = None,
    ) -> None:
        self.operation = operation
        self.operation_id = operation_id or _attr(operation, "operation_id")
        self.last_status: typing.Optional[str] = _attr(operation, "status")
        self.timeout = timeout
        action = _attr(operation, "action") or "operation"
        message = (
            f"{action} still {self.last_status or 'pending'} after {timeout:g}s "
            f"(operation {self.operation_id})"
        )
        IbeeError.__init__(self, message)


__all__ = ["OperationFailedError", "OperationTimeoutError"]
