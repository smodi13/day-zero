"use client";

import { useState } from "react";
import { useDrawOnScroll, usePrefersReducedMotion, useTweenedNumber } from "@/lib/motion";

/**
 * "The baseline is part of the claim" — the single most important finding of the
 * reproduction, built as an interaction rather than a sentence.
 *
 * Three steps over the SAME measured data: the bar never changes length because
 * the tokens never changed. What moves is the zero point — the thing the saving
 * is measured *against*. That is the whole argument, and making the bar hold
 * still while the comparison slides is the clearest way to say it.
 *
 * Every number is canonical and passed in from the export; the static HTML
 * renders the final figures, and the tween only smooths transitions between
 * steps the reader chooses.
 */

export interface BaselineStep {
  id: string;
  control: string;
  savings: number;
  caption: string;
}

export function BaselineReveal({
  vsRaw, minifyOnly, vsMinified,
}: { vsRaw: number; minifyOnly: number; vsMinified: number }) {
  const reduced = usePrefersReducedMotion();
  const [ref, draw] = useDrawOnScroll<HTMLDivElement>();
  const [step, setStep] = useState(0);

  const STEPS: BaselineStep[] = [
    {
      id: "raw",
      control: "vs RAW (pretty-printed)",
      savings: vsRaw,
      caption: "The published comparison. Measured against pretty-printed JSON, the median saving is large.",
    },
    {
      id: "split",
      control: "vs RAW — split by cause",
      savings: vsRaw,
      caption: `Of that ${vsRaw.toFixed(2)}%, minification alone — stripping whitespace, one line of code, no library — accounts for ${minifyOnly.toFixed(2)}%.`,
    },
    {
      id: "min",
      control: "vs MINIFIED",
      savings: vsMinified,
      caption: `Against a baseline that costs nothing, headroom's own contribution is ${vsMinified.toFixed(2)}% — real, lossless, and much smaller than the headline.`,
    },
  ];

  const active = STEPS[step];
  const shown = useTweenedNumber(active.savings, reduced ? 0 : 520);
  const minifyWidth = useTweenedNumber(step === 0 ? 0 : minifyOnly, reduced ? 0 : 620);

  return (
    <div ref={ref} className="panel-raised overflow-hidden">
      <div className="flex flex-wrap gap-2 border-b border-paper-line p-3 sm:p-4"
           role="group" aria-label="Baseline comparison step">
        {STEPS.map((s, i) => (
          <button key={s.id} type="button" onClick={() => setStep(i)}
                  aria-pressed={i === step} className="ctl">
            {i + 1}. {s.control}
          </button>
        ))}
      </div>

      <div className="p-5 sm:p-7">
        <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
          <span className="font-mono text-4xl font-semibold tabular-nums tracking-tight text-exec-deep sm:text-5xl">
            {shown.toFixed(2)}%
          </span>
          <span className="meta">median token saving · {active.control}</span>
        </div>

        {/* The measurement itself. Full bar = the raw token count. */}
        <div className="mt-6" aria-hidden="true">
          <div className="relative h-11 overflow-hidden rounded border border-paper-line bg-paper">
            {/* portion attributable to trivial minification */}
            <div className="bar-fill absolute inset-y-0 left-0 bg-unknown/25"
                 style={{ width: `${draw ? minifyWidth : 0}%` }} />
            {/* total saving vs raw — the bar that does not move between steps 1 and 2 */}
            <div className="bar-fill absolute inset-y-0 border-r-2 border-exec bg-exec/15"
                 style={{ left: 0, width: `${draw ? (step === 2 ? minifyOnly + (100 - minifyOnly) * (vsMinified / 100) : vsRaw) : 0}%` }} />
            {step > 0 && (
              <div className="bar-fill absolute inset-y-0 w-px bg-unknown"
                   style={{ left: `${minifyWidth}%` }} />
            )}
            <span className="absolute right-3 top-1/2 -translate-y-1/2 font-mono text-[11px] text-ink-dim">
              raw tokens
            </span>
          </div>
          <div className="mono mt-2 flex flex-wrap gap-x-5 gap-y-1 text-[11px] text-ink-dim">
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-block h-2 w-3 rounded-sm bg-unknown/25 ring-1 ring-unknown/40" />
              whitespace minification — free
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="inline-block h-2 w-3 rounded-sm bg-exec/25 ring-1 ring-exec/50" />
              headroom&rsquo;s own contribution
            </span>
          </div>
        </div>

        <p className="body mt-5 max-w-prose">{active.caption}</p>

        {/* Static, always-present statement of all three canonical figures. */}
        <dl className="mono mt-5 grid gap-x-8 gap-y-1 border-t border-paper-line pt-4 text-[12px] sm:grid-cols-3">
          {[["vs raw", vsRaw], ["minification alone", minifyOnly], ["vs minified", vsMinified]].map(
            ([l, v]) => (
              <div key={l as string} className="flex items-baseline justify-between gap-3">
                <dt className="text-ink-dim">{l as string}</dt>
                <dd className="text-ink">{(v as number).toFixed(2)}%</dd>
              </div>
            ),
          )}
        </dl>
      </div>
    </div>
  );
}
