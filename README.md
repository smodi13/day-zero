# DAY ZERO

### Founder Formation & Technical Diligence Engine

> ## 🚧 WORK IN PROGRESS — LOCAL / NOT YET PUBLISHED
> Phases 1–4 are complete locally: research, live sourcing, technical reproduction,
> deep diligence, unseen validation, and a static public research interface.
> **Nothing is deployed, no public repository exists, and no outreach has occurred.**

---

## Source → Verify → Diligence → Learn

DAY ZERO is a working system built as an independent work sample for an **AI Analyst**
application at **Array Ventures**. It tries to do the four things the role actually
requires, and to prove each one with an artifact rather than a claim:

| Stage | Question | Artifact |
| --- | --- | --- |
| **Source** | Can it find technical builders through public artifacts, without ranking people by prestige or popularity? | 102-repo live universe → 3 `INTRO_READY` leads (`outputs/intro_queue.json`) |
| **Verify** | Can it reproduce a technical claim against a meaningful baseline, instead of accepting marketing language? | Pre-registered Headroom reproduction (`outputs/phase3/headroom_summary.json`) |
| **Diligence** | Can it read architecture and code deeply enough to understand the real tradeoffs? | Sandlock deep diligence (`research/sandlock/`) |
| **Learn** | When its own rules fail, does it say so — and improve without rewriting prior results? | v1 failure → frozen v2 → unseen validation (`outputs/phase3/`, `outputs/phase4/`) |

The public interface in `web/` tells this story on seven routes:
`/` · `/current-3` · `/diligence/sandlock` · `/lab/headroom` · `/signals` ·
`/methodology` · `/about`.

## Current 3

Three builder leads currently survive evidence review (**not** a ranking; no scores
exist anywhere in the system):

1. `multikernel/sandlock` — process-based AI-agent sandbox (carried as `WATCH` with an
   explicit analyst override; the company is already selling)
2. `sipyourdrink-ltd/bernstein` — deterministic orchestrator for CLI coding agents
3. `scanaislop/aislop` — code-quality and security gate for AI-authored code

No introduction has been made and nobody has been contacted.

## Sandlock Diligence

Outside-in technical diligence at the level of the trust boundary: reconstructed
architecture, the project's own threat model versus analyst interpretation, comparisons
against Firecracker / gVisor / containers / raw Landlock, defensibility split into
proven / potential / not-a-moat, and pre-registered founder questions.

Verdict: **ADVANCE TO FOUNDER CONVERSATION** (the word *invest* is deliberately
unavailable from outside-in public work). **No public institutional financing was
identified in the reviewed sources** — which is a statement about what is public, not a
claim the company is bootstrapped.

## Headroom Reproduction

A published token-compression claim, tested against a protocol committed **before** any
measurement: 35 analyst-constructed samples (1.57 MB), two tokenizers, four baselines,
five pre-registered claims with thresholds.

Verdict: **PARTIALLY REPRODUCED.** Structured JSON: 46.30% median savings vs raw,
28.41% vs minified (the comparison that matters). Coding context: 0.00% at every
quantile vs raw, with three pre-registered rescue attempts falsified. Probe retention
1.0000, zero transformation errors. The headline finding: **the baseline is part of the
claim.**

## v1 Failure

The first frozen rule set scored the 10-case historical holdout at
**0 PASS / 2 PARTIAL / 4 MISS / 4 UNKNOWN**. Diagnosis: v1 defined evidence independence
as *different hostnames*, so a builder whose whole verifiable life is on GitHub could
never converge. The failing run is committed and preserved.

## v2 Repair

Independence was redefined as *evidence modalities over distinct dated events*, while
tightening four other axes. v2 was frozen (hashed, committed) **before** any rerun.
The same-cohort rerun (2/1/3/4) is labelled **post-hoc exploratory** and proves nothing
on its own; all negative controls remained rejected (0 regressions).

## Unseen Validation

