# DAY ZERO — X as a Signal Channel

**Status: designed, not built.** No X API call was made during Phase 1. No production
integration exists. Nothing was executed against the audited engine.

---

## 1. The role X plays

X is the fastest public surface for four things no other channel expresses well:

1. A builder saying, in their own words, **what they are building and why.**
2. An **explicit public statement of transition** — the only legitimate evidence for a
   Pool B operator→founder move.
3. A **hackathon result or demo** that has no other public index.
4. A **new collaboration** between two builders who do not yet share a repo.

X is structurally bad at everything else: depth, durability (7-day search window),
verification, non-English coverage, and anything a builder chose not to announce.

## 2. The governing rule

> **An X post is primary evidence that a person made a statement.
> It is never, by itself, evidence that the statement is true.**

Formalized in `source_quality.md` as the `statement_evidence` / `fact_evidence` split.

## 3. Required pipeline — no shortcuts

```
X POST
  → IDENTITY RESOLUTION      (ER-1 standard; a handle is not a person)
  → TECHNICAL ARTIFACT       (an artifact must exist and be openable)
  → INDEPENDENT CONFIRMATION (a non-X channel confirms the FACT, not the statement)
  → ANALYST REVIEW
```

**An X post alone can never create a Weekly 3 lead.** If the pipeline stalls at any
stage, the lead stops there and is recorded as stalled with the reason.

## 4. Query families

Ported from the audited engine's lane structure, re-aimed from *company traction* to
*construction and formation*.

### Family BUILDING
Construction verbs × technical nouns.
`built · shipped · "open sourced" · released · launching · "rewrote" · "benchmarked"`
combined with terms from Array's named themes (agent runtime, MCP, inference, KV cache,
sandbox, eBPF, agent identity, evals, context, token cost, data engine).
**Guard:** require `has:links`, exclude retweets, and exclude posts whose only link is
to x.com or an unresolved `t.co`.

### Family FORMING — use with the most care of any family
`"starting something" · "building something new" · "looking for a cofounder" ·
"founding engineer" · "starting a company" · "we're building"`

**Hard constraints on this family:**
- Only **explicit, first-person, present-tense** statements qualify.
- The statement must name or link to *something* — an artifact, a domain, a problem.
- A FORMING match creates a `candidate` record only. It cannot create a `FORMING` state
  on its own; `formation_framework.md` requires ≥2 signals from ≥2 channels.
- This family has the highest false-positive rate of any query in the system: it selects
  for people who *talk about* founding, which correlates weakly with founding and not at
  all with technical depth.

### Family TECHNICAL RELEASES
Posts containing repository links, arXiv links, benchmark results, or demo videos.
Highest precision family. Effectively a discovery feed for the GitHub and arXiv channels,
and the family most likely to justify the spend.

### Family OPERATOR TRANSITIONS
`"left my job" · "my last day at" · "after N years at, I'm" · "leaving X to build"`

**Explicit prohibitions, restated because this is where a sourcing tool becomes
surveillance:**
- Never infer a departure from **silence**.
- Never infer from **profile inactivity** or a follower-count change.
- Never infer from a **deleted post**.
- Never infer from a **bio edit** (removing an employer is not a resignation).
- Never infer from **rumor**, a third party's speculation, or a "who's leaving" thread.
- Never enrich against a data broker or an employment-history vendor to check.

If the person did not say it, DAY ZERO does not know it.

### Family HACKATHONS
`"won" · demo · "our project" ×` hackathon names. Cross-checked against the official
result page (manual — see the Devpost robots finding in `data_sources.md` §3).
The signal of interest is **not the win**. It is *continued commits three months later*.

## 5. What X may never establish on its own

Product performance · customer adoption · revenue · founder status · employment status ·
technical defensibility · funding · company formation.

Each requires a non-X source for the *fact*.

## 6. Reused controls from the audited engine

Ported as-is (see `existing_x_engine_audit.md` §2):

- `validator.py` — operator allowlist; `min_faves:`/`min_retweets:` rejected; exact query
  printed before execution.
- `approval.py` — SHA-256 canonical-request fingerprint, 15-minute TTL, fail-closed.
- `ledger.py` + `money.py` — exact-Decimal cost accounting, append-only audit.
- `ratelimit.py` — header-aware, bounded, single retry with approval and budget re-check.
- `urlutil.py` — `t.co` never invents an entity; x.com/twitter.com never a product domain.
- Engagement computed locally and **excluded from surfacing entirely** (DAY ZERO goes
  further than the original, which kept it as a tie-breaker).

## 7. Preconditions before any X spend in Phase 2

1. Re-verify current X API pricing and tier access. The reference in the audited engine
   is dated 2026-07-18 with a 30-day staleness gate — it is expired.
2. Confirm whether historical (non-7-day) search is available at an affordable tier. If
   not, X cannot contribute to the backtest and must be excluded from it entirely rather
   than approximated.
3. Set a per-run budget and route it through the ported approval gate.
4. Define, in advance, what question each query family is being paid to answer.

**Default posture: X ingestion is OFF.** GitHub, arXiv, registries and manual channels
are built and validated first. X is turned on only when there is a specific question it
is the best channel to answer — principally FORMING and operator transitions.
