# Hand-written (listed in .fernignore).
"""Typed errors for VM resize conflicts and recovery (snapshot / backup) jobs."""

from __future__ import annotations

import typing

from .conflict_error import ConflictError
from .operation_errors import OperationFailedError, _attr


class ResizeBlockedError(ConflictError):
    """409 from a resize whose precheck is not ``in_place``.

    ``decision`` is ``migration_required`` or ``blocked``; ``reasons``, ``warnings``
    and ``migration_checklist`` carry the server's explanation.
    """

    decision: typing.Optional[str] = None
    reasons: typing.List[typing.Any] = []
    warnings: typing.List[typing.Any] = []
    migration_checklist: typing.List[typing.Any] = []

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        detail = raw_body.get("detail") if isinstance(raw_body, dict) else None
        if isinstance(detail, dict):
            self.decision = detail.get("decision")
            self.reasons = list(detail.get("reasons") or [])
            self.warnings = list(detail.get("warnings") or [])
            self.migration_checklist = list(detail.get("migration_checklist") or [])


class RecoveryFailedError(OperationFailedError):
    """A snapshot, backup run or restore ended ``failed`` or ``cancelled``.

    ``resource`` is the final object (``SnapshotSet``, ``BackupRun`` or
    ``RecoveryRestore``); ``resource_id`` is its id.
    """

    code = "recovery_failed"

    def __init__(self, resource: typing.Any, *, kind: str = "recovery job", id_field: str = "restore_id") -> None:
        self.resource = resource
        self.kind = kind
        self.resource_id: typing.Optional[str] = _attr(resource, id_field)
        super().__init__(resource)
        status = self.status or "failed"
        message = f"{kind} {self.resource_id or ''} {status}".replace("  ", " ").strip()
        if self.error_message:
            message += f": {self.error_message}"
        self.message = message
        self.args = (message,)


class RecoveryRestoreFailedError(RecoveryFailedError):
    """A snapshot or backup restore ended ``failed`` or ``cancelled``."""

    code = "recovery_restore_failed"

    def __init__(self, restore: typing.Any) -> None:
        super().__init__(restore, kind="restore", id_field="restore_id")
        self.restore = restore


__all__ = ["RecoveryFailedError", "RecoveryRestoreFailedError", "ResizeBlockedError"]
