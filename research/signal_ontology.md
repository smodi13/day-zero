# DAY ZERO — Signal Ontology

**Version:** 1.0 — **FROZEN 2026-08-22 before any backtest evaluation.**
Any change after the first holdout run must be recorded as a new version with a dated
changelog entry and the backtest re-run from scratch. See `backtest_methodology.md` §5.

---

## 0. Design rules that govern every signal below

1. **A signal is an observation with a source, a timestamp, and a channel.** It is never
   a score.
2. **Signals do not sum.** There is no total. Analyst review reads the signal set.
3. **Every signal carries `evidence_status ∈ {OBSERVED, INFERRED, UNKNOWN}`.**
4. **Every signal carries `observed_at` (when it happened) and `collected_at` (when we
   saw it).** Backtests filter on `observed_at`; freshness uses `collected_at`.
5. **Volume is not quality.** No signal is defined as "count > N" without a
   corresponding depth test.
6. **Popularity is not a signal.** Follower count, stars, likes, and retweets are
   recorded as *context fields* and are explicitly barred from surfacing logic. Stars
   may be used only in one direction: as a *risk flag* when stars are high and
   construction depth is low (see NEG-1 in `negative_controls.md`).
7. **Prestige is not a signal.** Affiliation is a context field used for identity
   resolution and conflict-of-interest checks, never for ranking.

---

## 1. BUILD signals — "something was constructed"

| ID | Signal | Primary channel | What must be OBSERVED | Anti-pattern it must not fire on |
| --- | --- | --- | --- | --- |
| B-01 | Repository created | GitHub | repo `created_at`, owner, license | Forked/renamed repo of someone else's work |
| B-02 | First public release | GitHub releases, PyPI/crates.io/npm | tagged release with artifacts | A tag with no build |
| B-03 | Sustained construction | GitHub commits | commits by ≥1 identified human across ≥8 distinct weeks | Bot commits, `github-actions[bot]`, dependabot |
| B-04 | New technical package published | package registries | package exists, is installable, has a version history | Name-squatting, placeholder packages |
| B-05 | Benchmark published | repo/paper/site | a runnable benchmark *and* the numbers | A claim in a README with no harness |
| B-06 | Working demo | video, hosted demo, docs | reproducible or at least inspectable | A screenshot |
| B-07 | Public API / service launched | docs site, OpenAPI spec | endpoint documentation | A waitlist page |
| B-08 | Paper implementation shipped | repo ↔ paper link | repo implements a specific named paper | "Inspired by" with no correspondence |
| B-09 | Infrastructure-layer project | repo | operates below the application layer (runtime, kernel, scheduler, storage, protocol, compiler) | Application calling an infrastructure API |

**Instrumented example (verified 2026-08-22):** `Eventual-Inc/Daft` — B-01
(2022-04-25), B-03 (multi-contributor commits observed through 2022), B-09 (Rust
distributed query engine). All three fired more than two years before the Array-backed
seed round on 2024-10-01.

---

## 2. TECHNICAL DEPTH signals — "the thing is actually hard"

Depth is judged from the artifact, not from the description. Each signal requires the
analyst (or a deterministic check) to have looked at code, a paper, or a benchmark.

| ID | Signal | What qualifies | What does not |
| --- | --- | --- | --- |
| D-01 | Non-trivial systems work | kernel/eBPF/hypervisor/microVM/scheduler/allocator code authored by the builder | Docker-compose orchestration of others' systems |
| D-02 | Original architecture | a design that does not exist upstream, with a stated reason it must be different | A wrapper with a new CLI |
| D-03 | Performance engineering | measured optimization with a baseline and a method | "blazing fast" in a README |
| D-04 | Distributed systems | consensus, partitioning, failure handling, or cross-node coordination implemented | A client library for a distributed service |
| D-05 | Security research | a novel attack/defense, a CVE, or a kernel-level enforcement mechanism | A rules file for an existing scanner |
| D-06 | Compiler / database / runtime work | parser, IR, query planner, execution engine, or language runtime | An ORM |
| D-07 | Model infrastructure | serving, batching, KV-cache management, quantization kernels, speculative decoding | A prompt template library |
| D-08 | Evaluation systems | a harness with task definitions, verification, and reproducibility | A leaderboard screenshot |
| D-09 | Novel data infrastructure | a storage/query/processing substrate | A dashboard on top of a warehouse |
| D-10 | Deep domain implementation | encodes hard, real domain rules (HIPAA determination, clearing, freight tariffs, medical coding) | A domain-flavored chat UI |

