# Phase 2: From Public Signal to Founder Intro Queue

**Date:** 2026-08-23 · **Engine:** dayzero 0.2.0
**Freeze commit (A):** `75b4311ad9ce540e7f36f8d2ec927623f7f419f0`
**Frozen rules hash:** `ad0b7ae00630f7948e7c4444440af7c20fed61169370e46e076cd8f575a3566c`

---

## Executive Summary

Phase 2 turned the Phase 1 ontology into a working, tested, deterministic engine; froze the
evaluation rules and committed them **before** producing any result; and then ran the
historical holdout, the negative-control suite, and a live review over 102 verified
repositories.

The headline results are not flattering, and that is the point.

- **The historical holdout produced 0 PASS.** Pre-registered expectation was 3 PASS / 2
  PARTIAL / 3 MISS / 2 UNKNOWN. Actual: **0 PASS / 2 PARTIAL / 4 MISS / 4 UNKNOWN.** The
  system did **worse** than its own published prediction.
- **The strongest case in the cohort failed on a rule designed to prevent false
  positives.** Eventual/Daft — 2.5 years of multi-contributor Rust systems work, publicly
  visible before the Array-backed seed — reached PARTIAL, not PASS, because every piece of
  its pre-cutoff evidence came from GitHub and the frozen convergence rule requires two
  independent channels.
- **Zero negative controls were incorrectly promoted.** All seven live controls were
  rejected; the frontier-lab-engineer fixture (16k stars, no formation evidence) did not
  promote.
- **All three Phase 1 "Weekly 3" leads fell out of system eligibility.** One returned via
  a documented analyst override; two were downgraded on the merits.
- **X contributed nothing, and Phase 2 established why in a way that matters more than
  "it's noisy":** of 267 collected identities, **one** publishes a linkable X account.
- **Cost: $0.** 1,271 free API requests. Actual cost recorded as `UNKNOWN`, never invented.

The Intro Queue contains **3 leads**, so a CURRENT 3 was emitted. Nobody was contacted.

---

## What Changed From Phase 1

| Phase 1 position | Phase 2 result | Status |
| --- | --- | --- |
| Weekly 3: Cong Wang, Vivek Chand, Resham Joshi | None reached system eligibility. Cong Wang returns via override; the other two are downgraded | **Corrected** |
| Cong Wang's artifact is `kernelscript` | `multikernel/sandlock` is the current, on-thesis artifact — 807 commits, pushed daily, an arXiv paper, and a named commercial product | **Corrected** |
| AgentSight and Multikernel are independent leads | They share an author: arXiv:2605.26298 *Sandlock* is co-authored by **Cong Wang and Yusheng Zheng** | **New** |
| Backtest predicted ~30% hit rate | 0 PASS. The convergence rule blocks single-channel true positives | **Corrected** |
| "GitHub org creation date is the best formation signal" | Confirmed: 98 of 171 formation signals are GitHub-derived, and org `created_at` is the single most-used field | **Confirmed** |
| "Attention and construction are near-uncorrelated" | Confirmed at scale: ratios span 1,922 stars/commit to 0.1 | **Confirmed** |
| "69% of builders are UNCLASSIFIED by career" | **68.2% UNCLASSIFIED** on a 4× larger population | **Confirmed** |
| Sapiom expected UNKNOWN in the holdout | PARTIAL — its GitHub org and two repos were genuinely recoverable pre-cutoff | **Better than predicted** |
| ZecOps expected PASS via the research channel | MISS. No dated pre-2020 artifact was recoverable | **Worse than predicted** |

---

## Engine Architecture

```
data/collected/*.json          verified facts, committed, re-collectable
        │
        ├── adapters/github.py      network collector | offline parser (split)
        ├── adapters/arxiv.py       exact title-phrase + exact author-overlap
        ├── adapters/x.py           OFF by default, fail-closed, 5 preconditions
        └── adapters/manual.py      no automated Devpost path exists, by policy
        │
   build.py ── normalize ── resolve.py (ER-1/ER-2) ── signals.py ── formation.py
        │                                                    └── technical.py (9 dims)
        ▼
  data/day_zero.db   35 tables · attention and construction in SEPARATE tables · no score column
        │
   freeze.py ── frozen_rules_manifest.json (9 rule files, parsed-content hashes)
        │
        ├── holdout.py            [GATED] as-of enforcement, blinded packets
        ├── negative_controls.py  [GATED] same pipeline, no special-case code
        └── pipeline.py           [GATED] system eligibility → analyst selection
        ▼
  outputs/*.json (canonical) → outputs/*.md (generated, never hand-maintained)
```

