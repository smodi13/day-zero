# DAY ZERO — Phase 1 Report

**Date:** 2026-08-22 · **Status:** Phase 1 complete. Phase 2 not started.
**Author:** Sahil Modi, with Claude Code assistance (see §42).

Answers to the 48 decision-gate questions, in order.

---

### 1. What I learned about Array Ventures
$250M+ AUM across 4 funds, 80+ portfolio companies (52 shown as active on the site — the
two figures are inconsistent and are probably lifetime vs. active). Pre-seed, "at
inception," $250K–$3M, 9–10 investments a year against **200–300 inbound deals per month**
already triaged with AI tooling. Solo GP Shruti Gandhi — practicing AI engineer, Columbia
CS professor, SFERS commissioner — plus Elias Torres, Katie Jansen, Roy Scheer. Areas: AI
infrastructure, cybersecurity, HealthTech, FinTech, enterprise SaaS. Decisions in 48 hours.
Full detail and citations: `array_strategy.md`.

### 2. What appears genuinely distinctive
Three things, all source-backed:
- **They rebuild products to understand them.** *"In many cases, we attempt to recreate
  parts of a product ourselves to understand the technical complexity."* (Jan 2026)
- **They start the relationship before the round exists.** They led Sapiom's pre-seed
  roughly three weeks after the founder left Shopify; they wrote HappyRobot's first check
  when the founders "hadn't raised anything" and were pitching from Germany.
- **Their own building generates their thesis.** Sapiom's problem was identified "while
  testing agents in Array's own stack at the Array Ventures AI lab."

The implied inbound-to-investment rate is ~0.3%. This is a fund that is **inbound-saturated
and outbound-constrained** — which is the whole opportunity for DAY ZERO.

### 3. What Array AI Labs appears to do
Two things under one name. A **content lab** (AI-generated podcasts from guests' existing
public interviews; AI-generated video via NanoBanana/Kling/Seedance/ElevenLabs/Qwen), and
an **internal-operations engineering lab**: *Joyce*, a 24/7 office-hours agent for founders;
AI deal triage (300+ deals in under 48 hours, using portfolio companies Wokelo and Runable);
and a **24/7 AI coworker that replaced half their internal tools** — persistent structured
memory, a background observation→knowledge-base process, a "heartbeat" wake pattern, its own
filesystem sandbox with isolated execution, and on-demand tool acquisition. The second lab
produced an investment. UNKNOWN: headcount, budget, whether any Labs code is public.

### 4. Most relevant current themes from Shruti/Array's public writing
1. **Loop→Graph engineering and Accepted Work Units** (2026-07-22) — loops, hard exit
   conditions, objective verification, cost per accepted work unit, the Ralph Wiggum
   failure, goal drift, the **LoopOps stack** (job specs, state ledgers, tool envelopes,
   completion gates, budget policies, escalation queues), and vertical loops as defensibility.
2. **Agent security** (2026-04-28) — ~100 non-human identities per human user; agents as
   processes moving data through syscalls; four **explicitly-sought** categories: agent
   identity & authority, autonomous SOC/IR, AI red-teaming & pre-deployment testing, and
   "vibe coding security."
3. **AI economics infrastructure** (Theme 3) and **context management** (Theme 7).
4. **Governance / control layer** (Theme 2) and **edge intelligence / inference efficiency**
   (Theme 4).

Not publicly supported and therefore not claimed as Array themes: MCP-specific security,
agent evaluation as a standalone thesis, RL environments.

### 5. Should agent infrastructure be the first technical theme?
**Yes, but narrowed** — see `agent_infrastructure_thesis.md`. Unqualified "agent
infrastructure" covers both the most crowded area in open source (memory/context) and the
least crowded (economics), and adopting it wholesale would drown the system in wrappers.

**Recommended first theme: the agent execution and accountability layer** — isolation
boundaries, identity and authority, budget enforcement, and cost-per-accepted-work-unit
measurement. It sits at the intersection of Array's two most recent posts, is the area
where Array has *operating* rather than only thesis evidence, and — decisively — its claims
are verifiable on a laptop, unlike KV-cache quantization.

Second theme: agent-era security. Backtest theme: data infrastructure.

### 6. Exact previous X sourcing engine located
**`~/headline-x-sourcing`** — the canonical private engine. Python package `src/sourcing/`,
46 modules, ~12,450 LOC, 35 test files, 16 YAML configs, real run outputs in `data/output/`.
`pyproject.toml` name `headline-x-sourcing`, console script `headline-sourcing`.
Also found: `~/x-sourcing-engine-showcase` (sanitized public excerpt + 6 design docs, MIT),
`~/ldv-x-sourcing-engine` (re-skinned frontend), `~/x-sourcing-engine-showcase-private`
(3 text files), `~/ldv-thesis-engine` (unrelated).
**All were treated as read-only. Nothing was modified, committed, or executed.**