Nine eligible Array-portfolio cases v2's design had never touched, selected by a
deterministic rule bound to the v2 hash and committed **before** evidence retrieval
(COMMIT F). Result: **2 PASS / 0 PARTIAL / 1 MISS / 6 UNKNOWN** — out-of-sample with
respect to *rule development*, not venture performance, and no accuracy/precision/recall
statistic is reported from nine known-outcome cases.

The unseen test also **found the next weakness**: Perspective AI passed the v2
convergence gate on a marketing/content repository. v2 verifies evidence independence
but does not require technical depth at the convergence gate. The rule was **not**
changed after seeing the result; a depth requirement is a candidate for a future v3,
which has not been designed or validated.

## Source Limitations

- Discovery is **GitHub-led with multi-modal evidence** — not "multi-channel sourcing."
  GitHub supplied 100% of discovery; papers and domains enrich, they do not discover.
- Six of nine unseen cases were UNKNOWN because no GitHub organisation could be
  verifiably linked pre-announcement: companies without a public construction trail are
  structurally invisible to this system, and that is reported as data.
- Identity audit (Phase 4): 267 live identities, 166 (62.17%) mergeable under
  conservative rules, exactly 1 (0.37%) verifiably X-linkable. General identity
  resolution is no longer the bottleneck; **X-specific linkage is**.
- Domains: 70.59% of repositories have one, but only 32.35% contribute a distinct
  formation event. Presence is not signal.

## X Status

X ingestion is **disabled** (off by default, no credentials present; zero records in the
dataset). 28 bio @handles were deliberately **not** counted as X identities — a bare
@handle is insufficient evidence of cross-platform identity under the conservative merge
policy, and the handles are not exposed anywhere.

## Privacy

DAY ZERO researches **what people build**, not people. No emails, phones, addresses,
precise locations, employment inference, data brokers, people-search sites, facial
recognition, WHOIS registrant lookups, or guessed username matching. The public export
is scanned for forbidden fields at build time and again by tests. The full person
universe never reaches the frontend. Full rules: `research/data_ethics.md`.

## AI Disclosure

This project was built with **substantial AI assistance** (Claude Code): research
organisation, software implementation, structured extraction, classification assistance,
testing, debugging, experiment implementation, drafting, and synthesis. Public sources
are the factual evidence; AI output is never treated as primary evidence; observed
evidence is structurally distinct from inference; final sourcing selections and
recommendations are analyst judgments; and the system contains no global founder score —
the schema forbids one and tests enforce it.

## Independence

> **DAY ZERO is an independent research project and is not affiliated with, sponsored
> by, or endorsed by Array Ventures, Shruti Gandhi, Multikernel Technologies, Sandlock,
> Headroom Labs, or any person or company referenced in the analysis. It is based
> entirely on public information and is not investment advice.**

No individual named in this repository has been contacted in connection with it.

## Architecture

```
day-zero/
  research/     strategy, frameworks, diligence (research/sandlock/), methodology
  sources/      source_registry.csv — traceable source registry
  config/       frozen rule manifests (hashed)
  src/          Python sourcing engine (dayzero package)
  data/         canonical SQLite database (regenerable; gitignored)
  outputs/      canonical research outputs — the single source of truth
  experiments/  Headroom reproduction: protocol, dataset manifest, results
  tests/        320 tests (Python engine + frontend export + built site)
  scripts/      build_frontend_data.py — deterministic public export
  web/          Next.js static site (output: export); no runtime DB/API/AI
```

Data flow: `outputs/** → scripts/build_frontend_data.py → web/src/data/research.json
(≈63 KB, forbidden-key-guarded) → next build → web/out/`. No research value is typed
into a component; drift is caught by tests that compare built HTML against the export.

## Reproduction

```bash
python3 -m pytest                       # 320 tests
python3 scripts/build_frontend_data.py  # deterministic export (run twice → identical)
cd web && npm install && npm run build  # static site in web/out/
```

The commit history is the audit trail: rules and cohorts are hashed and committed before
the results they govern exist. Key hashes surface on `/methodology`.
