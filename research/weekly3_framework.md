# DAY ZERO — The Weekly 3

## 1. What it is

**Three builder/team leads that survive analyst review and are worth spending
relationship capital on.**

It is not the top 3 people on the internet, not the 3 highest-scoring records, and not
the 3 most impressive artifacts. It is the answer to a specific operational question:

> *Given a week of signal, which three people should a partner at a four-person fund
> actually reach out to, and what would we say?*

Array's job posting sets the target at **2–3 quality founder intros per week**. Against
9–10 investments per year, that is roughly 100–150 introductions producing ~10
investments — a ~7–10% intro-to-investment rate. The Weekly 3 bar must be calibrated to
that ratio, not to a demo-friendly one.

## 2. The hard rules

1. **If fewer than three genuinely survive, return one or two.** Or zero. Filling slots
   is the single fastest way to make the system worthless — a partner who is burned twice
   stops reading it.
2. **Identity must be resolved to `entity_graph.md` ER-1 standard.** You cannot introduce
   someone you cannot name.
3. **No lead may rest on a single channel.** Cross-source convergence is required
   (`signal_ontology.md` §8).
4. **An X post alone never produces a Weekly 3 lead.**
5. **Every claim in the record carries OBSERVED / INFERRED / UNKNOWN.**
6. **A "why not obvious" section is mandatory and must be falsifiable.** If the honest
   answer is "they are obvious," the lead is dropped — a fund does not need a system to
   tell it about a company that just announced a round.
7. **No contact happens as part of DAY ZERO.** The output is a research artifact and a
   recommendation. The human decides.

## 3. Record schema

Every Weekly 3 record contains, in order:

| Field | Requirement |
| --- | --- |
| `builder_or_team` | Resolved identity; named humans |
| `current_project` | Project + canonical artifact URL |
| `why_surfaced` | Which specific signals fired, with dates |
| `latest_meaningful_signal` | The most recent non-trivial change, dated |
| `technical_artifact` | The thing you can actually open |
| `technical_evidence` | TQ-1…TQ-9 assessment (`technical_quality_framework.md`) |
| `formation_evidence` | State + the signals supporting it (`formation_framework.md`) |
| `array_relevance` | Mapped to a **named, cited** Array theme — not a vibe |
| `why_non_obvious` | Falsifiable: what would a normal sourcing process have used to find this, and why didn't it |
| `technical_question` | One question whose answer changes the investment view |
| `commercial_question` | One question about who pays and why |
| `suggested_outreach_rationale` | Why *this fund*, in one sentence a founder would find credible |
| `identity_confidence` | HIGH / MEDIUM / LOW — LOW is disqualifying |
| `evidence_sources` | Every source_id, with tier |
| `what_would_make_us_drop_it` | Written *before* outreach, so the disconfirming evidence is named in advance |

The last field matters more than it looks. Writing down the kill criterion before you are
emotionally invested is the cheapest available protection against motivated reasoning.

## 4. What disqualifies a candidate

- Identity confidence LOW.
- Single-channel evidence.
- Formation evidence that rests on inference about someone's employment.
- Already funded and publicly announced (unless the artifact substantially predates it
  and the thesis is about a *future* round — say so explicitly).
- Outside Array's stated areas, however impressive.
- Abandonment signal (V-06) on the primary artifact.
- The analyst cannot answer "what is the hard part?"

## 5. Cadence and inventory

A weekly cadence does not mean weekly *discovery*. Formation evidence accumulates slowly.
The realistic model is a **standing watchlist** in which most entries are `BUILDING` and
unchanged, and the week's work is detecting the small number of *state transitions* —
a new org, a new collaborator, a first release, a founder statement.

This is why V-01…V-06 (velocity as change, not level) is the operational core of the
system, and why a system that re-ranks the same universe every week produces nothing.
