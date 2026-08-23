"""Phase 1 fixtures must remain recoverable, and the prestige trap must stay shut."""
from datetime import date

from dayzero import ids
from dayzero.negative_controls import _candidate_from_repo
from dayzero.review import evaluate

# Verified Phase 1 leads. Each must still be present and still carry real signals,
# unless an explicit status rule removes it (which the test would then show).
PHASE1_LEADS = [
    "multikernel/kernelscript",
    "vivekchand/clawmetry",
    "getagentseal/codeburn",
    "linnix-os/linnix",
    "spinningfactory/kloak",
    "eunomia-bpf/agentsight",
    "shepherd-agents/shepherd",
    "deeplethe/forkd",
    "Karib0u/rustinel",
    "h5i-dev/h5i",
]

NEGATIVE_CONTROL_REPOS = [
    "0xSero/turboquant",
    "zerobootdev/zeroboot",
    "dipampaul17/KVSplit",
    "scrya-com/rotorquant",
    "RyanCodrai/turbovec",
    "FutureMLS-Lab/OSCAR",
]


def test_phase1_leads_are_still_in_the_universe(conn):
    missing = [r for r in PHASE1_LEADS if not conn.execute(
        "SELECT 1 FROM repositories WHERE full_name=?", (r,)).fetchone()]
    assert missing == [], f"Phase 1 leads dropped out of collection: {missing}"


def test_phase1_leads_still_carry_technical_signals(conn):
    weak = []
    for full_name in PHASE1_LEADS:
        rid = ids.repo_id(full_name)
        n = conn.execute("SELECT COUNT(*) FROM technical_signals WHERE subject_id=?",
                         (rid,)).fetchone()[0]
        if n == 0:
            weak.append(full_name)
    assert weak == [], f"no technical signals derived for: {weak}"


def test_negative_control_repos_are_present_for_evaluation(conn):
    missing = [r for r in NEGATIVE_CONTROL_REPOS if not conn.execute(
        "SELECT 1 FROM repositories WHERE full_name=?", (r,)).fetchone()]
    assert missing == [], f"controls missing from collection: {missing}"


def test_frontier_lab_engineer_with_stars_cannot_be_intro_ready(built, conn):
    """NC-5. A frontier-lab employer plus a 16k-star repo plus zero formation
    evidence must NOT promote. This is the regression fixture that matters most."""
    subject = "RyanCodrai/turbovec"
    cand = _candidate_from_repo(conn, subject, built.signal_index, date(2026, 8, 23))
    assert cand is not None
    d = evaluate(cand, date(2026, 8, 23))
    assert d.state != "INTRO_READY", (
        f"prestige + stars promoted a candidate with no formation evidence: {d}")


def test_employer_field_is_never_a_formation_signal(conn):
    """No F-xx signal may be justified by an employer/company field."""
    rows = conn.execute(
        "SELECT observed_claim FROM evidence WHERE claim_class='formation'").fetchall()
    for (claim,) in rows:
        low = (claim or "").lower()
        assert "works at" not in low and "employed" not in low


def test_high_star_low_commit_repo_is_not_promoted(built, conn):
    cand = _candidate_from_repo(conn, "0xSero/turboquant", built.signal_index,
                                date(2026, 8, 23))
    if cand is None:
        return
    d = evaluate(cand, date(2026, 8, 23))
    assert d.state != "INTRO_READY"