### 7. What the existing X engine does
Thesis → curated queries (3 topic groups × 3 discovery lanes) → operator validator →
count preflight → **fingerprint-gated human approval** → recent search → SQLite cache →
URL canonicalization → deterministic extraction with Level A–D evidence tagging → builder
attribution across six independent dimensions → dedup and project consolidation →
deterministic 100-point scoring → platform-risk and replication overlays (both non-scoring)
→ six-bucket classification → selective profile enrichment → diligence queue → human
decision. Exact-Decimal cost ledgers, append-only audit trails, header-aware bounded rate
limiting, aware-UTC-only time handling. 450 tests. Real runs: 1,166 net-new posts → 153
analyst-adjudicated projects for ≈USD 7.72.

### 8. What should be reused
**Port nearly as-is:** `money.py` + `ledger.py` (exact-Decimal cost + append-only audit),
`approval.py` (SHA-256 canonical-request fingerprint, TTL, fail-closed), `timeutil.py`
(aware-UTC-only — a *correctness* precondition for an honest backtest), `urlutil.py`,
`registry.py` (exact/dot-boundary matching, substring forbidden), `validator.py`,
`ratelimit.py`, `cache.py`, `governance.py`.
**Reuse the concept:** evidence levels assigned at extraction time from source type; decay
only time-sensitive signals; ownership as six independent dimensions; engagement as
non-scoring; deterministic-first with the LLM never scoring; the explicit statement that
"a Post is not a project, and a project is not an incorporated startup."
**Reuse the discipline:** count-preflight before spend, fail-closed defaults, raw responses
stored before derived output, a published limitations page, metrics reconciliation.

### 9. What should NOT be reused
The 100-point total score (DAY ZERO has no totals); `customer_pull` and `workflow_depth` as
*surfacing* inputs (at Day 0 there are no customers, and requiring them guarantees you only
find the already-visible); `shipping_momentum` scored from raw counts; the category-based
platform-risk heuristic (config rot); the X-only `Company` entity model; the seven-day
window baked in as an assumption; the Next.js showcase frontends; and the customer/usage
keyword banks, which select for marketing language.

### 10. Recommended role for X within DAY ZERO
**One discovery channel of eight, off by default.** X is the fastest surface for four things
no other channel gives: a builder's own words about what they're building; an *explicit*
transition statement (the only legitimate Pool B evidence); hackathon results with no other
index; and a visible new collaboration before a shared repo exists. Governing rule: an X
post is Tier 1 evidence of a *statement* and Tier 3 evidence of a *fact*. Required pipeline:
POST → IDENTITY → ARTIFACT → INDEPENDENT CONFIRMATION → ANALYST REVIEW. Preconditions
before any spend: re-verify pricing (the audited reference is dated 2026-07-18 and past its
own 30-day staleness gate), confirm whether historical search exists at an affordable tier,
set a budget through the ported approval gate.

### 11. Final two-pool framework
**Pool A — young builders:** recent grads, grad students, hackathon participants, research
engineers, OSS maintainers, lab researchers. Evidence: repos, papers, official hackathon
results, lab pages, package registries.
**Pool B — operator → founder:** operators who have **publicly stated** they are building;
new orgs; new collaborations; early launches; founding-engineer recruiting.
Evidence: explicit first-person statements, org creation dates, domains, filings.
**Prohibition:** no inference of employment change from silence, inactivity, deleted posts,
bio edits, or rumor. **Finding:** only 31% of builders could be pool-classified from GitHub
alone (§22) — which is the strongest argument for keeping the X and in-person channels.

### 12. Final signal ontology
Seven families, frozen at v1.0: **BUILD** (B-01…B-09), **TECHNICAL DEPTH** (D-01…D-10),
**COLLABORATION** (C-01…C-05), **FORMATION** (F-01…F-08), **VELOCITY** (V-01…V-06, where
V-06 abandonment is a first-class signal), **COMMERCIALIZATION** (M-01…M-07, recorded but
barred from surfacing), **SOCIAL/X** (S-01…S-08, discovery only). Plus **cross-source
convergence** as a property of a signal set, not a signal type. Full definitions with
verified examples: `signal_ontology.md`.

