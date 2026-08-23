# DAY ZERO — Initial Builder Universe

**45 real builders / teams / technical projects.** Every record was verified against the
GitHub REST API on **2026-08-22**; papers were verified against the arXiv API the same
day. Nothing here is invented. Where a fact was not verifiable it is recorded as UNKNOWN.

Machine-readable version: `initial_builders.csv` (20 fields × 45 rows).

**This is not a ranking and not a final sourcing universe.** Its purpose is to
pressure-test the ontology against reality — and it did, producing four findings (§4)
that changed how I think the system should work.

---

## 1. How the universe was assembled

1. GitHub Search API, narrow topic queries windowed by `created_at`, across nine areas:
   agent memory, MCP/agent security, agent sandboxing, prompt-injection defense, agent
   identity, evaluation harnesses, inference/KV-cache, eBPF systems, and data infrastructure.
2. Candidates carried forward on **construction evidence**, not stars: owner commit count,
   contributor breadth, language/layer, license, and `pushed_at` recency.
3. Repository metadata pulled per candidate (`repos/{owner}/{repo}`).
4. Contributor lists pulled per candidate, with `[bot]` logins excluded.
5. Owner and organization profiles pulled — including **org `created_at`**, which is a
   formation signal, and **personal account `created_at`**, which occasionally is too.
6. arXiv checked by exact title phrase for projects that looked research-backed.
7. Deliberately excluded: well-funded obvious companies, "awesome" lists, tutorial repos,
   and single-vendor releases from large incumbents (ByteDance, Microsoft, Tencent,
   Alibaba, Yandex, Google, NVIDIA appeared repeatedly and were dropped).

**Deliberately included:** several artifacts that are *not* leads — an Anthropic engineer's
side project (DZ-034), four established companies (DZ-024, DZ-039, DZ-044, DZ-045), and
several highly-visible projects. They are landscape anchors, reproduction targets, and
negative controls. A universe containing only leads would be a universe that had already
been tuned.

---

## 2. Breakdown

### By builder pool

| Pool | Count | Share |
| --- | --- | --- |
| **A — young builder / researcher / OSS maintainer** | 8 | 18% |
| **B — experienced operator → founder** | 6 | 13% |
| **U — career stage not publicly determinable** | 31 | 69% |

`U` does **not** mean "unknown person." It means the person's career stage cannot be
established from public artifacts without an inference `data_ethics.md` forbids. Many `U`
records have fully resolved identities and excellent artifacts.

### By primary technical area

| Area cluster | Count |
| --- | --- |
| Agent execution / sandboxing / isolation | 7 |
| Agent observability / provenance / policy | 6 |
| Agent security / identity | 7 |
| Agent economics / cost / token reduction | 5 |
| Inference & model infrastructure | 9 |
| Agent memory / context | 6 |
| Evaluation | 3 |
| Data infrastructure | 2 |

### By source channel

| Channel | Count |
| --- | --- |
| GitHub only | 41 |
| GitHub + arXiv | 3 (DZ-013, DZ-027, DZ-028) |
| GitHub + mailing list + company site | 1 (DZ-001) |
| X / social | **0** |
| Hackathon | **0** |

### By evidence quality

| Grade | Count |
| --- | --- |
| HIGH | 7 |
| MEDIUM | 32 |
| LOW / requires verification | 6 |

---

## 3. Formation-state distribution

| State | Count | Examples |
| --- | --- | --- |
| BUILDING | 18 | DZ-011, DZ-018, DZ-029, DZ-034 |
| COLLABORATING | 6 | DZ-013, DZ-014, DZ-026, DZ-027, DZ-028 |
| FORMING | 9 | DZ-003, DZ-010, DZ-012, DZ-016, DZ-021 |
| LAUNCHED | 6 | DZ-001, DZ-024, DZ-035, DZ-039, DZ-044 |
| FUNDED | 0 | — |
| UNKNOWN | 6 | DZ-007, DZ-019, DZ-022, DZ-043 |

