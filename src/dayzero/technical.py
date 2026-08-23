"""Technical-dimension records.

Nine independent dimensions. There is no total, no composite, and no ranking
function. Any attempt to add one is caught by `tests/test_no_score.py`.

Values arrive from two places and are always labelled:
  * rule-derived from collected facts  -> assessed_by="rule"
  * analyst judgement                  -> assessed_by="analyst"
An LLM may never write here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .config import load
from .signals import SYSTEMS_LANGUAGES, DerivedSignal

DIMENSIONS = tuple(load("technical_dimensions.yaml")["dimensions"].keys())


@dataclass(frozen=True)
class DimensionValue:
    dimension: str
    value: str
    evidence_status: str
    basis: str
    assessed_by: str = "rule"

    def __post_init__(self) -> None:
        allowed = load("technical_dimensions.yaml")["dimensions"][self.dimension]["values"]
        if self.value not in allowed:
            raise ValueError(f"{self.dimension}: {self.value!r} not in {allowed}")


def derive(repo: dict[str, Any], depth: list[DerivedSignal],
           releases: list[dict], paper_linked: bool) -> list[DimensionValue]:
    """Conservative rule-derived values. Everything uncertain stays UNKNOWN so that
    an analyst has to look, rather than the system pretending to know."""
    con = repo.get("construction") or {}
    lang = repo.get("language")
    blob = " ".join([(repo.get("description") or ""), " ".join(repo.get("topics") or [])]).lower()
    observed_depth = {s.signal_type for s in depth if s.evidence_status == "OBSERVED"}

    out: list[DimensionValue] = []

    # systems_depth: language + layer markers are directly observable.
    if lang in SYSTEMS_LANGUAGES and {"D-01", "D-04", "D-06", "D-07"} & observed_depth:
        out.append(DimensionValue("systems_depth", "high", "OBSERVED",
                                  f"{lang} with {sorted({'D-01','D-04','D-06','D-07'} & observed_depth)}"))
    elif observed_depth:
        out.append(DimensionValue("systems_depth", "medium", "INFERRED",
                                  f"depth markers {sorted(observed_depth)} but language {lang}"))
    else:
        out.append(DimensionValue("systems_depth", "UNKNOWN", "UNKNOWN", "no depth markers observed"))

    # technical_difficulty: NOT derivable from metadata. This is the honest answer and
    # the entire justification for the reproduction lab.
    out.append(DimensionValue("technical_difficulty", "UNKNOWN", "UNKNOWN",
                              "not determinable from metadata; requires code read or reproduction"))

    out.append(DimensionValue("research_depth", "preprint" if paper_linked else "none_found",
                              "OBSERVED" if paper_linked else "UNKNOWN",
                              "linked arXiv paper with author overlap" if paper_linked
                              else "no arXiv match found"))

    has_number = any(t in blob for t in ("%", "x faster", "×", "ms", "tok/s", "vs "))
    has_baseline = any(t in blob for t in ("vs ", "beats", "compared to", "faster than",
                                           "than docker", "than "))
    if has_number and has_baseline:
        out.append(DimensionValue("performance_evidence", "specific_claim_with_baseline",
                                  "OBSERVED", "numeric claim with a named comparison in description"))
    elif has_number:
        out.append(DimensionValue("performance_evidence", "specific_claim_no_baseline",
                                  "OBSERVED", "numeric claim without a named baseline"))
    elif any(t in blob for t in ("fast", "efficient", "best", "#1")):
        out.append(DimensionValue("performance_evidence", "vague_claim", "OBSERVED",
                                  "superlative language with no measurement"))
    else:
        out.append(DimensionValue("performance_evidence", "none", "OBSERVED",
                                  "no performance claim in description"))

    lic = (repo.get("license") or "none").lower()
    if lic in ("none", "noassertion"):
        out.append(DimensionValue("reproducibility", "claim_only", "OBSERVED",
                                  f"license {repo.get('license')!r} limits reuse/verification"))
    else:
        out.append(DimensionValue("reproducibility", "partially", "INFERRED",
                                  f"open licence {repo.get('license')}; harness availability unverified"))

    docs = bool(repo.get("homepage"))
    out.append(DimensionValue("architecture_clarity", "partial" if docs else "undocumented",
                              "OBSERVED", "project/docs site present" if docs else "README only"))

    # usage_evidence: only NON-builder-sourced evidence counts. Stars never do.
    out.append(DimensionValue("usage_evidence", "UNKNOWN", "UNKNOWN",
                              "no third-party adopter identified; star/fork counts are not usage"))

    # originality: a very low commit count against high attention is a reupload tell.
    top = con.get("top_contributions") or 0
    if top <= 5 and (con.get("longevity_days") or 0) <= 7:
        out.append(DimensionValue("originality", "reupload", "OBSERVED",
                                  f"{top} commits over {con.get('longevity_days')} days"))
    else:
        out.append(DimensionValue("originality", "UNKNOWN", "UNKNOWN",
                                  "requires reading the implementation"))

    out.append(DimensionValue("defensibility_question_quality", "UNKNOWN", "UNKNOWN",
                              "analyst must author the question"))
    return out


def merge_analyst(rule_values: list[DimensionValue],
                  analyst_values: list[DimensionValue]) -> list[DimensionValue]:
    """Analyst judgement supersedes a rule value for the same dimension, and is
    labelled as such. The rule value is not deleted — it is simply not the one used."""
    by_dim = {v.dimension: v for v in rule_values}
    for v in analyst_values:
        by_dim[v.dimension] = v
    return [by_dim[d] for d in DIMENSIONS if d in by_dim]
