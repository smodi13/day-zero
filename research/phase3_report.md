# Phase 3: Reproduction, Diligence, and v2

**Date:** 2026-08-23
**Protocol commit (C):** `2056d35910cad745c58bf8ac784e299da301aedc`
**v2 rule commit (D):** `e8e3c64f56437bdac70db1957e841ac4d9d9fdbc`
**v1 frozen hash:** `ad0b7ae00630f7948e7c4444440af7c20fed61169370e46e076cd8f575a3566c` — **unchanged**
**v2 rule hash:** `435dfb8a568d8f07124125b08566cc9ced48f4d17ef76064978905968287f434`

---

## Executive Summary

Phase 3 was where DAY ZERO had to stop describing capabilities and demonstrate them.

**One technical claim was tested against a real baseline.** headroom's published
"60–95% fewer tokens for JSON, 15–20% for coding agents, same answers" came out
**PARTIALLY REPRODUCED**: the JSON claim holds as a *capability* (up to 92.47%, and
28.41% median beyond a minification baseline) with **1.0000 information retention across
35 samples**, while the coding-agent claim produced **0.00% on all 12 coding samples** with
three competing explanations tested and falsified. Cost: **$0, zero LLM calls.**

**One project got real diligence.** `multikernel/sandlock` — 3.3 MB of Rust, Landlock +
seccomp + seccomp user notification, an arXiv paper, an OCI shim, three SDKs, and a
published threat model that states in bold that a kernel LPE defeats it. Recommendation:
**ADVANCE TO FOUNDER CONVERSATION**, with the biggest gap named plainly — no evidence
anyone has ever tried to break it.

**The two documented v1 failures were repaired without loosening the bar.** v2 replaces
"independent websites" with "independent facts" and is *stricter* on four of five axes.
On the same ten historical cases it moves **0 PASS → 2 PASS** with **zero negative-control
regressions**. It is labelled POST-HOC everywhere it appears, and v1 stays published
beside it, unchanged.

**Nobody was contacted. No frontend was built. Nothing was deployed.**

---

## What Changed From Phase 2

| Phase 2 position | Phase 3 result |
| --- | --- |
| headroom is the best reproduction target because the claim is falsifiable | Confirmed — and the claim split cleanly: one half reproduces, one half does not |
| "NC-2 (wrapper presented as infrastructure) may apply to headroom" | **Answered with measurements: it does not.** Lossless schema factoring that beats minification by 28 points is engineering |
| Sandlock's escape surface vs a microVM was the open question | **Answered.** A microVM has a materially higher ceiling; sandlock does not dispute it and argues the ceiling is not the binding constraint for this workload |
| Multikernel and AgentSight were two independent leads | **They share a paper author.** One intellectual cluster, not two data points — now a v2 requirement |
| v1 convergence blocked the strongest true positive | **Repaired in v2** — Daft converges, and both key controls still reject |
| Analyst time was NOT_MEASURED | Instrument built and tested; **Phase 3's own review still NOT_MEASURED**, because the instrument was built mid-phase and estimating retroactively would defeat the point |

---

## Part A/B — EXP-1: the headroom reproduction

Full result: `headroom_reproduction.md`. Protocol: `phase3_experiment_protocol.md`.

**Verdict: PARTIALLY REPRODUCED.** Three of five pre-registered claims supported.

| Claim | Threshold | Measured | |
| --- | --- | --- | --- |
| A — reduces tokens | > 0% on JSON | 46.30% median | ✅ |
| B — **beats trivial minification** | ≥ 25% vs minified | **28.41%** median | ✅ |
| C — "same answers" | ≥ 0.95 retention | **1.0000** | ✅ |
| D — JSON 60–95% | median in band | 46.30% (p75 = 86.19%, max = 92.47%) | ❌ |
| E — coding agents 15–20% | ≥ 15% | **0.00%** | ❌ |

**The mechanism, from the code's own strategy string:** `lossless:table(60->len=3500)`.
Uniform JSON record arrays are rewritten to a schema header plus CSV-like rows.
Compression tracks *schema uniformity*, not size — the router's own heterogeneity score
predicts the outcome almost perfectly (`mixed:0.08` → 92.5% saved; `mixed:0.58` → 28.5%).

**Three things worth stating precisely:**

1. **The 60–95% headline is the top quartile, not the median.** Minification alone supplies
   30.84 of the 46.30 points at the median. Quoting the number against pretty-printed JSON
   is the friendliest available framing, and it took one afternoon on a laptop to find that
   out.
2. **The compression is genuinely lossless**, and I did not have to ask for it: running
   `lossless_only=True` produced byte-identical output to the default on every sample. The
   advertised savings do not come from truncation.
3. **On text you are better off running `sed`.** headroom returns code and prose unchanged
   while minification saves 7–10%, so headroom is ~8% *worse* than trivial whitespace
   stripping on those inputs.

**Fairness work before concluding CLAIM-E failed** (`headroom_supplementary.json`): a
six-file multi-turn coding session — 0.00%; tight context pressure — 0.00%; the optional
`[code]` extra installed — 0.00%. All three competing explanations falsified. The proxy,
`wrap`, MCP and Kompress-v2-base paths were **out of pre-registered scope and are named
rather than dismissed**; the coding claim may hold on one of them.

