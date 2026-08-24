# Headroom — public-subset sensitivity check

**This is not a replacement experiment.** The pre-registered EXP-1 run stands exactly
as recorded: 35 samples, 1,573,042 bytes, verdict `PARTIALLY_REPRODUCED`. Nothing
here supersedes it and nothing was recomputed to improve it.

One benchmark input — `json_users_120`, a 120-record slice of a raw GitHub
user-profile cache — is withheld from the public repository for third-party privacy
(`experiments/headroom/datasets/withheld/json_users_120.md`). That raises one fair
question, and this document answers it:

> Would a reader working only from the public repository have reached a different
> conclusion?

## Method

The pre-registered analysis was re-applied unchanged to the 34 distributable
samples: the same `dist()` quantile function from `experiments/headroom/analysis.py`,
the same thresholds from `config/experiments/headroom_v1.yaml`, the same claim
definitions and the same verdict rule, over the same canonical per-sample
measurements in `outputs/phase3/headroom_results.json`. No sample was re-tokenised
and no compression was re-run.

As a correctness check, the identical code path reproduces the original 35-sample
figures exactly (46.30 / 28.41 / 0.00 / 0.00 / 1.0000) before the sample is dropped.

Machine-readable output: `outputs/phase3/headroom_public_subset_sensitivity.json`.

## Result

| Measure | Original (35) | Public subset (34) | Δ |
| --- | --- | --- | --- |
| Structured JSON vs raw — median | 46.30% | 46.02% | −0.28 pp |
| Structured JSON vs raw — p25 / p75 | 39.00 / 86.19 | 38.26 / 75.34 | — |
| Structured JSON vs minified — median | 28.41% | 27.05% | −1.36 pp |
| Structured JSON vs minified — p25 / p75 | 14.25 / 80.16 | 14.16 / 64.60 | — |
| Coding context vs raw — median | 0.00% | 0.00% | 0.00 |
| Agent context vs raw — median | 0.00% | 0.00% | 0.00 |
| Probe retention | 1.0000 | 1.0000 | 0.00 |
| Transformation errors | 0 | 0 | 0 |
| Claims supported | A, B, C | A, B, C | none |
| Claims not supported | D, E | D, E | none |
| **Verdict** | **PARTIALLY_REPRODUCED** | **PARTIALLY_REPRODUCED** | **unchanged** |

Only the structured-JSON category loses a sample (12 → 11); the coding and agent
categories are untouched.

## Reading

**No headline conclusion depends on the withheld sample.** The verdict, every
pre-registered claim outcome, probe retention, the error count, and both
zero-savings results are identical. The two medians that move do so by well under
two percentage points, and neither crosses a pre-registered threshold: CLAIM-B's bar
is ≥ 25% vs minified and the public subset returns 27.05%, still supported;
CLAIM-D's band is 60–95% vs raw and the public subset returns 46.02%, still
unsupported.

The one visible effect is on the upper tail: p75 vs raw falls from 86.19 to 75.34
and p75 vs minified from 80.16 to 64.60. The withheld sample was a
highly-compressible profile record set, so removing it trims the best-case end of
the structured-JSON distribution. That makes the public subset a slightly
*less* flattering picture of headroom than the original run, not a more flattering
one — worth stating plainly, since the direction of a convenient omission is exactly
what a sceptical reader should check.

**The finding this experiment is known for is unaffected.** "The baseline is part of
the claim" rests on the gap between the vs-raw and vs-minified medians, and that gap
is 17.89 pp in the original and 18.97 pp in the public subset.