### 13. Most useful 10–15 public sourcing sources
GitHub REST · GitHub Search · GitHub GraphQL · arXiv API · OpenAlex · package registries
(PyPI/crates.io/npm) · Wayback CDX · SEC EDGAR · LKML/lore.kernel.org · Hacker News
(Algolia) · personal sites & blogs · official hackathon pages · accelerator cohort pages ·
conference programs · X API v2. Full table with limits and costs: `data_sources.md`.

### 14. Which sources are programmatic
GitHub (REST/Search/GraphQL), arXiv API, package registries, Wayback CDX, SEC EDGAR, HN
Algolia, direct fetch of personal/company sites. Paid/gated: X API v2, OpenAlex,
Semantic Scholar.

### 15. Which sources require manual research
Devpost (**by policy** — its `robots.txt` explicitly disallows `anthropic-ai`, `GPTBot`,
`ChatGPT-User`, `CCBot`, `Google-Extended`; verified 2026-08-22), individual hackathon
sites, accelerator cohort pages, conference programs, university lab pages, and all SF
in-person events.

### 16. Biggest data-access constraints
1. X recent search is a **7-day window** — the channel best suited to founder transitions
   has the shortest memory, and cannot support the backtest at all.
2. The hackathon channel is closed to automation by policy.
3. **There is no join key between GitHub and X identities.** Identity resolution depends on
   people voluntarily publishing links.
4. GitHub Search caps at 1,000 results per query with opaque relevance ordering.
5. Non-English and non-GitHub ecosystems are structurally under-covered.
6. X pricing reference is stale; no spend permitted until re-verified.
7. **No public source reliably indicates employment change**, and DAY ZERO forbids inferring
   it — so Pool B is fundamentally harder than Pool A.
8. Wayback coverage of small project sites is sparse, capping the backtest's use of web pages.

### 17. Founder-formation states
`BUILDING` → `COLLABORATING` → `FORMING` → `LAUNCHED` → `FUNDED`, plus `UNKNOWN`.
Entry conditions are deterministic; **FORMING requires ≥2 formation signals from ≥2
independent channels.** DAY ZERO's window is BUILDING → COLLABORATING → FORMING, before
FUNDED. No probability of founding is ever computed. `formation_framework.md`.

### 18. Technical-quality framework
Nine independently-assessed dimensions, each tagged OBSERVED/INFERRED/UNKNOWN, **with no
total**: TQ-1 difficulty (L0–L4) · TQ-2 originality · TQ-3 systems depth · TQ-4 research
depth · TQ-5 reproducibility · TQ-6 performance evidence · TQ-7 usage evidence · TQ-8
architecture clarity · TQ-9 the defensibility *question* (a question, not a rating).
The honest limitation: TQ-1 and TQ-5 usually cannot be assessed from outside — which is the
entire argument for the reproduction lab.

### 19. Accepted Work Unit definition
**One AWU = one founder or team lead that survives analyst review and is genuinely worth an
introduction.** Not a profile processed, not a signal ingested, not a candidate surfaced.
Eleven metrics defined (`accepted_work_unit.md`), none optimized in Phase 1. Baseline to
beat, derived from the audited engine's own run: ≈USD 2.13 API cost and **≈1.7 hours of
analyst time per AWU**. Any Phase 2 change that lowers API cost while raising analyst time
is a regression.

### 20. Weekly 3 definition
Three builder/team leads per cycle that survive analyst review and are worth relationship
capital. Fifteen mandatory fields including `why_non_obvious` (falsifiable) and
`what_would_make_us_drop_it` (written before outreach). **If fewer than three survive,
return fewer.** Calibrated against Array's ~2–3 intros/week against 9–10 investments/year.

### 21. Number of real builders/projects researched
**45**, every one verified against the GitHub API on 2026-08-22 (and the arXiv API where
relevant). `initial_builders.csv` (20 fields × 45 rows) and `initial_builders.md`.

### 22. Breakdown by pool
Pool A: **8** (18%) · Pool B: **6** (13%) · **U — career stage not publicly determinable:
31 (69%)**.
This is a finding, not a gap in the research: GitHub tells you what someone built, not
whether they are a second-year PhD student or a fifteen-year staff engineer, and inferring
it from account age or repo topic is exactly the guessing this project forbids.

### 23. Breakdown by primary source channel
GitHub only: **41** · GitHub + arXiv: **3** · GitHub + LKML + company site: **1** ·
X/social: **0** · Hackathon: **0**.
The zeros are honest: Phase 1 had no X access and the hackathon channel is manual-only.

