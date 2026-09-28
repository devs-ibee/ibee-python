"""Auto-paging helpers for list endpoints that return one page at a time.

Several list endpoints return at most one page (10 items by default for VMs and
firewall groups) and no total count. The ``iter_*`` methods and the ``list_*``
methods called without ``limit``/``offset`` use these helpers to fetch every page.
"""

from __future__ import annotations

import typing

T = typing.TypeVar("T")

DEFAULT_PAGE_SIZE = 100
DEFAULT_MAX_ITEMS = 10_000


def _value(item: typing.Any, key: str) -> typing.Any:
    if isinstance(item, typing.Mapping):
        return item.get(key)
    value = getattr(item, key, None)
    if value is None:
        extra = getattr(item, "model_extra", None)
        if isinstance(extra, dict):
            value = extra.get(key)
    if value is None:
        extra_v1 = getattr(item, "__dict__", None)
        if isinstance(extra_v1, dict):
            value = extra_v1.get(key)
    return value


def item_id(item: typing.Any, id_keys: typing.Sequence[str]) -> typing.Optional[str]:
    """The first present identifier of ``item`` among ``id_keys``, as a string."""
    for key in id_keys:
        value = _value(item, key)
        if value is not None and str(value) != "":
            return str(value)
    return None


def _items_of(page: typing.Any, items_key: str) -> typing.List[typing.Any]:
    if isinstance(page, list):
        return page
    value = _value(page, items_key)
    return list(value) if value else []


def paginate_offset(
    fetch_page: typing.Callable[[int, int], typing.Sequence[T]],
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    id_keys: typing.Sequence[str] = ("_id", "id"),
    max_items: int = DEFAULT_MAX_ITEMS,
    start_offset: int = 0,
) -> typing.Iterator[T]:
    """Yield every item from an ``offset``/``limit`` endpoint.

    ``fetch_page(limit, offset)`` returns one page. Paging stops at a short or
    empty page, or after ``max_items`` items. Items already seen (by the first
    present key in ``id_keys``) are skipped, because newest-first ordering shifts
    when resources are created while paging.
    """
    offset = start_offset
    seen: typing.Set[str] = set()
    produced = 0
    while True:
        items = list(fetch_page(page_size, offset))
        for item in items:
            identifier = item_id(item, id_keys)
            if identifier is not None:
                if identifier in seen:
                    continue
                seen.add(identifier)
            yield item
            produced += 1
            if produced >= max_items:
                return
        if len(items) < page_size or not items:
            return
        offset += len(items)


async def apaginate_offset(
    fetch_page: typing.Callable[[int, int], typing.Awaitable[typing.Sequence[T]]],
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    id_keys: typing.Sequence[str] = ("_id", "id"),
    max_items: int = DEFAULT_MAX_ITEMS,
    start_offset: int = 0,
) -> typing.AsyncIterator[T]:
    """Async variant of :func:`paginate_offset`."""
    offset = start_offset
    seen: typing.Set[str] = set()
    produced = 0
    while True:
        items = list(await fetch_page(page_size, offset))
        for item in items:
            identifier = item_id(item, id_keys)
            if identifier is not None:
                if identifier in seen:
                    continue
                seen.add(identifier)
            yield item
            produced += 1
            if produced >= max_items:
                return
        if len(items) < page_size or not items:
            return
        offset += len(items)


def _should_stop(page_number: int, limit: int, count: int, total: typing.Any) -> bool:
    if count == 0:
        return True
    if isinstance(total, int) and not isinstance(total, bool):
        return page_number * limit >= total
    return count < limit


def paginate_pages(
    fetch: typing.Callable[[int, int], typing.Any],
    *,
    limit: int,
    items_key: str,
    total_key: str = "total",
    start_page: int = 1,
) -> typing.Iterator[typing.Any]:
    """Yield every item from a ``page``/``limit`` endpoint whose envelope carries a total.

    ``fetch(page, limit)`` returns the envelope; items are read from ``items_key``.
    Paging stops when ``page * limit >= total`` or a page is empty.
    """
    page_number = start_page
    while True:
        envelope = fetch(page_number, limit)
        items = _items_of(envelope, items_key)
        for item in items:
            yield item
        if _should_stop(page_number, limit, len(items), _value(envelope, total_key)):
            return
        page_number += 1


async def apaginate_pages(
    fetch: typing.Callable[[int, int], typing.Awaitable[typing.Any]],
    *,
    limit: int,
    items_key: str,
    total_key: str = "total",
    start_page: int = 1,
) -> typing.AsyncIterator[typing.Any]:
    """Async variant of :func:`paginate_pages`."""
    page_number = start_page
    while True:
        envelope = await fetch(page_number, limit)
        items = _items_of(envelope, items_key)
        for item in items:
            yield item
        if _should_stop(page_number, limit, len(items), _value(envelope, total_key)):
            return
        page_number += 1


async def acollect(iterator: typing.AsyncIterator[T]) -> typing.List[T]:
    """Collect an async iterator into a list."""
    return [item async for item in iterator]


__all__ = [
    "DEFAULT_MAX_ITEMS",
    "DEFAULT_PAGE_SIZE",
    "acollect",
    "apaginate_offset",
    "apaginate_pages",
    "item_id",
    "paginate_offset",
    "paginate_pages",
]
