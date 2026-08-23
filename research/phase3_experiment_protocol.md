# EXP-1 — Pre-Registered Reproduction Protocol

**Status: PRE-REGISTERED. No result has been generated at the time this document is
committed.** The protocol, datasets, baselines, metrics and verdict thresholds are all
fixed before measurement, and the commit that contains them precedes the commit that
contains any result.

Machine-readable version: `config/experiments/headroom_v1.yaml`
Dataset manifest: `experiments/headroom/datasets/manifest.json`
(`manifest_sha256: c16472c28c06194bfc0ffcf57c0acc77363847866835014e6a19b4680f3622bf`)

---

## 1. The claim, exactly as published

Two published surfaces state the claim, and **they do not agree with each other**. Both
are recorded verbatim.

**CLAIM-SRC-A** — GitHub repository description, `headroomlabs-ai/headroom`, accessed
2026-08-23:

> "Compress tool outputs, logs, files, and RAG chunks before they reach the LLM.
> **20% fewer tokens for coding agents, 60-95% fewer tokens for JSON, same answers.**
> Library, proxy, MCP server."

**CLAIM-SRC-B** — `README.md`, branch `main`, accessed 2026-08-23:

> "**60–95% fewer tokens (for JSON data), 15-20% fewer tokens (for coding agents)** ·
> library · proxy · MCP · content-aware compressors · local-first · reversible"

**CLAIM-SRC-C** — README body:

> "Same answers, fraction of the tokens."

The coding-agent figure is **20%** in one place and **15-20%** in the other. That
discrepancy is recorded, not resolved in the project's favour: the protocol tests against
the *lower* bound (15%) for CLAIM-E and reports where the result falls relative to both.

### Author-disclosed context (recorded, not tested)

The README also publishes a benchmark table claiming savings of 92% / 92% / 73% / 47% on
four named agent workloads, and accuracy figures on GSM8K, TruthfulQA, SQuAD v2 and BFCL.
Those are the author's own measurements on the author's own workloads. **This experiment
does not attempt to reproduce them** — it tests the headline claim on datasets the author
did not choose, which is the more informative test.

### What the project itself discloses about mechanism

- The architecture is `ContentRouter` → `SmartCrusher` (JSON) / `CodeCompressor` (AST) /
  `Kompress-v2-base` (prose, a HuggingFace model).
- Compression is described as **reversible** via CCR: originals are cached locally and the
  model can call `headroom_retrieve`.
- The package is `headroom-ai`, Apache-2.0, tested here at version **0.36.5**.

## 2. Decomposition — five independently testable claims

Success on one never implies success on another. This is the whole reason the claim is
split.

| ID | Statement | Applies to |
| --- | --- | --- |
| **CLAIM-A** | Reduces tokens relative to raw input | all categories |
| **CLAIM-B** | Reduction **exceeds trivial minification** | structured JSON |
| **CLAIM-C** | Task-relevant information survives ("same answers") | all categories |
| **CLAIM-D** | JSON reduction reaches 60–95% | structured JSON |
| **CLAIM-E** | Coding-agent reduction reaches 15–20% | coding context |

**CLAIM-B is the decisive one.** Pretty-printed JSON is largely whitespace. A headline
measured against pretty JSON can be numerically large while the compressor contributes
almost nothing. Any protocol that compares only against raw input is not testing the
interesting part of the claim.

## 3. Two entry points, both tested

Discovered during protocol design and recorded **before** results, because it materially
affects what "headroom saves N%" means:

- `compress()` **protects `user`-role messages** and routes tool outputs. Content presented
  as a user message is returned unchanged (`router:protected:user_message`). The public
  claim is about tool outputs, so the test must present content that way, or it measures
  the wrong thing and unfairly reports zero.
- `SmartCrusher.crush()` exposes a `lossless_only` flag, so the JSON component can be
  measured in both its default and its strict-lossless configuration.

| Path | Entry point | What it measures |
| --- | --- | --- |
| **PATH-A** | `headroom.compress(messages, model_limit=200000)` | The product claim, on realistic agent message sequences |
| **PATH-B** | `headroom.SmartCrusher().crush(content, lossless_only=<bool>)` | The JSON component claim, on raw content |

## 4. Baselines

| ID | Transform |
| --- | --- |
| RAW | The input exactly as the source tool produces it |
| MINIFIED | Trivial whitespace removal (`json.dumps(separators=(',',':'))`; collapse blank lines and space runs for text) |
| COMPACT_JSON | Standard compact JSON — identical to MINIFIED for JSON, recorded separately so the JSON comparison is explicit |
| GZIP_B64 | gzip + base64. **A control, not a serious alternative** — it shows why byte-level compression is the wrong frame for token counting |
| HEADROOM | The system under test |

