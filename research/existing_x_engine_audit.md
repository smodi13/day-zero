# Existing X Sourcing Engine — Audit

**Audit date:** 2026-08-22
**Auditor:** Sahil Modi (with Claude Code assistance)
**Status of the audited repository:** READ-ONLY. Nothing in it was modified, committed, or executed.

---

## 0. Locating the engine

A conservative search of `~/` and `~/Projects/` surfaced five directories whose names
suggested X/Twitter sourcing:

| Directory | What it actually is |
| --- | --- |
| `~/headline-x-sourcing` | **The canonical engine.** Python package `src/sourcing/`, 46 modules, ~12,450 LOC, 35 test files, 16 YAML config files, real run outputs in `data/output/`. A Next.js frontend was later layered on top and re-skinned for a *different* application (Matchstick), which is why the top-level `README.md` no longer describes the engine. |
| `~/ldv-x-sourcing-engine` | A fork/re-skin of the same Next.js showcase for LDV Capital. Shares commit `2ad3643` with `headline-x-sourcing`. No independent engine code. |
| `~/x-sourcing-engine-showcase` | **Sanitized public excerpt** of the engine (`src/engine/`, ~10 modules), plus `docs/` (architecture, methodology, evidence-framework, limitations, cost-controls, metrics-reconciliation) and `demo/sanitized-sample-outputs/`. 95 tests. MIT licensed. This is the best-documented artifact. |
| `~/x-sourcing-engine-showcase-private` | Three text files: demo script, screen-share guide, and a public-showcase handoff document. No code. |
| `~/ldv-thesis-engine` | Unrelated Next.js thesis site. No X code. |

**Canonical source of truth for this audit:** `~/headline-x-sourcing/src/sourcing/`
(private engine) cross-read against `~/x-sourcing-engine-showcase/docs/` (public
documentation of the same design).

Package metadata (`pyproject.toml`): `name = "headline-x-sourcing"`, console script
`headline-sourcing = "sourcing.cli:main"`, Python ≥3.11, deps `requests, pydantic,
pandas, PyYAML, python-dotenv`, optional `anthropic`, dev `pytest`.

---

## 1. What the engine already does

### Pipeline (deterministic Python end-to-end)

```
sourcing thesis (YAML)
  → query construction (3 topic groups × 3 discovery lanes, curated not combinatorial)
  → query validator (runs BEFORE any network call)
  → count preflight  (GET /2/tweets/counts/recent)
  → human approval gate (SHA-256 request fingerprint, 15-minute TTL)
  → recent search    (GET /2/tweets/search/recent)
  → SQLite response cache (no resource refetched within a run)
  → URL resolution + canonicalization (no external HEAD/GET)
  → deterministic extraction & evidence tagging (Level A/B/C/D)
  → builder attribution / ownership (who is speaking?)
  → dedup (within-run + cross-run) → project consolidation
  → deterministic scoring (100 pts, 7 components) + penalties
  → platform-absorption risk overlay + replication-difficulty test (both non-scoring)
  → classification into 6 mutually exclusive dispositions
  → selective profile enrichment (GET /2/users, shortlist only)
  → diligence queue / report
  → human investment decision
```

### Module inventory (private engine, `src/sourcing/`)

