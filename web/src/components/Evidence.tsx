import type { ReactNode } from "react";

/** Evidence badges. Colour is never the only carrier: each state has a distinct
 *  glyph and an explicit text label, so the meaning survives greyscale, colour
 *  blindness and screen readers. */
const STATES = {
  OBSERVED:          { label: "Observed",      glyph: "●", cls: "text-observed border-observed/40 bg-observed/10" },
  OBSERVED_AS_CLAIM: { label: "Project claim", glyph: "◐", cls: "text-claim border-claim/40 bg-claim/10" },
  INFERRED:          { label: "Inferred",      glyph: "◑", cls: "text-inferred border-inferred/40 bg-inferred/10" },
  UNKNOWN:           { label: "Unknown",       glyph: "○", cls: "text-unknown border-unknown/40 bg-unknown/10" },
  NOT_FOUND:         { label: "Not found",     glyph: "✕", cls: "text-absent border-absent/40 bg-absent/10" },
} as const;

export type EvidenceState = keyof typeof STATES;

export function EvidenceBadge({ state, note }: { state: EvidenceState; note?: string }) {
  const s = STATES[state] ?? STATES.UNKNOWN;
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1.5 rounded border px-1.5 py-0.5 font-mono text-[10.5px] uppercase tracking-wider ${s.cls}`}
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
  const tone = kind === "signal" ? "border-signal/40 text-signal"
    : kind === "mixed" ? "border-claim/40 text-claim"
    : "border-line text-text";
  return (
    <div className={`panel-raised border-l-4 ${tone} px-5 py-4 sm:px-6`}>
      <p className="eyebrow">Verdict</p>
      <p className="mt-1 text-xl font-semibold tracking-tight sm:text-2xl">{label}</p>
      {sub ? <div className="meta mt-2 max-w-prose">{sub}</div> : null}
    </div>
  );
}

export function Stat({ value, label, note }: { value: string; label: string; note?: string }) {
  return (
    <div className="panel px-4 py-3">
      <div className="font-mono text-lg tracking-tight text-text">{value}</div>
      <div className="eyebrow mt-1">{label}</div>
      {note ? <div className="meta mt-1 text-[12px]">{note}</div> : null}
    </div>
  );
}

export function Hash({ value, label }: { value: string; label?: string }) {
  return (
    <span className="mono inline-flex items-center gap-1.5 break-all text-faint">
      {label ? <span className="text-faint/70">{label}</span> : null}
      <code className="text-dim">{value}</code>
    </span>
  );
}
