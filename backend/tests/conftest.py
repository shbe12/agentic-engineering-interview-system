"""Shared fakes for tests that would otherwise hit Supabase/OpenAI/ElevenLabs."""

import pytest


class FakeQuery:
    """Minimal stand-in for supabase-py's fluent query builder."""

    def __init__(self, table: "FakeTable", op: str, payload=None):
        self.table = table
        self.op = op
        self.payload = payload
        self.filters: dict = {}
        self.want_single = False

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def order(self, *_args, **_kwargs):
        return self

    def select(self, *_args, **_kwargs):
        return self

    def single(self):
        self.want_single = True
        return self

    def maybe_single(self):
        self.want_single = True
        return self

    def upsert(self, payload, on_conflict=None):
        self.op = "upsert"
        self.payload = payload
        if on_conflict:
            for key in on_conflict.split(","):
                self.filters[key] = payload.get(key)
        return self

    def execute(self):
        return self.table._run(self)


class FakeResult:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, db: "FakeSupabase", name: str):
        self.db = db
        self.name = name

    def insert(self, payload):
        return FakeQuery(self, "insert", payload)

    def select(self, *_args, **_kwargs):
        return FakeQuery(self, "select")

    def update(self, payload):
        return FakeQuery(self, "update", payload)

    def upsert(self, payload, on_conflict=None):
        return FakeQuery(self, "insert").upsert(payload, on_conflict)

    def _run(self, query: FakeQuery):
        return self.db.run(self.name, query)


class FakeSupabase:
    """Records rows per table in memory; enough for orchestrator/evaluator unit tests."""

    def __init__(self):
        self.rows: dict[str, list[dict]] = {}
        self._next_id = 1

    def table(self, name: str) -> FakeTable:
        self.rows.setdefault(name, [])
        return FakeTable(self, name)

    def run(self, table_name: str, query: FakeQuery) -> FakeResult:
        rows = self.rows[table_name]

        if query.op == "insert":
            row = dict(query.payload)
            row.setdefault("id", f"{table_name}-{self._next_id}")
            self._next_id += 1
            rows.append(row)
            return FakeResult([row])

        if query.op in ("update", "upsert"):
            matches = [r for r in rows if all(r.get(k) == v for k, v in query.filters.items())]
            if matches:
                matches[0].update(query.payload)
                return FakeResult(matches)
            row = dict(query.payload)
            row.setdefault("id", f"{table_name}-{self._next_id}")
            self._next_id += 1
            rows.append(row)
            return FakeResult([row])

        # select
        matches = [r for r in rows if all(r.get(k) == v for k, v in query.filters.items())]
        if query.want_single:
            return FakeResult(matches[0] if matches else None)
        return FakeResult(matches)


@pytest.fixture
def fake_supabase(monkeypatch):
    fake = FakeSupabase()
    # Each module does `from app.db.client import get_supabase`, binding its own
    # local name at import time — patch every call site, not just the source.
    for target in (
        "app.db.client.get_supabase",
        "app.interview.orchestrator.get_supabase",
        "app.evaluation.evaluator.get_supabase",
        "app.evaluation.report.get_supabase",
        "app.routes.resume.get_supabase",
    ):
        monkeypatch.setattr(target, lambda: fake)
    return fake
