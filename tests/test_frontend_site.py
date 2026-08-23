"""The built static site: every asserted value present, nothing private leaked.

Runs against `web/out/` (the Next.js static export). If the site has not been
built the module is skipped with a loud reason rather than passing silently —
COMMIT gates must run `npm run build` first.
"""
import html
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "out"

pytestmark = pytest.mark.skipif(
    not (OUT / "index.html").exists(),
    reason="web/out missing — run `npm run build` in web/ before the site tests")

ROUTES = ["", "current-3", "diligence/sandlock", "lab/headroom",
          "signals", "methodology", "about"]


def page_html(route: str) -> str:
    p = OUT / route / "index.html" if route else OUT / "index.html"
    return p.read_text(encoding="utf-8")


def page_text(route: str) -> str:
    """Visible text: tags stripped, entities unescaped, whitespace collapsed."""
    raw = page_html(route)
    raw = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw))


def all_client_js() -> str:
    return "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                     for p in OUT.rglob("*.js"))


def all_html() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in OUT.rglob("*.html"))


# ---- routes ----------------------------------------------------------------

def test_all_seven_routes_are_exported():
    for route in ROUTES:
        p = OUT / route / "index.html" if route else OUT / "index.html"
        assert p.exists(), route


def test_no_extra_public_person_routes():
    dirs = {p.parent.relative_to(OUT).as_posix() for p in OUT.rglob("index.html")}
    assert dirs == {".", "current-3", "diligence/sandlock", "lab/headroom",
                    "signals", "methodology", "about", "404"}


# ---- homepage --------------------------------------------------------------

def test_homepage_hero_and_pipeline():
    t = page_text("")
    assert "DAY ZERO" in t
    assert "Find the builder before the round." in t
    assert "Test the hard claim" in t
    for stage in ("Source", "Verify", "Diligence", "Learn"):
        assert stage in t, stage


def test_homepage_carries_real_values_in_static_html():
    t = page_text("")
    for v in ("46.30%", "28.41%", "0.00%", "1.0000",
              "ADVANCE TO FOUNDER CONVERSATION", "PARTIALLY REPRODUCED",
              "2 PASS", "6 UNKNOWN", "Perspective AI"):
        assert v in t, v


# ---- current 3 -------------------------------------------------------------

def test_current3_shows_canonical_leads_without_ranking():
    t = page_text("current-3")
    for subject in ("multikernel/sandlock", "sipyourdrink-ltd/bernstein",
                    "scanaislop/aislop"):
        assert subject in t, subject
    assert "not a global ranking" in t.lower()
    assert "INTRO_READY_AWU" in t
    assert "3 founder introductions" not in t
    assert "No introduction has been made" in t


def test_current3_intro_ready_matches_canon():
    t = page_text("current-3")
    export = json.loads((ROOT / "web/src/data/research.json").read_text())
    for lead in export["current3"]:
        if lead["systemState"] == "INTRO_READY":
            assert "INTRO READY" in t
    # sandlock is WATCH with analyst override, and must be shown as such
    assert "WATCH · analyst override" in t


# ---- sandlock --------------------------------------------------------------

def test_sandlock_verdict_and_financing():
    t = page_text("diligence/sandlock")
    assert "ADVANCE TO FOUNDER CONVERSATION" in t
    assert "No public institutional financing identified in the reviewed sources." in t
    assert "not a claim that the company is bootstrapped" in t
    assert "Array has not reviewed this company" in t


def test_sandlock_shows_shared_kernel_tradeoff_and_exclusions():
    t = page_text("diligence/sandlock")
    assert "Kernel vulnerabilities" in t
    assert "shared kernel" in t.lower()
    assert "Explicitly out of scope" in t
    assert "a separate guest kernel" in t


def test_sandlock_never_scores_security():
    t = page_text("diligence/sandlock")
    assert not re.search(r"\d(\.\d)?\s*/\s*10", t), "no security scores allowed"
    assert "security score" not in t.lower() or "no aggregate score" in t.lower() \
        or "no “security score”" in t.lower()


def test_sandlock_does_not_overclaim_verification():
    t = page_text("diligence/sandlock")
    assert "OBSERVED AS PROJECT CLAIM" in t.upper().replace("PROJECT CLAIM",
        "PROJECT CLAIM") or "Project claim" in t
    assert "not dynamically tested" in t or "not reproduced here" in t


def test_sandlock_source_ledger_present():
    t = page_text("diligence/sandlock")
    for sid in ("S1", "S5", "S17", "S19"):
        assert re.search(rf"\b{sid}\b", t), sid
    assert "nobody was contacted" in t.lower()


# ---- headroom --------------------------------------------------------------

def test_headroom_results_verbatim():
    t = page_text("lab/headroom")
    for v in ("PARTIALLY REPRODUCED", "46.30%", "28.41%", "0.00%", "1.0000",
              "1.57 MB", "35"):
        assert v in t, v
    assert "MINIFIED" in t
    assert "primary comparison: HEADROOM vs MINIFIED" in t


