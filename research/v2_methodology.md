# DAY ZERO v2 — Sourcing Methodology

> **v2 is POST-HOC relative to the v1 historical holdout.**
> Any re-run of the same ten cases under v2 is an **EXPLORATORY DIAGNOSTIC**, never
> out-of-sample validation. **v1 is preserved unchanged and permanently alongside v2** —
> its config, its frozen hash `ad0b7ae0…3566c`, its holdout results (0 PASS / 2 PARTIAL /
> 4 MISS / 4 UNKNOWN) and its negative-control results are never edited or replaced.

---

## The two failures v2 answers

### Failure 1 — convergence measured websites, not facts

Eventual/Daft reached only **PARTIAL** in the v1 holdout. Its pre-cutoff evidence was:

- GitHub organisation `Eventual-Inc` created 2022-02-03
- Repository `Daft` created 2022-04-25, Rust, Apache-2.0
- Sustained commits through 2022 from 15 distinct human authors
- Seven tagged releases before the cutoff
- Named, resolvable committers

Five substantial facts spanning 2.5 years — and v1 scored them as **one channel**, because
`github_org`, `github_repo`, `github_commits` and `github_releases` all collapse to
"github". The rule designed to stop single-channel false positives blocked the strongest
true positive in the cohort.

### Failure 2 — identity resolution read one surface

v1 computed identity confidence from GitHub profile fields alone. Cong Wang publishes no
`blog` value, so the strongest lead in the universe resolved to `medium` and required a
manual analyst override. Separately, only **1 of 267** collected identities publishes a
linkable X account, so X evidence could not attach to 99.6% of the universe.

---

## Change 1 — convergence redefined: independent FACTS, not independent WEBSITES

**Seven evidence modalities.** A modality is *what kind of fact this is*, independent of
where it is hosted:

`CONSTRUCTION` · `FORMATION` · `RESEARCH` · `COLLABORATION` · `COMMERCIALIZATION` ·
`IDENTITY` · `EXTERNAL_VALIDATION`

**Requirements (all must hold):**

| Requirement | v1 | v2 |
| --- | --- | --- |
| Distinct modalities | implicitly 2 families | **≥ 3** |
| Distinct **events** | *no concept existed* | **≥ 3** |
| CONSTRUCTION | BUILD **or** DEPTH accepted | **mandatory** |
| One of FORMATION / RESEARCH / COLLABORATION / EXTERNAL_VALIDATION | — | **mandatory** |
| Temporal spread | same-day collapse only | **≥ 30 days** between first and last event |

**This is stricter than v1 on four of five axes.** v2 is not v1 with the bar lowered; it
replaces a *proxy* for independence (hostname) with the thing the proxy was standing in
for (distinct facts), and then raises the count.

### The false-positive protection is preserved explicitly

Four deduplication rules keep the thing v1 got right:

- **DEDUP-1** — facts sharing an `underlying_event_key` are one event.
- **DEDUP-2** — same modality, same day, actor-controlled surfaces → one event. A launch
  post, a domain and an org registered on one day is **one decision announced three ways**.
- **DEDUP-3** — a press release, its syndicated rewrites, an aggregator entry and a social
  repost are **one event**, tracked through `sources.underlying_event_key`.
- **DEDUP-4** — stars, forks, watchers and "latest commit" are never events. Attention
  remains barred from surfacing entirely.

### The single most important line in v2

> **Self-publication is CONSTRUCTION, never EXTERNAL_VALIDATION.**

Publishing your own package to PyPI is something you built, not someone else's
endorsement. Without this line, the frontier-lab negative control (NC-5) would have a
fourth modality and would promote. It is written into
`config/v2/convergence_v2.yaml#external_validation_excludes`, and it is tested.

### Verified behaviour

