# DAY ZERO — Phase 4 Report

**Phase 4A: unseen v2 validation + identity/domain audits. Phase 4B: public research
interface.** Local only — not deployed, not published, nobody contacted.

Commits: F = `662392ab2e9e2eeec6549e08b2819d65aa03d4d8` (cohort freeze) ·
G = `302e5f76aef90952f26aec95c8aa4d431db0ef1f` (unseen validation + audits) ·
H = `051ed8132fe3c400af0815868e0c05a750e53a04` (public research interface).

---

## Executive Summary

Phase 4A asked the only question that matters after a repair: does v2 work on cases it
has never seen? Nine eligible Array-portfolio cases were selected by a deterministic rule
bound to the v2 hash and committed before any evidence retrieval. Result: **2 PASS /
0 PARTIAL / 1 MISS / 6 UNKNOWN**. The test validated the repair (both resolvable
formation-stage cases converged; zero negative-control regressions) and immediately
exposed the next design weakness: **Perspective AI passed the convergence gate on a
marketing/content repository**, because v2 verifies evidence *independence* but does not
require *technical depth* at the gate. The rule was not patched after the result; the
weakness is published as a limitation.

The identity audit revised a founding assumption: identity resolution generally is no
longer the bottleneck (62.17% mergeable under conservative rules); **X-specific identity
linkage is** (1 of 267 verifiable). The domain audit quantified presence-vs-signal:
70.59% of repos have a domain, 32.35% gain a distinct formation event from it.

Phase 4B built the public work sample: a seven-route static site that presents
Source → Verify → Diligence → Learn as a working system — flagship Sandlock diligence,
the Headroom reproduction with its baseline finding, and a methodology page that leads
with the system's own failure. All research values flow from a deterministic 63 KB
export; 51 new tests guard the site against drift, leakage, and overclaim; the research
corpus is bit-identical to COMMIT G.

## Unseen Cohort

Eligible universe: 9 cases (target was 12; all eligible cases used). Selection:
`SHA256(v2_frozen_hash + ":" + case_id)`, sorted ascending — the ordering cannot be
chosen post hoc without visibly changing v2 itself. Cutoff: the day before the earliest
verifiable financing announcement establishing Array's involvement; unresolvable dates
excluded as `CUTOFF_DATE_UNRESOLVED`, never for difficulty. Six of nine cases were
selected with `founder_or_team: UNKNOWN` — evidence the answer key was not consulted.
One declared bias: Blumira used the Series A date (seed date unverifiable), which biases
that case *toward* passing. No case was swapped or replaced after selection.

Cases (cutoffs): Perspective AI (2025-01-29), CandorIQ (2025-07-21), Wabi (2025-11-04),
MokSa.ai (2024-04-21), Capsule (2021-01-13), ORO (2022-11-02), Tumble (2022-10-04),
Blumira (2021-08-17), Zingly.ai (2025-07-20).

## Unseen V2 Result

**2 PASS / 0 PARTIAL / 1 MISS / 6 UNKNOWN.**

- **Blumira — PASS** (strongest true positive): 7 events, 4 modalities, 426-day span;
  a genuine pre-Series-A construction-and-formation trail.
- **Perspective AI — PASS**, and the pass is the failure (below).
- **MokSa.ai — MISS** (strongest miss): one formation-only event; no construction
  evidence recoverable pre-cutoff.
- **Six UNKNOWN**: no GitHub organisation verifiably linkable pre-announcement under
  v2 identity rules. This is the structural blindness of GitHub-led discovery stated as
  data, not smoothed over.

The result is out-of-sample with respect to **v2 rule development only**. Every case is
a known portfolio company, so hindsight bias remains; no accuracy/precision/recall/
win-rate statistic is derivable from nine known-outcome cases and none is reported.

## Perspective AI Failure

The most important methodology failure of the phase. The case satisfied every v2
convergence check — independent modalities, distinct events, construction present,
temporal spread — using a **marketing/content repository (SCSS, no licence)**. The
checks are working as designed; the design is wrong: v2 has no technical-depth
eligibility requirement at the convergence gate, even though depth signals exist
elsewhere in the system. **No post-result patch was made.** A depth requirement is the
leading v3 candidate; no v3 has been designed, frozen, or validated, and none is
claimed. This limitation is presented prominently on the public site (homepage and
methodology page).

## Identity Audit

267 live identities (Phase 2 universe, unchanged). States: 109 VERIFIED_CROSS_LINK,
57 STRONG_ARTIFACT_MATCH, 60 POSSIBLE_MATCH, 41 UNRESOLVED. Mergeable: 166 = **62.17%**.
X-linkable: **1 = 0.37%**.