**Narrowest claim actually supported:** *on JSON arrays of uniform-schema records, headroom
losslessly removes 60–90% of tokens versus pretty-printed input and ~85% versus minified
input, with no measured information loss; ~28% beyond minification on heterogeneous JSON;
nothing on code, prose or line-oriented logs.*

---

## Part C — Sandlock diligence

Full memo: `sandlock/investment_memo.md`. Architecture: `sandlock/architecture.md`.
Threat model: `sandlock/threat_model.md`. Sources: `sandlock/source_audit.md`.

**Recommendation: ADVANCE TO FOUNDER CONVERSATION.** Not *invest* — that word is
unavailable from outside-in public work and does not appear in the vocabulary.

**The architecture in one line, from the paper:** static, input-independent policy compiles
into kernel-enforced rules (Landlock + seccomp-bpf); a narrow supervisor handles
runtime-dependent decisions and virtualised effects (seccomp user notification).

**The core question, answered:** *what is sandlock's escape surface versus a microVM, and
what does its threat model deliberately exclude?*

A microVM has a **materially higher security ceiling** — two boundaries instead of one, a
narrow virtio surface instead of the full host syscall interface, and a guest compromise
that is contained. Sandlock does not dispute this; its own security page says in bold:
*"Kernel vulnerabilities. The workload runs on your kernel… This is the price of no
hypervisor."*

What sandlock argues is that for the agent workload the ceiling is often not the binding
constraint, while ~5 ms vs ~100 ms, no root, no image build, and **policy that can express
"this agent may POST to exactly this endpoint and may never see the API key"** are things a
microVM does not address at all. That is coherent — and it is a *product* argument, not a
*security* argument, and should be tested as one.

**Most important exclusion:** kernel vulnerabilities. Everything else out of scope is
physics (side channels) or operator error. Kernel escape is inherent to the architecture.

**What is genuinely defensible:** kernel-subsystem-maintainer expertise applied to a
userspace product (verifiable from the kernel record, not hireable on a normal timeline),
and a working seccomp-user-notification policy engine with CoW transactional semantics.
**Potential, not proven:** the agent-specific policy layer — HTTP ACL, credential
injection, deterministic execution. **Not a moat:** Landlock and seccomp are public kernel
features, speed is a number competitors can chase, and 358 stars is not evidence.

**Could a strong security team reproduce it?** The architecture, yes, in 6–12 months with
two or three engineers who genuinely understand seccomp notification. What stays hard: CoW
correctness, TOCTOU discipline, and kernel-maintainer judgement about which primitives will
exist in two years. **A real head start and a thin moat, both true at once.**

**Biggest risk: no evidence of adversarial contact.** No audit, no bounty, no published
escape attempt. For a security product, *survived adversarial contact* is the evidence that
matters, and it is absent from public sources.

**Funding:** no public institutional financing identified in the sources reviewed. **This
is not a claim that the company is bootstrapped** — that would need evidence I do not have.

**Is the AI sandboxing need new, or old wine?** *Partially new.* Isolation is a 30-year-old
problem; volume/latency and the no-root requirement are real but are performance and
ergonomics arguments. The genuinely new part is that **the threat is semantic**: a
prompt-injected agent makes a *legitimate* call with a *legitimate* credential to the wrong
endpoint. No namespace, container or microVM addresses that. An HTTP ACL plus a credential
the child never sees does.

**Thematic-mirroring guard: passed**, because the artifact is verifiable independent of
Array's thesis. **Caveat recorded:** its Array relevance still rests on the security thesis
being right about *buyers*, not just about threats — the most verifiable buyers today may
be CI and FaaS operators, neither of whom needs an AI thesis.

---

## Part D — v2 methodology

Full design: `v2_methodology.md`. **Everything below is POST-HOC EXPLORATORY.**

### Convergence: independent facts, not independent websites

Seven evidence modalities, an explicit event model, and four deduplication rules. **v2 is
stricter than v1 on four of five axes:** modalities 2 → 3, events (no concept) → 3,
CONSTRUCTION optional → mandatory, temporal spread (none) → 30 days.

The load-bearing line: **self-publication is CONSTRUCTION, never EXTERNAL_VALIDATION.**
Without it the frontier-lab control gains a fourth modality and promotes.

### Identity: four states, no fuzzy matching

`VERIFIED_CROSS_LINK` and `STRONG_ARTIFACT_MATCH` may merge; `POSSIBLE_MATCH` and
`UNRESOLVED` may not. Accepted evidence widens to personal sites, README author links,
package metadata, paper author pages, company team pages and ORCID. **Cong Wang now
resolves by rule** — exact name on three independent artifacts — removing the manual
override Phase 2 needed. Display-name similarity, employer and location remain forbidden.

### Exploratory historical re-run

