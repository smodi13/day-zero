"use client";

import { useState } from "react";
import { usePrefersReducedMotion } from "@/lib/motion";
import type { Dist, HeadroomSample } from "@/lib/research";

/**
 * Per-sample view of the reproduction results.
 *
 * Category and baseline are switchable with plain buttons (keyboard-first), and
 * the same numbers are always rendered as a visible table below the plot, so
 * the chart is never the sole carrier. Medians shown are the pre-registered
 * canonical ones — available only for the RAW and MINIFIED baselines, and never
 * computed in the browser.
 *
 * Motion: dots ease to their new x when the baseline changes, so the reader
 * SEES the distribution slide left as the comparison gets harder rather than
 * being shown two unrelated pictures. Nothing animates from zero: the first
 * paint is the true value.
 */

const CATS = [
  { id: "structured_json", label: "Structured JSON" },
  { id: "coding_context", label: "Coding context" },
  { id: "agent_context", label: "Agent context" },
] as const;

const BASELINES = [
  { id: "MINIFIED", label: "vs MINIFIED", key: "vsMinified" as const,
    note: "the comparison that matters: whitespace minification costs nothing and takes one line" },
  { id: "RAW", label: "vs RAW", key: "vsRaw" as const,
    note: "the marketing comparison: pretty-printed input" },
  { id: "COMPACT_JSON", label: "vs COMPACT_JSON", key: "vsCompact" as const,
    note: "canonical compact JSON re-serialisation — only defined for JSON-parseable samples" },
  { id: "GZIP_B64", label: "GZIP+B64 reference", key: "gzipVsRaw" as const,
    note: "NOT a headroom result — what gzip+base64 itself saves vs raw, shown for calibration. Negative values are base64 inflation." },
] as const;

type BaselineId = (typeof BASELINES)[number]["id"];
type CatId = (typeof CATS)[number]["id"];

const X_MIN = -100;
const X_MAX = 100;
const W = 760;
const PAD = 34;

function x(v: number): number {
  return PAD + ((v - X_MIN) / (X_MAX - X_MIN)) * (W - 2 * PAD);
}

export interface ExplorerProps {
  samples: HeadroomSample[];
  categories: Record<string, { vsRaw: Dist; vsMinified: Dist; minifyOnlyVsRaw: Dist; retention: number }>;
  primaryTokenizer: string;
}

