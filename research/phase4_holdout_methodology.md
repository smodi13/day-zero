# Phase 4 — Unseen v2 Validation: Cohort Methodology

**Frozen before any pre-cutoff evidence was retrieved.**
Manifest: `config/phase4_unseen_holdout.yaml`
v2 hash under test: `435dfb8a568d8f07124125b08566cc9ced48f4d17ef76064978905968287f434`

---

## Why this cohort exists

Phase 3 repaired a documented v1 failure and produced a v2 that scored 2 PASS on the same
ten cases v1 scored 0 on. That is **post-hoc**: v2 was designed after seeing v1 fail on
cases whose answers were already known. The obvious and correct challenge is *"you tuned
until it passed."*

The only answer to that challenge is a cohort **v2 has never been used to reason about**.
This is it.

## Eligibility criteria — all must hold

1. **Not in the original 10-case v1 holdout.** Those ten are excluded by construction: v2
   was designed against them, so they can never be out-of-sample.
2. **Not used to design v2.** v2's design used exactly one holdout case (B1 Eventual/Daft)
   and the negative-control fixtures. None of the nine selected cases appears in either.
3. **Not deeply analysed in Phases 1–3.** These companies appear in
   `array_portfolio_map.md` only as table rows carrying a name and a financing date. No
   technical evidence was gathered for any of them at any point.
4. **Array relationship publicly established.**
5. **An exact, verifiable public announcement date exists.**
6. **Founder or team identifiable enough to build an evidence packet** — or explicitly
   UNKNOWN, which is permitted (see below).
7. **No requirement that useful pre-cutoff technical evidence actually exists.**

### The rule that matters most

**Criterion 7 is the anti-bias rule, and it was enforced procedurally rather than by
promise.** Eligibility was decided using only: company name, founder/team where public,
Array relationship, and announcement date. At no point before the manifest was frozen did
I check whether a company had a GitHub organisation, a repository, a paper, or any other
artifact. Six of the nine cases were selected with `founder_or_team: UNKNOWN`, which is
itself evidence that the answer key was not consulted — a biased selector would have
resolved founders first.

## Cutoff rule

> The day before the earliest financing announcement with an exact, verifiable public date
> in which Array's relationship is publicly established.

A case whose announcement date could not be established is excluded as
**`CUTOFF_DATE_UNRESOLVED`** — never because it looked difficult.

**A known bias, declared:** for Blumira the exact seed-round announcement date could not be
verified, so the Series A date (2021-08-18) was used. That gives the system *more*
pre-cutoff time than Array's actual entry point, which biases that case **toward passing**.
It is reported here rather than quietly absorbed.

## Deterministic selection

```
selection_hash = SHA256(v2_frozen_hash + ":" + case_id)
sort ascending
take the first 12
```

Binding the hash to the v2 rule hash means the ordering could not have been chosen after
the fact without changing v2 itself, which would change the hash and be visible in git.

**Nine cases were eligible, fewer than the target of 12, so all nine are used.** The
ordering is recorded anyway, so the method is auditable and would have applied if more had
qualified.

**No case was swapped out after selection.** No case was inspected and then replaced.

## The selected cohort

| Order | Case | Company | Announcement | **Cutoff** | Selection hash |
| --- | --- | --- | --- | --- | --- |
| 1 | U07 | Tumble | 2022-10-05 | **2022-10-04** | `3726c361ddd4…` |
| 2 | U03 | Wabi | 2025-11-05 | **2025-11-04** | `472e903bb8bb…` |
| 3 | U09 | Zingly.ai | 2025-07-21 | **2025-07-20** | `5d1a3ff0df9b…` |
| 4 | U06 | ORO | 2022-11-03 | **2022-11-02** | `71138aa15017…` |
| 5 | U01 | Perspective AI | 2025-01-30 | **2025-01-29** | `a40c54c44173…` |
| 6 | U05 | Capsule | 2021-01-14 | **2021-01-13** | `ca49d31d1ea1…` |
| 7 | U02 | CandorIQ | 2025-07-22 | **2025-07-21** | `dcbc7dc9e869…` |
| 8 | U08 | Blumira | 2021-08-18 | **2021-08-17** | `f48a43b1faf9…` |
| 9 | U04 | MokSa.ai | 2024-04-22 | **2024-04-21** | `f5eda48d9d48…` |

Seventeen further companies were excluded, sixteen for `CUTOFF_DATE_UNRESOLVED` or
`NO_FINANCING_ANNOUNCEMENT`, and one — **Cast** — for `ENTITY_AMBIGUOUS`: Array's portfolio
lists a "Cast" described as account-management/customer-success software, which is a
different entity from the Kubernetes company Cast AI. That is the third name collision this
project has hit in Array's portfolio, after **Agency** and **Eventual**, and it was caught
by the same rule each time.

## What this cohort looks like, honestly

**It is a hard cohort for DAY ZERO, and that is not an accident of selection — it is what
Array's portfolio actually contains.** Of the nine: one consumer app platform, one SMS/CX
product, one procurement suite, one smart-laundry company, one retail-vision company, one
compensation-planning tool, one customer-research tool, one CX product, one security
product. Only Blumira sits anywhere near the infrastructure categories where public
technical artifacts are the norm.

**Phase 3 already predicted this failure mode:** *"companies that do not build in public
remain structurally invisible."* If that finding is real, this cohort should produce a lot
of MISS and UNKNOWN. Publishing the cohort before running it means that prediction is now
falsifiable rather than retrospective.

I am also including a case Phase 1 explicitly dismissed. Wabi was previously excluded from
the v1 cohort on the grounds that *"a $20M pre-seed by the founder of Replika is not a
discovery problem."* That judgement may well be right, but excluding it here would be
hand-picking, so it stays in.

## Limitations — stated before the result

1. **Known-winner bias remains.** Every case is an Array portfolio company and I know it.
   This is out-of-sample with respect to **v2's rule design**, not with respect to my
   knowledge that these companies exist and were funded.
2. **This is not investment-performance validation.** No accuracy, precision, recall, alpha
   or win-rate statistic is available from nine known-outcome cases, and none will be
   reported.
3. **Nine cases cannot produce a statistic** in any case.
4. **Evidence recoverability is confounded with time.** Capsule's cutoff is 2021, Wabi's is
   2025. Archival coverage and platform norms differ across that span.
5. **The Blumira cutoff is generous** (§ cutoff rule).
6. **Only the earliest verifiable announcement is used**, which may postdate Array's actual
   entry. Where it does, the test is easier than the real sourcing problem.

## What would count as a good result

Not "a high PASS count." A good result is **behaviour consistent with the stated design**:
convergence firing where multi-modal public artifacts genuinely exist, UNKNOWN where
nothing is recoverable, and no negative-control regression. **A cohort of mostly-closed-
source companies producing mostly MISS would confirm a limitation this project has already
published, and that is a legitimate outcome rather than a failure of the exercise.**

The rules will not be changed after the result. If v2 misses cases it should have caught,
that is documented and left for a future v3 recommendation.