**178 offline tests. No network required.**

---

## Frozen Rules Methodology

Nine rule files are hashed by **parsed content**, not bytes — so a comment edit is not a
rule change, and a value edit always is. The combined hash is recorded in every
evaluation output.

`holdout`, `negative-controls`, `review` and `intro-queue` all call `require_frozen()`
first and **fail closed** on any drift, with the message: *"Frozen evaluation configuration
has changed. Historical validation cannot proceed without explicitly creating a new
methodological version."* The manifest is never silently regenerated.

The two-commit structure is the proof: COMMIT A contains the engine, the tests and the
manifest, and **contains no holdout result, no control verdict and no intro queue**. Anyone
can verify that ordering from `git log`.

### One implementation bug, fixed; zero rule changes

After the freeze, the live review returned **zero** eligible candidates, with 57 blocked on
`IDENTITY_UNRESOLVED`. Diagnosis: `_candidate_from_repo` resolved the **repository owner**,
which for an org-owned repo is the organization, not a person. The frozen rule asks whether
the **author's** identity is resolvable. The code was not implementing the rule as written.

**IMPLEMENTATION BUG FIX:** identity now resolves to the principal human contributor.
Frozen hash before: `ad0b7ae0…3566c`. After: `ad0b7ae0…3566c`. **Unchanged.** No rule file
was touched.

---

## Live Builder Universe

| Metric | Count |
| --- | --- |
| Repositories | **102** |
| Identities (people) | 267 |
| Organizations | 66 |
| Papers (author-verified) | 6 |
| Sources | 273 |
| Evidence records | **1,586** |
| Relationships (graph edges) | **579** |
| Technical signals | 648 |
| Formation signals | 171 |
| Commercialization signals | 9 |
| Technical dimension assessments | 918 |
| Formation state-history rows | 134 |

## Career-Class Result

| Class | Count | Share |
| --- | --- | --- |
| UNCLASSIFIED | 182 | **68.2%** |
| OTHER_EXPLICIT | 65 | 24.3% |
| OPERATOR_TO_FOUNDER | 12 | 4.5% |
| YOUNG_BUILDER | 8 | 3.0% |

Phase 1 measured 69% on 45 records; Phase 2 measures 68.2% on 267. The finding held under
a 6× larger sample.

**The eligibility rules cannot read this field at all** — `Candidate` has no career
attribute, asserted by `test_candidate_has_no_career_field_at_all`. Every non-UNCLASSIFIED
value carries a `career_signal_evidence_id` pointing at a self-published statement.

---

## Source Channels

| Channel | Raw | Evidence rows | Formation signals | Requests | Cost |
| --- | --- | --- | --- | --- | --- |
| GitHub | 102 repos | 1,580 | 98 | 1,259 | $0.000000 |
| Research (arXiv) | 6 papers | 6 | 0 | 12 | $0.000000 |
| Web (project/company domains) | — | — | 73 | — | $0 |
| X | **0** | 0 | 0 | 0 | $0 (off) |
| Hackathon | **0** | 0 | 0 | 0 | manual-only by robots policy |
| Events | **0** | 0 | 0 | 0 | manual only |

**Discovery contribution** and **evidence contribution** diverge sharply: GitHub discovered
100% of the universe, but the *web* channel (project and company domains) supplies 73 of
171 formation signals — 43%. Formation lives on domains; construction lives on GitHub.

### GitHub
The dominant channel and, for now, effectively the only one. Org `created_at` is the single
most valuable field: free, precisely dated, unforgeable, and a *decision*.

### X
Zero records. See `x_integration_phase2.md`. The decisive finding is not noise but the
**absence of a join key**: 1 of 267 identities (0.37%) publishes a linkable X account.

### Papers
6 author-verified links from 12 queries. The exact-name overlap rule is strict enough that
it **refused a true link**: AgentSight's paper↔repo pair did not attach, because the
contributor's GitHub display name is `云微` and the paper says "Yusheng Zheng". That is the
conservative rule working as designed and costing real recall — documented, not patched.

### Manual sources
Zero hackathon and zero event records. Devpost's robots.txt disallows `anthropic-ai`,
`GPTBot`, `ChatGPT-User`, `CCBot` and `Google-Extended`. There is no automated adapter and
`test_no_automated_devpost_adapter_exists` asserts there never will be one.

