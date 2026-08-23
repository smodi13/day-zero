import type { ReactNode } from "react";

/** Evidence badges. Colour is never the only carrier: each state has a distinct
 *  glyph and an explicit text label, so the meaning survives greyscale, colour
 *  blindness and screen readers. */
const STATES = {
  OBSERVED:          { label: "Observed",      glyph: "●", cls: "text-exec-deep border-exec/35 bg-exec-pale" },
  OBSERVED_AS_CLAIM: { label: "Project claim", glyph: "◐", cls: "text-claim border-claim/35 bg-claim-pale" },
  INFERRED:          { label: "Inferred",      glyph: "◑", cls: "text-claim border-claim/35 bg-claim-pale" },
  UNKNOWN:           { label: "Unknown",       glyph: "○", cls: "text-unknown border-unknown/35 bg-unknown-pale" },
  NOT_FOUND:         { label: "Not found",     glyph: "✕", cls: "text-absent border-absent/35 bg-absent-pale" },
} as const;

export type EvidenceState = keyof typeof STATES;

export function EvidenceBadge({ state, note }: { state: EvidenceState; note?: string }) {
  const s = STATES[state] ?? STATES.UNKNOWN;
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1.5 rounded border px-1.5 py-0.5 font-mono text-[10.5px] uppercase tracking-wider transition-colors duration-200 ${s.cls}`}
      title={note}
    >
      <span aria-hidden="true">{s.glyph}</span>
      {s.label}
    </span>
  );
}

export function Verdict({ label, kind = "signal", sub }: {
  label: string; kind?: "signal" | "mixed" | "neutral"; sub?: ReactNode;
}) {
  const tone = kind === "signal" ? "border-l-exec text-exec-deep"
    : kind === "mixed" ? "border-l-claim text-claim"
    : "border-l-paper-line text-ink";
  return (
    <div className={`panel-raised border-l-4 px-5 py-4 sm:px-6 ${tone}`}>
      <p className="eyebrow">Verdict</p>
      <p className="mt-1 text-xl font-semibold tracking-tight sm:text-2xl">{label}</p>
      {sub ? <div className="meta mt-2 max-w-prose text-ink-soft">{sub}</div> : null}
    </div>
  );
}

export function Stat({ value, label, note }: { value: string; label: string; note?: string }) {
  return (
    <div className="panel card-quiet px-4 py-3">
      <div className="font-mono text-lg tabular-nums tracking-tight text-ink">{value}</div>
      <div className="eyebrow mt-1">{label}</div>
      {note ? <div className="meta mt-1 text-[12px]">{note}</div> : null}
    </div>
  );
}

export function Hash({ value, label }: { value: string; label?: string }) {
  return (
    <span className="mono inline-flex flex-wrap items-baseline gap-x-1.5 break-all text-ink-faint">
      {label ? <span>{label}</span> : null}
      <code className="text-ink-dim">{value}</code>
    </span>
  );
}
