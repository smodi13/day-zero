# DAY ZERO — Technical Quality Evidence Framework

**There is no technical founder score.** No number, no 1–100, no letter grade, no
weighted composite. Nine dimensions are assessed independently, each tagged
`OBSERVED / INFERRED / UNKNOWN`, and the analyst reads all nine.

The reason is not squeamishness about numbers — it is that these dimensions genuinely
trade off against each other. A project can be extremely original and completely
unreproducible. A project can be deeply systems-heavy and have zero users. Collapsing
them into a total destroys the only information an investor actually needs.

---

## 1. The nine dimensions

### TQ-1 — Technical difficulty
*How hard is the actual system?*

| Level | Meaning | Test |
| --- | --- | --- |
| L4 | Requires expertise most strong engineers do not have | kernel/hypervisor/compiler/consensus/numerics-level work |
| L3 | Requires serious engineering but is learnable | distributed control planes, custom runtimes, non-trivial concurrency |
| L2 | Substantial application engineering | well-built services over existing primitives |
| L1 | Integration | orchestration of others' APIs |
| L0 | Wrapper | a thin surface over one API |

**The L1/L2 boundary is where most misclassification happens.** A token-compression
proxy that reduces LLM spend 60–90% is L1 *if* it is prompt engineering and pattern
matching, and L3 *if* it involves real streaming transformation with correctness
guarantees. You cannot tell from the README. This is precisely why the reproduction lab
exists.

### TQ-2 — Originality
*Is this an original system/approach, or an assembly of existing components?*
Recorded as one of: `novel-mechanism`, `novel-application-of-known-mechanism`,
`competent-reimplementation`, `assembly`, `reupload`.
**`reupload` is a real and common category** — verified example: `0xSero/turboquant`,
1,735 stars, **2 commits**, a restatement of a published Google technique.

### TQ-3 — Systems depth
*Does the implementation require serious systems work?*
Evidence: language and layer (Rust/C/C++/Go/OCaml at kernel, VM, or runtime level),
presence of syscall/eBPF/KVM/CUDA surfaces, memory and concurrency handling, build
complexity. Verified L4-shaped examples in the initial universe: `multikernel/kernelscript`
(OCaml eBPF DSL), `deeplethe/forkd` (KVM microVM CoW fork), `eunomia-bpf/agentsight`
(eBPF), `Karib0u/rustinel` (ETW/ESF/eBPF endpoint detection), `uccl-project/uccl`
(GPU collectives).

### TQ-4 — Research depth
*Is there novel research?*
Evidence: a peer-reviewed or arXiv paper with the builder as an author, a novel
algorithm with a proof or ablation, or a result that advances a published baseline.
Verified: arXiv:2508.02736 (AgentSight), arXiv:2604.04921 (TriAttention),
arXiv:2512.19849 + arXiv:2604.17172 (UCCL-EP, UCCL-Zip).
**Absence of research depth is not a negative.** Most great infrastructure has no paper.

### TQ-5 — Reproducibility
*Can the claims be tested?*
`fully-reproducible` (harness + data + hardware available) / `partially` /
`claim-only` / `unfalsifiable-as-stated`.
This dimension **gates the reproduction lab**: only `fully` or `partially` qualify.

### TQ-6 — Performance evidence
*Are there benchmarks, and are they honest?*
Assessed on: is there a named baseline? are the conditions stated? is the harness
public? does the claim have units? Verified contrast —
`scrya-com/rotorquant` states "better PPL (6.91 vs 7.07), 28% faster decode, 5.3x faster
prefill, 44x fewer params" (specific, falsifiable, named baseline, **no license, no
push since 2026-04-23**) vs. `MemPalace/mempalace` "the best-benchmarked open-source AI
memory system" (no baseline, no numbers, 58k stars).

### TQ-7 — Usage evidence
*Does anyone actually use it?*
Only non-builder-sourced evidence counts: downstream dependents, packages depending on
it, named adopters reported by a third party, real issues from real users, forks with
divergent commits. **Stars do not count.**

### TQ-8 — Architecture clarity
*Can the system be understood and interrogated?*
Is there an architecture document? Are module boundaries meaningful? Can a reader state
what the hard part is? Undocumented is not automatically bad, but it makes every other
dimension INFERRED rather than OBSERVED, and it makes the founder harder to diligence.

### TQ-9 — Defensibility question
**Deliberately a question, not a rating.**
*What specifically would be hard for a strong engineer or a well-resourced team to
reproduce in 3 months?*
Valid answers are concrete: a body of kernel expertise; a data flywheel; a correctness
property nobody else has proven; a distribution position; three years of edge cases.
Invalid answers: "the model," "the prompt," "first-mover advantage," "the team."
If the honest answer is *nothing*, that is written down as **nothing**.

---

## 2. Assessment record format

```yaml
artifact: github.com/deeplethe/forkd
assessed_at: 2026-08-22
assessed_by: analyst
dimensions:
  TQ1_difficulty:      {value: L3-L4,                 status: INFERRED, basis: "KVM CoW microVM fork; not read line-by-line"}
  TQ2_originality:     {value: novel-application,     status: INFERRED, basis: "fork() semantics applied to agent microVMs"}
  TQ3_systems_depth:   {value: high,                  status: OBSERVED, basis: "Rust; KVM isolation; snapshot CoW"}
  TQ4_research_depth:  {value: none-found,            status: UNKNOWN,  basis: "no arXiv match"}
  TQ5_reproducibility: {value: partially,             status: INFERRED, basis: "requires KVM; not runnable on macOS host"}
  TQ6_performance:     {value: specific-claim,        status: OBSERVED, basis: "~100ms for 100 children; ~150ms branch — stated, untested"}
  TQ7_usage:           {value: unknown,               status: UNKNOWN,  basis: "207 forks, 9 open issues; no named adopters"}
  TQ8_architecture:    {value: partial,               status: OBSERVED, basis: "README only"}
  TQ9_defensibility_q: "What in the CoW snapshot path is hard to reproduce, given Firecracker and CH already exist?"
```

**No `total` field exists in this schema. That is intentional and enforced.**

---

## 3. How AI may and may not be used here

| Allowed | Forbidden |
| --- | --- |
| Extract stated claims from a README into structured fields | Decide whether a claim is true |
| Classify a repo into a technical area | Assign TQ-1 as a fact |
| Summarize an architecture document | Write TQ-9 |
| Find the paper that matches a repo | Assert the paper's quality |
| Draft the diligence question | Answer it |

Every AI-produced field is stored with `produced_by: model` and is rendered separately
from evidence. An analyst must convert it to `OBSERVED` by checking the source. This
mirrors the audited X engine's rule that the LLM never assigns a number — a rule worth
preserving verbatim.

---

## 4. The honest limitation

Eight of the nine dimensions can be assessed from metadata and a careful read. **TQ-1 and
TQ-5 usually cannot.** The difference between an L1 wrapper and an L3 system is often
invisible from outside, and it is the single most decision-relevant fact.

That is the entire argument for the reproduction lab: it is not a flourish, it is the
only way to move TQ-1 from INFERRED to OBSERVED. And it is what Array already says it
does — *"in many cases, we attempt to recreate parts of a product ourselves to understand
the technical complexity."*