Zero FUNDED is the intended shape: the filter selected for artifacts, not for rounds.

---

## 4. What building this universe actually taught me

These are the Phase 1 findings, and three of them are inconvenient.

### Finding 1 — GitHub alone cannot classify the two pools the role describes
Only **14 of 45** builders (31%) could be assigned to Pool A or Pool B from public
evidence. GitHub tells you what someone built. It does not tell you whether they are a
second-year PhD student or a fifteen-year staff engineer, and inferring it from account
age, writing style, or repository topic is exactly the guessing this project forbids.

**Consequence:** the two-pool taxonomy in Array's job description is not derivable from
the highest-value programmatic channel. It requires either a self-declared statement
(the X channel), an academic affiliation (the papers channel), or a human (the SF
ecosystem module). This is the strongest argument I found for keeping X in the design —
and it is an argument about *identity*, not about discovery.

### Finding 2 — attention and construction are close to uncorrelated
Verified pairs from this universe:

| Project | Stars | Owner commits | Active days |
| --- | --- | --- | --- |
| `0xSero/turboquant` | 1,735 | **2** | 2 |
| `zerobootdev/zeroboot` | 2,434 | **24** | 6 |
| `vivekchand/clawmetry` | **399** | 3,111 | 190+ |
| `FootprintAI/Containarium` | **273** | 987 | 230+ |
| `brontoguana/krasis` | **513** | 768 | 190+ |

Any system that ranks by stars gets this exactly backwards. The three lowest-star projects
in that table represent roughly 4,800 commits of sustained human work; the two highest-star
projects represent 26.

### Finding 3 — the best formation signals are boring metadata
The single most informative field in the entire sweep was **GitHub organization
`created_at`**. It is free, precisely dated, unforgeable, and it is a *decision* — someone
chose to create an entity. Personal account creation dates matter too: `congwang-mk`
created an account on **2025-08-21**, seventeen years into a Linux kernel career, three
weeks before submitting the multikernel patch series to LKML.

Nobody is going to out-source anyone with sentiment analysis of launch tweets. They might
with `orgs/{login}.created_at`.

### Finding 4 — the highest-depth areas have the lowest formation rates
Inference and model infrastructure produced the most technically impressive artifacts
(DZ-026, DZ-027, DZ-028, DZ-031) and almost no formation signals — they are academic
groups doing academic work (NC-7). Agent economics produced the *least* impressive
artifacts by systems-depth standards and the *most* formation signals (DZ-010, DZ-011,
DZ-012). Depth and formation are not the same axis, which is precisely why
`technical_quality_framework.md` refuses to combine them into one number.

---

## 5. Analyst review — 12 selected for deeper review

Selected on evidence strength and Array relevance, **not numerically**. Ordered by
technical area, not by rank.

---

### AR-1 · DZ-001 · Cong Wang — Multikernel Technologies

**What they built.** `multikernel/kernelscript`, a type-safe DSL in OCaml for
eBPF-centric kernel customization (502 stars, 524 owner commits, Apache-2.0), alongside
the multikernel Linux design — patches submitted to LKML in September 2025 proposing
per-application dedicated kernel instances for isolation without hypervisor overhead.

**Technical artifact.** Public repo + public LKML patch series + `multikernel.io`.

**Why technically interesting.** This is a genuine L4 artifact: writing a typed DSL that
compiles to eBPF, and separately proposing a multikernel architecture upstream, are both
things that require kernel expertise that is not learnable in a quarter. The isolation
claim — near-native performance with kernel-level isolation and no hypervisor — is exactly
the primitive the entire agent-sandbox category is reaching for from above.

**What changed recently.** Org created 2025-03-08; LKML patches Sept 2025; personal
account created 2025-08-21; kernelscript last pushed 2026-06-26.

**Formation evidence.** F-01 domain, F-02 org, F-03 explicit first-person founder bio,
F-06 "Inc." — four signals, at least three independent channels. State: LAUNCHED.