### 24. The 15 most interesting initial leads
| # | Builder / team | Project | Area | Pool | State |
| --- | --- | --- | --- | --- | --- |
| 1 | Cong Wang | multikernel / kernelscript | Kernel, eBPF, isolation | B | LAUNCHED |
| 2 | Vivek Chand | ClawMetry | Agent observability + cost governance | B | FORMING |
| 3 | Resham Joshi | CodeBurn / AgentSeal | Agent cost accounting | B | FORMING |
| 4 | Parth Shah | Linnix | eBPF observability + incident detection | U | FORMING |
| 5 | Dhia Ayachi | kloak | Zero-trust for agent runtimes | B | FORMING |
| 6 | `mikehasa` | agentacct | Agent work-step accounting | U | BUILDING |
| 7 | Yusheng Zheng | AgentSight | eBPF agent observability (+ paper) | A | COLLABORATING |
| 8 | Derek Chong + collaborators | Shepherd | Reversible agent execution | A | COLLABORATING |
| 9 | `Karib0u` | Rustinel | Cross-platform EDR in Rust | U | BUILDING |
| 10 | `brontoguana` | krasis | Hybrid LLM runtime, VRAM-limited | U | BUILDING |
| 11 | Hideaki Takahashi | h5i | Per-agent disposable sandboxes | A | FORMING |
| 12 | BoxLite team | boxlite | Embeddable micro-VM | U | FORMING |
| 13 | DeepLethe / `WaylandYang` | forkd | KVM microVM CoW fork | U | BUILDING |
| 14 | Jiarong Xing + collaborators | kvcached | Elastic KV cache / GPU sharing | A | COLLABORATING |
| 15 | Hiroki Suezawa | cicd-sensor | eBPF CI/CD supply-chain security | B | BUILDING |

### 25. Provisional Weekly 3
**Nobody has been contacted.** Five of twelve reviewed candidates survived the disqualifiers.
Three selected:

**W1 — Cong Wang / Multikernel Technologies.**
*Why this person:* Linux kernel traffic-control maintainer since 2017, 1,000+ kernel
commits, prior Red Hat/Twitter/ByteDance, now Founder & CEO of Multikernel Technologies.
Built `kernelscript`, a type-safe OCaml DSL for eBPF-centric kernel customization, and
submitted the multikernel patch series to LKML in September 2025 — per-application dedicated
kernel instances giving kernel-level isolation without hypervisor overhead.
*Why now:* org created 2025-03-08 → LKML patches Sept 2025 → personal GitHub account
created 2025-08-21 → repo active through 2026-06-26. A formation arc spread across 15 months
and four independent channels.
*Why Array:* isolation is the primitive the entire agent-sandbox category is reaching for
from above; Array's own AI coworker runs in a sandbox with isolated execution; adjacent to
Theme 4.
*Why not obvious:* **72 GitHub followers, 2 public personal repos, no X-native presence.**
The highest-signal evidence lives on a kernel mailing list and in an OCaml repository —
surfaces no AI sourcing tool indexes.
*Technical question:* does per-application kernel isolation beat microVM snapshot-restore on
cold-spawn latency *and* memory amplification, or only on steady state?
*Commercial question:* is the buyer a hyperscaler or an agent platform? Those are different
companies.
*Must verify before intro:* whether an institutional round has already closed; whether the
LKML work has upstream traction; whether the commercial wedge is AI workloads.

**W2 — Vivek Chand / ClawMetry.**
*Why this person:* **3,111 owner commits against 399 stars** — a 7.8:1 construction-to-
attention ratio, among the highest in the universe. Zero-config observability *and
governance* across 20+ agent runtimes: live token costs, sessions, tool calls, crons.
*Why now:* created 2026-02-13, pushed 2026-08-23, `clawmetry.com` live, self-published
first-person "Building ClawMetry."
*Why Array:* Themes 2 and 3 simultaneously — the control layer and the economics layer.
*Why not obvious:* 95 followers, 399 stars, Amsterdam. Invisible to every popularity ranker.
*Technical question:* does zero-config instrumentation stay *correct* across 20+
heterogeneous runtimes, or degrade to lowest-common-denominator metrics?
*Commercial question:* is agent governance a buying center in 2026, or a 2027 category?
*Must verify before intro:* whether there is a team; whether the governance claim is
enforcement or reporting. **His current employment is context only and must not be raised
as, or read as, a departure signal.**

**W3 — Resham Joshi / CodeBurn.**
*Why this person:* built local-first per-task cost attribution across 37 agent tools —
independently converging on **cost per unit of work**, which is Array's own published
metric. Stated motivation: "Built CodeBurn because 50M tokens/week is wild."
*Why now:* org created 2026-04-18, 1,234 commits, `npx` distribution, explicit first-person
founder statement.
*Why Array:* Theme 3 and directly the Accepted Work Unit frame from July 2026.
*Why not obvious:* three named projects from one founder reads as unfocused to any system
scoring consistency; he is in Germany, not SF.
*Technical question:* does per-task attribution across 37 heterogeneous tools produce
*comparable* units, or 37 incomparable ones? Comparability is the entire product.
*Commercial question:* who pays — the engineer or the finance function?
*Must verify before intro:* which of three projects is the company; whether there is a
co-founder.

