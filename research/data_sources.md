# DAY ZERO — Data Source Universe

**Verified:** 2026-08-22. Rate limits and access notes below were checked live where
marked ✅. Anything not checked is marked UNVERIFIED and must be confirmed before Phase 2.

---

## 1. Source register

| # | Source | Type | Access method | Signal value | Structured? | Historical depth | Rate limit | Cost | Key limitation | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | **GitHub REST API** | Primary artifact | `gh api` / REST, authenticated | **Highest.** BUILD, DEPTH, COLLABORATION, VELOCITY, F-02 | Yes | Full history since repo creation | ✅ **5,000 req/hr core** (authenticated); 60/hr unauthenticated | Free | No private activity; bots pollute contributor lists | **PRIMARY CHANNEL. Build first.** |
| S2 | **GitHub Search API** | Discovery | REST `search/repositories` | Discovery of new repos by topic/date | Yes | `created_at` filters work well | ✅ **30 req/min**; ✅ code search **10 req/min** | Free | Relevance ranking is opaque; 1,000-result cap per query | Primary discovery loop; paginate by date windows, not by score |
| S3 | **GitHub GraphQL** | Primary artifact | `gh api graphql` | Efficient multi-entity fetch | Yes | Same | ✅ 5,000 points/hr | Free | Point cost model differs from REST | Use for batch enrichment in Phase 2 |
| S4 | **arXiv API** | Primary research | `https://export.arxiv.org/api/query` | TQ-4 research depth; C-03 co-author↔committer | Yes (Atom) | Full archive | Courtesy ~1 req / 3s; ✅ site `robots.txt` sets `Crawl-delay: 15` for HTML | Free | Title/phrase search needs exact quoting (`ti:"X"`) or results are noise — verified the hard way this session | **PRIMARY for the research channel.** Use the API, never scrape `/abs`. |
| S5 | **OpenAlex** | Research index | REST, polite pool with email in UA | Author disambiguation, institution linkage, citation context | Yes | Deep | ~100k/day polite pool (UNVERIFIED) | Free | Author disambiguation is probabilistic — must not be used as ER-1 merge evidence | Use for *context*, never for identity merging |
| S6 | **Semantic Scholar API** | Research index | REST, key on request | Paper↔code links, influential-citation counts | Yes | Deep | Key-gated (UNVERIFIED) | Free tier | Coverage gaps in systems venues | Optional; secondary to S4 |
| S7 | **Package registries** (PyPI, crates.io, npm) | Primary artifact | Public JSON APIs | B-04 package published; TQ-7 downstream dependents | Yes | Full version history | Generous (UNVERIFIED per-registry) | Free | Download counts are trivially inflatable | Good for B-04 and dependent graphs; ignore download counts |
| S8 | **Devpost** | Hackathon | ⚠️ see below | F-05, S-07, hackathon→project continuity | Partially | Multi-year | — | Free | **`robots.txt` explicitly disallows `anthropic-ai`, `GPTBot`, `ChatGPT-User`, `CCBot`, `Google-Extended`, `BLEXBot`, `Omgilibot`** (verified 2026-08-22) | **MANUAL RESEARCH ONLY.** Do not crawl with an AI agent. See §3. |
| S9 | **Official hackathon sites** (AI Tinkerers SF, university hackathons, lab-run events) | Hackathon | Per-site; check each `robots.txt` | Same as S8 | No | Event-scoped | Per site | Free | Wildly inconsistent structure; pages disappear after the event | Manual, with results archived at collection time |
| S10 | **X / Twitter API v2** | Social discovery | Official API, paid | S-01…S-08; the only good channel for explicit founder-transition statements | Yes | ⚠️ recent search = **7 days** | Bounded; header-aware retry required | ~USD 0.005/post read, 0.010/user (reference from 2026-07-18, **now stale — must re-verify**) | 7-day window; announcement bias; English-only in practice; no identity linkage to GitHub | **Optional, off by default.** See `x_channel.md`. |
| S11 | **Accelerator cohort pages** (YC, and others) | Formation | Public pages | F-05 accelerator participation | Semi | Batch-scoped | Per site | Free | **Prestige trap** — an accelerator page is a *formation* signal, never a quality signal | Use for F-05 only; never rank by it |
| S12 | **SEC EDGAR (Form D)** | Formation confirmation | `data.sec.gov` REST, declared UA required | F-08 — confirmation of financing | Yes | Deep | ~10 req/s (UNVERIFIED) | Free | **Lagging by construction.** Confirms; never discovers | Backtest confirmation field only |
| S13 | **Company/product sites & docs** | Primary artifact | Direct fetch | F-01, F-07, M-03…M-05, TQ-8 | No | Snapshot | — | Free | Marketing language; no history without S14 | Read; do not trust claims |
| S14 | **Wayback Machine / CDX API** | Historical | `web.archive.org/cdx` | **Critical for the backtest**: what a page said *before* a cutoff | Yes | Deep | Generous (UNVERIFIED) | Free | Sparse coverage of small sites | **Essential.** Without it, look-ahead bias is unavoidable for S13. |
| S15 | **LKML / mailing-list archives** (lore.kernel.org) | Primary artifact | Public archives | Deep-systems evidence invisible on GitHub | Semi | Deep | Generous | Free | Requires domain literacy to read | High value, low volume. Verified use: Multikernel's Sept 2025 patch series. |
| S16 | **Conference programs** (OSDI, NSDI, SOSP, USENIX Sec, MLSys, NeurIPS) | Research | Public program pages | TQ-4; lab↔person linkage | No | Deep | — | Free | Annual cadence | Manual, high signal-to-noise |
| S17 | **University lab pages** | Research | Public pages | Affiliation; group membership | No | Deep | — | Free | Stale frequently | Context only. **Never a ranking input.** |
| S18 | **Technical community surfaces** (Hacker News, Lobsters, specialist Discords/forums) | Discovery | HN Algolia API is public | Discovery of artifacts with no other index | Partially | Deep (HN) | Generous | Free | Popularity-biased; heavy US/EN skew | Discovery only, Tier 3 |
| S19 | **SF ecosystem events** (meetups, demo days, research talks) | In-person | Public listings | Events that produce no online artifact at all | No | Forward-looking | — | Free/ticket | Not automatable; that is the point | Manual. See `sf_ecosystem.md`. |
| S20 | **Personal sites / blogs** | Primary | Direct fetch | ER-1 merge evidence; F-03 statements | No | Varies | — | Free | The single best source for identity resolution | Always check when a `blog` field exists |

