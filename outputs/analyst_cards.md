# Analyst Cards

**As of:** 2026-08-23  
**Frozen rules hash:** `ad0b7ae00630f7948e7c4444440af7c20fed61169370e46e076cd8f575a3566c`  
**Anyone contacted:** no

System eligibility comes from the frozen configuration. Analyst selection is a separate human act and is recorded with the original system state, a reason and the evidence.

## multikernel/sandlock

- **Current workflow state:** `INTRO_READY` (system: `WATCH`, analyst override applied)
- **Current public status:** no institutional financing identified in the public sources reviewed
- **Career signal class:** recorded only where self-published; not used in eligibility
- **Formation state (system):** `BUILDING` · identity `medium` · owner scope `unregistered`
- **Signals fired:** B-01, B-02, B-03, B-08, B-09, C-03, D-01, D-05, F-01, F-02, F-06, V-02, V-03
- **Independent channels:** github, research, web
- **Themes:** agent_execution_isolation, agent_verification, security

**Builder / team.** Cong Wang and the Multikernel Technologies team (8 human contributors on sandlock)

**Project.** multikernel/sandlock — process-based AI agent sandbox for Linux, no container

**Why now.** 807 owner commits, pushed the day of review; sandlock.io registered 2026-08-08; an arXiv paper published 2026-05-25; and a company products page that now lists "Multikernel Sandbox (AI agent sandboxing runtime)" as a commercial product.

**Technical artifact.** github.com/multikernel/sandlock (Rust, Apache-2.0) + arXiv:2605.26298

**Technical-depth evidence.** Kernel-level isolation using unprivileged Linux primitives, from a maintainer of the Linux networking traffic-control subsystem. Systems depth OBSERVED; technical difficulty remains UNKNOWN until the escape surface is tested.

**Formation evidence.** GitHub org Multikernel Technologies, Inc. created 2025-03-08 (F-02, F-06); multikernel.io and sandlock.io (F-01); commercial product page and demo booking (F-07). No public financing round was found in the sources reviewed.

**Array relevance.** Agent execution isolation. Array's own AI coworker runs "in its own filesystem sandbox with isolated execution", and the April 2026 security post argues agents move data through syscalls where existing tooling cannot see them.

**Why company-first sourcing may miss it.** 358 stars on the sandbox repo; the founder has 72 GitHub followers, no blog field and no X-native presence; the strongest corroborating evidence sits on LKML and arXiv. No institutional financing was identified in the public sources reviewed, so no funding database would surface it.

**Strongest positive evidence.** Four independent channels spanning 17 months (org registry, company domain, LKML, arXiv), plus a paper co-authored with the AgentSight author — a cross-link between two independently-surfaced Phase 1 leads.

**Strongest negative evidence.** The company is already selling. This is closer to the late edge of Day 0 than Phase 1 assumed, and a round may exist that is simply not public.

**What must be verified before an introduction.** Whether a priced round has closed; team size; whether sandlock is the commercial focus or a research artifact beside the cloud-OS product.

**Technical question.** Sandlock claims confinement using unprivileged Linux primitives. What is the actual escape surface compared with a microVM boundary, and what does the paper's threat model deliberately exclude?

**Commercial / formation question.** Multikernel now sells three products (Private Cloud, Sandbox, LiveUpdate). Is the agent sandbox a wedge into the cloud-OS business, or the business itself? Those imply different buyers and different funding paths.

**Analyst override.**

- Original system state: `WATCH`
- Analyst state: `INTRO_READY`
- Reason: System state WATCH / IDENTITY_UNRESOLVED. The automated identity check reads only GitHub profile fields, and Cong Wang publishes no `blog` value, so it resolved to medium. His identity is in fact resolvable to ER-1 standard by artifact cross-reference.
- Evidence: multikernel.io/about.html names Cong Wang as Founder & CEO with a described kernel record; arXiv:2605.26298 "Sandlock: Confining AI Agent Code with Unprivileged Linux Primitives" lists Cong Wang as an author; the GitHub account congwang-mk is the top contributor to multikernel/sandlock with 807 commits.

---

## sipyourdrink-ltd/bernstein