Revised conclusion: the Phase 1 assumption "identity resolution is the bottleneck" is
wrong in its general form — conservative merging already handles ~62%. The bottleneck is
**X-specific linkage**. This is reported as a methodological update, not hidden as a
contradiction.

## X Decision

28 bio @handles were deliberately not counted as X identities: on GitHub a bare @handle
is overwhelmingly a GitHub-org reference, and treating it as an X account would be the
fuzzy matching v2 forbids. The handles are not exposed anywhere. X ingestion remains
disabled (no credentials; zero records). On current evidence, paid X API access is not
justified: with 0.37% verifiable linkage, the expected yield per dollar is far below the
GitHub channel's, and the honest first step would be improving verifiable cross-linking,
not buying volume.

## Domain Signal

70.59% of repositories have a project domain; 32.35% gain a **distinct** formation event
from it (the rest duplicate the decision already evidenced by the GitHub organisation).
Presence is not signal; the site visualises exactly this gap. WHOIS/registrant/reverse-
WHOIS enrichment remains excluded by policy.

## Frontend Architecture

`outputs/** → scripts/build_frontend_data.py → web/src/data/research.json (62,970 bytes,
sha256-manifested, forbidden-key-guarded, byte-identical across runs) → Next.js 15.5.23
static export (`output: "export"`) → web/out/`. No runtime database, API, auth, or AI.
No research value is typed into a component; tests compare built HTML against the
export. The typed data layer (`web/src/lib/research.ts`) is the single import point.
Dependency-free motion: transform-only reveals over an IntersectionObserver hook with
threshold-0, scroll-fallback and above-viewport safeguards; global smooth scrolling was
removed after it was found to silently cancel long anchor jumps.

## Homepage Story

