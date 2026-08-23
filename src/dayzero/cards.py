"""Analyst cards, generated from canonical data.

Markdown is never hand-maintained alongside JSON — it is rendered from it, so the two
cannot drift.
"""
from __future__ import annotations

import json
from typing import Any

from .config import OUTPUT_DIR

def _q(record: dict, key: str) -> str:
    """Questions are authored by the analyst and stored alongside the card."""
    return (record.get("card") or {}).get(key) or "(not recorded)"


CARD_FIELDS = [
    ("builder_or_team", "Builder / team"),
    ("project", "Project"),
    ("why_now", "Why now"),
    ("technical_artifact", "Technical artifact"),
    ("technical_depth", "Technical-depth evidence"),
    ("formation_evidence", "Formation evidence"),
    ("array_relevance", "Array relevance"),
    ("why_company_first_sourcing_may_miss_it",
     "Why company-first sourcing may miss it"),
    ("strongest_positive", "Strongest positive evidence"),
    ("strongest_negative", "Strongest negative evidence"),
    ("what_must_be_verified_before_introduction",
     "What must be verified before an introduction"),
]


def render(intro: dict[str, Any], review: dict[str, Any],
           status: dict[str, str]) -> str:
    lines = [
        "# Analyst Cards", "",
        f"**As of:** {intro['as_of']}  ",
        f"**Frozen rules hash:** `{intro['rules_hash']}`  ",
        "**Anyone contacted:** no",
        "",
        "System eligibility comes from the frozen configuration. Analyst selection is a "
        "separate human act and is recorded with the original system state, a reason and "
        "the evidence.",
        "",
    ]
    for r in intro["intro_queue"]:
        card = r.get("card") or {}
        ov = r.get("analyst_override")
        lines += [f"## {r['subject']}", ""]
        lines.append(f"- **Current workflow state:** `INTRO_READY`"
                     f" (system: `{r['system_state']}`"
                     + (f", analyst override applied)" if ov else ")"))
        lines.append(f"- **Current public status:** "
                     f"{status.get(r['subject'], 'no institutional financing identified in the public sources reviewed')}")
        lines.append(f"- **Career signal class:** recorded only where self-published; "
                     f"not used in eligibility")
        lines.append(f"- **Formation state (system):** `{r['formation_state']}` · "
                     f"identity `{r['identity_confidence']}` · owner scope `{r['owner_scope']}`")
        lines.append(f"- **Signals fired:** {', '.join(r['signal_types'])}")
        lines.append(f"- **Independent channels:** {', '.join(r['channels'])}")
        lines.append(f"- **Themes:** {', '.join(r['themes'])}")
        lines.append("")
        for key, label in CARD_FIELDS:
            if card.get(key):
                lines.append(f"**{label}.** {card[key].strip()}")
                lines.append("")
        # The two required questions live at the record level, not inside the card.
        ar_q = r.get("card", {})
        lines += ["**Technical question.** " + (r.get("technical_question") or
                                                _q(r, "technical_question")), ""]
        lines += ["**Commercial / formation question.** " +
                  (r.get("commercial_or_formation_question") or
                   _q(r, "commercial_or_formation_question")), ""]
        if ov:
            lines += ["**Analyst override.**", "",
                      f"- Original system state: `{ov['original_system_state']}`",
                      f"- Analyst state: `{ov['analyst_state']}`",
                      f"- Reason: {ov['reason'].strip()}",
                      f"- Evidence: {ov['evidence'].strip()}", ""]
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    intro = json.loads((OUTPUT_DIR / "intro_queue.json").read_text(encoding="utf-8"))
    review = json.loads((OUTPUT_DIR / "review_queue.json").read_text(encoding="utf-8"))
    (OUTPUT_DIR / "analyst_cards.md").write_text(render(intro, review, {}), encoding="utf-8")
    return 0
