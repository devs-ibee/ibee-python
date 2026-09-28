"""Base class for errors raised by the SDK itself (not by an HTTP response)."""

from __future__ import annotations

import typing


class IbeeError(Exception):
    """Base class for SDK-originated, non-HTTP errors.

    Attributes
    ----------
    code : str
        Stable lower-case snake_case identifier for the error condition.
    message : str
        Human-readable description. ``str(error)`` returns this value.
    """

    code: str = "ibee_error"

    def __init__(self, message: str, *, code: typing.Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code

    def __str__(self) -> str:
        return self.message