| Case | Company | Cutoff | **v1** | **v2** | Why it moved |
| --- | --- | --- | --- | --- | --- |
| B1 | Eventual (Daft) | 2024-09-30 | PARTIAL | **PASS** | 4 modalities, 6 events, **909-day span** — the v1 failure repaired |
| B2 | Sapiom | 2026-02-04 | PARTIAL | **PASS** | 3 modalities, 4 events, 144-day span |
| B3 | HappyRobot | 2024-12-03 | MISS | **PARTIAL** | Construction now recognised; still fails events, modalities and spread |
| B4 | Flamingo | 2025-10-27 | UNKNOWN | UNKNOWN | No recoverable evidence |
| B5 | Meibel | 2025-05-27 | UNKNOWN | UNKNOWN | — |
| B6 | Integral | 2023-09-04 | UNKNOWN | UNKNOWN | — |
| B7 | Mozart Data | 2020-11-10 | MISS | MISS | Org created after the cutoff |
| B8 | ZecOps | 2020-01-01 | MISS | MISS | Org only; no construction artifact |
| B9 | Era Software | 2021-10-05 | MISS | MISS | Org created after the cutoff |
| B10 | Wokelo | 2024-10-08 | UNKNOWN | UNKNOWN | — |

**v1: 0 PASS / 2 PARTIAL / 4 MISS / 4 UNKNOWN → v2: 2 PASS / 1 PARTIAL / 3 MISS / 4
UNKNOWN.** Three cases moved, all upward. **No accuracy percentage is claimed under either
version**, and ten known portfolio companies cannot produce one.

**What was repaired:** the modality/event model. Daft's five GitHub-hosted facts are now
five facts rather than one channel.
**What was NOT repaired:** the structural blind spot. B4, B5, B6, B10 remain UNKNOWN under
both. **Companies that do not build in public stay invisible, and no rule change fixes
that.**

### Negative controls under v2 — zero regressions

| Control | v1 | v2 | Failed v2 checks |
| --- | --- | --- | --- |
| NC-1 turboquant | DROP | **STILL REJECTED** | modalities, events, formation-like, spread |
| NC-3 zeroboot | DROP | **STILL REJECTED** | modalities, events, **spread** |
| NC-3b KVSplit | DROP | **STILL REJECTED** | modalities, events, formation-like, spread |
| NC-4 rotorquant | DROP | **STILL REJECTED** | modalities |
| **NC-5 turbovec** | WATCH | **STILL REJECTED** | modalities, **formation-like** |
| NC-7 OSCAR | WATCH | **STILL REJECTED** | **spread only** |

**Zero incorrectly promoted, same as v1.** One honest narrowing: **NC-7 now fails on
temporal spread alone.** It has three modalities (construction, research, identity), so a
research artifact with a longer publication history would pass v2's convergence gate. That
is a thinner margin than v1 had, it is reported rather than buried, and it is why NC-7's
downstream formation requirement still matters.

---

## Analyst time

Instrument built, tested, and ready. **Phase 3's own review time is reported as
NOT_MEASURED**, because the instrument was built mid-phase and timing those sessions
retroactively would be an estimate presented as a measurement. Phase 1 and Phase 2 are
never backfilled. Real numbers begin in Phase 4.

---

## Privacy / Ethics

All prior restrictions hold and are still test-enforced: no secrets, no personal phone
numbers or addresses, no private emails, no sensitive inference, no inferred job departure,
no raw social dumps, no personal absolute paths in system artifacts.

Two Phase 3 specifics: **WHOIS enrichment and domain-registrant lookup are explicitly
prohibited** in `config/v2/domain_signal_v2.yaml` because registrant data is personal data;
and the experiment dataset contains only public API responses, permissively licensed public
repo files, self-produced output and synthetic data, with provenance recorded per sample
and a test asserting no private-data category exists.

---

## Limitations

1. **The experiment tested the library path only.** Proxy, `wrap`, MCP and the prose model
   were out of scope and are named.
2. **Quality was measured as information preservation, not end-to-end task accuracy.** No
   budget was spent; the limitation was pre-registered, not discovered afterwards.
3. **Sandlock was never executed.** It needs Linux 6.12; the test machine is macOS/M1. The
   5 ms and Redis figures are the project's own and were not independently reproduced.
4. **v2 is post-hoc**, designed after seeing v1 fail on cases whose answers were known. It
   needs a cohort it has never seen before it earns any claim.
5. **Still one live sourcing channel.** X remains disabled; the identity join is still the
   bottleneck, and v2's identity work has not been measured against a real X population.
6. **Phase 3 analyst time is unmeasured.**
7. **Closed-source companies remain invisible** — unchanged by anything in Phase 3.

---

## Phase 4 Plan

1. **A new holdout cohort v2 has never seen.** This is the only thing that converts v2 from
   a repair into evidence.
2. **Measure analyst time from day one.**
3. **Resolve the identity join empirically** — apply v2 identity rules across the universe
   and count how many builders reach `STRONG_ARTIFACT_MATCH`. Only then decide about X.
4. **The public artifact**, if and only if the substance holds up. Recommendations in §92
   of the decision-gate answers.
5. **Do not run more reproductions until one is genuinely decision-relevant.** EXP-1 earned
   its place because the outcome was uncertain and the claim was load-bearing. Running
   experiments to look rigorous is the same failure as processing profiles to look thorough.