| Module | LOC | Responsibility |
| --- | --- | --- |
| `cli.py` | 989 | Command surface for every phase |
| `x_client.py` | 516 | X API v2 client: recent search, `/2/users` batch (≤100), timelines for shortlist only, explicit pagination, cache-through |
| `validator.py` | 144 | Operator allowlist; rejects `min_faves:`/`min_replies:`/`min_retweets:`; enforces conjunction-required operators; 512-char warning; prints exact query before execution |
| `filters.py` | 380 | Rule-based extraction (no LLM): signals, artifacts, claims, categories; evidence level assigned **at extraction time** from source type |
| `ownership.py` | 396 | Six independent dimensions: artifact evidence level, announcement attribution, actor↔project relation, project identity, artifact owner scope, lead disposition |
| `evidence.py` | 86 | Time decay applied **only** to time-sensitive signals; enduring facts never decay |
| `scoring.py` | 261 | 100-point deterministic score from `config/scoring.yaml`; explicitly excludes follower count, virality, investor followers, writing style |
| `platform_risk.py` | 130 | Platform-absorption risk + visible-feature replication test; both kept out of the numeric score |
| `classify.py` | 107 | 6 buckets: contact_now, investigate_moat, stealth_founder_lead, likely_feature, watchlist, archive |
| `registry.py` | 103 | Config-driven org registry; exact/dot-boundary domain match, exact GitHub-owner match, **substring matching forbidden** |
| `urlutil.py` | 114 | `unwound_url > expanded_url > url`; strips tracking params; `x.com`/`twitter.com`/`t.co` never treated as a product domain; unresolved shorteners never invent a project |
| `approval.py` | 494 | Canonical request → SHA-256 fingerprint; changing fields/expansions/page size/config version invalidates approval; decisions persisted atomically |
| `ledger.py` | 213 | Append-only JSONL cost audit; current-run and project-to-date ledgers |
| `money.py` | 62 | Exact `Decimal` currency; rejects floats, NaN, negatives, placeholder strings |
| `ratelimit.py` | 190 | Header-aware bounded retry from `x-rate-limit-reset`; at most one retry; re-checks approval + budget before retrying |
| `timeutil.py` | 76 | Aware-UTC only; naive datetimes rejected at boundaries; monotonic `Stopwatch` for durations |
| `cache.py` | 144 | SQLite cache: posts, users, timelines, generic http_cache |
| `governance.py` | 130 | Separate append-only governance audit (renames, approval invalidations, migrations) |
| `engagement.py` | 153 | Engagement computed locally from `public_metrics`; explicitly **non-scoring**, tie-breaker only |
| `llm.py` | 123 | Optional Claude summarization; **never** assigns a number; requires `--llm` + key; degrades gracefully |
| `enrichment*.py`, `pilot*.py`, `broad_market*.py`, `preflight.py`, `pipeline.py`, `report.py`, `aggregate.py`, `models.py`, `runstate.py`, `config.py`, `pricing.py`, `analysis.py` | ~7,600 | Phase runners, Pydantic models, reporting |

### Real-run results already produced (from the showcase README)

- Pilot: 6 query families / 3 lanes → 177 returned Post resources, 176 unique Posts,
  146 unique authors, 30 direct-builder claims, 20 Level-A artifact Posts, 29 retained
  leads, 11 profiles enriched, ≈ USD 1.085 estimated.
- Broad run: 20 query families → 1,486 aggregate 7-day count, 1,279 returned Post
  resources, 1,166 net-new Posts, 967 unique authors, 190 direct-builder claims, 851
  Posts with external artifact links, 737 strict Level A, 187 actionable Posts, 159
  consolidated projects, 153 after analyst adjudication, 14 profiles enriched.
  ≈ USD 7.720 of USD 25.000 allowance.
- Tests: 450 passing in the private engine; 95 in the sanitized showcase.

---

## 2. What is reusable

Ranked by how directly it transfers to DAY ZERO.

### Tier 1 — reuse the design and port the code nearly as-is

1. **`money.py` + `ledger.py` + `pricing.yaml`** — exact-Decimal cost accounting with an
   append-only audit trail. DAY ZERO will spend real money on X and possibly on LLM
   extraction; this is solved and correct.
2. **`approval.py`** — fingerprint-gated human approval with TTL. This is the exact
   mechanism DAY ZERO needs so that no paid or outbound-shaped action executes without
   an explicit, non-stale human decision.
3. **`timeutil.py`** — aware-UTC-only discipline and monotonic durations. This is a
   *precondition* for an honest backtest: look-ahead bias is fundamentally a timestamp
   bug, and this module already refuses naive datetimes at every boundary.
4. **`urlutil.py`** — canonical URL selection, tracking-param stripping, `t.co`
   never inventing an entity, GitHub `owner/repo` extraction. Directly reusable as
   DAY ZERO's artifact-URL normalizer.
5. **`registry.py`** — exact/dot-boundary matching with substring matching explicitly
   forbidden. DAY ZERO's entity resolution needs precisely this conservatism.
6. **`validator.py`** — X operator allowlist. Still correct and still necessary.
7. **`ratelimit.py`** — header-aware bounded retry with approval/budget re-check.
8. **`cache.py`** — response cache keyed by request signature.
9. **`governance.py`** — audit trail separate from cost.

### Tier 2 — reuse the *concept*, rewrite the implementation

10. **Evidence levels A/B/C/D assigned at extraction time from source type.** This is the
    single best idea in the engine and it becomes DAY ZERO's `source_quality` tiering.
11. **Time decay applied only to time-sensitive signals; enduring facts never decay.**
    Directly becomes DAY ZERO's velocity/formation recency handling.
12. **Ownership as six *independent* dimensions rather than one label.** DAY ZERO needs
    exactly this: "who is speaking", "what is their relation to the artifact", and "how
    good is the artifact" must never collapse into one number.
