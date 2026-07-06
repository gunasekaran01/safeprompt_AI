"""
In-memory stand-in for Supabase's `.table(...)` data layer.

This lets the backend run WITHOUT the Supabase service-role secret key.
Authentication still goes through the real Supabase project (see
supabase_client.py) using the ordinary anon/public key, which is not a
secret and is already checked into frontend/.env -- only the *data*
tables (analyses, reports, profiles, user_settings) are redirected here
instead of to Postgres.

Implements just enough of the PostgREST query-builder surface that
app/db/crud.py, app/services/history_service.py, and
app/services/profile_service.py exercise: `.select()/.insert()/.update()
/.delete()`, `.eq()`, `.ilike()`, `.order()`, `.range()`, `.limit()`, and
`.execute()` returning an object with `.data`/`.count`.

Also mimics the Postgres column defaults declared in supabase/schema.sql
(`id uuid default gen_random_uuid()`, `created_at/generated_at default
now()`) by filling those fields in on insert if the caller didn't
provide them -- the real app code never sets them itself, exactly like
it wouldn't need to against a real Postgres table.

Data lives only for the lifetime of this process (an in-memory dict) and
is lost on restart. That's the trade-off for not needing any database
credentials at all; if you want it to survive restarts, swap this out
for a small SQLite file later.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# Timestamp field name varies by table (mirrors schema.sql's actual
# column names -- `reports` uses `generated_at`, everything else uses
# `created_at`).
_CREATED_AT_FIELD = {"reports": "generated_at"}


class FakeResponse:
    """Mimics the `.data` / `.count` shape of a real supabase-py response."""

    def __init__(self, data: Optional[List[Dict[str, Any]]] = None, count: Optional[int] = None):
        self.data = data or []
        self.count = count


class _LocalQuery:
    def __init__(self, rows: List[Dict[str, Any]], table_name: str):
        self._rows = rows  # same list object the table owns -- mutations persist
        self._table_name = table_name
        self._mode: Optional[str] = None
        self._payload: Optional[Dict[str, Any]] = None
        self._filters: List[Tuple[str, str, Any]] = []
        self._order_field: Optional[str] = None
        self._order_desc: bool = False
        self._range: Optional[Tuple[int, int]] = None
        self._limit_n: Optional[int] = None
        self._count_requested: Optional[str] = None

    def select(self, _columns: str = "*", count: Optional[str] = None) -> "_LocalQuery":
        self._mode = "select"
        self._count_requested = count
        return self

    def insert(self, payload: Dict[str, Any]) -> "_LocalQuery":
        self._mode = "insert"
        self._payload = dict(payload)
        return self

    def update(self, payload: Dict[str, Any]) -> "_LocalQuery":
        self._mode = "update"
        self._payload = dict(payload)
        return self

    def delete(self) -> "_LocalQuery":
        self._mode = "delete"
        return self

    def eq(self, field: str, value: Any) -> "_LocalQuery":
        self._filters.append(("eq", field, value))
        return self

    def ilike(self, field: str, pattern: str) -> "_LocalQuery":
        self._filters.append(("ilike", field, pattern))
        return self

    def order(self, field: str, desc: bool = False) -> "_LocalQuery":
        self._order_field = field
        self._order_desc = desc
        return self

    def range(self, start: int, end: int) -> "_LocalQuery":
        self._range = (start, end)
        return self

    def limit(self, n: int) -> "_LocalQuery":
        self._limit_n = n
        return self

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

    def _apply_defaults(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Fills in id/created_at-style Postgres defaults if missing."""
        row.setdefault("id", str(uuid.uuid4()))
        ts_field = _CREATED_AT_FIELD.get(self._table_name, "created_at")
        now = datetime.now(timezone.utc).isoformat()
        row.setdefault(ts_field, now)
        row.setdefault("updated_at", now)
        return row

    def execute(self) -> FakeResponse:
        if self._mode == "insert":
            row = self._apply_defaults(dict(self._payload or {}))
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
                row["updated_at"] = datetime.now(timezone.utc).isoformat()
            return FakeResponse(data=matched)

        # select
        if self._order_field:
            matched = sorted(
                matched,
                key=lambda row: (row.get(self._order_field) is None, row.get(self._order_field)),
                reverse=self._order_desc,
            )

        total = len(matched)

        if self._range is not None:
            start, end = self._range
            matched = matched[start : end + 1]
        elif self._limit_n is not None:
            matched = matched[: self._limit_n]

        count = total if self._count_requested else None
        return FakeResponse(data=matched, count=count)


class _LocalTable:
    def __init__(self, name: str):
        self._name = name
        self.rows: List[Dict[str, Any]] = []

    def select(self, columns: str = "*", count: Optional[str] = None) -> _LocalQuery:
        return _LocalQuery(self.rows, self._name).select(columns, count)

    def insert(self, payload: Dict[str, Any]) -> _LocalQuery:
        return _LocalQuery(self.rows, self._name).insert(payload)

    def update(self, payload: Dict[str, Any]) -> _LocalQuery:
        return _LocalQuery(self.rows, self._name).update(payload)

    def delete(self) -> _LocalQuery:
        return _LocalQuery(self.rows, self._name).delete()


class LocalDataStore:
    """
    Process-wide in-memory replacement for Supabase's data tables. One
    instance is shared for the life of the running backend (see
    supabase_client.get_supabase_client's lru_cache), so data written in
    one request is visible to the next -- it just doesn't survive a
    restart.
    """

    def __init__(self):
        self._tables: Dict[str, _LocalTable] = {}

    def table(self, name: str) -> _LocalTable:
        if name not in self._tables:
            self._tables[name] = _LocalTable(name)
        return self._tables[name]
