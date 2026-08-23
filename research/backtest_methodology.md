# DAY ZERO — Historical Holdout / Time-Travel Methodology

**Status: DESIGNED AND FROZEN. NOT YET RUN.**

The question: *could DAY ZERO have surfaced strong Array-backed founders before the
opportunity became obvious?*

---

## 1. Why the freeze order matters more than the result

A backtest run *after* the rules are tuned is not evidence — it is a description of the
tuning. So the order is fixed and recorded:

1. ✅ Signal ontology frozen (`signal_ontology.md` v1.0, 2026-08-22)
2. ✅ Formation states frozen (`formation_framework.md`)
3. ✅ Technical quality dimensions frozen (`technical_quality_framework.md`)
4. ✅ Acceptance criteria frozen (§4 below)
5. ✅ Cohort selected **and expected outcomes predicted** (`array_portfolio_map.md` §4)
6. ⬜ Backtest run — **Phase 2, not now**
7. ⬜ Results published, including misses

Step 5 is the unusual one and the most important. The expected PASS/PARTIAL/MISS for each
of the ten cohort companies is already written down. If the actual results are better
than the predictions across the board, that is a signal that something leaked — not that
the system is good.

**Predicted going in: 3 PASS, 2 PARTIAL, 3 MISS, 2 UNKNOWN. ~30% hit rate.**

---

## 2. The cohort

Ten companies, selected in `array_portfolio_map.md` §4 on **evidence recoverability**,
not on success. Three are expected to fail outright and are kept deliberately.

| ID | Company | Milestone | **Cutoff** |
| --- | --- | --- | --- |
| B1 | Eventual / Daft | Seed 2024-10-01 (Array participated) | **2024-09-30** |
| B2 | Sapiom | Seed 2026-02-05 (Array led the *pre*-seed earlier) | **2026-02-04** |
| B3 | HappyRobot | Series A 2024-12-04 | **2024-12-03** |
| B4 | Flamingo | Stealth exit 2025-10-28 | **2025-10-27** |
| B5 | Meibel | $7M 2025-05-28 | **2025-05-27** |
| B6 | Integral | Seed 2023-09-05 | **2023-09-04** |
| B7 | Mozart Data | Seed 2020-11-11 | **2020-11-10** |
| B8 | ZecOps | Acquisition 2022-11-17 | **2020-01-01** |
| B9 | Era Software | Acquisition 2022-10-05 | **2021-10-05** |
| B10 | Wokelo | $4M 2024-10-09 | **2024-10-08** |

Cutoffs are the day before the public milestone, except B8 where the milestone is an
acquisition years after the interesting window and the cutoff is set to the period when
discovery would have mattered.

---

## 3. Preventing look-ahead bias

This is a timestamp-discipline problem, and it is solved structurally rather than by
promising to be careful.

### 3.1 Two timestamps on everything
Every node, edge and signal carries `observed_at` (when the fact happened) and
`collected_at` (when we recorded it). Backtest queries filter **only** on `observed_at`.

### 3.2 Fields with no defensible `observed_at` are excluded outright
Current star count, current follower count, current bio text, current README, current
repo description, current homepage — all of these describe *today*. They are not
approximated backwards; they are **removed from the backtest query surface entirely.**

This is a genuinely costly rule. It means a 2024 backtest cannot use a repo's current
description. The alternative — "the description probably didn't change much" — is exactly
how look-ahead bias enters.

### 3.3 Reconstruct, do not remember
Permitted pre-cutoff evidence:
- **GitHub:** commits, releases, tags, org creation, repo creation, contributor activity —
  all with authoritative API timestamps and all filterable by `until=<cutoff>`.
- **arXiv:** `published` date is authoritative.
- **Package registries:** version release dates.
- **Wayback / CDX:** the *snapshot* of a page as of a date before the cutoff. If no
  snapshot exists before the cutoff, the page contributes nothing.
- **Dated press and dated posts:** only if the publication date is verifiable.

### 3.4 Blind-run protocol
The person running a case must not have read the outcome for that case first. In practice,
for a solo project: outcomes are recorded in a **separate file** from the case files, the
case analysis is written and committed first, and only then is the outcome appended. The
git history is the audit trail — if the outcome commit precedes the analysis commit, the
case is void.

### 3.5 Outcome isolation
Post-cutoff information lives **only** in a field literally named `OUTCOME`, which is
written after the decision and never referenced by any rule.

### 3.6 The leakage checklist (run per case)
- [ ] Every evidence item has an `observed_at` ≤ cutoff
- [ ] No current-state field used
- [ ] No source whose publication date is unverifiable
- [ ] No knowledge of the co-investor list used
- [ ] No search query that included the company's later name if the name changed
- [ ] The analyst can state what they knew and when, without referring to OUTCOME

### 3.7 The unavoidable, honest caveat
**I already know these ten companies are Array portfolio companies.** That knowledge
cannot be unlearned. It biases *where I look*, even if it does not bias what I count.

Mitigations, stated plainly rather than hidden:
- The cohort includes three companies I expect to miss.
- Negative controls (`negative_controls.md`) are run through the *same* pipeline in the
  *same* session, so the acceptance criteria must reject them too.
- Expected outcomes are published before the run.
- The decision rule is mechanical (§4), so "would this have surfaced?" is a criteria
  check, not a judgement call.
- **Where the result is close, it is recorded as PARTIAL, not PASS.**

This bias cannot be eliminated by a solo researcher working with a known portfolio. The
correct response is to say so, not to claim a clean-room that does not exist.

---

## 4. Decision rule — FROZEN

For each case, applying only pre-cutoff evidence:

### PASS
The company's founder(s) would have reached the analyst review queue, i.e. **all** of:
1. ≥1 BUILD signal **and** ≥1 TECHNICAL DEPTH signal, attributable to an identified person;
2. cross-source convergence per `signal_ontology.md` §8 (≥2 signals, ≥2 independent
   channels, ≥1 Tier-1 source);
3. identity resolvable to ER-1 standard;
4. the artifact falls inside Array's stated investment areas;
5. no disqualifier from `weekly3_framework.md` §4.

### PARTIAL
The founder or artifact would have **surfaced** (criterion 1 met) but at least one of
criteria 2–5 fails on pre-cutoff evidence.

### MISS
No pre-cutoff evidence would have surfaced the person or the artifact at all.

### UNKNOWN
Pre-cutoff public data is insufficient to determine what would have happened — for
example, because the relevant surfaces were never archived.

**A MISS is an allowed and expected outcome. The rules do not change afterward to improve
recall.** If the rules are found to be wrong, that is a v2.0 of the ontology, dated, with
the v1.0 backtest results left published alongside.

---

## 5. Change control

`signal_ontology.md` v1.0 and this document are frozen as of 2026-08-22. Before the first
backtest run, a SHA-256 of both files (plus `formation_framework.md` and
`technical_quality_framework.md`) is recorded in the run's output. Any post-hoc edit
changes the hash and invalidates the run.

## 6. What the backtest can and cannot prove

**Can:** that the ontology detects specific, dated, public evidence that existed before a
financing event; that the acceptance criteria reject plausible false positives; where the
channel coverage has holes.

**Cannot:** that DAY ZERO would have *gotten the meeting*, that Array would have invested,
or that the criteria generalize beyond ten cases. Ten cases is a design validation, not a
statistical result, and it will be reported as such.
