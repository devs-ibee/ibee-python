# Hand-written (listed in .fernignore).
"""Typed errors for Block Storage, Object Storage and CDN."""

from __future__ import annotations

import typing

from ..core.api_error import ApiError

CDN_PURGE_FAILED_MESSAGE = "Cache purge failed"


class CdnPurgeFailedError(ApiError):
    """The CDN answered a purge with HTTP 200 but ``success: false``: nothing was purged.

    This commonly happens for ``prefix`` and ``tag`` purges. ``mode`` is the purge
    mode, ``message`` the server's explanation and ``body`` the full result.
    Pass ``raise_on_failure=False`` to ``purge_cdn_cache`` to get the result instead.
    """

    code = "cdn_purge_failed"

    def __init__(
        self,
        body: typing.Any,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        *,
        mode: typing.Optional[str] = None,
    ) -> None:
        self.mode = mode
        super().__init__(status_code=200, headers=headers, body=body)

    def _populate(self, raw_body: typing.Any) -> None:
        super()._populate(raw_body)
        record = raw_body if isinstance(raw_body, dict) else {}
        self.code = "cdn_purge_failed"
        self.mode = getattr(self, "mode", None) or record.get("mode")
        message = record.get("message")
        self.message = str(message).strip() if isinstance(message, str) and message.strip() else CDN_PURGE_FAILED_MESSAGE

    def __str__(self) -> str:
        return f"{self.message} (mode: {self.mode})"


def raise_for_cdn_purge(result: typing.Any) -> typing.Any:
    """Raise :class:`CdnPurgeFailedError` when a purge result says ``success: false``."""
    if isinstance(result, dict) and result.get("success") is False:
        raise CdnPurgeFailedError(result, mode=result.get("mode"))
    return result


__all__ = ["CDN_PURGE_FAILED_MESSAGE", "CdnPurgeFailedError", "raise_for_cdn_purge"]