**Explicit anti-rule:** a project that wraps an existing API is classified as
**integration**, not infrastructure, regardless of star count. `context-mode`,
`headroom`, and `rtk` are all *plausibly* deep (token-accounting and transformation
layers) and all *plausibly* thin (proxies over other people's protocols). Each is marked
`D-XX: INFERRED — requires reproduction` rather than asserted. That is what the
reproduction lab exists to resolve.

---

## 3. COLLABORATION signals — "this is becoming a team"

| ID | Signal | What must be OBSERVED |
| --- | --- | --- |
| C-01 | New co-maintainer | a second identified human with commit access and substantial commits |
| C-02 | Repeated collaborator | the same two identities appearing across ≥2 distinct artifacts |
| C-03 | Co-author → co-committer | a paper co-author appears as a repo contributor (or vice versa) |
| C-04 | New GitHub organization | org `created_at`, with the builder as a member/owner |
| C-05 | Complementary skills | contributor set spans distinct technical layers (e.g. kernel + control plane + frontend) |

**Instrumented examples (verified 2026-08-22):**
- C-03: `WeianMao/triattention` — repo contributors overlap with the author list of
  arXiv:2604.04921 (*TriAttention: Efficient Long Reasoning with Trigonometric KV
  Compression*, 2026-04-06).
- C-04: `multikernel` org created 2025-03-08; `congwang-mk` GitHub account created
  2025-08-21 — a new org *and* a new personal account for an operator with a 17-year
  kernel history.
- C-02: `shepherd-agents/shepherd` contributors `dcx` (Derek Chong, Stanford NLP) and
  `wyshi` (Northeastern University) — an academic pair appearing on one commercial-shaped
  artifact.

---

## 4. FORMATION signals — "a company may be forming"

Formation signals are the ones most likely to be over-read. Each requires an explicit
public statement or a registrable fact. **Nothing here may be inferred from silence,
inactivity, deleted posts, or a profile edit.**

| ID | Signal | Required evidence | Forbidden inference |
| --- | --- | --- | --- |
| F-01 | New project name + domain | domain resolves, project site exists, linked from the artifact | Domain purchase alone |
| F-02 | New GitHub organization | org created; builder is a public member | An org someone was added to |
| F-03 | Explicit founder statement | the person says, publicly and in the first person, that they are founding/building a company | A bio containing the word "founder" |
| F-04 | Recruiting collaborators | a public post or repo/site page seeking a cofounder or founding engineer | Any generic job board listing |
| F-05 | Accelerator participation | an official cohort page listing the person/company | A logo on a personal site |
| F-06 | Incorporation evidence | a public registration, an official "Inc."/"Ltd." in the org profile, or a state filing | Guessing from a `.ai` domain |
| F-07 | Public launch | a dated launch post from the builder plus a live product surface | A landing page with a waitlist |
| F-08 | Form D / financing filing | SEC EDGAR filing | — (this is confirmation, not discovery) |

**Instrumented example (verified 2026-08-22):** Cong Wang / Multikernel Technologies —
F-01 (`multikernel.io`), F-02 (org created 2025-03-08), F-03 (GitHub bio: "Founder and
CEO at @multikernel"), F-06 (org name "Multikernel Technologies, Inc."), plus LKML patch
submission in Sept 2025. Four independent formation signals, none of them inferred.

**Counter-example the ontology must reject:** `RyanCodrai/turbovec` — a serious Rust
vector index with 351 owner commits and Python bindings, built by someone whose GitHub
bio reads "Member of Technical Staff at Anthropic." Strong BUILD and DEPTH signals,
**zero FORMATION signals.** DAY ZERO must classify this as BUILDING and stop. Reading
employment-at-a-lab as pre-departure intent is exactly the invasive inference the
mandate forbids.

---

## 5. VELOCITY signals — "the activity is changing"

Velocity is measured as *change*, never as *level*.

| ID | Signal | Definition | Guard |
| --- | --- | --- | --- |
| V-01 | Activity acceleration | commit-weeks in the last 90 days vs. the prior 90 days, for identified humans only | Ignore bot commits and vendored-dependency bulk commits |
| V-02 | Release cadence change | interval between tagged releases shortening | A single release is not a cadence |
| V-03 | External contributor growth | new contributors who are not the owner and not bots | Drive-by typo PRs excluded |
| V-04 | Issue engagement | real issues opened by non-owners and resolved | Issue count alone (`rtk` has 1,998 open issues — that is a *load* signal, not a quality signal) |
| V-05 | Scope expansion | new subsystems/modules appearing, or the README's claim surface widening | Refactors |
| V-06 | **Abandonment** (negative velocity) | `pushed_at` older than 90 days on a project that had <120 days of activity | — |

**V-06 is a first-class signal, not an absence.** Three verified examples:
`zerobootdev/zeroboot` (2,434 stars; 24 commits; active 2026-03-15 → 2026-03-21),
`dipampaul17/KVSplit` (362 stars; 9 commits; active 2025-05-16 → 2025-05-21),
`0xSero/turboquant` (1,735 stars; **2 commits**; active 2026-03-25 → 2026-03-27).
All three are high-attention, near-zero-construction artifacts.

---

## 6. COMMERCIALIZATION signals — recorded, never used for surfacing

These exist to inform the analyst and to answer "is this already obvious?" They are
**explicitly excluded from discovery logic**, because requiring them guarantees DAY ZERO
only finds companies that are already visible.

| ID | Signal | Note |
| --- | --- | --- |
| M-01 | Named users / adopters | Only if the adopter is named by a source other than the builder |
| M-02 | Integrations shipped | Observable in code |
| M-03 | Documentation maturing | A docs site with versioning and a getting-started path |
| M-04 | Productized API | Auth, rate limits, and a pricing surface |
| M-05 | Pricing page | Exists and quotes numbers |
| M-06 | Enterprise deployment / pilot | Requires a non-builder source |
| M-07 | Customer reference | Requires a non-builder source |

---

## 7. SOCIAL / X signals — discovery only

| ID | Signal | What it establishes | What it does NOT establish |
| --- | --- | --- | --- |
| S-01 | Project launch post | that the person made this statement, at this time | that the project works |
| S-02 | Build-in-public update | continuity of attention | progress |
| S-03 | Explicit founder-transition statement | that the statement was made | that the departure occurred |
| S-04 | Benchmark discussion | that a claim was made publicly | the benchmark result |
| S-05 | Recruiting post | intent to add people | that a team exists |
| S-06 | New technical collaboration | that two people are publicly associated | a working relationship |
| S-07 | Hackathon result | a pointer to an official result page | that the project continued |
| S-08 | Demo video | that a demo was shown | that it generalizes |

**Governing rule:** every S-xx signal must be paired with a non-X confirmation of the
*fact*, not merely of the *statement*, before it can contribute to a Weekly 3 record.

---

## 8. Cross-source convergence (the signal that matters most)

Convergence is not a signal type — it is a *property of a signal set*. It is defined as:

> **≥2 signals from ≥2 independent channels, about the same resolved entity, within a
> 180-day window, where at least one is a BUILD or DEPTH signal and at least one is a
> COLLABORATION or FORMATION signal.**

"Independent channel" means the sources do not derive from each other. A tweet linking
to a repo is **one** channel, not two — the tweet is a pointer. A paper on arXiv and a
repo with overlapping authorship are **two**.

Convergent sets are ranked above high activity on any single platform. See
`cross_source_signals.md` for the strongest instances found in the initial universe.

---

## 9. Signals DAY ZERO deliberately does NOT define

Recorded so the omissions are visible and auditable:

- **Founding probability.** No signal estimates whether someone will start a company.
- **Departure inference.** No signal derives employment change from anything except an
  explicit public statement by the person.
- **Founder quality.** No signal scores a human being.
- **Team fit / personality.** Not observable from public artifacts, and not our business.
- **Location tracking.** Beyond a self-published professional location field and
  voluntarily public event participation.
- **Follower/star thresholds as inclusion criteria.** Barred in §0.6.
