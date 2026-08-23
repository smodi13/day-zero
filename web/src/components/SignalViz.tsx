"use client";

import { useState } from "react";
import { useDrawOnScroll, usePrefersReducedMotion } from "@/lib/motion";
import type { AvcRow } from "@/lib/research";

/**
 * Identity resolution, shown as states rather than a funnel of losses.
 *
 * The bars are deliberately NOT nested inside one another: 267 → 166 → 1 is not
 * a story about 165 people being discarded, it is three different measurements
 * of the same population. Each bar is drawn against the full universe and
 * labelled with what it counts, so the reader cannot read attrition into it.
 */
export function IdentityStates({
  total, mergeable, mergeablePct, xLinkable, xPct,
}: {
  total: number; mergeable: number; mergeablePct: number;
  xLinkable: number; xPct: number;
}) {
  const reduced = usePrefersReducedMotion();
  const [ref, on] = useDrawOnScroll<HTMLDivElement>();

  const bars = [
    { label: "Live identities collected", n: total, pct: 100,
      note: "the Phase 2 universe, unchanged", tone: "bg-ink/70" },
    { label: "Mergeable under conservative rules", n: mergeable, pct: mergeablePct,
      note: "resolvable without fuzzy matching — the assumption that failed", tone: "bg-exec/70" },
    { label: "Verifiably X-linkable", n: xLinkable, pct: xPct,
      note: "the measurement that did not improve", tone: "bg-absent/70" },
  ];

  return (
    <div ref={ref} className="panel p-5">
      <p className="eyebrow">Three measurements of one population</p>
      <div className="mt-4 grid gap-4">
        {bars.map((b, i) => (
          <div key={b.label}>
            <div className="flex flex-wrap items-baseline justify-between gap-x-3">
              <span className="text-[13.5px] font-medium text-ink">{b.label}</span>
              <span className="mono text-[12.5px] text-ink">
                {b.n.toLocaleString()}
                <span className="text-ink-faint"> · {b.pct.toFixed(2)}%</span>
              </span>
            </div>
            <div className="mt-1.5 h-2.5 overflow-hidden rounded-full bg-paper-soft ring-1 ring-paper-line">
              <div className={`bar-fill h-full rounded-full ${b.tone}`}
                   style={{
                     width: on ? `${Math.max(b.pct, 0.6)}%` : "0%",
                     transitionDelay: reduced ? undefined : `${i * 160}ms`,
                   }} />
            </div>
            <p className="meta mt-1 text-[12px]">{b.note}</p>
          </div>
        ))}
      </div>
      <p className="meta mt-4 border-t border-paper-line pt-3 text-[12.5px]">
        These are identity-resolution states, not candidate quality. Nobody was
        &ldquo;lost&rdquo; between the bars — the same people are counted three times, under
        three different evidentiary standards.
      </p>
    </div>
  );
}

/**
 * Attention and construction as two independent axes.
 *
 * Log-scaled on both axes because the spread is four orders of magnitude, and
 * plotted with NO diagonal, NO quadrant labels and NO ranking — a point being
 * up-and-left is not a verdict on anyone. Hovering or focusing a point reveals
 * its two raw measurements and nothing else.
 */