---

## Attention vs Construction

Stored in separate tables; `signals.py` and `review.py` are AST-checked to contain no
attention field access.

**Highest attention per commit** (descriptive only):

| Repo | Stars | Top human commits | Stars/commit |
| --- | --- | --- | --- |
| ComposioHQ/awesome-claude-skills | 73,056 | 38 | 1,922.5 |
| 0xSero/turboquant | 1,735 | **2** | 867.5 |
| rtk-ai/rtk | 77,106 | 530 | 145.5 |
| lasso-security/claude-hooks | 262 | 2 | 131.0 |

**Lowest attention per commit:**

| Repo | Stars | Top human commits | Stars/commit |
| --- | --- | --- | --- |
| OpenIntegrationEngine/engine | 216 | 1,489 | 0.1 |
| dredozubov/hazmat | 160 | 1,268 | 0.1 |
| rustledger/rustledger | 374 | 2,733 | 0.1 |
| **vivekchand/clawmetry** | 399 | **3,112** | 0.1 |
| multikernel/kerf | 30 | 156 | 0.2 |

The spread is four orders of magnitude. Any system that ranks by stars inverts this table.

**Important distinction, stated plainly:** attention is barred from *system* logic, but the
analyst legitimately used public visibility to answer a *different* question — "is this
already obvious?" — which the Intro Queue schema requires. Four system-eligible candidates
(graphify at 109k stars, headroom at 67k, rtk at 77k, mempalace at 58k) were held back on
that basis. That is a human judgement, recorded as an override with a reason, not a rule.

---

## Person ↔ Artifact Graph

579 edges over 441 nodes. Edge kinds: `MAINTAINS`, `CONTRIBUTED_TO`, `OWNED_BY`,
`IMPLEMENTS`. Every edge carries an evidence id or is null-by-construction, and
`test_graph_edges_reference_known_nodes` asserts no dangling edges.

Bots are excluded from personhood entirely (`[bot]`-suffixed logins), from contributor
counts, and from every velocity signal.

---

## Multikernel Correction

**This is a data/artifact correction, and it was material.**

Phase 1 anchored on `multikernel/kernelscript` — an OCaml eBPF DSL, 524 commits, last
pushed 2026-06-26. Phase 2 collection of the full organization surfaced 16 repositories,
including:

| Repo | Created | Pushed | Commits | What |
| --- | --- | --- | --- | --- |
| `sandlock` | 2026-03-13 | **2026-08-23** | 807 | "The lightest AI sandbox. A process-based sandbox for Linux, no container" |
| `linux` | 2025-09-15 | 2026-08-22 | — | Linux kernel with Multikernel support |
| `branchfs` | 2026-02-02 | 2026-05-23 | — | FUSE filesystem, lightweight atomic branching |
| `branching` | 2026-02-10 | 2026-03-14 | — | copy-on-write branching for AI agents |
| `daxfs` | 2026-01-24 | 2026-08-16 | — | disaggregated filesystem for CXL |

Plus **arXiv:2605.26298, *Sandlock: Confining AI Agent Code with Unprivileged Linux
Primitives* (2026-05-25), authored by Cong Wang and Yusheng Zheng** — which links two
Phase 1 leads that were treated as independent.

Plus a company products page listing **"Multikernel Sandbox (AI agent sandboxing
runtime)"** as one of three commercial products.

**Phase 1 materially understated what Multikernel is building.** The correction moved it
from "a kernel DSL, adjacent to the theme" to "a shipping AI-agent sandbox at the centre of
the theme."

**Funding / status resolution (question 27):** no public financing round, investor, or
filing was found for Multikernel Technologies in the sources reviewed. The company site
names no investors. Status recorded as **launched** — commercial products and demo booking
— **not** `institutional_round_public`. It is therefore not disqualified by the
`STATUS_TOO_LATE` rule, but it is honestly at the *late* edge of Day 0, and "a round may
exist that is simply not public" is recorded as its strongest negative.

`branchfs` and `branching` were both **dropped as ABANDONED** by the same rules — the
organization is not treated as a single blessed entity.

---

## Negative Controls

| Result | Count |
| --- | --- |
| CORRECTLY_REJECTED | 3 |
| REJECTED_FOR_A_DIFFERENT_REASON | 4 |
| COVERED_BY_UNIT_TEST (class-level) | 5 |
| **INCORRECTLY_PROMOTED** | **0** |

