# DAY ZERO — Negative Controls

Plausible false positives. Every one is a **real, verified artifact** found in the same
GitHub sweep that produced the initial builder universe (all metadata verified via the
GitHub API on 2026-08-22). None is a strawman — several are things I found genuinely
interesting before checking the second number.

A negative control passes if the frozen acceptance criteria reject it **for the stated
reason**, without a special case.

---

## NC-1 — Viral repository, near-zero construction

**`0xSero/turboquant`** — 1,735 stars · 194 forks · **2 commits** · created 2026-03-25 ·
last push 2026-03-27 · GPL-3.0 · owner has 260 public repos and 1,770 followers.
Description: "TurboQuant: Near-optimal KV cache quantization for LLM inference (3-bit
keys, 2-bit values) with Triton kernels + vLLM integration."

Everything about the description is Array-relevant: KV-cache compression, Triton kernels,
vLLM. The technique is real — it is a published Google/ICLR method. The *repository* is a
two-commit restatement, dead within 48 hours.

**Why it must be rejected:** B-03 (sustained construction) fails — two commits is not
construction. TQ-2 classifies it as `reupload`. V-06 (abandonment) fires. Stars are
explicitly barred from surfacing logic.
**What it tests:** that attention is not construction.

---

## NC-2 — Thin wrapper presented as infrastructure

**Class control.** A large fraction of "agent memory" and "agent framework" repositories
in the 2026 GitHub landscape are a database plus an MCP server plus a prompt template.
Several in the initial sweep carry five-figure star counts and describe themselves as
"memory infrastructure" or a "memory OS."

**Why it must be rejected (or downgraded):** TQ-1 must resolve to L0/L1 (wrapper /
integration), not L3. The `signal_ontology.md` §2 anti-rule is explicit: *a project that
wraps an existing API is classified as integration, not infrastructure, regardless of star
count.*
**Why this is the hardest control:** the difference between "SQLite + FTS5 + MCP with a
real retrieval design" and "SQLite + FTS5 + MCP" is not visible from the README. This is
the control that most requires the reproduction lab, and the one where DAY ZERO is most
likely to be wrong.

---

## NC-3 — Abandoned technical project with a formation shell

**`zerobootdev/zeroboot`** — 2,434 stars · **24 commits by a single contributor** ·
created 2026-03-15 · **last push 2026-03-21** · org `zerobootdev` created 2026-03-19 ·
domain `zeroboot.dev` · "Sub-millisecond VM sandboxes for AI agents via copy-on-write
forking."

This is the dangerous one, because the **formation signals are real**: a new GitHub org
(F-02), a live domain (F-01), a specific technical claim, and 2,434 people paying
attention. A formation-hungry system would surface this immediately.

**Why it must be rejected:** `formation_framework.md` requires FORMING to sit on top of a
construction base. B-03 fails (24 commits, 6 active days). V-06 fires (no push in 5
months). The org and domain are a shell around a demo.
**What it tests:** that formation signals cannot substitute for construction signals.

Companion case: **`dipampaul17/KVSplit`** — 362 stars · 9 commits · active 2025-05-16 →
2025-05-21 · SF-based owner · "8-bit keys & 4-bit values, reducing memory by 59% with <1%
quality loss ... optimized for M1/M2/M3." Well-specified, locally reproducible, exactly
the kind of thing DAY ZERO wants — and dead after five days. Same rejection, same reason.

---

## NC-4 — Specific benchmark claim, no license, no continuation

**`scrya-com/rotorquant`** — 1,043 stars · created 2026-03-26 · **last push 2026-04-23** ·
**no license** · top contributor has **9,510 public repositories**.
Claim: "Beats TurboQuant: better PPL (6.91 vs 7.07), 28% faster decode, 5.3x faster
prefill, 44x fewer params. Drop-in llama.cpp integration."

The claim is admirably falsifiable — named baseline, units, four separate metrics. TQ-6
scores well. But TQ-5 (reproducibility) is compromised by the absent license, V-06 fires,
and the maintainer's 9,510-repo profile is a mass-creation pattern that materially lowers
the prior that any single repo represents sustained personal work.

**Why it must be rejected:** V-06 abandonment; identity/ownership context makes TQ-1
INFERRED at best; no formation signals.
**What it tests:** that a *good* claim is not the same as a *supported* claim, and that
maintainer-level context matters.

---

## NC-5 — Strong artifact, strong depth, zero formation — and an employer that invites bad inference

**`RyanCodrai/turbovec`** — 16,239 stars · 1,403 forks · created 2026-03-26 · actively
pushed · MIT · **351 owner commits** · published on PyPI. Rust vector index with Python
bindings. Owner bio: **"Member of Technical Staff at Anthropic."**

Real construction, real systems depth, real distribution. And **no formation evidence at
all** — no org, no company, no domain, no founder statement.

