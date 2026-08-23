"""Attention and construction are separate models and never combine."""
import inspect

from dayzero import review, signals


def test_stored_in_separate_tables(conn):
    att = {c[1] for c in conn.execute("PRAGMA table_info(repo_attention)")}
    con = {c[1] for c in conn.execute("PRAGMA table_info(repo_construction)")}
    assert "stars" in att and "stars" not in con
    assert "top_contributions" in con and "top_contributions" not in att


def _code_only(mod) -> str:
    """Source with comments and docstrings stripped, so prose about attention does
    not count as reading attention."""
    import ast
    tree = ast.parse(inspect.getsource(mod))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and ast.get_docstring(node):
            node.body = node.body[1:]
    return ast.unparse(tree)


ATTENTION_ACCESS = ('["attention"]', "['attention']", '"stars"', "'stars'",
                    '"forks"', "'forks'", '"watchers"', "'watchers'",
                    '"followers"', "'followers'")


def test_signal_module_never_reads_attention():
    src = _code_only(signals)
    for banned in ATTENTION_ACCESS:
        assert banned not in src, f"signals.py accesses {banned}"


def test_review_module_never_reads_attention():
    src = _code_only(review)
    for banned in ATTENTION_ACCESS:
        assert banned not in src, f"review.py accesses {banned}"


def test_commit_count_is_not_a_global_score():
    """Commit count gates ONE boolean (sustained construction). It never orders leads."""
    src = inspect.getsource(signals)
    assert "SUSTAINED_MIN_CONTRIBUTIONS" in src
    assert "sorted(" not in inspect.getsource(review.evaluate)


def test_diagnostic_ratio_is_descriptive_only(conn):
    from dayzero.diagnostics import attention_vs_construction
    d = attention_vs_construction(conn)
    assert "Descriptive divergence only" in d["note"]
    assert d["repos_measured"] > 0


def test_known_divergence_examples_survive(conn):
    """Phase 1's finding, re-verified against live data."""
    from dayzero.diagnostics import attention_vs_construction
    d = attention_vs_construction(conn, limit=100)
    hi = {x["repo"]: x for x in d["high_attention_low_construction"]}
    lo = {x["repo"]: x for x in d["low_attention_high_construction"]}
    if "0xSero/turboquant" in hi:
        assert hi["0xSero/turboquant"]["top_contributions"] <= 5
    if "vivekchand/clawmetry" in lo:
        assert lo["vivekchand/clawmetry"]["top_contributions"] > 1000
