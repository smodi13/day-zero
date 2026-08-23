# DAY ZERO — Technical Reproduction Lab

## 0. Why this exists

Array, in its own words (*15 Themes*, 2026-01-09):

> "We don't just review pitch decks — we use the products ourselves. ... **In many cases,
> we attempt to recreate parts of a product ourselves to understand the technical
> complexity.**"

The reproduction lab is not a novelty bolted onto a sourcing tool. It is the automation of
something Array already does by hand, and it is the only mechanism that moves TQ-1
(technical difficulty) and TQ-5 (reproducibility) from INFERRED to OBSERVED — the two
dimensions that most determine whether a pre-seed check is defensible.

## 1. Selection rules (frozen)

A project qualifies for reproduction only if **all six** hold:

1. **The claim is specific.** It has a number, a unit, and a named baseline.
2. **A relevant artifact exists** and is obtainable (public repo or published binary).
3. **The experiment can be run safely** — no attacking third-party systems, no scraping
   under a prohibiting policy, no running untrusted code outside an isolated environment.
4. **A meaningful baseline exists** — something to compare against that is not the
   project's own prior version.
5. **The result can falsify something.** If every plausible outcome leaves the investment
   view unchanged, the experiment is theater.
6. **It is feasible on the hardware actually available** (§2) or on free/low-cost
   infrastructure.

Explicitly disqualifying: experiments whose conclusion is guaranteed; experiments
requiring large GPUs; experiments that need private data.

## 2. Hardware reality — verified 2026-08-22

```
Apple M1 · arm64 · 8 GB RAM · macOS
python3 3.14.3 ✅   node v24.14.0 ✅   cargo ✗ (not installed)   docker ✗ (not installed)
no CUDA · no KVM · no Linux kernel
```

This is a hard constraint and it disqualifies several of the most *interesting* candidates
outright. Stating that up front is more useful than proposing an experiment that cannot run:

| Not feasible locally | Why |
| --- | --- |
| `deeplethe/forkd` microVM fork latency (~100ms / 100 children) | Requires KVM; there is no KVM on macOS |
| KV-cache quantization (`rotorquant`, `OSCAR`, `triattention`, `turboquant`) | Requires CUDA GPUs and multi-GB model weights |
| `youssofal/MTPLX` MLX speculative decoding (3× on Qwen-3.8-27B) | A 27B model does not fit in 8 GB |
| `eunomia-bpf/agentsight` eBPF overhead | Requires a Linux kernel |
| `boxlite-ai/boxlite`, `earendil-works/gondolin` | microVM / Linux |

These become **cloud-tier experiments** (a spot Linux VM with nested virtualization for
the microVM cases, ~USD 5–15 per run) and are deferred.

---

## 3. Candidate experiments

### EXP-1 — Token-compression claim (`headroomlabs-ai/headroom`) — **RECOMMENDED PRIMARY**

**CLAIM (verbatim from the repo description, 2026-08-22):** *"Compress tool outputs, logs,
files, and RAG chunks before they reach the LLM. **20% fewer tokens for coding agents,
60–95% fewer tokens for JSON, same answers.** Library, proxy, MCP server."*
Python · Apache-2.0 · created 2026-01-07 · actively pushed · 246 pages of contributors ·
lead contributor 1,164 commits · docs site.

**BASELINE:** the identical corpus with no compression, tokenized with the same tokenizer.
Secondary baselines: `json.dumps(..., separators=(',',':'))` (trivial minification) and
generic `gzip`-then-base64 — because if a stated 60–95% JSON reduction is matched by
whitespace minification, the interesting part of the claim evaporates.

**TEST:**
1. Build a fixed corpus of real agent tool output: `git diff`s, `pytest` output, `npm ls`
   JSON, OpenAPI specs, log files, directory listings. Freeze and hash it.
2. Tokenize before/after with a real tokenizer; report the distribution, not the mean.
3. For "same answers": select ~30 questions answerable **only** from the corpus content,
   ask them against compressed and uncompressed context with a small model, and measure
   answer agreement. Estimated cost: a few USD.

**METRICS:** token reduction (median, p10, p90) split by content type; compression
wall-time; answer-agreement rate; a count of factual items destroyed by compression.

**FAILURE MODES TO WATCH:** cherry-picked corpus; reduction concentrated entirely in
whitespace; "same answers" measured only on questions that never needed the dropped
content; compression latency exceeding the token savings in wall-clock terms.

**WHAT WOULD SUPPORT THE CLAIM:** ≥20% median reduction on realistic coding-agent output
that is *not* matched by trivial minification, with answer agreement ≥95%.
**WHAT WOULD WEAKEN IT:** reduction ≈ minification; agreement dropping on
retrieval-style questions; savings only on synthetic JSON.

**INVESTMENT IMPLICATION:** this sits directly on Array Theme 3 (*AI Economics
Infrastructure: do more with less*) and on the cost-per-Accepted-Work-Unit thesis from the
July 2026 Loop post. If lossy context compression preserves answers, the token-cost curve
for agent workloads bends and there is a real infrastructure layer. If it is minification
plus marketing, the category is a feature of every agent framework by next quarter.
**Feasible locally: yes.** Pure Python + tokenizer + a handful of cheap API calls.

---