| Case | v1 | v2 | Why |
| --- | --- | --- | --- |
| **Eventual/Daft** | ✗ not converged | **✓ converged** | 5 modalities, 5 events, 887-day span |
| **turbovec** (NC-5) | ✗ rejected | **✗ still rejected** | 2 modalities; PyPI rejected as self-published; no formation-like modality |
| **zeroboot** (NC-3) | ✗ rejected | **✗ still rejected** | org + domain same day collapse to one event; 4-day span fails the 30-day floor |

---

## Change 2 — identity resolution with four confidence states

| State | May merge? | Requires |
| --- | --- | --- |
| `VERIFIED_CROSS_LINK` | ✅ | A first-party surface explicitly links the two identities |
| `STRONG_ARTIFACT_MATCH` | ✅ | **Exact full-name** match across **≥ 2 independent artifacts** |
| `POSSIBLE_MATCH` | ❌ | Suggestive; recorded, never merged, never intro-eligible |
| `UNRESOLVED` | ❌ | No accepted evidence |

**Accepted evidence for `VERIFIED_CROSS_LINK`** widens well beyond v1's single field:
GitHub `blog`, a personal site linking both profiles, README author links, package-registry
author metadata, a paper author page linking the repository, a company team page, ORCID, or
an explicit bio statement naming the other handle.

**Forbidden, unchanged from v1 and non-negotiable:** display-name similarity, surname-only
match, avatar, city, employer, technical topic, **or any combination of these**. v2 does
not solve the join with fuzzy matching.

### Verified behaviour

**Cong Wang** now resolves to `STRONG_ARTIFACT_MATCH` from three independent artifacts —
`multikernel.io/about.html` names him as founder, arXiv:2605.26298 lists him as an author,
and `congwang-mk` is the top contributor to `multikernel/sandlock`. **This removes the need
for the Phase 2 manual analyst override**: the same conclusion is now reached by rule.

A person appearing on **one** artifact stays `POSSIBLE_MATCH` and is not intro-eligible.

---

## Change 3 — the domain signal, modelled properly

Phase 2 measured that **formation lives on domains** (73 of 171 formation signals) while
**construction lives on GitHub**. v2 models six distinct domain facts — domain resolves,
docs site, pricing/products page, company identity, site links the GitHub org, team page
names people — mapped to their real modalities rather than lumped into "one weak formation
signal."

One domain contributes **at most one FORMATION event**, so a five-page marketing site
cannot manufacture convergence.

**Prohibited:** WHOIS enrichment, registrant lookup, reverse WHOIS, DNS-history broker
data. Registrant data is personal data. **Allowed:** fetching the public page as any
ordinary reader would, honouring robots.txt.

---

## Change 4 — analyst-time instrumentation

Phase 2 refused to invent analyst-review time and reported `NOT_MEASURED`. Phase 3 begins
measuring it with a monotonic clock: candidate, action, start, end, active seconds.

**Phase 1 and Phase 2 are never backfilled.** A fabricated baseline would be worse than no
baseline. `minutes_per_intro_ready_awu` becomes meaningful from Phase 3 forward and is
labelled as covering Phase 3 only.

---

## What v2 does NOT change

- No score, anywhere. Still enforced by schema and AST tests.
- Attention metrics still barred from all surfacing logic.
- Career class still optional, still evidence-backed, still unreadable by the eligibility rules.
- X still **disabled by default** and still fail-closed on five preconditions.
- No automated Devpost adapter, by robots policy.
- Formation still requires explicit public statements; no departure is ever inferred.

---

## The honest limitation of v2

**v2 was designed after seeing v1 fail on a case whose answer I already knew.** That is the
definition of post-hoc. Three things constrain the damage:

1. The v1 results stay published, unchanged, beside v2 — including the 0 PASS.
2. v2 is **stricter** on four of five convergence axes, so it is not "loosen until Daft
   passes."
3. Every v1 negative control is re-run under v2, and any regression is reported rather than
   suppressed.

What would make v2 credible is a **new cohort v2 has never seen**. That is Phase 4 work,
and until it happens the correct description of v2's historical numbers is *exploratory
diagnostic* — which is how they are labelled everywhere they appear.