### 26. Evidence supporting each
**W1:** GitHub org `multikernel` created 2025-03-08 (API) · `multikernel.io` and
`multikernel.io/about.html` · LKML patch series Sept 2025, independently reported ·
GitHub bio "Founder and CEO at @multikernel" · `kernelscript` 502 stars / 524 owner commits
/ Apache-2.0 · account created 2025-08-21. **Four independent channels, 15-month spread.**
**W2:** `clawmetry` 3,111 owner commits, MIT, created 2026-02-13, pushed 2026-08-23 (API) ·
`clawmetry.com` · self-published bio. Identity HIGH.
**W3:** `codeburn` 9,609 stars / 1,234 top-contributor commits / MIT / created 2026-04-13 ·
org `getagentseal` created 2026-04-18 · `codeburn.app` + `agentseal.org` · explicit
"Founder · CodeBurn, Eywa, AgentSeal" bio. Identity HIGH.

### 27. Biggest weakness for each
**W1:** he may already be funded. A kernel founder with this record and a company since
March 2025 is not undiscovered by everyone — only by attention-ranked systems. **This is the
single most likely way W1 is wrong.**
**W2:** one person, no org, no company entity, no team. Formation rests on a domain and a
bio line. Observability is also brutally crowded.
**W3:** three concurrent projects. Focus is a genuine open question, and cost tracking is a
plausible feature of the coding tools themselves rather than a company.

### 28. Three strongest cross-source formation signals
**CS-1 — Cong Wang / Multikernel:** four independent channels (GitHub org, company domain,
LKML, personal profile) spanning March 2025 → June 2026. The LKML channel is unfakeable.
**CS-2 — AgentSight:** arXiv:2508.02736 (2025-08-02) ↔ repo (created 2025-07-07) with
author↔committer overlap. The repo predates the paper by 26 days. Converges to
COLLABORATING, **not** FORMING — eunomia-bpf is an established community.
**CS-3 — UCCL:** two arXiv papers (2512.19849, 2604.17172) ↔ 16 months of repo history ↔
verified author↔committer overlap. High-confidence convergence, **low non-obviousness** —
the author list includes Ion Stoica and Scott Shenker, and pretending that is a discovery
would be hero worship.
Full analysis plus three instructive near-misses: `cross_source_signals.md`.

### 29. Historical holdout companies selected
Eventual/Daft · Sapiom · HappyRobot · Flamingo · Meibel · Integral · Mozart Data · ZecOps ·
Era Software · Wokelo. Ten, selected on **evidence recoverability, not success**, with three
expected misses kept deliberately. Excluded and why: `array_portfolio_map.md` §4.

### 30. Proposed cutoff dates
B1 Eventual **2024-09-30** · B2 Sapiom **2026-02-04** · B3 HappyRobot **2024-12-03** ·
B4 Flamingo **2025-10-27** · B5 Meibel **2025-05-27** · B6 Integral **2023-09-04** ·
B7 Mozart Data **2020-11-10** · B8 ZecOps **2020-01-01** · B9 Era Software **2021-10-05** ·
B10 Wokelo **2024-10-08**.
**Predicted before running: 3 PASS, 2 PARTIAL, 3 MISS, 2 UNKNOWN (~30% hit rate).**

### 31. How look-ahead bias will be prevented
Two timestamps on everything (`observed_at`, `collected_at`); backtests filter only on
`observed_at`. **Fields with no defensible `observed_at` — current stars, current followers,
current bio, current README — are excluded from the backtest surface entirely rather than
approximated.** Evidence is reconstructed from timestamped sources (GitHub `until=`, arXiv
`published`, registry release dates, Wayback snapshots strictly before the cutoff). Blind-run
protocol with the analysis committed before the outcome, so git history is the audit trail.
Post-cutoff information lives only in an `OUTCOME` field referenced by no rule. A per-case
leakage checklist. Ontology and criteria hashed before the run.
**Stated honestly:** I already know these are Array portfolio companies, and that biases
where I look. It is mitigated by expected-outcome pre-registration, deliberate expected
misses, negative controls run through the same criteria, a mechanical decision rule, and
recording close calls as PARTIAL. It cannot be eliminated, and claiming otherwise would be
the dishonest move.