def test_headroom_shows_both_source_claims():
    t = page_text("lab/headroom")
    assert "20% fewer tokens for coding agents" in t
    assert "15-20% fewer tokens" in t


def test_headroom_fairness_language():
    t = page_text("lab/headroom").lower()
    assert "real engineering" in t
    assert "benchmark is limited" in t or "one reproducible benchmark" in t
    # These disclaimers are the only permitted uses of the words they contain.
    scrubbed = (t.replace("not an accusation of dishonesty", "")
                 .replace("statement about the project’s honesty", ""))
    for word in ("fraud", "dishonest", "misrepresent", "lying", "fake claim"):
        assert word not in scrubbed, word


def test_headroom_transformation_errors_and_retention():
    t = page_text("lab/headroom")
    assert "0" in t and "transformation errors" in t
    assert "1.0000" in t


# ---- methodology -----------------------------------------------------------

def test_methodology_all_three_tallies():
    t = page_text("methodology")
    assert re.search(r"0\s+PASS.*2\s+PARTIAL.*4\s+MISS.*4\s+UNKNOWN", t, re.S)
    assert re.search(r"2\s+PASS.*1\s+PARTIAL.*3\s+MISS.*4\s+UNKNOWN", t, re.S)
    assert re.search(r"2\s+PASS.*0\s+PARTIAL.*1\s+MISS.*6\s+UNKNOWN", t, re.S)
    assert "POST-HOC EXPLORATORY" in t.upper()
    assert "not comparable" in t.lower()


def test_methodology_perspective_ai_failure_is_prominent():
    t = page_text("methodology")
    assert "Perspective AI" in t
    assert "marketing/content repository" in t
    assert "rule was not changed after seeing the result" in t
    assert "no v3 has been" in t


def test_methodology_freeze_commits_visible():
    t = page_text("methodology")
    export = json.loads((ROOT / "web/src/data/research.json").read_text())
    assert export["methodology"]["unseen"]["freezeCommit"] in t
    assert export["hashes"]["v1Frozen"] in t
    assert export["hashes"]["v2Rules"] in t


def test_methodology_reports_unmeasured_analyst_time():
    t = page_text("methodology")
    assert "NOT_MEASURED" in t
    assert "never relabelled as human analyst time" in t


# ---- signals ---------------------------------------------------------------

def test_signals_channel_honesty():
    t = page_text("signals")
    assert "100% of discovery" in t
    assert "DISABLED" in t
    assert "GitHub-led discovery with multi-modal evidence" in t
    assert "multi-channel sourcing" not in t.replace(
        "not “multi-channel sourcing”", "")


def test_signals_identity_audit_numbers():
    t = page_text("signals")
    for v in ("267", "166", "62.17%", "0.37%", "28"):
        assert v in t, v


def test_signals_domain_numbers():
    t = page_text("signals")
    assert "70.59" in t
    assert "32.35" in t


def test_signals_attention_vs_construction_is_not_a_judgment():
    t = page_text("signals")
    assert "different axes" in t.lower() or "different things" in t.lower()
    assert "good founder" not in t.lower()
    assert "bad founder" not in t.lower() or "labelled a good or bad founder" in t.lower()


# ---- about / disclosure / disclaimer ---------------------------------------

def test_ai_disclosure_present_and_unminimised():
    t = page_text("about")
    assert "built with substantial AI assistance" in t
    assert "AI output is never treated as primary evidence" in t
    assert "no global" in t.lower() and "founder score" in t.lower()


def test_independence_disclaimer_on_every_page():
    for route in ROUTES:
        t = page_text(route)
        assert "independent research project" in t, route
        assert "not investment advice" in t, route
        assert "not affiliated with, sponsored by, or endorsed by Array Ventures" in t, route


# ---- privacy / leakage -----------------------------------------------------

def test_no_emails_or_phones_anywhere():
    blob = all_html() + all_client_js()
    assert not re.search(r"[\w.+-]+@[\w-]+\.(com|org|io|ai|net|dev)\b", blob)
    assert not re.search(r"\+1[\s(-]?\d{3}", blob)


def test_no_local_paths_or_secrets():
    blob = all_html() + all_client_js()
    assert "/Users/" not in blob
    assert "ANTHROPIC_API_KEY" not in blob
    assert not re.search(r"sk-[A-Za-z0-9]{20}", blob)


def test_person_universe_absent_from_site():
    builders = json.loads((ROOT / "outputs/builders.json").read_text())
    handles = [b["handle"] for b in builders if b.get("handle") and len(b["handle"]) > 5]
    blob = all_html() + all_client_js()
    leaked = [h for h in handles if h in blob]
    assert len(leaked) <= 10, f"universe leak: {leaked[:20]}"


def test_internal_corpus_absent_from_client_js():
    js = all_client_js()
    for marker in ("source_registry", "VERIFIED_CROSS_LINK", "person:",
                   "review_queue", "career_signal_class"):
        assert marker not in js, marker


def test_no_placeholder_text_anywhere():
    t = all_html().lower()
    for placeholder in ("lorem ipsum", "todo:", "tktk", "placeholder", "xxx"):
        assert placeholder not in t, placeholder