export function AttentionConstruction({ high, low }: { high: AvcRow[]; low: AvcRow[] }) {
  const reduced = usePrefersReducedMotion();
  const [sel, setSel] = useState<string | null>(null);

  const rows = [
    ...high.map((r) => ({ ...r, band: "attention" as const })),
    ...low.map((r) => ({ ...r, band: "construction" as const })),
  ];

  const W = 720, H = 330, PAD = 52;
  const lx = (v: number) => Math.log10(Math.max(v, 1));
  const maxStars = Math.max(...rows.map((r) => lx(r.stars)));
  const maxCommits = Math.max(...rows.map((r) => lx(r.top_contributions)));
  const px = (v: number) => PAD + (lx(v) / maxCommits) * (W - PAD - 28);
  const py = (v: number) => H - PAD - (lx(v) / maxStars) * (H - PAD - 26);

  const active = rows.find((r) => r.repo === sel) ?? null;

  return (
    <div className="panel-raised overflow-hidden">
      <div className="scroll-x px-2 pt-3">
        <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full min-w-[520px]" role="img"
             aria-label="Attention (stars) against construction (commits by the owning contributor), both log-scaled. Every plotted repository is also listed in the table below.">
          {/* axes */}
          <line x1={PAD} y1={H - PAD} x2={W - 16} y2={H - PAD} stroke="#DFE3E1" />
          <line x1={PAD} y1={16} x2={PAD} y2={H - PAD} stroke="#DFE3E1" />
          {[1, 10, 100, 1000].map((t) => (
            <g key={`x${t}`}>
              <line x1={px(t)} y1={H - PAD} x2={px(t)} y2={H - PAD + 4} stroke="#A9B0AC" />
              <text x={px(t)} y={H - PAD + 16} fontSize="10" fill="#878E97" textAnchor="middle"
                    fontFamily="ui-monospace, monospace">{t.toLocaleString()}</text>
            </g>
          ))}
          {[10, 1000, 100000].map((t) => (
            <g key={`y${t}`}>
              <line x1={PAD - 4} y1={py(t)} x2={PAD} y2={py(t)} stroke="#A9B0AC" />
              <text x={PAD - 8} y={py(t) + 3.5} fontSize="10" fill="#878E97" textAnchor="end"
                    fontFamily="ui-monospace, monospace">{t.toLocaleString()}</text>
            </g>
          ))}
          <text x={W / 2} y={H - 6} fontSize="10.5" fill="#5C646E" textAnchor="middle"
                fontFamily="ui-monospace, monospace" letterSpacing="0.08em">
            CONSTRUCTION — commits by the owning contributor (log)
          </text>
          <text x={14} y={H / 2} fontSize="10.5" fill="#5C646E" textAnchor="middle"
                fontFamily="ui-monospace, monospace" letterSpacing="0.08em"
                transform={`rotate(-90 14 ${H / 2})`}>
            ATTENTION — stars (log)
          </text>

          {rows.map((r) => {
            const isActive = active?.repo === r.repo;
            return (
              <g key={r.repo}>
                <circle
                  cx={px(r.top_contributions)} cy={py(r.stars)}
                  r={isActive ? 8 : 5.5}
                  fill={r.band === "attention" ? "#8A6209" : "#4A7A0F"}
                  fillOpacity={isActive ? 0.9 : 0.55}
                  stroke={r.band === "attention" ? "#8A6209" : "#4A7A0F"}
                  strokeWidth="1.2"
                  /* The dots are the measurement, so they are never scaled in
                     from zero: a missed observer or a frozen transition would
                     leave the plot empty. Their entrance comes from the parent
                     Reveal wrapper, which only moves a transform on an already
                     opaque element. Only the hover response animates here. */
                  style={reduced ? undefined : {
                    transition: "r 180ms ease-out, fill-opacity 180ms ease-out",
                  }}
                />
                <title>{`${r.repo}: ${r.stars.toLocaleString()} stars, ${r.top_contributions.toLocaleString()} commits`}</title>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Every point is reachable by keyboard from this list, and the list is
          the accessible equivalent of the plot. */}
      <div className="border-t border-paper-line p-3 sm:p-4">
        <p className="eyebrow mb-2">Hover or focus a repository</p>
        <div className="flex flex-wrap gap-1.5">
          {rows.map((r) => (
            <button key={r.repo} type="button"
                    onMouseEnter={() => setSel(r.repo)} onMouseLeave={() => setSel(null)}
                    onFocus={() => setSel(r.repo)} onBlur={() => setSel(null)}
                    aria-pressed={sel === r.repo}
                    className="ctl mono break-all text-[11.5px]">
              {r.repo}
            </button>
          ))}
        </div>
        <div className="mt-3 min-h-[3.25rem] rounded border border-paper-line bg-paper px-4 py-2.5"
             aria-live="polite">
          {active ? (
            <p className="mono text-[12.5px] text-ink">
              {active.repo} — <span className="text-claim">{active.stars.toLocaleString()} stars</span>
              {" · "}<span className="text-exec-deep">{active.top_contributions.toLocaleString()} commits</span>
              {active.stars_per_commit !== null && (
                <span className="text-ink-dim"> · {active.stars_per_commit.toLocaleString()} stars per commit</span>
              )}
            </p>
          ) : (
            <p className="meta text-[12.5px]">
              Two independent measurements. Neither axis is a judgment about a builder, and
              no combined score exists anywhere in the system.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