### 32. Negative-control design
Eleven controls, **every one a real verified artifact**, not a strawman: viral repo with 2
commits (NC-1) · thin wrapper as infrastructure (NC-2) · abandoned project with a real
formation shell (NC-3) · precise benchmark claim, no license, dead (NC-4) · **strong
artifact by a frontier-lab engineer with zero formation evidence (NC-5 — the mistake I would
most plausibly make)** · established org resurfaced as new (NC-6) · research with no
formation (NC-7) · hackathon demo that stopped (NC-8) · large following, weak artifact
(NC-9) · excellent but out-of-scope (NC-10) · **name-collision false positive using two
real collisions from Array's own portfolio (NC-11)**.
Pass criteria include: no rule may be added after seeing a control, and no control may be
rejected by a rule that also rejects a cohort company expected to PASS.

### 33. Three to five potential reproduction experiments
EXP-1 headroom token compression · EXP-2 rtk token-reduction proxy · EXP-3 agentmemory
benchmark-claim provenance · EXP-4 forkd microVM fork latency (cloud) · EXP-5 shepherd
reversible-execution overhead and KV-cache reuse (cloud). Full protocols:
`reproduction_lab.md`.

### 34. Recommended primary experiment
**EXP-1 — `headroomlabs-ai/headroom`.** Claim: *"20% fewer tokens for coding agents, 60–95%
fewer tokens for JSON, same answers."* Baselines: no compression, plain JSON minification,
and gzip. Test: a frozen, hashed corpus of real agent tool output; token distributions, not
means; plus ~30 questions answerable only from the corpus, asked against compressed and
uncompressed context to test "same answers."
Chosen because the outcome is genuinely uncertain — **I do not know whether the 60–95% JSON
figure survives a whitespace-minification baseline**, and that is exactly why it is worth
running.

### 35. Recommended backup experiment
**EXP-2 — `rtk-ai/rtk`** ("60–90% token reduction on common dev commands"). Same theme,
different implementation; running both converts two marketing claims into one head-to-head
measurement. Backup rather than primary only because it depends on a published arm64 release
binary (cargo is not installed locally).
EXP-3 is cheap enough that it should probably run alongside the primary regardless.

### 36. Can the primary experiment run locally / cheaply?
**Yes.** Verified local environment: Apple M1, arm64, **8 GB RAM**, Python 3.14.3, Node
24.14.0, no cargo, no Docker, no CUDA, no KVM. EXP-1 needs a tokenizer, a corpus, and a few
dollars of small-model calls.
**Equally important: EXP-4 and EXP-5 CANNOT run locally** — they need KVM and Linux. They
are explicitly deferred to a ~USD 5–15 cloud tier rather than quietly dropped or, worse,
claimed.

### 37. Best initial technical diligence question
> **"What in this system would still be hard for a strong team with a year and real funding
> to reproduce — and can you show me the part where that difficulty lives?"**

It is the operational form of TQ-9, it cannot be answered with a demo, and the *shape* of
the answer is diagnostic: strong builders answer with a specific subsystem and a reason;
weaker answers reach for "the team," "first-mover advantage," or "the model."
For W1 concretely: *does per-application kernel isolation beat microVM snapshot-restore on
cold-spawn latency and memory amplification, or only on steady state?*

### 38. SF ecosystem module design
Tracks hackathons, meetups, research talks, demo days, builder nights and university events
as public forward-looking records. Schema includes `sourcing_objective` and
`builder_profile_sought`; **`attendance` defaults to null and is human-entered only — the
system never represents the operator as having attended anything.** The governing rule
(NC-8): a hackathon signal cannot contribute to a Weekly 3 until a BUILD signal appears
**≥90 days after the event** — persistence, not the win. Demo days are rated low-value on
purpose: by demo day the round is usually done. `sf_ecosystem.md`.

### 39. Privacy / data-ethics rules
**DAY ZERO researches what people build. It does not research people.**
No addresses, phone numbers, or private emails · no family, demographic, political,
religious, health, or sexuality data or inference · no location beyond self-published
professional context · no data brokers · nothing behind a login or a prohibiting robots
policy · no deleted content · **no inference of employment change from silence, inactivity,
deletion, or a bio edit** · no de-anonymization of pseudonymous builders · no scoring of
human beings · removal on request without question · adverse technical findings stay
internal. The test before adding any field: *would this builder recognize their record as a
fair description of their public work, or would they feel surveilled?* `data_ethics.md`.

