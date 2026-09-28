# Hand-written (listed in .fernignore).
"""Typed errors for networking operations."""

from __future__ import annotations

import typing

from .not_found_error import NotFoundError

RESERVED_IP_TARGET_UNSUPPORTED_MESSAGE = (
    "This VM has no VPC attachment. Use reserved_ips.convert_vm_public_ip_to_reserved_ip to keep its current "
    "public IP; attaching a held Reserved IP to a non-VPC VM is not yet available in the public API."
)
_VPC_ALLOCATION_MARKER = "require a vpc network allocation"


class ReservedIpTargetUnsupportedError(NotFoundError):
    """404 from Reserved IP attach/move because the target VM has no VPC network allocation.

    Subclasses ``NotFoundError`` so 0.3.0 handlers keep working; ``message``
    explains what to do instead.
    """

    code = "reserved_ip_target_unsupported"

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        self.code = "reserved_ip_target_unsupported"
        self.message = RESERVED_IP_TARGET_UNSUPPORTED_MESSAGE

    def __str__(self) -> str:
        return f"{RESERVED_IP_TARGET_UNSUPPORTED_MESSAGE} (status_code: {self.status_code}, body: {self.body})"


def is_vpc_allocation_required(error: BaseException) -> bool:
    """Whether a 404 says the Reserved IP target needs a VPC network allocation."""
    if not isinstance(error, NotFoundError):
        return False
    texts = [getattr(error, "message", None), str(getattr(error, "raw_body", "") or "")]
    return any(isinstance(text, str) and _VPC_ALLOCATION_MARKER in text.lower() for text in texts)


def as_reserved_ip_target_error(error: NotFoundError) -> ReservedIpTargetUnsupportedError:
    converted = ReservedIpTargetUnsupportedError(headers=error.headers, body=error.body)
    converted._populate(getattr(error, "raw_body", error.body))
    converted.idempotency_key = getattr(error, "idempotency_key", None)
    return converted
