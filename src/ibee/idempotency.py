"""Idempotency keys, compatible with the keys the IBEE portal generates.

Only some public routes honour an idempotency key:

* the 22 cloud/GPU VM writes, through the ``X-Idempotency-Key`` header;
* block-storage volume create/attach/detach/resize, through the ``idempotency_key`` body field;
* block-storage volume delete, through the ``idempotency_key`` query parameter.

The SDK fills a key automatically on those routes when the caller does not pass
one, reuses the same key on every transport retry, and records it on any raised
error as ``error.idempotency_key`` so the caller can retry the logical call safely.
"""

from __future__ import annotations

import re
import typing
import uuid
from urllib.parse import unquote

from .validation import normalize_api_path

IDEMPOTENCY_HEADER = "X-Idempotency-Key"
MAX_IDEMPOTENCY_KEY_LENGTH = 128

VE_KEYED_ROUTE = re.compile(
    r"^/?compute/(cloud-vms|gpu-vms)(/[^/]+(/actions/"
    r"(start|stop|reboot|access|resize|resize-plan|resize-root-disk|attach-volume|detach-volume))?)?/?$"
)
BLOCK_STORAGE_BODY_KEYED_ROUTE = re.compile(r"^/?block-storage/volumes(/[^/]+/(attachments|detach|resize))?/?$")
BLOCK_STORAGE_QUERY_KEYED_ROUTE = re.compile(r"^/?block-storage/volumes/[^/]+/?$")

_UNSAFE_SEGMENT_CHARS = re.compile(r"[^A-Za-z0-9_-]")
_BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"


def _sanitize(value: str) -> str:
    return _UNSAFE_SEGMENT_CHARS.sub("", value)


def _base36(value: int) -> str:
    if value == 0:
        return "0"
    digits = []
    while value:
        value, remainder = divmod(value, 36)
        digits.append(_BASE36[remainder])
    return "".join(reversed(digits))


def fnv1a36(value: str) -> str:
    """32-bit FNV-1a over UTF-16 code units, in base 36 (identical to the portal's hash)."""
    data = value.encode("utf-16-le", "surrogatepass")
    h = 0x811C9DC5
    for index in range(0, len(data), 2):
        h ^= data[index] | (data[index + 1] << 8)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return _base36(h)


def _trim(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    digest = fnv1a36(value)
    return f"{value[: max(0, max_length - len(digest) - 1)]}-{digest}"


def _raw_parts(parts: typing.Iterable[typing.Any]) -> str:
    return "-".join(str(part).strip() for part in parts if part is not None and str(part).strip())


def build_idempotency_key(scope: str, *parts: typing.Any) -> str:
    """Build a fresh key ``<scope>-<parts>-<hash>-<random16>`` (at most 128 characters).

    Every call returns a different key. Reuse the returned key to retry the same
    logical operation.
    """
    raw = _raw_parts(parts)
    segments = [
        _trim(_sanitize(scope or "") or "request", 32),
        _trim(_sanitize(raw), 48),
        fnv1a36(raw) if raw else None,
        uuid.uuid4().hex[:16],
    ]
    return "-".join(segment for segment in segments if segment)[:MAX_IDEMPOTENCY_KEY_LENGTH]


def build_stable_idempotency_key(scope: str, *parts: typing.Any) -> str:
    """Build a deterministic key: the same scope and parts always give the same key."""
    raw = _raw_parts(parts)
    segments = [
        _trim(_sanitize(scope or "") or "request", 32),
        _trim(_sanitize(raw), 64),
        fnv1a36(raw) if raw else "empty",
    ]
    return "-".join(segment for segment in segments if segment)[:MAX_IDEMPOTENCY_KEY_LENGTH]


def _header_value(headers: typing.Optional[typing.Mapping[str, typing.Any]], name: str) -> typing.Optional[str]:
    if not headers:
        return None
    lowered = name.lower()
    for key, value in headers.items():
        if isinstance(key, str) and key.lower() == lowered and value is not None:
            return str(value)
    return None


def _non_empty(value: typing.Any) -> typing.Optional[str]:
    if value is None:
        return None
    text = str(value)
    return text if text.strip() else None


def ve_auto_key_scope(
    method: str, path: typing.Optional[str], json_body: typing.Any = None
) -> typing.Optional[typing.Tuple[str, typing.Optional[str]]]:
    """For a keyed VM write, return ``(scope, identity)`` used to build its automatic key.

    ``scope`` is ``<cloud|gpu>-vm-<action>``; identity is the VM id (or the VM name
    for create). Returns ``None`` for any other request.
    """
    match = VE_KEYED_ROUTE.fullmatch(normalize_api_path(path).lstrip("/"))
    if match is None:
        return None
    family = "cloud" if match.group(1) == "cloud-vms" else "gpu"
    vm_segment = match.group(2)
    action = match.group(4)
    method = method.upper()
    if vm_segment is None:
        if method != "POST":
            return None
        name = json_body.get("name") if isinstance(json_body, dict) else None
        return f"{family}-vm-create", (str(name) if name is not None else None)
    vm_id = unquote(vm_segment.split("/")[1])
    if action is None:
        return (f"{family}-vm-delete", vm_id) if method == "DELETE" else None
    if method not in ("POST", "PATCH"):
        return None
    return f"{family}-vm-{action}", vm_id


def find_idempotency_key(
    method: str,
    path: typing.Optional[str],
    headers: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    json_body: typing.Any = None,
    params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
) -> typing.Optional[str]:
    """Return the non-empty idempotency key this request carries on a route that honours it."""
    method = method.upper()
    relative = normalize_api_path(path).lstrip("/")
    if method in ("POST", "PATCH", "DELETE") and VE_KEYED_ROUTE.fullmatch(relative):
        key = _non_empty(_header_value(headers, IDEMPOTENCY_HEADER))
        if key is not None:
            return key
    if method == "POST" and BLOCK_STORAGE_BODY_KEYED_ROUTE.fullmatch(relative) and isinstance(json_body, dict):
        key = _non_empty(json_body.get("idempotency_key"))
        if key is not None:
            return key
    if method == "DELETE" and BLOCK_STORAGE_QUERY_KEYED_ROUTE.fullmatch(relative) and params:
        key = _non_empty(params.get("idempotency_key"))
        if key is not None:
            return key
    return None


def any_idempotency_key(
    headers: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    json_body: typing.Any = None,
    params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
) -> typing.Optional[str]:
    """The key a request carries in any location, whether or not the route honours it."""
    key = _non_empty(_header_value(headers, IDEMPOTENCY_HEADER))
    if key is None and isinstance(json_body, dict):
        key = _non_empty(json_body.get("idempotency_key"))
    if key is None and params:
        key = _non_empty(params.get("idempotency_key"))
    return key


__all__ = [
    "BLOCK_STORAGE_BODY_KEYED_ROUTE",
    "BLOCK_STORAGE_QUERY_KEYED_ROUTE",
    "IDEMPOTENCY_HEADER",
    "MAX_IDEMPOTENCY_KEY_LENGTH",
    "VE_KEYED_ROUTE",
    "any_idempotency_key",
    "build_idempotency_key",
    "build_stable_idempotency_key",
    "find_idempotency_key",
    "fnv1a36",
    "ve_auto_key_scope",
]