### 40. Recommended Phase 2 architecture
```
config/  frozen ontology + query specs, versioned and hashed
  ↓
ingest/  github_rest · github_search · arxiv · registries · wayback · edgar
  ↓      (each: rate-limited, cached, raw-response-first, timestamped)
resolve/ entity resolution (ER-1..ER-6) — conservative, never merges on name
  ↓
signal/  deterministic signal extraction → signals + signal_sources
  ↓
state/   formation_states (deterministic) + technical_assessments (human/AI-assisted)
  ↓
review/  analyst queue → weekly3 (human decision)
  ↓
lab/     reproduction experiments (frozen corpus, published harness)
  ↓
backtest/ cutoff-filtered replay + negative-control suite
```
SQLite, Python, deterministic-first. **No score column anywhere** — enforced by schema.
Ported from the audited engine: `money`, `ledger`, `approval`, `timeutil`, `urlutil`,
`registry`, `validator`, `ratelimit`, `cache`, `governance`.
Build order: GitHub → arXiv → Wayback → registries + personal sites → EDGAR → LKML/HN → X
last, gated. **No frontend until the underlying system earns one.**

### 41. Exact files created
```
day-zero/
  .gitignore
  README.md
  research/array_strategy.md                  research/array_portfolio_map.md
  research/existing_x_engine_audit.md         research/signal_ontology.md
  research/entity_graph.md                    research/formation_framework.md
  research/technical_quality_framework.md     research/weekly3_framework.md
  research/accepted_work_unit.md              research/data_sources.md
  research/x_channel.md                       research/backtest_methodology.md
  research/negative_controls.md               research/reproduction_lab.md
  research/agent_infrastructure_thesis.md     research/initial_builders.csv
  research/initial_builders.md                research/cross_source_signals.md
  research/sf_ecosystem.md                    research/data_ethics.md
  research/source_quality.md                  research/data_model.md
  research/phase1_report.md
  sources/source_registry.csv
  config/   (empty — .gitkeep)
  src/      (empty — .gitkeep)
```

### 42. Any code written
**No production code.** Three throwaway research scripts were run from the session
scratchpad and are deliberately **not** committed: a GitHub Search wrapper (`gh api` +
`jq`), a repo/contributor/org detail fetcher, and an arXiv title-phrase query script. Two
generator scripts produced `initial_builders.csv` and `sources/source_registry.csv` from
hand-verified data. Phase 1 wrote no pipeline, no database, and no frontend, per the mandate.

### 43. Validation status
| Item | Status |
| --- | --- |
| 45 builder records | ✅ Every repo, owner and org verified live against the GitHub API, 2026-08-22 |
| 4 research papers | ✅ Verified via arXiv API, exact title-phrase match |
| GitHub API limits | ✅ Verified live (core 5,000/hr, search 30/min, code_search 10/min) |
| Devpost + arXiv robots policies | ✅ Fetched and read, 2026-08-22 |
| Local hardware | ✅ Verified (M1, 8 GB, no cargo/docker/CUDA/KVM) |
| Array claims | ✅ Every figure traced to a cited public source; inconsistencies (80+ vs 52 companies; $2.5M vs $3M) reported rather than reconciled |
| Backtest | ⬜ **Designed and frozen. Not run.** |
| Reproduction experiments | ⬜ **Selected. Not run.** |
| Negative-control suite | ⬜ **Designed. Not executed.** |
| CSV integrity | ✅ 45 rows × 20 fields; 50 source rows × 11 fields; parsed and counted |

### 44. Git repository root
`~/day-zero` — verified with `git rev-parse --show-toplevel`.
Note: the home directory `~` is itself a git repository; `day-zero` was
initialized as an independent repo with its own `.git`, so its toplevel resolves to
`day-zero` and not to home.

### 45. Git commit hash
`5049772e748dc7e21df2bc67e5832e277b105721` (short: `5049772`), the Phase 1 commit on `main`. Committed after this report was written, so the hash names the commit that contains it.

### 46. Anything in this project concept I think is misguided
Five things, honestly:

1. **"Weekly" is the wrong cadence for formation.** Company formation does not produce
   weekly signal. A weekly system that re-ranks the same universe will manufacture novelty.
   The realistic model is a **standing watchlist where the week's work is detecting state
   transitions**, and some weeks correctly produce zero. The framework says this, but the
   name "Weekly 3" pushes against it.

2. **The two-pool taxonomy is not derivable from the best channel.** 69% of builders could
   not be pool-classified from GitHub. The pools are a *hiring* description of where to look,
   not a *data* schema. Forcing every record into A or B would require exactly the
   career-stage inference the project forbids.

3. **"Before the company is obvious" is partly a contradiction.** The evidence that makes a
   builder legible to DAY ZERO — a repo, an org, a domain, a paper — is public. Anyone
   looking at the same surfaces sees the same thing. The edge is not secret information; it
   is **reading the artifact properly and reading it consistently.** That is a smaller and
   more defensible claim than "we find hidden founders," and the project should make it.

