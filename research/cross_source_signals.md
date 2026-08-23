# DAY ZERO — Cross-Source Convergent Signals

**Definition** (from `signal_ontology.md` §8):

> ≥2 signals from ≥2 **independent** channels, about the same resolved entity, within a
> 180-day window, where at least one is a BUILD or DEPTH signal and at least one is a
> COLLABORATION or FORMATION signal.

"Independent" means the sources do not derive from one another. **A tweet linking to a
repo is one channel, not two** — the tweet is a pointer, not a second witness. A paper and
a repo with overlapping authorship are two.

Convergent sets rank above high activity on any single platform. High activity on one
platform is what a scraper finds. Convergence is what a *system* finds.

---

## The three strongest instances found

### CS-1 · Cong Wang / Multikernel — **four independent channels**

| Channel | Signal | Date | Verification |
| --- | --- | --- | --- |
| GitHub org | F-02 org `multikernel` created | **2025-03-08** | GitHub API |
| Company site | F-01 `multikernel.io`; F-06 "Multikernel Technologies, Inc." | live | site + org profile |
| Linux kernel mailing list | D-01/D-06 multikernel patch series submitted to LKML | **Sept 2025** | LKML archive; independently reported by technical press |
| GitHub personal | F-03 first-person bio "Founder and CEO at @multikernel"; account created **2025-08-21** | 2025-08-21 → | GitHub API |
| GitHub repo | B-01/B-03/D-06 `kernelscript`, 524 owner commits, OCaml eBPF DSL, Apache-2.0 | ongoing → 2026-06-26 | GitHub API |

**Why this is the strongest set in the universe.** Four genuinely independent surfaces —
an org registry, a domain, a kernel mailing list, and a personal profile — none of which
derives from the others, converging on one resolved identity inside a six-month window.
The LKML channel in particular is *unfakeable*: kernel patch review is public, adversarial,
and cannot be gamed with marketing.

**And it is invisible to conventional sourcing.** 72 GitHub followers. Two public personal
repos. No X-native presence found. Every high-signal surface here is one that an
attention-ranked or social-listening tool does not index at all.

---

### CS-2 · AgentSight — **paper ↔ repository ↔ community**, verified through arXiv

| Channel | Signal | Date | Verification |
| --- | --- | --- | --- |
| arXiv | TQ-4 arXiv:2508.02736 *AgentSight: System-Level Observability for AI Agents Using eBPF*; authors Yusheng Zheng, Yanpeng Hu, Tong Yu, Andi Quinn | **2025-08-02** | arXiv API, exact title match |
| GitHub | B-01 repo created; B-03 sustained construction in C/eBPF; 207 human commits | **2025-07-07** → 2026-08-22 | GitHub API |
| GitHub identity | C-03 paper author ↔ repo contributor overlap (`yunwei37` = Yusheng Zheng, company field `eunomia-bpf`) | ongoing | GitHub API |
| Project site | `eunomia.dev/agentsight` | live | site |

**Why it matters.** The repository was created **26 days before** the paper was published.
The construction preceded the publication — the ordering is itself a signal about how this
group works, and it is only visible if you check both channels and compare timestamps.

**Honest limitation:** this converges to `COLLABORATING`, **not** `FORMING`. `eunomia-bpf`
is an established open-source community (org created 2022-08-20, 151 repos), not a new
entity. The convergence is real and the formation is absent, and the system must report
both.

---

### CS-3 · UCCL — **two papers ↔ one repository ↔ an academic lab**

| Channel | Signal | Date | Verification |
| --- | --- | --- | --- |
| arXiv | arXiv:2512.19849 *UCCL-EP: Portable Expert-Parallel Communication* — Mao, Zhang, Cui, Huang, You, Chen, Xu, Gu, Shenker, Raiciu, Zhou, Stoica | **2025-12-22** | arXiv API |
| arXiv | arXiv:2604.17172 *UCCL-Zip: Lossless Compression Supercharged GPU Communication* — Ma, Lao, Xu, Wang, Mao, Meng, Zhen, Wu, Stoica, Wang, Zhou | **2026-04-19** | arXiv API |
| GitHub | B-01/B-03/D-04/D-07 repo created, 47 pages of contributors, C++/CUDA | **2025-01-06** → active | GitHub API |
| GitHub identity | C-03 `MaoZiming` (Ziming Mao, UC Berkeley PhD) and `YangZhou1997` (Yang Zhou, Asst Prof UC Davis) appear as both authors and top committers | ongoing | GitHub API + self-published homepages |

**Why it matters technically.** Two papers, sixteen months of repository history, and a
verifiable author↔committer overlap. TQ-1 resolves to L4 on observed evidence rather than
inference. This is what the strongest form of cross-source evidence looks like.

**Why DAY ZERO should be honest about it.** The author lists include Ion Stoica and Scott
Shenker. When a Berkeley systems group with that author list forms a company, it will not
be a discovery — it will be a competitive process. Claiming this as a non-obvious find
would be exactly the hero-worship failure mode the mandate warns about. It is recorded as a
**high-confidence convergence with low non-obviousness**, and those are different axes.

---

## Near-misses, and what they teach

### NM-1 · Shepherd — convergence that collapses on inspection
`shepherd-agents/shepherd`: repo created 2026-06-24, org created 2026-06-24, domain
`shepherd-agents.ai` live. Three formation-shaped facts — **announced simultaneously.**
Under the independence rule this is *one* channel (a coordinated launch), not three.
Classified FORMING PARTIAL rather than FORMING.

**Lesson:** simultaneity is the tell. Genuine multi-channel convergence usually has
*temporal spread* — Multikernel's signals span March 2025 to June 2026. A launch produces
three artifacts in one day; a formation produces them over months.

### NM-2 · zeroboot — formation shell with no construction
Org created 2026-03-19, domain `zeroboot.dev`, repo with 2,434 stars. Two formation
channels, and **24 commits over six days** with no push since. Rejected by the BUILD-base
requirement (`negative_controls.md` NC-3).

**Lesson:** convergence of *formation* signals alone is not convergence. The definition
requires a BUILD or DEPTH signal in the set for exactly this reason.

### NM-3 · TriAttention — genuine convergence, zero formation
arXiv:2604.04921 (2026-04-06) ↔ `WeianMao/triattention` (created 2026-04-04), with
author↔committer overlap including recognized quantization researchers. Real
paper↔code convergence — and no org, no domain, no company, no statement.

**Lesson:** paper + code is a *depth* convergence, not a *formation* convergence. Treating
every strong systems paper with a repo as a company-in-formation would flood the system
with noise and would badly misread what academic groups are doing (NC-7).

---

## What the convergence analysis actually revealed

**1. The three strongest sets all involve a non-GitHub, non-social channel.**
LKML, arXiv, arXiv. Every one of the strongest signals in this universe came from a surface
that a GitHub-plus-Twitter sourcing tool does not touch.

**2. Zero convergent sets involved X.** Not because X is worthless — because DAY ZERO's
Phase 1 had no X access, and because the entities that converge most strongly (kernel
developers, systems researchers) are the least X-native population in technology. This is a
real limitation and a real finding.

**3. Temporal spread distinguishes formation from launch** (NM-1). This should become an
explicit rule in ontology v2: signals arriving within the same 24 hours from surfaces
controlled by the same person count as one channel.

**4. Depth convergence and formation convergence are different things** (NM-3), and
conflating them is the single easiest way to turn a sourcing system into a paper-alert
service.