13. **Engagement as a non-scoring tie-breaker.** Keep the discipline; DAY ZERO should go
    further and drop engagement from surfacing entirely.
14. **Deterministic-first, LLM-never-scores.** Preserve verbatim.
15. **Dedup + project consolidation, with "a Post is not a project, and a project is not
    an incorporated startup"** stated explicitly in the output.

### Tier 3 — reuse the operating discipline, not the code

16. Count-preflight before retrieval, so volume is known before spend.
17. Fail-closed defaults everywhere (missing config → stop, not guess).
18. Raw responses stored before any derived output.
19. Explicit written limitations page shipped alongside results.
20. Metrics reconciliation document explaining why stage counts are not nested subsets.

---

## 3. What should NOT be reused

1. **The 100-point Primary Sourcing Score (`scoring.py` + `scoring.yaml`).**
   It was built to rank *companies* for a fund evaluating early traction. DAY ZERO
   evaluates *people and artifacts before a company exists*. Collapsing "technical
   difficulty", "formation evidence" and "commercial pull" into one number is exactly
   the failure mode DAY ZERO is designed to avoid. Keep the components as *separate,
   uncombined dimensions*; discard the total.

2. **`customer_pull` (15 pts) and `workflow_depth` (15 pts) as surfacing inputs.**
   At Day 0 there are no customers. Requiring them guarantees the engine only finds
   companies that are already visible — the opposite of the mandate. Retain them as
   *later-stage diligence fields*, not as sourcing criteria.

3. **`shipping_momentum` scored from raw signal counts.** Commit/release counting is a
   volume proxy. DAY ZERO explicitly rejects raw activity as a quality signal.

4. **`platform_risk.py`'s crowded-category heuristic.** It encodes 2025-era category
   assumptions in config and will silently rot. DAY ZERO should ask the defensibility
   question per artifact, not per category label.

5. **The X-only entity model.** In this engine, a "Company" is assembled from Posts. In
   DAY ZERO the primary entity is a **Person ↔ Artifact** pair, and X is one of eight
   channels. The `models.py` `Company` aggregate should not be carried over.

6. **The seven-day recent-search assumption baked into the pipeline.** DAY ZERO's
   backtest requires historical windows; a 7-day-only design cannot support it. This has
   to be an explicit configuration boundary, not an implicit assumption.

7. **The Next.js showcase frontends** (`headline-x-sourcing/app`, `ldv-x-sourcing-engine`).
   They are re-skinned demo surfaces for other funds and carry unrelated sample data.
   Phase 1 builds no frontend at all.

8. **`config/keywords.yaml`'s customer/usage banks** (`"our customers"`, `"paying
   customer"`, `"downloads"`, `"stars on github"`). These select for marketing language.
   DAY ZERO's keyword banks must select for *construction* language and then verify off-platform.

---

## 4. What would need modification for Array

| Dimension | Existing engine | Required for DAY ZERO / Array |
| --- | --- | --- |
| Primary entity | Company (assembled from Posts) | Person ↔ Artifact, with Company as a *later* state |
| Primary channel | X only | GitHub primary; X is discovery-only |
| Target stage | Early traction / "contact now" | Pre-formation: BUILDING → COLLABORATING → FORMING |
| Output unit | Diligence queue of companies | ~3 founder/team leads per cycle (Weekly 3) |
| Score | One 100-pt total | No total. Separate dimensions, each tagged OBSERVED/INFERRED/UNKNOWN |
| Evidence for "customers" | Scored heavily | Not a surfacing input at all |
| Technical depth | 3 pts inside `defensibility` | A first-class, multi-dimension framework with reproduction tests |
| Time window | 7-day recent search | Configurable; historical windows required for the backtest |
| Identity | X author id | Cross-channel identity resolution, ambiguous identities kept separate |
| Geography | Global | Global artifacts + an explicit SF in-person ecosystem module |
| Freeze discipline | Query approval | Query approval **plus** a frozen acceptance ruleset hashed before backtesting |

---

## 5. Data-quality weaknesses (of the engine as it stands)

1. **Seven-day recall ceiling.** Recent search cannot see a repo that launched five weeks
   ago. Roughly all pre-formation building activity is older than seven days.
2. **Announcement bias.** The lanes select for people who *announce*. Many of the
   strongest builders in the sample I gathered for DAY ZERO (e.g. a single-maintainer
   C++ LLM runtime with 768 commits and 10 followers) never post a launch tweet.
3. **Claim vs. truth.** The engine correctly records that a builder *said* something, but
   its Level A test is "an external artifact URL exists" — not "the artifact supports the
   claim." A repo link proves a repo, not a benchmark.