**Array relevance.** Adjacent to Theme 4 and directly relevant to agent isolation. Array's
own AI coworker "runs in its own filesystem sandbox with isolated execution."

**Why normal VC sourcing misses it.** 72 GitHub followers. Two public personal repos. No
X-native presence found. The evidence lives on a mailing list and in an OCaml repository —
two surfaces no AI sourcing tool indexes.

**Strongest evidence.** Verifiable, dated, cross-channel: GitHub org, GitHub account,
LKML archive, company site, third-party technical press.
**Weakest evidence.** No public information on funding, team size, or commercial wedge.

**Technical diligence question.** Does per-application kernel isolation beat microVM
snapshot-restore on cold-spawn latency *and* memory amplification, or only on steady state?
**Commercial question.** Is the buyer a hyperscaler (cloud OS) or an agent platform
(isolation substrate)? Those are different companies.

**What would make this an intro.** Confirmation that the commercial wedge is agent/AI
workload isolation rather than generic HPC, and that a round has not already closed.
**What would make us drop it.** Evidence of an already-completed institutional round, or
that the LKML work stalled upstream without traction.

---

### AR-2 · DZ-010 · Resham Joshi — CodeBurn / AgentSeal

**What they built.** `codeburn` — local-first tracking of AI coding token usage and cost
across 37 tools and agents, by model, project, and task (9,609 stars, 1,234 commits, MIT,
`npx` distribution).

