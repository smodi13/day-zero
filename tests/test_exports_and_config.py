"""Canonical export validation and config well-formedness."""
import json

import yaml

from dayzero.config import CONFIG_DIR, FROZEN_RULE_FILES, load
from dayzero.export import builders, cost_ledger, graph, projects, signals


def test_every_config_file_parses():
    for p in sorted(CONFIG_DIR.glob("*.yaml")):
        assert isinstance(yaml.safe_load(p.read_text(encoding="utf-8")), dict), p.name


def test_every_frozen_rule_file_exists():
    for name in FROZEN_RULE_FILES:
        assert (CONFIG_DIR / name).exists(), name


def test_signal_types_reference_declared_families():
    cfg = load("signal_types.yaml")
    families = set(cfg["families"])
    for sid, s in cfg["signals"].items():
        assert s["family"] in families, sid


def test_attention_fields_are_barred_in_config():
    barred = set(load("signal_types.yaml")["barred_from_surfacing"])
    assert {"stars", "forks", "followers"} <= barred


def test_projects_export_separates_attention_and_construction(conn):
    rows = projects(conn)
    assert rows
    r = rows[0]
    assert set(r["attention"]) == {"stars", "forks", "watchers", "open_issues"}
    assert "stars" not in r["construction"]


def test_graph_edges_reference_known_nodes(conn):
    g = graph(conn)
    node_ids = {n["id"] for n in g["nodes"]}
    dangling = [e for e in g["edges"]
                if e["from_id"] not in node_ids and e["to_id"] not in node_ids]
    assert dangling == []


def test_graph_edge_kinds_are_from_the_declared_vocabulary(conn):
    allowed = {"BUILT", "MAINTAINS", "CONTRIBUTED_TO", "AUTHORED", "COAUTHORED_WITH",
               "MEMBER_OF", "FOUNDED", "PARTICIPATED_IN", "ANNOUNCED",
               "COLLABORATED_WITH", "LINKED_TO", "OWNED_BY", "IMPLEMENTS"}
    kinds = {e["kind"] for e in graph(conn)["edges"]}
    assert kinds <= allowed, f"unexpected edge kinds: {kinds - allowed}"


def test_builders_export_is_json_serializable(conn):
    json.dumps(builders(conn))
    json.dumps(signals(conn))
    json.dumps(cost_ledger(conn))


def test_exports_are_sorted_for_reproducibility(conn):
    names = [r["full_name"] for r in projects(conn)]
    assert names == sorted(names)