4. **Project-name normalization is string-based.** Two unrelated companies sharing a name
   will consolidate incorrectly. I hit this twice in one afternoon of DAY ZERO research:
   two distinct companies called **Agency** (an agent-observability startup vs. an Array
   portfolio company founded by Elias Torres) and two distinct companies called
   **Eventual** (the Daft data engine vs. a climate fintech). Both would merge under a
   name-normalization rule.
5. **Enrichment is shortlist-only for budget reasons**, so most identities in the funnel
   are never resolved beyond an X handle.
6. **English-only (`lang: en`).** Real systems work from China, Japan, Korea, and Europe is
   structurally invisible. My GitHub pass surfaced strong candidates from Beijing,
   Tokyo, Singapore, Milan, Lille, and Istanbul.
7. **No link between an X author and a GitHub identity** beyond a URL appearing in text.
8. **Retweet exclusion + `has:links`** biases toward promotional posts over technical
   threads.
9. **`data/cache.db` and `data/output/` hold raw third-party content** and are not
   appropriate to carry into a public repository.

---

## 6. API / cost limitations

Recorded from `config/pricing.yaml` (a **reviewer-supplied reference**, dated
`2026-07-18`, with a 30-day staleness gate — not live-verified pricing):

| Unit | Reference rate |
| --- | --- |
| Post resource read (recent search) | USD 0.005 |
| User lookup (`/2/users`) | USD 0.010 |
| `counts/recent` request | USD 0.005 |

Project allowance recorded: USD 25.000 total; USD 7.720 estimated cumulative spend
across the pilot and broad runs.

Constraints that carry into DAY ZERO:

- **Pricing must be re-verified before any DAY ZERO X call.** The reference is now
  ~5 weeks old and past its own staleness threshold; the engine is designed to fail
  closed on this, and that behavior should be preserved.
- **Cost is per *returned Post resource*, not per useful lead.** In the broad run,
  1,279 returned Post resources produced 153 analyst-adjudicated projects — roughly
  USD 6.40 of retrieval for 153 projects, or ≈ USD 0.042 per project *before* any
  human review time. This is the number DAY ZERO's Accepted Work Unit accounting has
  to beat or justify.
- **The console was never reconciled** (`cumulative_observed_console_spend_usd: null`).
  All figures above are estimates. DAY ZERO must reconcile against a console it
  actually controls, or state plainly that it cannot.
- **Rate limits** are handled but bounded: one retry, ≤120s auto-wait.
- **Whether the current X API tier still supports these endpoints at these prices is
  UNKNOWN and must be re-verified**, not assumed from a 2026-07 config file.

---

## 7. How X should fit into DAY ZERO

**Role: a discovery channel, not the system.**

X is the fastest public surface for four things DAY ZERO cares about and that GitHub
does not directly express:

1. A builder saying, in their own words, *what they are building and why*.
2. An explicit, public statement of transition ("I left X to build Y", "looking for a
   cofounder", "hiring our first founding engineer").
3. Announcement of a hackathon result or demo that has no other public index.
4. A visible new collaboration between two builders who have no shared repo yet.

X is structurally bad at everything else DAY ZERO needs — depth, durability,
verification, non-English coverage, and anything older than the search window.

**Therefore the rule is:**

> An X post is primary evidence that a person *made a statement*.
> It is never, by itself, evidence that the statement is *true*.

**And the pipeline constraint:**

```
X POST → IDENTITY RESOLUTION → TECHNICAL ARTIFACT → INDEPENDENT CONFIRMATION → ANALYST REVIEW
```

An X post alone can never create a Weekly 3 lead. Full design in `x_channel.md`.

**Recommended posture for Phase 2:** keep X ingestion **optional and off by default.**
Build the GitHub + papers + hackathon channels first, verify the ontology works without
paid data, and turn X on only when (a) pricing is re-verified, (b) a budget is approved
through the ported `approval.py` gate, and (c) there is a specific question X is the
best channel to answer — principally the FORMING and operator-transition signals that
GitHub cannot see.

---

## 8. Explicit non-actions

- No file in `~/headline-x-sourcing`, `~/x-sourcing-engine-showcase`,
  `~/x-sourcing-engine-showcase-private`, `~/ldv-x-sourcing-engine`, or
  `~/ldv-thesis-engine` was created, modified, deleted, or committed.
- No code was copied into `~/day-zero` during Phase 1. Reuse decisions above are
  recommendations for Phase 2, to be implemented as fresh code with attribution.
- No X API call was made during this audit.
