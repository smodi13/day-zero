# Founder Intro Queue

**As of:** 2026-08-23  
**Frozen rules hash:** `ad0b7ae00630f7948e7c4444440af7c20fed61169370e46e076cd8f575a3566c`  
**Anyone contacted:** no

> The queue holds however many leads survive review — 0, 1, 2, 3 or more. It is never padded to reach three.

## 3 lead(s) cleared eligibility

### multikernel/sandlock

- **Builder Or Team:** Cong Wang and the Multikernel Technologies team (8 human contributors on sandlock)
- **Project:** multikernel/sandlock — process-based AI agent sandbox for Linux, no container
- **Why Now:** 807 owner commits, pushed the day of review; sandlock.io registered 2026-08-08; an arXiv paper published 2026-05-25; and a company products page that now lists "Multikernel Sandbox (AI agent sandboxing runtime)" as a commercial product.
- **Technical Artifact:** github.com/multikernel/sandlock (Rust, Apache-2.0) + arXiv:2605.26298
- **Technical Depth:** Kernel-level isolation using unprivileged Linux primitives, from a maintainer of the Linux networking traffic-control subsystem. Systems depth OBSERVED; technical difficulty remains UNKNOWN until the escape surface is tested.
- **Formation Evidence:** GitHub org Multikernel Technologies, Inc. created 2025-03-08 (F-02, F-06); multikernel.io and sandlock.io (F-01); commercial product page and demo booking (F-07). No public financing round was found in the sources reviewed.
- **Array Relevance:** Agent execution isolation. Array's own AI coworker runs "in its own filesystem sandbox with isolated execution", and the April 2026 security post argues agents move data through syscalls where existing tooling cannot see them.
- **Why Company First Sourcing May Miss It:** 358 stars on the sandbox repo; the founder has 72 GitHub followers, no blog field and no X-native presence; the strongest corroborating evidence sits on LKML and arXiv. No institutional financing was identified in the public sources reviewed, so no funding database would surface it.
- **Strongest Positive:** Four independent channels spanning 17 months (org registry, company domain, LKML, arXiv), plus a paper co-authored with the AgentSight author — a cross-link between two independently-surfaced Phase 1 leads.
- **Strongest Negative:** The company is already selling. This is closer to the late edge of Day 0 than Phase 1 assumed, and a round may exist that is simply not public.
- **What Must Be Verified Before Introduction:** Whether a priced round has closed; team size; whether sandlock is the commercial focus or a research artifact beside the cloud-OS product.

- System state: `WATCH` · formation `BUILDING` · identity `medium`
- Signals: B-01, B-02, B-03, B-08, B-09, C-03, D-01, D-05, F-01, F-02, F-06, V-02, V-03

### sipyourdrink-ltd/bernstein

- **Builder Or Team:** Alex Chernysh (solo; Sip Your Drink Ltd)
- **Project:** bernstein — deterministic orchestrator for CLI coding agents
- **Why Now:** 3,669 commits since 2026-03-22, pushed the day of review; bernstein.run live; a registered UK company (F-06) created eight days after the repo.
- **Technical Artifact:** github.com/sipyourdrink-ltd/bernstein (Python, Apache-2.0)
- **Technical Depth:** Removing the model from the coordination loop is an architectural stance, not a wrapper: it converts an LLM-orchestration problem into a scheduling problem. Depth markers OBSERVED across D-02/D-04/D-05/D-06; difficulty UNKNOWN until read.
- **Formation Evidence:** F-01 bernstein.run; F-02 org 2026-03-28; F-06 'Ltd' in the registered org name.
- **Array Relevance:** Objective verification and failure recovery — the two LoopOps components Shruti's July 2026 post names as missing (completion gates, escalation queues).
- **Why Company First Sourcing May Miss It:** 960 stars against 3,669 commits. A one-person studio with no press, no accelerator and no financing identified in the public sources reviewed.
- **Strongest Positive:** The highest construction-to-attention ratio in the eligible set, with a registered company behind it.
- **Strongest Negative:** Studio of one. No co-founder, no external contributor above 37 commits, and deterministic orchestration is a crowded idea even if this implementation is not.
- **What Must Be Verified Before Introduction:** Whether anyone runs Bernstein in production; whether the determinism claim holds under tool failure; whether the founder intends a company or a tool.

- System state: `INTRO_READY` · formation `FORMING` · identity `high`
- Signals: B-01, B-02, B-03, D-02, D-04, D-05, D-06, F-01, F-02, F-06, V-02, V-03

### scanaislop/aislop

- **Builder Or Team:** Kenny Olawuwo (software/security engineer) + 5 contributors
- **Project:** aislop — code-quality and security gate for AI-authored code
- **Why Now:** 319 owner commits since 2026-03-06, pushed 2026-08-22; org created 2026-04-19; scanaislop.com live.
- **Technical Artifact:** github.com/scanaislop/aislop (TypeScript, MIT)
- **Technical Depth:** Security and compiler-adjacent markers OBSERVED (D-02, D-05, D-06). Difficulty UNKNOWN: the honest question is whether this is real analysis or rule packaging.
- **Formation Evidence:** F-01 scanaislop.com; F-02 org created 2026-04-19.
- **Array Relevance:** "Vibe coding security" — securing production code written by agents — is one of the four categories Array's April 2026 security post says it is ACTIVELY SEEKING.
- **Why Company First Sourcing May Miss It:** 572 stars. No financing identified in the public sources reviewed, and the category is described in Array's own writing as unfilled.
- **Strongest Positive:** Sits on a category Array has publicly stated it wants and cannot find.
- **Strongest Negative:** Lowest technical-depth confidence of the three. A code-quality gate is the easiest thing on this list for an incumbent linter vendor to absorb.
- **What Must Be Verified Before Introduction:** Whether the detection is agent-specific or generic; whether any team has it in a CI gate; who the second engineer is.

- System state: `INTRO_READY` · formation `FORMING` · identity `high`
- Signals: B-01, B-02, B-03, D-02, D-05, D-06, F-01, F-02, V-02

## CURRENT 3

| Rank | Subject |
| --- | --- |
| 1 | multikernel/sandlock |
| 2 | sipyourdrink-ltd/bernstein |
| 3 | scanaislop/aislop |