Zero controls promoted. But four were rejected for a reason other than the one predicted,
and that is worth reporting precisely:

- **NC-1** (turboquant, 1,735 stars / 2 commits): predicted `INSUFFICIENT_TECHNICAL_DEPTH`,
  actual `ABANDONED`. The abandonment rule fired first.
- **NC-5** (frontier-lab engineer, 16k stars, zero formation): predicted
  `NO_FORMATION_EVIDENCE`, actual `IDENTITY_UNRESOLVED`. **The intended guard did not
  fire.** The right outcome happened for the wrong reason: the profile publishes no real
  name, so identity blocked it before formation was ever assessed. If that person added a
  name and a personal site tomorrow, the formation guard would then have to hold on its
  own — and it is untested in that configuration. Documented, not patched.
- **NC-6** and **NC-7**: same pattern.

---

## Historical Holdout

**0 PASS · 2 PARTIAL · 4 MISS · 4 UNKNOWN.** Pre-registered: 3 / 2 / 3 / 2.

| Case | Company | Cutoff | Pre-registered | Verdict | As-of items | Channels |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | Eventual (Daft) | 2024-09-30 | PASS | **PARTIAL** | 7 | github |
| B2 | Sapiom | 2026-02-04 | UNKNOWN | **PARTIAL** | 5 | github |
| B3 | HappyRobot | 2024-12-03 | PASS | **MISS** | 2 | company_site, hackathon_official |
| B4 | Flamingo | 2025-10-27 | PARTIAL | UNKNOWN | 0 | — |
| B5 | Meibel | 2025-05-27 | UNKNOWN | UNKNOWN | 0 | — |
| B6 | Integral | 2023-09-04 | PARTIAL | UNKNOWN | 0 | — |
| B7 | Mozart Data | 2020-11-10 | MISS | **MISS** | 0 | — |
| B8 | ZecOps | 2020-01-01 | PASS | **MISS** | 1 | github |
| B9 | Era Software | 2021-10-05 | MISS | **MISS** | 0 | — |
| B10 | Wokelo | 2024-10-08 | MISS | UNKNOWN | 0 | — |

### The most important result in Phase 2

**B1 failed on `cross_source_convergence`.** Eventual/Daft had, before the cutoff: a GitHub
org created 2022-02-03, a Rust repo created 2022-04-25, 100+ commits from 15 distinct human
authors, 7 tagged releases, and named resolvable committers (Sammy Sidhu, Jay Chia). Every
one of those is a *GitHub* source, and the frozen rule collapses `github_org`,
`github_repo`, `github_commits` and `github_releases` into **one** channel.

So the rule that exists to stop single-channel false positives also blocks the single
strongest true positive in the cohort. That is a genuine precision/recall trade-off,
discovered by the method rather than argued about. **It is a RULE DESIGN weakness. It was
not fixed.** A v2 ontology should probably treat "GitHub org + independently-dated code
history + a package registry entry" as more than one witness — but changing it now would
make this holdout meaningless.

### Which signal types were useful historically
Only two: **repository/organization creation dates** and **commit history**. Both are
GitHub. Releases helped once (B1). Accelerator pages produced formation evidence with no
construction evidence (B3), which is insufficient under the frozen rules.

### The biggest systematic miss
**Companies with no public code.** B4, B5, B6, B9, B10 — five of ten — produced *zero*
recoverable pre-cutoff evidence. DAY ZERO can only see builders who build in public. For a
fund whose portfolio includes HealthTech, FinTech and vertical AI companies that ship
closed products, that is a structural coverage limit, not a tuning problem.

Two name collisions were correctly refused during evidence assembly: `flamingo-run` (a
Brazilian GCP serverless org) and `integral-ai` (a robotics company) share names with Array
portfolio companies and were **not** merged.

---

## Intro Queue

Three leads cleared. **CURRENT 3 emitted. Nobody contacted.**

