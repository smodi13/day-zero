"""Source lineage: a press release re-syndicated four times is one signal, not four."""
from dayzero import ids


def test_sources_table_has_a_lineage_key(conn):
    cols = {c[1] for c in conn.execute("PRAGMA table_info(sources)")}
    assert "underlying_event_key" in cols


def test_same_url_is_one_source_row(conn):
    dupes = conn.execute(
        "SELECT COUNT(*) FROM (SELECT url FROM sources GROUP BY url HAVING COUNT(*)>1)"
    ).fetchone()[0]
    assert dupes == 0


def test_repeated_evidence_from_one_source_does_not_multiply(conn):
    """Evidence ids are a deterministic function of (entity, claim, source, date), so
    re-observing the same fact cannot inflate the count."""
    a = ids.evidence_id("e", "c", "s", "2026-01-01")
    b = ids.evidence_id("e", "c", "s", "2026-01-01")
    assert a == b


def test_convergence_collapses_a_coordinated_same_day_announcement():
    from dayzero.signals import DerivedSignal, convergence
    sigs = [DerivedSignal("B-01", "BUILD", "r", "repository", "2026-06-24", "github", "OBSERVED", ""),
            DerivedSignal("F-01", "FORMATION", "r", "repository", "2026-06-24", "web", "OBSERVED", ""),
            DerivedSignal("F-02", "FORMATION", "o", "organization", "2026-06-24", "github", "OBSERVED", "")]
    c = convergence(sigs)
    assert c["channel_count"] == 1, "same-day multi-surface launch is one channel"
    assert c["converged"] is False


def test_convergence_accepts_temporally_spread_channels():
    from dayzero.signals import DerivedSignal, convergence
    sigs = [DerivedSignal("B-01", "BUILD", "r", "repository", "2025-07-14", "github", "OBSERVED", ""),
            DerivedSignal("F-01", "FORMATION", "r", "repository", "2025-03-08", "web", "OBSERVED", "")]
    assert convergence(sigs)["converged"] is True


def test_convergence_requires_both_families():
    from dayzero.signals import DerivedSignal, convergence
    only_build = [DerivedSignal("B-01", "BUILD", "r", "repository", "2025-01-01", "github", "OBSERVED", ""),
                  DerivedSignal("B-02", "BUILD", "r", "repository", "2025-06-01", "web", "OBSERVED", "")]
    assert convergence(only_build)["converged"] is False
