# Sandlock — Source Audit

All evidence gathered 2026-08-23. Primary sources first. Every claim in the other
Sandlock documents traces back to a source ID here.

## Primary sources

| ID | Source | Type | What it establishes |
| --- | --- | --- | --- |
| **S1** | `github.com/multikernel/sandlock` (GitHub API) | primary artifact | Rust, Apache-2.0, created 2026-03-13, pushed 2026-08-23, 358 stars, 38 forks, 19 open issues, 4.4 MB. Topics: `landlock`, `seccomp`, `sandboxing`, `rust`, `ai-agents`, `promptinjection`, `faas`, `linux` |
| **S2** | Repository tree (`git/trees/main?recursive=1`) | primary artifact | Module layout and file sizes; the code inventory in `architecture.md` |
| **S3** | `README.md` (817 lines) | primary artifact | Mechanism claims, comparison table, kernel requirements, CLI surface |
| **S4** | `docs/sandbox-reference.md` (540 lines) | primary artifact | Every policy field, defaults, protection opt-out semantics, behavioural notes |
| **S5** | arXiv:2605.26298 — *Sandlock: Confining AI Agent Code with Unprivileged Linux Primitives*, 2026-05-25, Cong Wang and Yusheng Zheng | research paper | Architecture thesis, performance claims (~5 ms startup, Redis at bare-metal throughput) |
| **S6** | `sandlock.io/security.html` (site source, `multikernel/sandlock.io`) | official statement | The project's own threat model: trust tiers, in-scope and out-of-scope attacks |
| **S7** | `sandlock.io/comparison.html` | official statement | Self-comparison to containers, Firecracker, gVisor, bubblewrap/firejail, OpenShell |
| **S8** | `sandlock.io` navigation + footer | official statement | Two named commercial products; "What is open, what is licensed"; Multikernel Technologies, Inc., San Jose |
| **S9** | GitHub contributors API | primary artifact | 8 human contributors: congwang-mk 807, dzerik 173, ghazariann 71, sachin2605 20, solarhell 5, apollo13 1, mrsimpson 1, gokwok 1 |
| **S10** | GitHub participation stats | primary artifact | Commits/week, last 12 weeks: 73, 58, 31, 35, 46, 31, 40, 89, 64, 41, 19, 10 |
| **S11** | GitHub releases API | primary artifact | v0.8.1 (2026-05-27) → v0.8.6 (2026-08-08); roughly monthly cadence |
| **S12** | Recent commit log | primary artifact | Active PR review (PR #192, "riscv64 review blockers"), multi-architecture work (x86_64, aarch64, riscv64) |
| **S13** | `orgs/multikernel/repos` | primary artifact | 16 repositories; the project graph in `architecture.md` §7 |
| **S14** | `multikernel.io/about.html` | official statement | Cong Wang as Founder & CEO; three named products |
| **S15** | GitHub languages API | primary artifact | Rust 3,321,536 · Python 503,404 · C 125,532 · Go 75,477 · Shell 22,560 |
| **S16** | `crates/sandlock-core/src/landlock.rs` (881 lines, read) | primary artifact | Landlock ruleset construction; ABI gating; access-mask computation |
| **S17** | `search/code?q=sandlock+org:eunomia-bpf` | primary artifact | 49 hits; AgentSight-org repos referencing sandlock in docs/drafts |

## Secondary sources

| ID | Source | Establishes |
| --- | --- | --- |
| **S18** | Phase 2 collection (`data/collected/github_repos.json`) | Independent, dated snapshot of the same artifact taken before this diligence began |
| **S19** | Phase 2 `outputs/intro_queue.json` | The lead's system state and analyst override at the research date |

## What could not be established

| Question | Status |
| --- | --- |
| Funding, investors, valuation | **No public evidence found.** No round, filing, or investor named on the site, in the repo, or in search results reviewed |
| Revenue, customers, paid users | **UNKNOWN.** No pricing page, no customer logos, no case studies found |
| Team size | **UNKNOWN.** 8 GitHub contributors is a floor, not a headcount |
| Whether contributors are employees | **UNKNOWN.** Not inferable and not inferred |
| Independent security audit | **None found** |
| Production deployments | **UNKNOWN** |

## Evidence-handling notes

- The company's postal address appears on its own website. It is a corporate address on a
  public company page; no individual's personal contact information was collected, and
  none appears in any DAY ZERO output.
- Contributor identities are GitHub logins and self-published display names only. No
  employment status was inferred for anyone.
- `sandlock.io/security-model/`, `/comparison/`, `/products/` return 404; the real paths
  are `security.html` and `comparison.html`. The site's own navigation links to the 404s —
  a real defect, noted because it is the kind of thing a careful reader should report
  rather than silently work around.
