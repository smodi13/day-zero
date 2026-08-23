# DAY ZERO — Accepted Work Unit

## 1. Where this comes from

Shruti Gandhi, *Loop to Graph Engineering for Measuring AI Spend* (insights.array.vc,
2026-07-22), proposes **Accepted Work Units (AWU)** as the unit of measurement for agent
work: each loop produces measurable, accept/reject-able output, and the metric that
matters is **cost per accepted work unit**, not tokens consumed. The post names the
failure modes that make this necessary — the *Ralph Wiggum failure* (an agent declaring
completion without hard gates), *goal drift*, and *flawed loop accumulation* (bad
assumptions propagating while review debt and token waste pile up silently).

DAY ZERO is itself a loop. It should be measured with its own customer's metric.

## 2. The definition

> **One Accepted Work Unit = one founder or team lead that survives analyst review and is
> genuinely worth an introduction.**

Not a profile processed. Not a signal ingested. Not a candidate surfaced. **Accepted.**

The accept/reject gate is the analyst, and the gate is *hard*: a lead is accepted only
when the analyst would put their own name on the introduction.

## 3. The funnel

```
raw signals ingested
   ↓  (channel-level, deterministic)
resolved entities                    ← identity resolution, ER-1
   ↓
potentially relevant builders        ← area filter + BUILD/DEPTH signals present
   ↓
analyst review queue                 ← cross-source convergence achieved
   ↓
diligence-ready builders             ← identity HIGH, artifact readable, questions formed
   ↓
ACCEPTED founder intros (AWU)        ← analyst would put their name on it
```

Every stage records: entered, exited, rejected, and **the reason for rejection**.
Rejection reasons are the most valuable data the system produces — they are the only way
to distinguish "the channel is bad" from "the filter is bad" from "the week was quiet."

## 4. Metrics (defined now, deliberately NOT optimized in Phase 1)

| Metric | Definition | Why it matters |
| --- | --- | --- |
| `raw_signals_processed` | Signals ingested per cycle | Denominator. Never a headline number — that is volume theater. |
| `candidate_yield` | potentially-relevant ÷ resolved entities | Is the area filter working? |
| `analyst_acceptance_rate` | AWU ÷ analyst review queue | The core quality metric. A rate near 1.0 means the queue is too small; near 0.05 means the system is wasting human time. |
| `false_positive_rate` | rejected-at-analyst ÷ analyst review queue, by reason | Which failure mode dominates |
| `evidence_completeness` | % of accepted leads with ≥2 independent channels and identity HIGH | Guards against a Weekly 3 built on thin evidence |
| `human_review_time_per_AWU` | Minutes of analyst time ÷ AWU | The real cost. Almost certainly dominates API cost. |
| `source_yield` | AWU attributable to each channel ÷ that channel's cost | Which channels to keep, which to cut |
| `cost_per_AWU` | (API cost + compute + analyst time × loaded rate) ÷ AWU | Array's own metric, applied to us |
| `duplicate_rate` | Entities already in the watchlist resurfaced as new | Measures memory, not discovery |
| `stale_signal_rate` | Signals whose `observed_at` is >90 days old at surfacing | Measures latency |
| `state_transition_recall` | Known transitions detected ÷ known transitions that occurred | Measured against the backtest cohort |

## 5. What "accepted" must never mean

Borrowing the failure modes from the source post, mapped onto sourcing:

- **Ralph Wiggum failure:** the system declares a lead "ready" because every field is
  populated. Populated ≠ verified. The hard gate is *identity resolved + artifact opened
  + a question formed*, not field completeness.
- **Goal drift:** the acceptance bar quietly relaxes to keep the Weekly 3 at three. The
  countermeasure is rule 1 of `weekly3_framework.md` — return fewer.
- **Flawed loop accumulation:** the same weak channel keeps producing the same weak leads
  and nobody notices because the funnel numbers look healthy. The countermeasure is
  `source_yield` measured per channel and reviewed.

## 6. An honest baseline to beat

From the audited X engine's own broad run (`existing_x_engine_audit.md` §6):
1,279 returned Post resources → 153 analyst-adjudicated projects, at ≈USD 6.40 of
retrieval — roughly **USD 0.042 per project, before any human time.**

But "project" there is not "accepted founder intro." If even 3 of those 153 would have
survived a DAY ZERO analyst review, the real figure is ≈**USD 2.13 per AWU in API cost**
— and if each of the 153 took two minutes to adjudicate, that is 5.1 hours of human time,
or **~1.7 hours per AWU.**

**That is the number DAY ZERO has to beat, and it is a human-time number, not an API
number.** Any Phase 2 optimization that reduces API spend while increasing analyst
review time is a regression. This is stated now so it cannot be quietly forgotten later.

## 7. Phase 1 scope

Phase 1 **defines** these metrics and instruments nothing. Optimizing a metric before the
ontology is validated is how a sourcing tool becomes a volume machine.
