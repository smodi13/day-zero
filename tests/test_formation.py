"""Formation-state semantics and history preservation."""
from datetime import date

from dayzero.config import load
from dayzero.formation import compute_state, history, mark_stale
from dayzero.signals import DerivedSignal


def S(t, fam, day, chan="github", status="OBSERVED"):
    return DerivedSignal(t, fam, "r", "repository", day, chan, status, "")


def test_forming_requires_two_independent_channels():
    same_channel = [S("F-01", "FORMATION", "2026-01-01"), S("F-02", "FORMATION", "2026-02-01")]
    assert compute_state(same_channel, author_resolved=True).state != "FORMING"
    two = [S("F-01", "FORMATION", "2026-01-01", "web"),
           S("F-02", "FORMATION", "2026-02-01", "github")]
    assert compute_state(two, author_resolved=True).state == "FORMING"


def test_same_day_coordinated_launch_counts_as_one_channel():
    """Phase 1 near-miss NM-1: simultaneity is the tell."""
    same_day = [S("F-01", "FORMATION", "2026-06-24", "web"),
                S("F-02", "FORMATION", "2026-06-24", "github")]
    assert compute_state(same_day, author_resolved=True).state != "FORMING"


def test_building_requires_build_and_depth_and_a_resolved_author():
    sigs = [S("B-01", "BUILD", "2026-01-01"), S("D-01", "TECHNICAL_DEPTH", "2026-01-01")]
    assert compute_state(sigs, author_resolved=True).state == "BUILDING"
    assert compute_state(sigs, author_resolved=False).state == "UNKNOWN"


def test_history_is_preserved_not_collapsed():
    sigs = [S("B-01", "BUILD", "2026-01-01"), S("D-01", "TECHNICAL_DEPTH", "2026-01-02"),
            S("C-04", "COLLABORATION", "2026-03-01"),
            S("F-01", "FORMATION", "2026-05-01", "web"),
            S("F-02", "FORMATION", "2026-06-01", "github")]
    h = history(sigs, author_resolved=True)
    states = [x.state for x in h]
    assert states == ["BUILDING", "COLLABORATING", "FORMING"]
    assert [x.as_of for x in h] == sorted(x.as_of for x in h)


def test_later_state_does_not_overwrite_earlier_rows(conn):
    rows = conn.execute(
        "SELECT project_id, COUNT(*) n FROM formation_state_history"
        " GROUP BY project_id HAVING n > 1").fetchall()
    assert len(rows) > 0, "at least one subject should have a multi-step history"


def test_negative_velocity_never_supports_a_state():
    sigs = [S("B-01", "BUILD", "2026-01-01"), S("D-01", "TECHNICAL_DEPTH", "2026-01-01"),
            S("V-06", "VELOCITY", "2026-02-01")]
    st = compute_state(sigs, author_resolved=True)
    assert "V-06" not in st.supporting


def test_construction_evidence_never_decays():
    sigs = [S("B-01", "BUILD", "2020-01-01"), S("D-01", "TECHNICAL_DEPTH", "2020-01-01")]
    stale = mark_stale(sigs, date(2026, 8, 23))
    assert stale["B-01"] is False and stale["D-01"] is False


def test_formation_evidence_goes_stale():
    stale = mark_stale([S("F-01", "FORMATION", "2020-01-01", "web")], date(2026, 8, 23))
    assert stale["F-01"] is True


def test_forbidden_inferences_are_declared():
    f = set(load("formation_states.yaml")["forbidden_inferences"])
    assert {"departure_from_silence", "departure_from_bio_edit",
            "founding_probability", "career_stage_from_account_age"} <= f
