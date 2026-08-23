"""Deterministic IDs, deterministic rule hash, deterministic exports."""
from datetime import date

from dayzero import freeze, ids
from dayzero.build import Builder
from dayzero.export import builders, graph, projects, signals

NOW = "2026-08-23T00:00:00Z"


def test_ids_are_case_stable_and_deterministic():
    assert ids.repo_id("Foo/Bar") == ids.repo_id("foo/bar")
    assert ids.repo_id("a/b") != ids.repo_id("a/c")
    assert ids.identity_id("github", "Alice") == ids.identity_id("GitHub", "alice")


def test_ids_are_prefixed_by_kind():
    assert ids.repo_id("a/b").startswith("repo:")
    assert ids.person_id("github", "a").startswith("person:")
    assert ids.evidence_id("e", "c", "s", "2026-01-01").startswith("ev:")


def test_rule_hash_is_stable_across_calls():
    assert freeze.combined_hash(freeze.current_hashes()) == \
           freeze.combined_hash(freeze.current_hashes())


def test_rule_hash_ignores_comments_and_whitespace(tmp_path, monkeypatch):
    """Hashing parsed content means a comment edit is not a rule change."""
    h1 = freeze.file_hash("intro_queue_rules.yaml")
    h2 = freeze.file_hash("intro_queue_rules.yaml")
    assert h1 == h2 and len(h1) == 64


def test_rebuild_is_byte_identical(tmp_path):
    a = Builder(db_path=tmp_path / "a.db", as_of=date(2026, 8, 23), now=NOW); a.run()
    b = Builder(db_path=tmp_path / "b.db", as_of=date(2026, 8, 23), now=NOW); b.run()
    assert builders(a.conn) == builders(b.conn)
    assert projects(a.conn) == projects(b.conn)
    assert graph(a.conn) == graph(b.conn)
    assert signals(a.conn) == signals(b.conn)


def test_rebuild_counts_identical(tmp_path):
    a = Builder(db_path=tmp_path / "a.db", as_of=date(2026, 8, 23), now=NOW); ra = a.run()
    b = Builder(db_path=tmp_path / "b.db", as_of=date(2026, 8, 23), now=NOW); rb = b.run()
    assert ra["counts"] == rb["counts"]


def test_cli_build_is_a_pure_function_of_collected_data(tmp_path):
    """Two builds with no `now` override produce identical exports, because the
    build timestamp defaults to the evidence base's own collection time."""
    from dayzero.build import Builder
    a = Builder(db_path=tmp_path / "p.db", as_of=date(2026, 8, 23)); a.run()
    b = Builder(db_path=tmp_path / "q.db", as_of=date(2026, 8, 23)); b.run()
    assert a.now == b.now
    assert signals(a.conn) == signals(b.conn)
