# DAY ZERO — Founder-Formation Evidence Framework

**We do not predict founding.** No probability, no score, no "87% likely to start a
company." Predicting a person's future employment decisions from public data is both
technically unsound and an invasion of exactly the kind DAY ZERO exists to avoid.

Instead we **classify the evidence that already exists.**

---

## 1. States

States are ordered but not monotonic — a person can move backwards (a project is
abandoned) and can sit in one state indefinitely.

### `BUILDING`
**Definition:** a strong technical artifact exists and the person authored it.
**Entry requires:** ≥1 BUILD signal **and** ≥1 TECHNICAL DEPTH signal, with the person
resolved as an author (see `entity_graph.md` §3).
**Does not require:** any intent to commercialize. Most people in this state will never
start a company, and that is fine — DAY ZERO is not entitled to an opinion about it.

### `COLLABORATING`
**Definition:** repeated technical collaboration exists between identified people.
**Entry requires:** ≥1 COLLABORATION signal (C-01…C-05) beyond a single drive-by PR.
**Note:** this state is about *working relationships that survive*, which is the closest
observable proxy to team formation that does not require inference.

### `FORMING`
**Definition:** multiple public signals suggest a company or team is being formed.
**Entry requires:** **≥2 FORMATION signals from ≥2 independent channels.** One signal is
never enough. A GitHub org alone is not forming. A domain alone is not forming.
**Explicitly forbidden as entry evidence:** profile inactivity, deleted posts, a bio edit,
a "stealth" label with nothing behind it, rumor, or a third party's speculation.

### `LAUNCHED`
**Definition:** a company or product has publicly launched.
**Entry requires:** F-07 (dated launch statement by the builder + a live product surface).

### `FUNDED`
**Definition:** financing is publicly established.
**Entry requires:** a financing announcement from the company, a Form D, or a
credible independent report.
**Role in DAY ZERO:** this is the state we are trying to *arrive before*. It is a
confirmation field for the backtest, not a target.

### `UNKNOWN`
**Definition:** insufficient evidence to classify.
**This is a real, frequently-correct answer.** A system that never returns UNKNOWN is
guessing.

---

## 2. The window DAY ZERO actually targets

```
BUILDING ──► COLLABORATING ──► FORMING ──► LAUNCHED ──► FUNDED
   └──────────── DAY ZERO's window ────────┘        └── everyone else's window ──┘
```

Value is created in the first three states. By `LAUNCHED` the company is in databases;
by `FUNDED` it is in everyone's inbox. Array's own pattern supports this: they led
Sapiom's pre-seed roughly three weeks after the founder left Shopify, and wrote
HappyRobot's first check when the founders "hadn't raised anything."

---

## 3. State assignment is evidence-driven, not judgement-driven

The state is computed deterministically from the signal set. The *analyst* decides
whether a `FORMING` person is worth an introduction; the *system* decides only whether
the evidence for `FORMING` exists. Keeping these separate is what stops the system from
becoming an opinion generator.

| State | Deterministic entry condition |
| --- | --- |
| BUILDING | `count(BUILD) ≥ 1 AND count(DEPTH) ≥ 1 AND author_resolved` |
| COLLABORATING | `BUILDING AND count(COLLABORATION) ≥ 1` |
| FORMING | `count(FORMATION) ≥ 2 AND distinct_channels(FORMATION) ≥ 2` |
| LAUNCHED | `F-07 observed` |
| FUNDED | `F-08 observed OR financing_source_tier ≤ 2` |
| UNKNOWN | none of the above |

A person can be `BUILDING` and `FORMING` simultaneously with no `COLLABORATING` evidence
(a solo founder). The states are labels on evidence sets, not a state machine that must
be traversed in order.

---

## 4. Worked examples from the initial universe (all verified 2026-08-22)

| Person / team | State | Evidence | What is explicitly NOT claimed |
| --- | --- | --- | --- |
| **Cong Wang** (`congwang-mk`, Multikernel Technologies) | **FORMING → LAUNCHED** | F-01 `multikernel.io`; F-02 org created 2025-03-08; F-03 bio "Founder and CEO at @multikernel"; F-06 "Multikernel Technologies, Inc."; D-01/D-06 multikernel Linux patches to LKML (Sept 2025) + `kernelscript` eBPF DSL in OCaml | No claim about whether he left a prior employer, when, or why. His prior roles (Red Hat, Twitter, ByteDance) are context for reading the artifact, not evidence of a transition. |
| **Derek Chong + collaborators** (`shepherd-agents/shepherd`) | **COLLABORATING** (FORMING: PARTIAL) | B-01 repo 2026-06-24; C-04 org created same day; C-02 recurring contributors incl. a Northeastern faculty identity; D-02 CoW fork substrate with stated benchmarks | Org creation + a `.ai` domain is **one** formation channel, not two. Not classified FORMING. |
| **Ryan Codrai** (`RyanCodrai/turbovec`) | **BUILDING** | B-01/B-03/B-09 Rust vector index, 351 owner commits, Python bindings on PyPI, D-07 built on TurboQuant | Bio says "Member of Technical Staff at Anthropic." **Zero** formation signals. No inference of intent to leave. Not a lead. |
| **Yusheng Zheng** (`yunwei37`, eunomia-bpf / AgentSight) | **COLLABORATING** | B-01 repo 2025-07-07; C-03 arXiv:2508.02736 author overlap with repo contributors; D-01/D-05 eBPF system-level agent observability | eunomia-bpf is an established open-source community (org created 2022-08-20), not a new formation. |
| **`brontoguana`** (`krasis`) | **BUILDING**, identity LOW | B-03 768 owner commits; D-07 hybrid LLM runtime for VRAM-constrained hardware | Identity is unresolved. Cannot be introduced. Watchlist only. |
| **`adammiribyan`** (`zerobootdev/zeroboot`) | **UNKNOWN** | F-01/F-02 org + domain exist (formation-shaped) but B-03 fails: 24 commits over 6 days, no push since 2026-03-21 | Formation shell with no sustained construction. This is the shape a false positive takes. |

---

## 5. Freshness and decay

Formation evidence is time-sensitive; construction evidence is not.

- A FORMATION signal older than **270 days** with no subsequent BUILD or VELOCITY signal
  is marked `stale` and the person drops out of FORMING back to their construction-based
  state. Companies that formed and went quiet are not leads.
- BUILD and DEPTH signals **never decay**. A well-engineered system built in 2022 is
  still a well-engineered system. (This mirrors the enduring-vs-decayable split in the
  audited X engine, which was correct.)
- V-06 (abandonment) actively demotes: a project with no push in 90 days, whose total
  active life was under 120 days, removes its BUILD signals from surfacing eligibility.

---

## 6. What this framework refuses to do

1. Assign a probability to anyone founding anything.
2. Infer a departure, a resignation, or a job search from anything other than an explicit
   first-person public statement.
3. Treat "stealth" as evidence. Stealth is the absence of evidence.
4. Treat an employer's name as a formation signal in either direction.
5. Rank people.