Hero ("Find the builder before the round. / Test the hard claim before the meeting.")
with a static-SVG pipeline diagram — Source → Verify → Diligence, Learn feeding back —
then: Current 3 preview → Sandlock flagship → Headroom verification ("The baseline is
part of the claim") → the failure/repair/unseen triptych → the Perspective AI callout →
six operating rules → verifiable hashes. The failure section is above the fold count of
most portfolio sites' first metric.

## Current 3

`multikernel/sandlock` (WATCH · analyst override, and shown as such),
`sipyourdrink-ltd/bernstein` (INTRO_READY), `scanaislop/aislop` (INTRO_READY) —
presented in surfacing order with an explicit "not a global ranking" statement, full
canonical records (why surfaced, why missed, formation and depth evidence, strongest
positive/negative, both open questions, verification prerequisites), and no scores.

## Sandlock Presentation

Verdict first (ADVANCE TO FOUNDER CONVERSATION; *invest* absent from the vocabulary and
the page says so), financing wording exact and badged NOT FOUND with the
not-bootstrapped clarification and an explicit "Array has not reviewed this company."
Then: why surfaced, architecture with the paper's organising idea, the interactive
four-way trust-boundary diagram (Sandlock / Firecracker / gVisor / raw Landlock) with
full textual equivalents, the project's stated threat model in scope/out of scope, a
hostile-workload outcome table, the semantic-execution-policy insight as the analytical
centrepiece, a dimension-by-dimension comparison table with an explicit no-score note,
the shared-kernel trade stated plainly in a gains/gives-up pair, construction evidence,
a 13-claim evidence ledger, commercial status, the Multikernel project graph, the
AgentSight relationship stated precisely, defensibility (proven/potential/not-a-moat),
seven pre-registered founder questions, upgrade/downgrade triggers, and the S1–S19
source ledger with working inline references.

## Headroom Presentation

Neutral title ("Token compression reproduction"). Both public claims verbatim with the
20% vs 15–20% discrepancy noted and resolved against the experiment. Design: 35 samples,
1.57 MB, 12/12/11, two tokenizers, four baselines, MINIFIED primary — with the reasoning
stated. Interactive per-sample explorer (category × baseline, canonical medians only,
GZIP+B64 labelled as a reference compressor, full table fallback). Verdict PARTIALLY
REPRODUCED with the pre-registered scoreboard (A/B/C supported, D/E not). The finding —
30.84% of the 46.30% headline is supplied by minification alone; headroom's own
contribution is 28.41% — is the centrepiece. The three falsified rescue attempts
(SUPP-1/2/3) are shown. Fairness is explicit and tested: real engineering, strong
structured-data result, coding claim not reproduced *in this benchmark*, benchmark
limited — and no fraud/dishonesty framing anywhere.

## Methodology Presentation

The full evolution: Phase 1 ontology → v1 frozen → 0/2/4/4 → diagnosis → v2 frozen
(stricter on four axes, independence redefined) → exploratory 2/1/3/4 (labelled
POST-HOC EXPLORATORY, "proves nothing on its own") → unseen 2/0/1/6 with the
per-case table → the Perspective AI callout → an eight-step commit timeline with real
hashes → the not-comparable-as-performance caution stated before any number →
HUMAN_ANALYST_ACTIVE_TIME = NOT_MEASURED with the no-relabelling rule.

## Privacy

Professional artifacts only; no emails, phones, locations, employment inference, or
personal biography anywhere in export or HTML (tested). The full person universe stays
home: 257 of 267 universe handles are absent from the export (the remainder appear only
inside public repo slugs used by the analyses); internal IDs (`person:`) and the
evidence store are absent (tested). Bio @handles not exposed. Export forbidden-key guard
refuses `email/phone/address/location/followers/score/founder_score/probability`.

## AI Disclosure

On `/about`, unminimised: built with substantial AI assistance (Claude Code) across
research organisation, implementation, extraction, classification, testing, debugging,
experiment implementation, drafting, synthesis — with the boundaries: sources are the
evidence, AI output never primary evidence, observed/inferred structurally distinct,
selections and recommendations are analyst judgments, unequal manual diligence
acknowledged, no global founder score (schema + test enforced).

## Testing

320 tests passing: 269 pre-existing Python tests (unchanged) + 51 new frontend tests in
two files. `test_frontend_export.py` (21): manifest integrity, in-process double-build
determinism, size ceiling, forbidden keys, universe non-export, canonical fidelity for
every number the site asserts, verbatim wordings, no-statistic labels. 
`test_frontend_site.py` (30): all seven routes and no extras, hero and static values in
HTML, ranking/verification/fairness language guards, per-page number checks, disclaimer
on every page, email/phone/path/secret scans, universe absence from HTML+JS, internal
corpus markers absent from client JS, placeholder scan.

## Responsive QA

Tested in Chrome (real browser, not CSS inspection): all 7 routes × all 7 widths
(320/390/768/1024/1280/1440/1700) checked programmatically for horizontal overflow —
49/49 clean after fixing a real overflow (long mono tokens in the SUPP cards at 320).
Visual passes at 1280–1500 desktop and 390/320 mobile for home, current-3, sandlock
(diagram + toggles), headroom (explorer + baseline switching), signals, methodology.
Keyboard: native buttons focusable with aria-pressed state changes; details/summary
native; skip link; :focus-visible outline. Anchor navigation verified after fixing a
real bug (global smooth scroll cancelled long jumps; source-ledger links now land
exactly, sticky-nav-cleared, with :target highlight). Reveal safety verified: computed
opacity 1 on all reveal blocks pre-trigger; motion is transform-only; reduced-motion CSS
zeroes all animation.

## Bundle Analysis

Client JS (final build): **790.6 KB raw / 245.9 KB gzip** total; largest chunk
`framework-*.js` 177.3 KB raw / 56.2 KB gzip. First Load JS 103–109 KB per route.
Route-specific additions: sandlock 7.3 KB, headroom 7.3 KB (explorer was refactored from
importing the whole export to props — page chunk fell from 16.8 KB to 2.75 KB), others
≤4.2 KB. The heavy chunks are the React/Next framework baseline; no further optimisation
attempted per the no-vanity rule.

## Research Freeze

`git diff 302e5f7 -- outputs research/sandlock research/*.md src config data sources
experiments` = **empty**. Phase 4A results, unseen cohort, v2 hash, historical results,
Headroom experiment, Sandlock recommendation, Current 3 eligibility, source counts and
the identity audit are bit-identical to COMMIT G. The export script reads canonical
files; it does not write them.

## Remaining Weaknesses

1. **Perspective AI depth gap** — the known, deliberately unpatched v2 design weakness.
2. **Six unseen UNKNOWNs** — GitHub-led discovery cannot see companies without a public
   construction trail; the honest ceiling of the current system.
3. **Sandlock performance claims not reproduced** (kernel 6.12 requirement vs macOS test
   machine); carried as project claims, clearly labelled, but a reproduction would be
   stronger.
4. **Human analyst time unmeasured** — the instrument exists; no human ran it.
5. **One benchmark, one entry point** for Headroom; six untested configurations listed.
6. **Single-viewer QA** — responsive/accessibility checks were automated + one reviewer;
   no screen-reader hardware pass.
7. The dark-only visual theme is a deliberate commitment, not a limitation, but it has
   not been tested with users who prefer light UIs.

## Publication Recommendation

**READY FOR FINAL POLISH + PUBLICATION** — pending the explicit publication decision,
which is out of scope for this phase. Nothing in the validation gates blocks it: tests,
types, lint, audit, build, determinism, freeze, privacy and static-value checks all
pass. The remaining work is judgment-level polish (wording passes, possibly a favicon/
OG image, hosting choice) rather than engineering.