1. **`multikernel/sandlock`** — Cong Wang + 8 contributors. Analyst override from WATCH
   (identity resolvable by ER-1 artifact cross-reference that the GitHub-only check
   couldn't see). Four channels, 17-month spread, arXiv paper, commercial product.
2. **`sipyourdrink-ltd/bernstein`** — Alex Chernysh, solo, registered UK company,
   **3,669 commits**, 960 stars, deterministic orchestration with no model in the
   coordination loop. System-eligible without override.
3. **`scanaislop/aislop`** — Kenny Olawuwo, security engineer, 572 stars, code-quality and
   security gate for agent-authored code. Sits on **"vibe coding security"**, one of the
   four categories Array's April 2026 post says it is *actively seeking*. System-eligible.

Full cards with both required questions: `outputs/analyst_cards.md`.

## Watchlist

63 entries. The most useful:

- **`h5i-dev/h5i`** (Hideaki Takahashi, Columbia PhD) — system-**eligible**, held by
  analyst judgement. Rust per-agent disposable sandboxes, pushed daily. Nothing
  distinguishes a research prototype from a company yet. *Best watchlist candidate.*
- **`vivekchand/clawmetry`** — 3,112 of 3,142 human commits are the founder's; no
  contributor above 17 commits; at least three near-identical tools now in the universe.
- **`spinningfactory/kloak`** — on Array's agent-identity mandate; the Sapiom
  differentiation question is unanswered from public evidence. *Not penalised for the
  adjacency itself.*
- **`linnix-os/linnix`** — the "why not cheaper Datadog" question remains unanswered, and
  the repo carries no licence, which also caps reproducibility.
- **`getagentseal/codeburn`** — downgraded by the thematic-mirroring guard (below).

### Thematic-mirroring guard: CodeBurn

Asked directly — *would CodeBurn be interesting if Array had never published the Accepted
Work Unit argument?* It is a local cost-accounting reader over 37 agent log formats:
integration-level depth, npx-distributed, real but not scarce. The universe now contains
**three** tools doing substantially the same job (`codeburn`, `agentacct`, `clawmetry`),
which is the clearest available evidence that the idea is not scarce. Its Phase 1
distinctiveness came substantially from vocabulary resonance with Array's own writing.
**Downgraded to WATCH.** The guard did its job.

---

## Source Yield

| Channel | Raw | Review candidates | INTRO_READY | Cost |
| --- | --- | --- | --- | --- |
| GitHub | 102 | 8 | 3 | $0 |
| Research | 6 | 0 (evidence only) | 0 | $0 |
| Web (domains) | — | 73 formation signals | — | $0 |
| X | 0 | 0 | 0 | $0 |
| Hackathon / events | 0 | 0 | 0 | — |

**Funnel:** 102 repositories → 267 identities → 66 system-passing on artifact+depth →
8 REVIEW → **3 INTRO_READY_AWU**.

**Highest Intro-Ready yield: GitHub** (trivially — it is the only live channel).
**Noisiest source: GitHub search descriptions.** Theme classification runs off repository
descriptions, and one test caught a plain-text budget tracker matching "agent economics"
via the word *budget*. The marker was tightened before the freeze; the failure mode is
inherent to description-based classification.

**Cost per INTRO_READY_AWU: $0.00 in API spend** (1,271 free requests). Human review time
was **not instrumented** and is therefore **not reported** — inventing it would be worse
than omitting it. Phase 1's own estimate of ~1.7 analyst-hours per accepted lead remains
the only figure available, and it is an estimate from a different system.

---

## Agent Execution & Accountability

**It remains the strongest first theme, and Phase 2 strengthened the case.**

All three Intro Queue leads sit inside it, from three different sub-themes: execution
isolation (sandlock), objective verification (bernstein), and code accountability (aislop).
That is convergent evidence from independent builders rather than thesis-fitting.

Theme distribution across the 102-repo universe: `agent_execution_isolation` and `security`
are the largest clusters; `agent_memory_context` is the most crowded and lowest-signal, as
Phase 1 predicted; `agent_economics` — after the marker was tightened — is the smallest and
least contested.

Two honest adjustments:
- **`agent_verification` deserves promotion.** Bernstein's "no model in the coordination
  loop" and aislop's CI gate are both verification plays, and the category was under-weighted
  in Phase 1 relative to isolation.
- **`agent_memory_context` should be de-prioritised.** It produced the two highest-star
  eligible candidates (graphify, mempalace), both rejected — one as already-obvious, one on
  an unfalsifiable claim. High attention, low discoverable signal.

---

## SF Field-Sourcing Plan

**Designed, wired, and deliberately empty.**

`data/manual/events.yaml` contains zero records. The import path exists and is tested
(`test_manual_event_requires_sourcing_fields`, `test_event_attendance_defaults_to_not_attended`),
and `events.attendance_status` defaults to `NOT_ATTENDED` at the schema level with a CHECK
constraint. **The system never sets `ATTENDED`; only a human may.** A test asserts the
count of `ATTENDED` rows is zero.

No events were researched in Phase 2 because the engine was the priority and populating a
forward-looking calendar has a shelf life of weeks. The plan for Phase 3:

| Event type | What to look for | Maps to |
| --- | --- | --- |
| SF hackathons (AI Tinkerers and university-run) | Teams that existed *before* the event; whoever wrote the hard part | Pool A discovery; the only channel that reaches builders with no repo yet |
| Systems / kernel meetups | Maintainers of things other attendees already depend on | `agent_execution_isolation` — where sandlock-class builders actually are |
| Security meetups | People building enforcement, not dashboards | "vibe coding security", Array's stated unfilled category |
| Research talks (Berkeley, Stanford) | PhD students shipping tools beside papers | The h5i / AgentSight profile |
| Demo days | Nothing | By demo day the round is usually done |

**The rule that makes this worth doing** (negative control NC-8): a hackathon signal cannot
contribute to the Intro Queue until a BUILD signal appears **≥90 days after the event**.
The signal is persistence, never the win. That also turns an in-person evening into a
durable asset: a name noted in August becomes a checkable GitHub query in November.

This channel matters more after Phase 2, not less. It is one of only two places the
career-class gap (68.2% UNCLASSIFIED) can actually be closed, and unlike X it does not
depend on someone having published a linkable handle.

---

## Privacy / Ethics

Enforced in code, not just in prose. `tests/test_privacy.py` asserts:
no forbidden column exists in the 35-table schema (address, phone, family, demographic,
health, political, precise location, `departure_*`, `is_leaving`); no sensitive phrasing
appears in any canonical output; **no email address appears in any output**; the builders
export carries only eight professional fields; `attendance_status='ATTENDED'` count is zero;
`contacted` count is zero.

No forbidden inference was used. Employer fields appear as context only —
`test_employer_field_is_never_a_formation_signal` asserts no formation-class evidence row
is justified by employment. Tejas Chopra's "Netflix, Inc." field and Ryan Codrai's
"Anthropic" field are both recorded and both explicitly excluded from formation reasoning.

---

## Limitations

1. **0 PASS in the holdout.** The convergence rule blocks single-channel true positives.
   Known, documented, not patched.
2. **One live channel.** GitHub discovered 100% of the universe. X is off; hackathons and
   events are empty. Calling this multi-channel would be false.
3. **Closed-source companies are invisible.** Five of ten holdout cases produced zero
   recoverable evidence.
4. **Theme classification reads repository descriptions**, which is shallow and
   English-biased.
5. **Formation signals attach to the wrong subject.** F-03 (founder statement) attaches to
   a person; F-01 (domain) attaches to a repository; nothing joins them. This is why
   ClawMetry showed `NO_FORMATION_EVIDENCE` despite having both. **Rule/model design gap,
   documented, not patched.**
6. **Two of three Intro Queue leads needed the analyst.** One required an override; the
   others required analyst-authored questions. This is not an autonomous system and does
   not claim to be.
7. **Human review time was never measured**, so cost-per-AWU is incomplete.
8. **The holdout is a design validation, not a measurement.** Ten known portfolio companies
   evaluated by someone who knows they are portfolio companies cannot produce a statistic.
9. **Strict author matching costs real links** (AgentSight).

---

## Phase 3 Plan

1. **Run EXP-1** (headroom token compression) against a frozen, hashed corpus with a
   minification baseline. It remains primary: most falsifiable claim in the universe, runs
   on an 8 GB M1, genuinely uncertain outcome. **EXP-2 (rtk) remains backup.**
2. **Full technical diligence on `multikernel/sandlock`** — a different target from the
   reproduction, deliberately. It has a paper with a stated threat model, real code, a
   named commercial product, and competitive alternatives (Firecracker, gVisor, Landlock)
   to compare against.
3. **Fix the two documented design gaps as a v2 ontology**, with the v1 holdout results
   left published beside them: join person-level and artifact-level formation signals, and
   reconsider whether GitHub sub-sources constitute one witness or several.
4. **Solve the identity join before spending on X.** The bottleneck is not X's noise; it is
   that 0.37% of builders publish a linkable handle.
5. **Instrument analyst review time**, so cost-per-AWU is a real number.
