# EXP-1 — headroom Reproduction Result

**Verdict: PARTIALLY REPRODUCED.**

Protocol pre-registered in commit `2056d35910cad745c58bf8ac784e299da301aedc`, before any
measurement. Thresholds were not moved after results were seen.

| | |
| --- | --- |
| Target | `headroom-ai` 0.36.5 (Apache-2.0), `headroomlabs-ai/headroom` |
| Samples | 35 (12 structured JSON · 12 coding context · 11 agent context), 1.57 MB |
| Tokenizers | `o200k_base`, `cl100k_base` |
| Baselines | RAW · MINIFIED · COMPACT_JSON · GZIP_B64 · HEADROOM |
| Environment | Apple M1, 8 GB, Python 3.14.3, no GPU |
| **Cost** | **$0. Zero LLM calls. Zero paid resources.** |
| Transformation errors | **0 / 224 measurements** |

---

## Result against the five pre-registered claims

| Claim | Threshold | Measured | Verdict |
| --- | --- | --- | --- |
| **CLAIM-A** — reduces tokens vs raw | > 0% on JSON | **46.3%** median | ✅ **Supported** |
| **CLAIM-B** — beats trivial minification | ≥ 25% vs minified on JSON | **28.41%** median | ✅ **Supported** |
| **CLAIM-C** — "same answers" | ≥ 0.95 probe retention | **1.0000** | ✅ **Supported** |
| **CLAIM-D** — JSON reduction 60–95% | median inside band | **46.3%** median (below band) | ❌ **Not supported** |
| **CLAIM-E** — coding agents 15–20% | ≥ 15% vs raw | **0.00%** | ❌ **Not supported** |

---

## The numbers

### Structured JSON (n = 12), `o200k_base`

| Metric | median | p25 | p75 | max |
| --- | --- | --- | --- | --- |
| headroom vs raw | **46.30%** | 39.00% | 86.19% | **92.47%** |
| headroom vs minified | **28.41%** | — | — | 86.85% |
| minification alone vs raw | 30.84% | — | — | — |

### Coding context (n = 12)

| Metric | median | p25 | p75 | max |
| --- | --- | --- | --- | --- |
| headroom vs raw | **0.00%** | 0.00% | 0.00% | **0.00%** |
| headroom vs minified | **−8.00%** | — | — | — |
| minification alone vs raw | 7.40% | — | — | — |

### Agent context (n = 11)

| Metric | median | p75 | max |
| --- | --- | --- | --- |
| headroom vs raw | **0.00%** | 28.94% | 72.48% |
| headroom vs minified | −8.67% | — | 51.97% |

Both tokenizers agree to within ~1 percentage point throughout (`json_contributors`:
92.47% on `o200k_base`, 92.48% on `cl100k_base`), so the result is not a tokenizer artifact.

### Per-sample extremes

| Sample | Category | vs raw | vs minified | Router |
| --- | --- | --- | --- | --- |
| `json_contributors` | JSON | **92.47%** | 86.59% | `router:mixed:0.08` |
| `json_users_120` | JSON | 91.14% | 86.85% | `router:mixed:0.10` |
| `json_repos_all` | JSON | 89.81% | 85.34% | `router:mixed:0.11` |
| `agent_trace_needle` | agent | 72.48% | 51.97% | `router:mixed:0.21` |
| `json_out_review_queue` | JSON | 28.45% | **−4.90%** | `router:mixed:0.58` |
| every `code_*` sample | coding | **0.00%** | −0.83 … −10.38% | `router:protected:recent_code` |

---

## What actually happens

The mechanism is **lossless tabular compaction**, and it is a real technique rather than
marketing. A JSON array of uniform records is rewritten from repeated key-value objects
into a schema header plus CSV-like rows:

```
{"items":"[60]{created_at:string,id:int,meta.owner:string,...}
2026-01-01,0,team-a,...
```

The strategy string the library reports is literally `lossless:table(60->len=3500)`.

That explains the entire shape of the result:

- **Compression scales with schema uniformity, not with size.** The router emits a
  heterogeneity score, and it predicts the outcome almost perfectly: `mixed:0.08` →
  92.5% saved; `mixed:0.58` → 28.5% saved; no uniform array → 0%.
- **Code and prose get 0%** because there is no repeated schema to factor out.
- **Nothing is thrown away.** Probe retention was **1.0 across all 35 samples and all
  three headroom variants**, including the 92%-compressed ones.

I also ran both `lossless_only=False` and `lossless_only=True` on the JSON component API.
**They produced identical output on every sample** — the lossy truncation paths
(`max_items_after_crush=15`) never fired with an empty query. The advertised savings on
this data come entirely from the lossless path, which is a stronger result for the project
than the lossy one would have been.

---

## Failure analysis