4. **The reproduction lab does not scale to sourcing volume.** One experiment is days of
   work. At 2–3 leads a week it can serve maybe one lead a month. It is a *diligence*
   instrument, not a *sourcing* filter, and pretending otherwise would be automation theater.

5. **The backtest, done by one person who knows the portfolio, is a design validation and
   not a measurement.** Ten cases with a known answer key cannot produce a statistic. It
   proves the ontology detects real dated evidence and rejects plausible false positives.
   That is genuinely worth doing. It is not "our system would have found 7 of 10."

### 47. Three ways generic "AI VC sourcing tool" applicants will likely approach this differently
1. **They will build an LLM scorer.** Scrape profiles, prompt a model with "rate this founder
   1–100," rank, ship a leaderboard. It demos beautifully and is unfalsifiable, unauditable,
   and quietly encodes prestige — because the model's prior about "strong founder" is
   trained on who already got funded. DAY ZERO has **no score column anywhere**, enforced by
   schema, and its nine technical dimensions are deliberately uncombinable.
2. **They will optimize for volume.** "We processed 100,000 profiles." Volume is the easiest
   metric to move and the least correlated with usefulness — my own audited engine's honest
   number was 1,166 posts → 153 projects → maybe 3 real leads. DAY ZERO's unit is the
   **Accepted Work Unit**, and its baseline explicitly counts **analyst hours**, which is the
   cost that actually binds a four-person fund.
3. **They will tune the backtest until it wins.** Pick 10 famous portfolio companies, iterate
   the criteria until 8 light up, present 80% recall. DAY ZERO froze the ontology first,
   **published expected outcomes before running** (3 PASS / 2 PARTIAL / 3 MISS / 2 UNKNOWN),
   deliberately kept three companies it expects to miss, hashes the criteria before the run,
   and states the bias it cannot eliminate.

A fourth, quieter difference: most such tools will treat "left OpenAI to build something" as
a *signal to infer*. DAY ZERO treats it as a *statement to verify*, and refuses to infer it
at all — which costs recall, and is the right trade.

### 48. What would make DAY ZERO genuinely useful to Array rather than merely impressive
1. **Find the person on the mailing list.** W1 — a kernel maintainer with 72 GitHub
   followers who founded a company and submitted patches to LKML — is the proof of concept.
   No AI sourcing tool indexes LKML. A tool that reliably surfaces four or five people like
   that per quarter is worth more than one that ranks ten thousand.
2. **Watch `orgs/{login}.created_at`, not launch tweets.** The most informative field in the
   entire sweep was free, precisely dated, and unforgeable. Formation is a *decision*, and
   decisions leave registry entries before they leave marketing.
3. **Answer the question Array is already answering by hand.** They rebuild products to
   understand them. A system that arrives with the reproduction already run — "their
   compression claim survives a minification baseline; here is the harness" — saves the
   scarcest resource in a four-person fund.
4. **Report honest zeroes.** A week with one lead, or none, told plainly, is what makes the
   weeks with three credible. The fastest way to become ignored is to fill three slots.
5. **Measure the human cost.** Array measures AI work in Accepted Work Units. A sourcing tool
   that cannot state its cost per accepted intro — *including analyst minutes* — is asking a
   fund to take its usefulness on faith.
6. **Be small enough to actually run.** SQLite, Python, free APIs, one laptop. A four-person
   fund cannot operate a data platform. It can operate a script that runs on Monday and
   produces a short, sourced, honest document.

---

## AI disclosure

Claude Code was used substantially throughout Phase 1: organizing the research, gathering
and reading sources, querying the GitHub and arXiv APIs, structured extraction into CSV,
classification, auditing the prior X engine, drafting, and writing the generator scripts.

**The boundary, applied throughout:**
- Source facts are evidence. **AI output is not evidence.**
- OBSERVED / INFERRED / UNKNOWN are maintained separately, and AI-produced fields are
  labelled and require verification against a source to be promoted.
- **AI does not decide who should receive an investment or an introduction.**
- **AI never assigns a score to a person.** No model call in this project outputs a rating of
  a human being.
- The Weekly 3 selections, the disqualifications, the cohort choices, the expected-outcome
  predictions, and the judgements in §46 are analyst judgements.

Every factual claim in this repository about a real person, project, company, or paper was
verified against a primary source, and every such source is recorded in
`sources/source_registry.csv` with an access date.

---

## PHASE 1 DECISION GATE — STOP

Phase 2 has not begun and will not begin automatically.