**Why technically interesting.** Not for systems depth — it is L2. It is interesting
because it is **cost attribution per unit of work**, which is the measurement layer
Shruti's July 2026 post argues is missing. The founder's stated motivation ("Built
CodeBurn because 50M tokens/week is wild") is the AWU problem discovered from the bottom up.

**Formation evidence.** F-01 two domains, F-02 org created 2026-04-18, F-03 explicit
"Founder · CodeBurn, Eywa, AgentSeal." Three signals, multiple channels. State: FORMING.

**Array relevance.** Theme 3 (AI Economics Infrastructure) and directly the
cost-per-Accepted-Work-Unit frame.

**Why normal sourcing might miss it.** Three named projects from one person reads as
unfocused to any system scoring consistency, and the founder is in Germany rather than SF.

**Strongest evidence.** Explicit first-person founder statement plus a real distribution
channel (`npx`) plus 1,234 commits.
**Weakest evidence.** Which of three projects is the company is genuinely unclear, and
there is no public revenue or customer signal.

**Technical question.** Does per-task cost attribution across 37 heterogeneous tools
produce *comparable* units, or 37 incomparable ones? Comparability is the whole product.
**Commercial question.** Who pays — the engineer (observability, low willingness to pay)
or the finance function (spend control, high)?

**What would make this an intro.** Evidence of convergence onto one project and any
enterprise-side pull. **What would make us drop it.** Continued three-way splitting, or
the measurement collapsing into a feature of the coding tools themselves.

---

### AR-3 · DZ-012 · Vivek Chand — ClawMetry

**What they built.** Zero-config observability and governance across 20+ agent runtimes —
live token costs, sessions, tool calls, crons. **3,111 owner commits** against 399 stars.

**Why technically interesting.** Instrumenting 20+ heterogeneous agent runtimes without
configuration is a genuine integration-engineering problem, and the *governance* framing
(not just observability) puts it on the control-layer side of Theme 2.

**Formation evidence.** F-01 `clawmetry.com`; F-03 self-published "Building ClawMetry."
Two signals. **His employment at Booking.com is context only and is explicitly not read as
a departure signal.**

**Why normal sourcing misses it.** 95 followers, 399 stars, Amsterdam. The
commits-to-stars ratio (7.8:1) is one of the highest in the universe and is invisible to
every popularity-ranked system.

**Strongest evidence.** Sustained construction at extreme volume with a public first-person
statement of intent.
**Weakest evidence.** No org, no company entity, no team.

**Technical question.** Does zero-config instrumentation stay correct across 20+ runtimes,
or degrade to lowest-common-denominator metrics that miss what matters per runtime?
**Commercial question.** Is agent governance a buying center yet, or a 2027 category?

---

### AR-4 · DZ-011 · `mikehasa` — agentacct

**What they built.** Per-task agent work-step accounting: tools used, files changed, tests
run, time and tokens spent. Local-first, no login, no telemetry. Created 2026-07-24 — six
weeks old at audit.

**Why technically interesting.** It is the closest artifact in the entire universe to
Array's own published Accepted Work Unit concept, built independently and apparently
without knowledge of it. Someone converged on "measure agent work in units of work" from
first principles.

**Formation evidence.** **None.** State: BUILDING.
**Identity confidence: LOW** — no name, no company, no blog, 9 followers, one public repo.

**Why this is in the review anyway.** It is the single best illustration of what DAY ZERO
is supposed to find and of why the identity rule matters. The artifact is exactly on
thesis. The person cannot be introduced, because ER-3 says you cannot introduce someone
you cannot name. The correct action is a watchlist entry and a `pushed_at` monitor — not a
lead, and not an attempt to identify them.

**Technical question.** Can "work steps" be defined consistently enough across agents to
be an accounting unit rather than a prettier log view?
**Commercial question.** N/A until identity resolves.

---

### AR-5 · DZ-013 · Yusheng Zheng — AgentSight (eunomia-bpf)

**What they built.** eBPF-based system-level observability for AI agents, in C, with a
peer-reviewable paper: **arXiv:2508.02736**, *AgentSight: System-Level Observability for
AI Agents Using eBPF* (2025-08-02).

**Why technically interesting.** Array's security post argues that agents "move data
through syscalls" and that endpoint, DLP and SaaS tooling all miss it. AgentSight is the
only artifact in this universe that instruments at exactly that layer *and* has a paper
behind it. Cross-source convergence is real here: paper authorship overlaps repo
contributors (C-03).

**Formation evidence.** None. `eunomia-bpf` is an established open-source eBPF community
(org created 2022-08-20, 151 repos, 755 followers). State: COLLABORATING.

**Why normal sourcing misses it.** 599 stars. It is a research artifact in an established
community, in C, about kernel instrumentation.

**Technical question.** What is the measured overhead of eBPF-based agent tracing under a
realistic multi-agent workload — and does it stay under the threshold where teams turn it off?
**Commercial question.** Is system-level agent observability a product, or a feature that
Datadog and CrowdStrike ship within four quarters?

**What would make this an intro.** Any formation signal — a new org, a domain, a statement.
Today there is none, and manufacturing one would be inventing evidence.

---

### AR-6 · DZ-014 · Derek Chong + Stanford NLP collaborators — Shepherd

**What they built.** A runtime substrate that turns agent execution into a reversible,
Git-like trace so meta-agents can observe, fork, replay, and revert any run. Two
precisely-stated claims: copy-on-write fork **~5× faster than `docker commit`**, and
**~95% KV-cache reuse on replay.**

**Why technically interesting.** These two claims together are the mechanism that would
make agent replay economically viable — which is the missing piece of the LoopOps stack
Shruti describes (state ledgers, completion gates, escalation queues). Reversibility is
also the honest answer to the goal-drift failure mode: if you can revert, drift is
recoverable rather than terminal.

**Formation evidence.** F-01 `shepherd-agents.ai`, F-02 org created 2026-06-24 — but the
org, domain and repo all appeared the same day, which is arguably **one** announcement
rather than two independent channels. Classified COLLABORATING, FORMING PARTIAL.

**Why normal sourcing misses it.** Two months old, 100 commits, and it comes from an NLP
group. Investors index Stanford NLP for models, not for execution substrates.

**Technical question.** Does ~95% KV-cache reuse hold when the forked branch diverges
*early* in the trace, or only for late-branch replay?
**Commercial question.** Is the buyer an agent platform (infrastructure sale) or an
enterprise agent team (tooling sale)?

**What would make us drop it.** If it stays a research project — which for a Stanford NLP
artifact is the most likely outcome and not a criticism.

---

### AR-7 · DZ-016 · Parth Shah — Linnix

**What they built.** eBPF-powered Linux observability with AI incident detection, in Rust,
AGPL-3.0. Org `linnix-os` created **2025-08-06**, three months *before* the repo.

**Why technically interesting.** eBPF + Rust + incident detection is a real systems stack,
and the AGPL choice plus an org created before the code is a deliberate commercial posture
rather than an afterthought.

**Formation evidence.** F-02 org (pre-dating the artifact), F-03 self-published "Currently:
Linnix." Two signals. State: FORMING.

**Why normal sourcing misses it.** **10 followers.** Three public repos. Four org
followers. There is no ranking system on earth that surfaces this person today.

**Technical question.** Does AI incident detection over eBPF telemetry beat well-tuned
threshold alerting, or add inference latency without precision gains?
**Commercial question.** Observability is the most crowded infrastructure market there is.
What is the wedge that is not "cheaper Datadog"?

---

### AR-8 · DZ-020 · `Karib0u` — Rustinel

**What they built.** A cross-platform EDR in Rust spanning **ETW (Windows), ESF (macOS),
and eBPF (Linux)**, with Sigma rules, YARA, IOCs and ECS NDJSON output. 141 owner commits,
Apache-2.0, docs site.

**Why technically interesting.** Writing an EDR that spans three OS telemetry subsystems
is a serious capability signal — most commercial EDRs are built by teams over years. It is
also directly in Array's named cybersecurity area.

**Formation evidence.** F-01 `docs.rustinel.io` only. **One channel. Not FORMING.**

**Why normal sourcing misses it.** Pseudonymous, French, 72 followers, and the artifact
requires domain literacy to evaluate.

**Technical question.** How does a solo-maintained EDR handle detection-rule maintenance,
which is where commercial EDR cost actually lives?
**Formation question.** No org, no company, no statement. This is a relationship to build,
not a lead to act on.

---

### AR-9 · DZ-021 · Dhia Ayachi — kloak

**What they built.** `kloak`, cloud-native zero-trust security for AI agent run
environments, in C, AGPL-3.0, under the `spinningfactory` org (created 2024-01-08).

**Why technically interesting.** Array explicitly says it is seeking "agent identity and
authority management systems." kloak is one of only three artifacts in the universe
aimed at that, and the only one whose contributor is an identified individual with a
distributed-systems background rather than an anonymous org.

**Formation evidence.** F-01 `getkloak.io`, F-02 org. Two signals. His employment at
Polygon.io is context only.

**Why normal sourcing misses it.** 4 org followers, 25 personal followers, 261 stars.

**Technical question.** What does zero-trust mean concretely at the agent-runtime layer —
mTLS between agents, or per-syscall authorization? These are different products with
different moats.
**Commercial question.** Sapiom already occupies the budget-and-permission layer in Array's
portfolio. What is kloak's non-overlapping surface?

---

### AR-10 · DZ-008 · Tejas Chopra — Headroom Labs

**What they built.** `headroom` — compress tool outputs, logs, files and RAG chunks before
they reach the LLM. Library + proxy + MCP server. 1,164 top-contributor commits, docs site,
Apache-2.0.

**Why in this review.** Not because it is non-obvious — 67,223 stars is the opposite of
non-obvious. It is here because it carries **the most falsifiable claim in the universe**
("20% fewer tokens for coding agents, 60–95% fewer for JSON, **same answers**") and is
therefore the recommended primary reproduction experiment (EXP-1).

**Formation evidence.** F-01 domain + docs, F-02 org "Headroom Labs" created 2026-06-16.
Two signals. **The GitHub company field reads "Netflix, Inc." — this is recorded as
possibly stale and is explicitly NOT read as a transition signal.**

**Technical question.** Does the 60–95% JSON figure survive a plain whitespace-minification
baseline, and does "same answers" hold on questions that require the *dropped* content?
**Commercial question.** Is context compression a product, or a feature every agent
framework ships by default within two quarters?

---

### AR-11 · DZ-003 · BoxLite

**What they built.** An embeddable Rust micro-VM for agents — "light enough to embed on
your laptop, elastic enough to power an agentic cloud." Created 2025-12-07, 570
top-contributor commits, 34 pages of contributors.

**Why technically interesting.** It has the longest sustained construction history of any
microVM-for-agents project found, and a materially lower star count than the abandoned
`zeroboot` (2,273 vs 2,434) — a direct illustration of Finding 2.

**Formation evidence.** F-01 `boxlite.ai`, F-02 org created 2025-11-17, org self-describes
as "The AI agent infrastructure company." Two-to-three signals. State: FORMING.

**Weakest evidence.** No public org members, no identified founding team. Identity
confidence MEDIUM, which is currently disqualifying for a Weekly 3 slot.

**Technical question.** How does an embeddable micro-VM handle memory amplification at
100+ concurrent agents on one host?
**Commercial question.** Does this sell to agent platforms, or is it displaced by whatever
the model providers ship natively?

---

### AR-12 · DZ-034 · Ryan Codrai — turbovec *(reviewed as a negative control)*

**What they built.** A Rust vector index on TurboQuant with Python bindings, 16,239 stars,
351 owner commits, published on PyPI.

**Why it is in the analyst review.** Because it is the mistake I would most plausibly make.
The reasoning chain *"frontier-lab engineer + serious independent side project + Array
wants operators leaving labs to build = lead"* is seductive and entirely invented. There is
no formation evidence. There is no statement. Reading intent from an employer field is the
precise behavior `formation_framework.md` §6.2 and `data_ethics.md` §2 prohibit.

**Verdict: BUILDING. Not a lead. Recorded so the reasoning is visible and auditable.**

---

## 6. Provisional Weekly 3

**Nobody has been contacted. This is a research output only.**

Applying `weekly3_framework.md` §4 disqualifiers to the twelve reviewed candidates:

- AR-4 (`mikehasa`), AR-8 (`Karib0u`) — identity confidence LOW → disqualified
- AR-5 (AgentSight), AR-12 (turbovec) — zero formation evidence → disqualified
- AR-10 (Headroom), AR-11 (BoxLite) — AR-10 is not non-obvious; AR-11 has no identified
  founder → disqualified
- AR-6 (Shepherd) — formation signals collapse to one channel; FORMING PARTIAL → held
- AR-3 (ClawMetry), AR-7 (Linnix), AR-9 (kloak) — survive
- AR-1 (Multikernel), AR-2 (CodeBurn) — survive

**Five survive. Three are selected. The full write-ups — including why each was chosen over
the other two — are in `../research/phase1_report.md` §25–27.**

| # | Lead | State | Why now |
| --- | --- | --- | --- |
| **W1** | **Cong Wang — Multikernel Technologies** | LAUNCHED | Deepest verifiable technical moat in the universe; formation evidence across four independent channels; essentially invisible to attention-ranked sourcing |
| **W2** | **Vivek Chand — ClawMetry** | FORMING | Extreme construction-to-attention ratio (3,111 commits / 399 stars); explicit first-person build statement; directly on Themes 2 and 3 |
| **W3** | **Resham Joshi — CodeBurn / AgentSeal** | FORMING | Only builder in the universe who independently converged on cost-per-unit-of-work measurement, which is Array's own published metric |

**Not selected, and why:** Parth Shah / Linnix (AR-7) — genuinely compelling and the most
invisible builder found, but observability is the most crowded infrastructure market and
I could not answer the "why not cheaper Datadog" question from public evidence.
Dhia Ayachi / kloak (AR-9) — strong area fit, but Sapiom already occupies the adjacent
surface in Array's portfolio and the differentiation question is unresolved.

Both remain on the watchlist. Neither was dropped for lack of quality.