**Zero transformation errors. Zero probe losses.** The failures are all *failures to
compress*, not failures of correctness — a materially better failure mode.

| Category | Classification | Count |
| --- | --- | --- |
| Code / prose returned unchanged | routing decision (`protected:recent_code`, `protected:analysis_context`) | 12 |
| Text-shaped agent output unchanged | no uniform schema to factor | 7 |
| Output larger than a minified baseline | headroom preserves whitespace that minification removes | 19 |
| Semantic information lost | **none** | **0** |
| Parser failure | **none** | **0** |

The one genuinely negative finding is the third row: for text-shaped content, **you are
better off running `sed` than running headroom** — headroom returns the input unchanged
while trivial minification saves 7–10%.

## Competing explanations tested and falsified

Before concluding CLAIM-E is unsupported, three alternatives were tested
(`outputs/phase3/headroom_supplementary.json`, labelled as supplementary and unable to
change the verdict):

1. *Savings come from older conversation turns, not the current file.* → **Falsified.** A
   six-file multi-turn session: 16,803 → 16,803 tokens, 0.00%.
2. *Context pressure triggers it.* → **Falsified.** `model_limit=20000` against 16,803
   tokens: still 0.00%.
3. *It needs the optional `[code]` extra.* → **Falsified for the library path.** Installed
   the extra; router still returns `protected:recent_code`, 0.00%.

**Named but untested** (out of pre-registered scope): the proxy path, the `wrap <agent>`
path (which also installs Serena semantic code navigation), the MCP server, the
`Kompress-v2-base` prose model, cross-agent memory, and sessions much longer than 17k
tokens. The coding claim may hold on one of those. This experiment does not rule that out,
and says so rather than declaring the claim false.

---

## Answers to the pre-registered questions

**Did headroom reduce tokens?** Yes, on structured JSON: 46.3% median, up to 92.47%.

**Did it beat trivial minification?** **Yes — 28.41% median beyond minified JSON.** This
was the decisive test and headroom passes it. On text it does not: it is 8% *worse* than
`sed`.

**On which input types?** Only where a uniform record schema exists. Machine-generated
API responses, paginated results, and structured tool traces. Not code, not prose, not
line-oriented logs.

**Did quality hold?** Yes. **1.0000 probe retention**, 0 losses in 224 measurements.

**Where did it fail?** Coding context, completely and by design of the router.

**Is the public claim reproduced?** **Partially.** The JSON claim reproduces *as a
capability but not as a typical outcome*: 60–95% is the top quartile of my sample
(p75 = 86.2%), not the median (46.3%). The coding-agent claim (15–20%) did not reproduce
at all on the library path.

### The narrowest claim actually supported

> **On JSON arrays of uniform-schema records, headroom losslessly removes 60–90% of tokens
> versus pretty-printed input and roughly 85% versus minified input, with no measured
> information loss. On heterogeneous JSON it saves ~28% beyond minification. On source
> code, prose, and line-oriented logs it saves nothing and is slightly worse than
> whitespace stripping.**

That is a real, defensible, useful claim — and it is narrower than what is published.

**Strongest finding against:** 0.00% on every one of 12 coding-context samples, against a
published 15–20%, with three competing explanations tested and falsified.

**Strongest finding for:** 1.0 probe retention while removing 86% of tokens versus a
minified baseline. The compression is genuinely lossless, and the `lossless_only` flag was
not even needed to achieve it.

---

## Investment implication — stated separately, deliberately

A technical result is not an investment recommendation. Reading them as the same thing is
the error this whole project is built to avoid. What the experiment supports:

1. **The core technique is real and honestly implemented.** Lossless schema factoring that
   beats minification by 28 points, with zero information loss, is engineering rather than
   prompt-wrapping. Negative control NC-2 (thin wrapper presented as infrastructure) does
   **not** apply here — that question is now answered with measurements.
2. **The addressable surface is narrower than the marketing.** The value is concentrated in
   uniform-schema machine output. That is a real and large category in agent workloads, but
   it is not "everything your agent reads."
3. **The headline is measured against the friendliest baseline.** Quoting 60–95% against
   pretty-printed JSON, when minification alone supplies 31 points of it, is the kind of
   framing a technical investor should test — and it took one afternoon on a laptop.
4. **The 0% coding result is the sharpest founder question**, because coding agents are the
   distribution channel: `wrap claude|codex|cursor|…`. If the library path saves nothing on
   code, the question is what the proxy and `wrap` paths do differently, and whether the
   measured savings there come from compression or from Serena-style retrieval — which is a
   different product with a different moat.

**What this does not tell us:** whether the proxy/wrap product delivers its claim, whether
anyone pays, or whether the technique is defensible. Tabular compaction of JSON is a
well-understood idea; the moat question is unresolved by this experiment and is not
answered by 67,000 GitHub stars.