### EXP-2 — Comparative token-proxy claim (`rtk-ai/rtk`) — **RECOMMENDED BACKUP**

**CLAIM:** *"CLI proxy that reduces LLM token consumption by 60–90% on common dev
commands. Single Rust binary, zero dependencies."* 77,100 stars · Apache-2.0 · created
2026-01-22 · 1,998 open issues · team of 3+ identified contributors.

**BASELINE:** the same commands with no proxy; and EXP-1's compressor on identical input,
which turns two separate marketing claims into one head-to-head measurement.

**TEST:** fixed command set (`git status`, `git diff`, `ls -R`, `npm ls`, `cargo tree`,
`pytest -v`), tokenized before/after. Install from a published release binary (no cargo
required).
**METRICS:** per-command token reduction; information loss (can the original command
intent still be satisfied?); overhead.
**SUPPORTS:** ≥60% median reduction across a command set *the project did not choose*.
**WEAKENS:** the 60–90% range holding only for commands with pathological output.
**IMPLICATION:** same theme as EXP-1. The 1,998 open issues are themselves a diligence
question — enormous adoption with an unresolved issue backlog is a signal about
maintainability, not about correctness.
**Feasible locally: yes**, if a prebuilt arm64 binary is published; otherwise install Rust.

---

### EXP-3 — Benchmark-claim provenance (`rohitg00/agentmemory`)

**CLAIM:** *"#1 Persistent memory for AI coding agents based on real-world benchmarks."*
TypeScript · Apache-2.0 · created 2026-02-25 · 399 owner commits.

This is a **meta-claim**, and it is the cheapest high-value experiment in the set:
*does a runnable benchmark exist, and does it produce the stated ranking?*

**TEST:** locate the benchmark harness; run it as published; attempt to reproduce the
ranking against at least one named competitor (e.g. `Gentleman-Programming/engram`, a Go
binary with SQLite + FTS5).
**SUPPORTS:** a harness exists, runs, and reproduces the ordering.
**WEAKENS:** no harness; unpublished evaluation set; the ranking is self-reported.
**IMPLICATION:** "agent memory" is one of the most crowded categories in the 2026 landscape
and maps to Array Theme 7 (*Knowledge-infused AI: Context Management*). The only durable
differentiator in a crowded category is measurement. A team that publishes a reproducible
harness is doing something structurally different from a team that publishes a claim.
**Feasible locally: yes** (Node 24 present). Zero GPU.

---

### EXP-4 — Fork latency (`deeplethe/forkd`) — cloud tier

**CLAIM:** *"Spawn 100 children in ~100ms from a warm parent; BRANCH a live VM in ~150ms.
KVM-isolated, snapshot CoW."* Rust · Apache-2.0 · created 2026-05-11 · active.
**BASELINE:** Firecracker snapshot-restore; Cloud Hypervisor; `docker commit`.
**TEST:** on a nested-virtualization Linux instance, measure cold spawn, warm fork, and
branch latency at n = 1/10/100, plus memory amplification.
**WHY IT IS INTERESTING:** if the numbers hold, this is genuine L4 systems work with a
clear moat question. If they hold only for a trivial guest, the claim is a microbenchmark.
**Feasible locally: NO.** Requires KVM; ~USD 5–15 per run on a cloud instance.

---

### EXP-5 — Reversible-execution overhead (`shepherd-agents/shepherd`) — cloud tier

**CLAIM:** *"copy-on-write fork ~5× faster than docker commit, with ~95% KV-cache reuse on
replay."* Python · MIT · created 2026-06-24 · Stanford NLP-affiliated contributors.
**BASELINE:** `docker commit` for the fork claim; a naive re-prompt for the cache claim.
**WHY IT IS INTERESTING:** two independent, precisely-stated claims, one systems and one
inference-economics. The 95% KV-reuse claim in particular is the mechanism that would make
agent replay affordable — directly the LoopOps layer Shruti describes.
**Feasible locally: NO** (Docker not installed; Linux needed for a fair comparison).

---

## 4. Recommendation

**PRIMARY: EXP-1 (headroom token compression).**
Falsifiable, locally feasible on an 8 GB M1, costs a few dollars, and lands on Array's
stated AI-economics thesis and on the cost-per-AWU frame from Shruti's own July 2026 post.
It also has a genuinely uncertain outcome: I do not know whether the 60–95% JSON figure
survives a minification baseline, and that is precisely why it is worth running.

**BACKUP: EXP-2 (rtk).**
Same theme, different implementation, and running both converts two marketing claims into
one comparison. Chosen as backup rather than primary only because it depends on a
prebuilt arm64 release binary being available.

**EXP-3** is the cheapest and should probably be run alongside the primary regardless.
**EXP-4 and EXP-5** are the most technically interesting and are explicitly deferred to a
cloud tier — noted rather than quietly dropped.

## 5. Protocol

1. Freeze and hash the input corpus before running anything.
2. Record the artifact's exact commit SHA.
3. Publish the harness alongside the result.
4. Report the distribution, never a single headline number.
5. **Publish results that contradict the project's claim, and notify nobody** — this is
   internal technical diligence, not public criticism of a builder. Results stay in the
   diligence record.
6. A failed reproduction is **not** an automatic negative on the founder. Ambitious claims
   in a README are normal. What it changes is the *question you ask them*, which is the
   entire point.