**Why it must be rejected:** state is `BUILDING`. There are zero FORMATION signals.
**What it really tests:** the temptation to reason *"frontier-lab engineer + serious
side project + Array wants operators leaving labs = lead."* That chain is invention. It
is precisely the inference `formation_framework.md` §6.2 and `data_ethics.md` forbid.
This control exists because it is the mistake I would most plausibly make.

---

## NC-6 — Established organization resurfaced as a new venture

**`thunder-id/thunderid`** — 564 stars · Go · "high-performance, open-source identity
stack ... for humans, AI agents, and machines." Directly on Array's stated "agent identity
and authority management" mandate.

But the top six contributors (1,098 / 553 / 464 / 436 / 400 / 388 commits) are a coherent
group whose commit history is consistent with an existing enterprise identity-product
engineering team, not a new formation. **This requires verification before any claim is
made** — but the *shape* is the control: a mature codebase with a large, coordinated
contributor set is usually a rebrand, a fork, or a corporate open-source release.

**Why it must be flagged:** the `registry.py`-style organization registry (ported from the
audited engine) exists exactly to catch this. `artifact_owner_scope` must resolve to
`established_organization`, which routes to research rather than to outreach.
**What it tests:** that "new to us" is not "new."

---

## NC-7 — Paper with no formation signal

**`FutureMLS-Lab/OSCAR`** — 556 stars · MIT · project page · "Offline Spectral
Covariance-Aware Rotation for 2-bit KV Cache Quantization." Org created 2026-03-09, named
as a lab.

Genuine research depth (TQ-4). No org-as-company signals, no domain that is a product, no
founder statement, no commercial surface.

**Why it must be rejected:** this is a research group publishing research. It is a
`BUILDING`/`COLLABORATING` watchlist entry and a good relationship to have, but F-01…F-08
are all absent. Treating every strong systems paper as a company-in-formation would
generate enormous noise and would misread what academic labs are doing.
**What it tests:** that research ≠ formation.

---

## NC-8 — Hackathon demo that did not continue

**Class control**, with `dipampaul17/KVSplit` (NC-3 companion) as the closest verified
instance: a well-specified, well-benchmarked artifact built in a compressed burst and
never touched again.

Hackathon projects are a *legitimate and important* Pool A channel — Array explicitly asks
the analyst to attend hackathons, and AgentOps/Agency is a real example of a hackathon
project that became a company. But the signal of interest is **not the demo and not the
win**. It is *continued commits three months later*.

**Rule:** a hackathon signal (S-07 / F-05) may enter the graph immediately but cannot
contribute to a Weekly 3 until a BUILD signal exists **≥90 days after the event**.
**What it tests:** that DAY ZERO measures persistence, not event outcomes.

---

## NC-9 — Large following, weak artifact

Any account whose technical reputation rests on commentary, curation, or teaching rather
than construction. Verified shapes from the sweep: curated "awesome" lists and tutorial
repositories carrying 40,000–70,000 stars.

**Why it must be rejected:** `signal_ontology.md` §0.6 bars follower and star counts from
surfacing logic entirely. A curation repo generates no BUILD or DEPTH signal because
curation is not construction.
**What it tests:** that the system is not a popularity ranker.

---

## NC-10 — Technically excellent, outside Array's areas

Verified instances from the sweep: a Rust GTK network-connection monitor; a cross-platform
Logitech-Options alternative; a plain-text accounting tool; a game speed modifier. Several
have high stars, real systems depth, sustained solo construction, and would score well on
TQ-1 and TQ-3.

**Why it must be rejected:** area filter. Not AI infrastructure, data, security, HealthTech,
FinTech, or enterprise.
**What it tests:** that "impressive" does not override "relevant." A sourcing system that
surfaces brilliant work a fund cannot act on is a worse tool than one that surfaces less.

---

## NC-11 — Name-collision false positive

Two verified cases, both from Array's own portfolio (see `array_portfolio_map.md` §2 and
`entity_graph.md` ER-5):

- **"Agency"** — Array's portfolio company (Elias Torres, Klaviyo exit) vs. AgentOps/Agency
  (Reibman/Silverman/Qiu, $2.6M pre-seed led by 645 Ventures + Afore, **Array did not
  participate**).
- **"Eventual"** — Eventual/Daft (data engine, $7.5M seed 2024-10-01, CRV, Array
  participated) vs. Eventual (climate fintech, $7.5M seed 2025-07, AlleyCorp/Upfront).

The second pair collides on **name and round size**.

**Why it must be rejected:** ER-2 forbids merging on name similarity, and ER-5 requires an
explicit collision check before any project or company merge.
**What it tests:** that the system does not manufacture false statements about who backed
whom — the single most damaging error class for a tool used by a fund.

---

## Pass criteria for the control suite

The suite passes when, running the **frozen** criteria:

1. All eleven controls are rejected or correctly downgraded.
2. Each rejection cites a **pre-existing** rule — no rule added after seeing the control.
3. No control is rejected by a rule that also rejects a cohort company that should PASS.
4. NC-2 and NC-6 are permitted to resolve as "requires verification" rather than a clean
   reject; the system is allowed to say *I cannot tell yet*, and that is a correct answer.