export function HeadroomExplorer(hr: ExplorerProps) {
  const reduced = usePrefersReducedMotion();
  const [cat, setCat] = useState<CatId>("structured_json");
  const [baseline, setBaseline] = useState<BaselineId>("MINIFIED");

  const b = BASELINES.find((bb) => bb.id === baseline)!;
  const samples = hr.samples
    .filter((sm) => sm.category === cat)
    .map((sm) => ({ ...sm, value: sm[b.key] }))
    .filter((sm): sm is HeadroomSample & { value: number } => sm.value !== null)
    .sort((a2, b2) => a2.value - b2.value);

  const dist = hr.categories[cat];
  const median = baseline === "RAW" ? dist.vsRaw.median
    : baseline === "MINIFIED" ? dist.vsMinified.median : null;
  const total = hr.samples.filter((sm) => sm.category === cat).length;

  const rowH = 16;
  const H = 70 + samples.length * rowH;
  const move = reduced ? "none" : "cx 520ms cubic-bezier(.22,.61,.36,1), fill 300ms ease-out";

  return (
    <div className="panel-raised overflow-hidden">
      <div className="grid gap-3 border-b border-paper-line p-3 sm:grid-cols-2 sm:p-4">
        <div role="group" aria-label="Sample category" className="flex flex-wrap gap-2">
          {CATS.map((c) => (
            <button key={c.id} type="button" onClick={() => setCat(c.id)}
                    aria-pressed={c.id === cat} className="ctl">
              {c.label}
            </button>
          ))}
        </div>
        <div role="group" aria-label="Comparison baseline"
             className="flex flex-wrap gap-2 sm:justify-end">
          {BASELINES.map((bb) => (
            <button key={bb.id} type="button" onClick={() => setBaseline(bb.id)}
                    aria-pressed={bb.id === baseline} className="ctl font-mono text-[11.5px]">
              {bb.label}
            </button>
          ))}
        </div>
      </div>

      <div className="px-4 pt-3 sm:px-5" aria-live="polite">
        <p className="meta text-[12.5px]">
          <span className="mono text-ink">{samples.length}</span>
          {samples.length !== total ? ` of ${total}` : ""} samples ·{" "}
          {median !== null ? (
            <>canonical median{" "}
              <span className="mono text-ink">{median.toFixed(2)}%</span> · </>
          ) : (
            <>no pre-registered median for this view — per-sample values only · </>
          )}
          {b.note}
        </p>
      </div>

      <div className="scroll-x px-2 pb-1">
        <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full min-w-[560px]" role="img"
             aria-label={`Token savings per sample, ${CATS.find((c) => c.id === cat)!.label}, ${b.label}. The table below lists every value.`}>
          {[-100, -50, 0, 50, 100].map((t) => (
            <g key={t}>
              <line x1={x(t)} y1={26} x2={x(t)} y2={H - 30}
                    stroke={t === 0 ? "#A9B0AC" : "#E4E7E4"} strokeWidth={t === 0 ? 1.5 : 1} />
              <text x={x(t)} y={16} textAnchor="middle" fill="#878E97"
                    fontFamily="ui-monospace, monospace" fontSize="10">{t}%</text>
            </g>
          ))}
          <text x={x(0)} y={H - 10} textAnchor="middle" fill="#878E97"
                fontFamily="ui-monospace, monospace" fontSize="10">
            ← output grew vs baseline · token savings · output shrank →
          </text>

          {median !== null && (
            <g style={reduced ? undefined : { transition: "transform 520ms cubic-bezier(.22,.61,.36,1)" }}>
              <line x1={x(median)} y1={24} x2={x(median)} y2={H - 30}
                    stroke="#4A7A0F" strokeWidth="1.5" strokeDasharray="5 3" />
              <text x={x(median)} y={H - 34} textAnchor="middle" fill="#35590A"
                    fontFamily="ui-monospace, monospace" fontSize="10">
                median {median.toFixed(2)}%
              </text>
            </g>
          )}

          {samples.map((sm, i) => {
            const cy = 40 + i * rowH;
            const neg = sm.value < 0;
            return (
              <g key={sm.id}>
                <line x1={x(0)} y1={cy} x2={x(sm.value)} y2={cy}
                      stroke={neg ? "#A32B32" : "#4A7A0F"} strokeWidth="1" opacity="0.35"
                      style={reduced ? undefined : { transition: "x2 520ms cubic-bezier(.22,.61,.36,1)" }} />
                <circle cx={x(sm.value)} cy={cy} r="4"
                        fill={neg ? "#A32B32" : "#4A7A0F"}
                        style={{ transition: move }}>
                  <title>{`${sm.id}: ${sm.value.toFixed(2)}%`}</title>
                </circle>
              </g>
            );
          })}
        </svg>
      </div>

      <details className="border-t border-paper-line">
        <summary className="cursor-pointer px-5 py-3 text-[13px] text-ink-dim transition-colors hover:text-exec-deep">
          Per-sample values as a table ({samples.length} rows, tokenizer{" "}
          <span className="mono">{hr.primaryTokenizer}</span>)
        </summary>
        <div className="scroll-x border-t border-paper-line">
          <table className="text-[12.5px]">
            <thead>
              <tr className="border-b border-paper-line bg-paper">
                <th className="px-4 py-2">Sample</th>
                <th className="px-4 py-2">Raw tokens</th>
                <th className="px-4 py-2">Minified</th>
                <th className="px-4 py-2">Headroom</th>
                <th className="px-4 py-2">{b.label}</th>
                <th className="px-4 py-2">Probe retention</th>
              </tr>
            </thead>
            <tbody>
              {samples.map((sm) => (
                <tr key={sm.id} className="border-b border-paper-line last:border-b-0">
                  <td className="mono px-4 py-1.5 text-ink-dim">{sm.id}</td>
                  <td className="mono px-4 py-1.5 text-ink-dim">{sm.raw.toLocaleString()}</td>
                  <td className="mono px-4 py-1.5 text-ink-dim">{sm.minified.toLocaleString()}</td>
                  <td className="mono px-4 py-1.5 text-ink-dim">{sm.headroom.toLocaleString()}</td>
                  <td className="mono px-4 py-1.5 text-ink">{sm.value.toFixed(2)}%</td>
                  <td className="mono px-4 py-1.5 text-ink-dim">{sm.retention.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
