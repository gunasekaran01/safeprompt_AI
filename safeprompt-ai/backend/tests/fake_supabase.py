"""
In-memory stand-in for `supabase.Client`, used by the test suite instead
of a real Supabase project.

Implements just enough of the PostgREST query-builder surface that
app/db/crud.py exercises — `.table().select()/.insert()/.delete()`,
`.eq()`, `.ilike()`, `.order()`, `.range()`, `.limit()`, and `.execute()`
returning an object with `.data` / `.count` — so crud.py's functions run
unmodified against it. This keeps the test suite fast, fully offline, and
free of any dependency on real SUPABASE_URL / SUPABASE_ANON_KEY /
SUPABASE_SERVICE_ROLE_KEY credentials.

Not a full PostgREST reimplementation — only the operations crud.py
actually uses are supported.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


class FakeResponse:
    """Mimics the `.data` / `.count` shape of a real supabase-py response."""

    def __init__(self, data: Optional[List[Dict[str, Any]]] = None, count: Optional[int] = None):
        self.data = data or []
        self.count = count


class _FakeQuery:
    def __init__(self, rows: List[Dict[str, Any]]):
        # Reference to the *same* list object the table owns, so
        # insert/delete mutate the table's actual storage.
        self._rows = rows
        self._mode: Optional[str] = None
        self._payload: Optional[Dict[str, Any]] = None
        self._filters: List[Tuple[str, str, Any]] = []
        self._order_field: Optional[str] = None
        self._order_desc: bool = False
        self._range: Optional[Tuple[int, int]] = None
        self._limit_n: Optional[int] = None
        self._count_requested: Optional[str] = None

    # -- entry points (mirror supabase-py's query builder) ------------------

    def select(self, _columns: str = "*", count: Optional[str] = None) -> "_FakeQuery":
        self._mode = "select"
        self._count_requested = count
        return self

    def insert(self, payload: Dict[str, Any]) -> "_FakeQuery":
        self._mode = "insert"
        self._payload = payload
        return self

    def update(self, payload: Dict[str, Any]) -> "_FakeQuery":
        self._mode = "update"
        self._payload = payload
        return self

    def delete(self) -> "_FakeQuery":
        self._mode = "delete"
        return self

    # -- filters / modifiers --------------------------------------------------

    def eq(self, field: str, value: Any) -> "_FakeQuery":
        self._filters.append(("eq", field, value))
        return self

    def ilike(self, field: str, pattern: str) -> "_FakeQuery":
        self._filters.append(("ilike", field, pattern))
        return self

    def order(self, field: str, desc: bool = False) -> "_FakeQuery":
        self._order_field = field
        self._order_desc = desc
        return self

    def range(self, start: int, end: int) -> "_FakeQuery":
        self._range = (start, end)
        return self

    def limit(self, n: int) -> "_FakeQuery":
        self._limit_n = n
        return self

    # -- execution --------------------------------------------------------

    def _matches(self, row: Dict[str, Any]) -> bool:
        for kind, field, value in self._filters:
            if kind == "eq":
                if row.get(field) != value:
                    return False
            elif kind == "ilike":
                needle = str(value).strip("%").lower()
                if needle not in str(row.get(field, "")).lower():
                    return False
        return True

    def execute(self) -> FakeResponse:
        if self._mode == "insert":
            row = dict(self._payload or {})
            self._rows.append(row)
            return FakeResponse(data=[row])

        matched = [row for row in self._rows if self._matches(row)]

        if self._mode == "delete":
            remaining = [row for row in self._rows if row not in matched]
            self._rows[:] = remaining
            return FakeResponse(data=matched)

        if self._mode == "update":
            for row in matched:
                row.update(self._payload or {})
            return FakeResponse(data=matched)

        # select
        if self._order_field:
            matched = sorted(
                matched, key=lambda row: row.get(self._order_field), reverse=self._order_desc
            )

        total = len(matched)

        if self._range is not None:
            start, end = self._range
            matched = matched[start : end + 1]
        elif self._limit_n is not None:
            matched = matched[: self._limit_n]

        count = total if self._count_requested else None
        return FakeResponse(data=matched, count=count)


class _FakeTable:
    def __init__(self):
        self.rows: List[Dict[str, Any]] = []

    def select(self, columns: str = "*", count: Optional[str] = None) -> _FakeQuery:
        return _FakeQuery(self.rows).select(columns, count)

    def insert(self, payload: Dict[str, Any]) -> _FakeQuery:
        return _FakeQuery(self.rows).insert(payload)

    def update(self, payload: Dict[str, Any]) -> _FakeQuery:
        return _FakeQuery(self.rows).update(payload)

    def delete(self) -> _FakeQuery:
        return _FakeQuery(self.rows).delete()


class _FakePostgrest:
    """No-op stand-in for `Client.postgrest`, just enough to support
    `.auth(access_token)` (used by app.db.supabase_client.get_user_scoped_client)
    without needing a real HTTP client underneath."""

    def auth(self, _access_token: Optional[str]) -> None:
        return None


class FakeSupabaseClient:
    """
    A minimal in-memory stand-in for `supabase.Client`. Each table is an
    isolated in-memory list, created lazily on first access, so a fresh
    `FakeSupabaseClient()` per test gives full isolation between tests.
    """

    def __init__(self):
        self._tables: Dict[str, _FakeTable] = {}
        self.postgrest = _FakePostgrest()

    def table(self, name: str) -> _FakeTable:
        if name not in self._tables:
            self._tables[name] = _FakeTable()
        return self._tables[name]