**Primary comparison: HEADROOM vs MINIFIED.**

## 5. Datasets — fixed before measurement

**35 samples · 1,573,042 bytes · manifest committed with a SHA-256 per sample.**

| Category | Samples | What |
| --- | --- | --- |
| `structured_json` | 12 | Real public GitHub API responses collected in Phase 2; DAY ZERO's own canonical JSON outputs |
| `coding_context` | 12 | Source files from permissively licensed public repos (Daft Apache-2.0, agentsight MIT, uccl Apache-2.0, sandlock Apache-2.0), DAY ZERO's own source, and a git diff |
| `agent_context` | 11 | pytest output, git log / ls-files, CLI diagnostics, `pip list`, directory listings, and four synthetic needle-in-haystack cases (FATAL log line, Python traceback, paginated API output, agent tool trace) |

All samples are public data, self-produced output, or files from permissively licensed
public repositories. No private data, nothing behind authentication, no personal data.
Provenance is recorded per sample.

## 6. Tokenizers

The published claim names no tokenizer, so it is tested against two families and reported
separately for each: **`o200k_base`** (GPT-4o / o-series) and **`cl100k_base`** (GPT-4 /
GPT-3.5). No universal token-saving claim will be made from a single tokenizer.

## 7. Quality test — CLAIM-C

**"Same answers" is not judged by the compression system, and not judged by an LLM.**

Each sample carries **3–6 ground-truth probes** defined in `build_datasets.py` *before*
any compression runs: exact strings a downstream task would need — an error code
(`ENOSPC-4711`), a specific field value, the last item in a paginated list
(`SKU-13-024`), a function name, a specific commit. The builder asserts every probe is
present in the original; a sample whose probes are missing is a malformed sample and fails
the build.

After compression, each probe is scored **retained (1)** or **lost (0)**.

**Stated limitation, pre-registered:** presence is necessary but not sufficient. A model
might fail to *use* a retained value, and a value dropped by headroom might still be
recoverable through its CCR `headroom_retrieve` tool at the cost of an extra round trip.
This test measures **information preservation in the delivered context** — the part that is
objective, deterministic and free. It is **not** a full end-to-end task-accuracy benchmark,
and the report will say so rather than overclaiming.

**LLM calls: 0. Paid resources: none.** If a paid model were ever required, the protocol
requires stopping and asking for approval before spending.

## 8. Metrics

`token_reduction_vs_raw` · `token_reduction_vs_minified` · `token_reduction_vs_compact_json`
· `probe_retention_rate` · `probe_retention_delta_vs_minified` · `transformation_error_rate`
· `compression_time_ms` · per-category breakdown · per-tokenizer breakdown.

Reported as distributions — **median, p25, p75, min, max, n** — never as a mean alone, and
**never combined into a single score**.

## 9. Pre-registered verdicts

Thresholds are fixed here and are **not** moved after results are seen.

**REPRODUCED** — all of:
- median `token_reduction_vs_minified` ≥ **25%** on structured JSON
- median `token_reduction_vs_raw` inside the published **60–95%** band on structured JSON
- median `token_reduction_vs_raw` ≥ **15%** on coding context
- overall `probe_retention_rate` ≥ **0.95**

**PARTIALLY REPRODUCED** — at least one of CLAIM-A…E supported at its threshold and at
least one failing at its threshold.

**NOT REPRODUCED** — median `token_reduction_vs_minified` < **5%** on structured JSON, OR
overall `probe_retention_rate` < **0.80**.

**INCONCLUSIVE** — the software could not be run as documented, or the minimum sample
count per category could not be reached.

## 10. Environment

```
Apple M1 · arm64 · 8 GB RAM · macOS
Python 3.14.3 (isolated venv)
headroom-ai 0.36.5 (cp310-abi3-macosx_11_0_arm64 wheel)
tiktoken 0.14.0
No GPU. No paid API. No network access during measurement.
```

`ast-grep-cli`, `pydantic`, `httpx` and `rich` are installed as headroom dependencies.
The exact resolved environment is captured in the results file at run time.

## 11. What this protocol deliberately does not do

- It does not reproduce the author's own benchmark table (§1) — testing on datasets the
  author did not choose is the more informative experiment.
- It does not measure end-to-end task accuracy with a live model (no budget was spent).
- It does not test the proxy, the MCP server, the `wrap` integrations, the cross-agent
  memory, or the `Kompress-v2-base` prose model, which requires a HuggingFace download that
  8 GB of RAM makes unattractive. **Scope is the library-level compression claim only**,
  and the report will state that boundary.
- It does not convert a technical result into an investment recommendation. That inference
  is made separately and explicitly.
