# X Integration — Phase 2 Provenance and Result

## 1. What was reused from the audited engine, and how

The Phase 1 audit of `~/headline-x-sourcing` (see `existing_x_engine_audit.md`) was used
as a **read-only design reference**. Nothing was imported at runtime from that absolute
path, and no file in it was modified. DAY ZERO is independently reproducible: `pip install
-e .` plus the committed `data/collected/` is sufficient to rebuild everything.

Every reuse below is a **reimplementation of a concept**, written fresh against DAY ZERO's
own schema. The provenance is recorded so the lineage is honest rather than hidden.

| DAY ZERO module | Concept taken from | What changed |
| --- | --- | --- |
| `dayzero/money.py` | exact-Decimal currency; floats and placeholders rejected | Added an explicit `UNKNOWN` marker so an undetermined cost is never silently written as `0` |
| `dayzero/cost.py` | append-only cost ledger, per-run and per-source | Simplified to one ledger; records `requests`, `units` and a `unit_label` so free sources are auditable too |
| `dayzero/timeutil.py` | aware-UTC-only; naive datetimes rejected at boundaries; monotonic durations | Added `parse_date` for the cutoff path. This is a correctness precondition for the holdout, not a style choice |
| `dayzero/urlutil.py` | `unwound > expanded > url`; tracking-param stripping; `t.co`/`x.com` never a product domain | Added `POSTING_PLATFORMS` (linktree, medium, substack) so a linktree is not read as a company domain |
| `dayzero/registry.py` | exact / dot-boundary matching; **substring matching forbidden** | Repointed from "is this an established company's post" to "is this artifact owned by an established organization" (negative control NC-6) |
| `dayzero/adapters/x.py` | SHA-256 canonical-request fingerprint; approval gating; fail-closed | Extended: the guard also fails closed on **stale pricing**, and returns a refusal object rather than raising, so a build continues without X |
| `dayzero/adapters/github.py` | network collector separated from offline parser; cache-first | New, but follows the same shape so the standard test suite needs no network |
| Evidence levels A–D | assigned at extraction time from source type | Replaced by a **claim-specific authority** model (§3 below), which is strictly stronger |
| Six-dimension ownership model | who is speaking vs. what they are speaking about | Became `claim_class` + `first_party` on every evidence row |

## 2. What was deliberately NOT reused

Confirmed dropped in implementation, not merely in intention:

- **The 100-point Primary Sourcing Score.** There is no total anywhere. `tests/test_no_score.py` inspects every column name in the live 35-table schema and every identifier in `src/`, and fails on `score`, `*_score`, `probability_of_*`, or a `total` column on `technical_assessments`.
- **`customer_pull` and `workflow_depth` as Day-0 requirements.** Commercialization signals are collected (9 of them) and are barred from surfacing. `intro_queue_rules.yaml` accepts formation **or** commercial evidence, so a pre-revenue builder is not excluded by construction.
- **Raw-count momentum.** Commit count gates exactly one boolean (`B-03` sustained construction: top human contributor ≥ 40 commits over ≥ 56 days). It never orders anything.
- **The X-only company schema.** The primary entity is a repository/person pair; `social_signals` is a peripheral table with zero rows.
- **The implicit seven-day window.** No time window is hard-coded. The holdout runs over arbitrary historical cutoffs.

## 3. The one genuine improvement over the original

The audited engine assigned a single evidence level per source. DAY ZERO makes authority a
property of the **(source, claim) pair**, in `config/source_quality.yaml`:

```yaml
- id: AR-1  # a builder's own post
  when: {first_party: true, claim_class: statement}
  authority: 1        # authoritative that the statement was made
- id: AR-2
  when: {first_party: true, claim_class: technical_performance}
  authority: 3        # NOT evidence the claim is true
```

`tests/test_evidence.py::test_source_authority_is_claim_specific` asserts that the same
source returns authority 1 for `statement` and 3 for `technical_performance`.

## 4. What actually happened to X in Phase 2

**X ingestion never ran, and the reason is recorded rather than glossed.**

The guard refused at the first precondition: `DAYZERO_X_ENABLED` was not set and no bearer
token was present. Had both been present it would still have refused, because the carried-
over pricing reference is dated 2026-07-18 with a 30-day staleness gate that expired on
2026-08-17. Eleven tests in `tests/test_x_adapter.py` exercise each refusal path.

**Result: 0 X records. 0 X-derived evidence rows. $0 spent.**

## 5. The X incremental-value test — an empirical answer

Phase 2 could not run a with-X / without-X comparison on live posts. It produced something
more useful and more decisive: a measurement of whether the **join key even exists**.

Of **267 collected GitHub identities, exactly one** publishes an X or Twitter URL in the
`blog` field (`janetkuo`, an incidental contributor, not a lead). That is **0.37%**.

A further 32 profiles mention an `@handle` in the bio, but nearly all of those are GitHub
org handles (`@runta-dev`, `@columbia`, `@FailproofAI`), not X accounts.

This matters more than a noisy-signal complaint:

> Under DAY ZERO's entity-resolution rules, an X account cannot be attached to a builder
> without ER-1 evidence — an explicit self-published cross-link, shared small-org
> membership, an artifact cross-reference, or an explicit bio statement. In this
> population that evidence exists for **1 of 267 people**. So even with a funded X
> budget, X evidence could not have been *joined* to 99.6% of the universe without
> committing exactly the name-similarity merge that ER-2 forbids.

**Did X change any Intro Queue decision? No — and it could not have**, because none of the
three Intro Queue leads publishes a linkable X account. The channel's cost is not its
main problem; its main problem is that it does not connect to the artifact graph.

## 6. Recommendation for Phase 3

**Keep the X design. Do not fund X ingestion yet.**

X remains the only channel that can carry two things GitHub cannot: an explicit first-person
transition statement, and a hackathon result with no other index. Those are real gaps —
see the career-class result (69% UNCLASSIFIED) and the hackathon channel (0 records, closed
by robots policy).

But the sequence should be:

1. **Re-verify X pricing and tier access.** Nothing may be spent against an expired reference.
2. **Spend the first budget on identity, not discovery.** The bottleneck is the join key. A
   small, targeted `/2/users` lookup for a handful of named leads is worth more than a
   broad recent-search sweep, because it either produces an ER-1 cross-link or proves the
   channel cannot connect.
3. **Only then consider the FORMING and OPERATOR_TRANSITION query families**, and only for
   the population where an identity link already exists.

Turning X on for discovery before solving the join is how a sourcing tool ends up with a
large pile of posts it cannot attribute to anyone.