---

## 2. Programmatic vs. manual

**Fully programmatic (build these):** S1, S2, S3, S4, S7, S12, S14, S18 (HN), S20 (fetch).
**Programmatic but paid / gated:** S10 (X), S5/S6 (research indices).
**Manual by policy or by nature:** S8 (Devpost — robots policy), S9, S11, S16, S17, S19.

The manual set is not a weakness to apologize for. Array's job posting asks the analyst
to *attend* hackathons and community events. The right design is a system that handles
the programmatic channels completely so that human time is spent where only humans can
go — which is exactly what §5 of `accepted_work_unit.md` is measuring.

## 3. The Devpost finding (verified, and it matters)

`https://devpost.com/robots.txt`, fetched 2026-08-22:

```
User-agent: *
Disallow:

User-agent: BLEXBot        Disallow: /
User-agent: CCBot          Disallow: /
User-agent: ChatGPT-User   Disallow: /
User-agent: GPTBot         Disallow: /
User-agent: Google-Extended Disallow: /
User-agent: anthropic-ai   Disallow: /
User-agent: Omgilibot      Disallow: /
```

Devpost permits general crawlers and specifically bans AI crawlers, **including
`anthropic-ai`**. DAY ZERO is an AI-assisted research system. The defensible reading is
that automated agent-driven collection from Devpost is out of bounds, regardless of what
UA string is sent. **Decision: the hackathon channel is manual-research-only in Phase 2.**
Hackathon signals enter the graph through analyst-entered records citing the official
result page, with the page archived at entry time.

This is a real constraint that meaningfully weakens Pool A coverage, and it is recorded
rather than worked around.

## 4. Biggest data-access constraints (ranked)

1. **X recent search is a 7-day window.** The channel best suited to catching founder
   transitions has the shortest memory of any channel. It cannot support the backtest at
   all, and it can only support live sourcing if polled continuously.
2. **The hackathon channel is closed to automation** (§3). Pool A's most distinctive
   surface is manual.
3. **Nothing links a GitHub identity to an X identity.** There is no join key. Identity
   resolution depends on people voluntarily publishing links, which many do not.
4. **GitHub Search caps at 1,000 results per query** and its relevance ordering is
   opaque. Discovery must be done through many narrow date-windowed queries, not one
   broad one.
5. **Non-English and non-GitHub ecosystems are structurally under-covered.** Gitee,
   Codeberg, and mailing-list-based projects are largely invisible. The initial universe
   already skews toward what GitHub search surfaces in English.
6. **X pricing is stale** (reference dated 2026-07-18, 30-day staleness gate exceeded).
   No X spend may occur until it is re-verified.
7. **No public source reliably indicates employment change**, and DAY ZERO forbids
   inferring it. This means Pool B is fundamentally harder to source than Pool A, and
   Pool B leads will lean on org/domain/artifact formation rather than departure.
8. **Wayback coverage of small project sites is sparse**, which caps how much of the
   backtest can rely on S13.

## 5. Recommended build order for Phase 2

1. **S1 + S2 + S3** — GitHub. Free, deep, historical, and it alone supports BUILD, DEPTH,
   COLLABORATION, VELOCITY, and F-02.
2. **S4** — arXiv. Free, gives cross-source convergence immediately (verified: AgentSight,
   TriAttention, UCCL all resolve paper↔repo this way).
3. **S14** — Wayback CDX. Required before any backtest is credible.
4. **S7 + S20** — package registries and personal sites. Cheap, and S20 is the highest-
   yield identity-resolution source there is.
5. **S12** — EDGAR, as a backtest confirmation field only.
6. **S15 + S18** — mailing lists and HN, for artifacts GitHub search misses.
7. **S10** — X, last, gated behind re-verified pricing and an explicit approval.