- **Current workflow state:** `INTRO_READY` (system: `INTRO_READY`)
- **Current public status:** no institutional financing identified in the public sources reviewed
- **Career signal class:** recorded only where self-published; not used in eligibility
- **Formation state (system):** `FORMING` · identity `high` · owner scope `unregistered`
- **Signals fired:** B-01, B-02, B-03, D-02, D-04, D-05, D-06, F-01, F-02, F-06, V-02, V-03
- **Independent channels:** github, web
- **Themes:** agent_observability, agent_verification

**Builder / team.** Alex Chernysh (solo; Sip Your Drink Ltd)

**Project.** bernstein — deterministic orchestrator for CLI coding agents

**Why now.** 3,669 commits since 2026-03-22, pushed the day of review; bernstein.run live; a registered UK company (F-06) created eight days after the repo.

**Technical artifact.** github.com/sipyourdrink-ltd/bernstein (Python, Apache-2.0)

**Technical-depth evidence.** Removing the model from the coordination loop is an architectural stance, not a wrapper: it converts an LLM-orchestration problem into a scheduling problem. Depth markers OBSERVED across D-02/D-04/D-05/D-06; difficulty UNKNOWN until read.

**Formation evidence.** F-01 bernstein.run; F-02 org 2026-03-28; F-06 'Ltd' in the registered org name.

**Array relevance.** Objective verification and failure recovery — the two LoopOps components Shruti's July 2026 post names as missing (completion gates, escalation queues).

**Why company-first sourcing may miss it.** 960 stars against 3,669 commits. A one-person studio with no press, no accelerator and no financing identified in the public sources reviewed.

**Strongest positive evidence.** The highest construction-to-attention ratio in the eligible set, with a registered company behind it.

**Strongest negative evidence.** Studio of one. No co-founder, no external contributor above 37 commits, and deterministic orchestration is a crowded idea even if this implementation is not.

**What must be verified before an introduction.** Whether anyone runs Bernstein in production; whether the determinism claim holds under tool failure; whether the founder intends a company or a tool.

**Technical question.** "No model in the coordination loop" is the whole claim. Where exactly does determinism break — tool output ordering, retries, or agent nondeterminism — and what does the orchestrator do when a sub-agent returns something unparseable?

**Commercial / formation question.** A one-person studio with 3,669 commits and a registered company. Is Bernstein the product, or infrastructure for a product? And who is the first buyer — platform teams, or individual engineers?

---

## scanaislop/aislop

- **Current workflow state:** `INTRO_READY` (system: `INTRO_READY`)
- **Current public status:** no institutional financing identified in the public sources reviewed
- **Career signal class:** recorded only where self-published; not used in eligibility
- **Formation state (system):** `FORMING` · identity `high` · owner scope `unregistered`
- **Signals fired:** B-01, B-02, B-03, D-02, D-05, D-06, F-01, F-02, V-02
- **Independent channels:** github, web
- **Themes:** agent_verification, security

**Builder / team.** Kenny Olawuwo (software/security engineer) + 5 contributors

**Project.** aislop — code-quality and security gate for AI-authored code

**Why now.** 319 owner commits since 2026-03-06, pushed 2026-08-22; org created 2026-04-19; scanaislop.com live.

**Technical artifact.** github.com/scanaislop/aislop (TypeScript, MIT)

**Technical-depth evidence.** Security and compiler-adjacent markers OBSERVED (D-02, D-05, D-06). Difficulty UNKNOWN: the honest question is whether this is real analysis or rule packaging.

**Formation evidence.** F-01 scanaislop.com; F-02 org created 2026-04-19.

**Array relevance.** "Vibe coding security" — securing production code written by agents — is one of the four categories Array's April 2026 security post says it is ACTIVELY SEEKING.

**Why company-first sourcing may miss it.** 572 stars. No financing identified in the public sources reviewed, and the category is described in Array's own writing as unfilled.

**Strongest positive evidence.** Sits on a category Array has publicly stated it wants and cannot find.

**Strongest negative evidence.** Lowest technical-depth confidence of the three. A code-quality gate is the easiest thing on this list for an incumbent linter vendor to absorb.

**What must be verified before an introduction.** Whether the detection is agent-specific or generic; whether any team has it in a CI gate; who the second engineer is.

**Technical question.** Detecting "dead code, unsafe casts, swallowed errors" is classic static analysis. What is genuinely different about agent-authored code that a tuned existing linter would miss, and is that difference measurable?

**Commercial / formation question.** Is the buyer the platform team that owns the CI gate, or the security team that owns the risk? The pricing and the wedge differ.

---
