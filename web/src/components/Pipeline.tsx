"use client";

import { usePrefersReducedMotion } from "@/lib/motion";

const STEPS = [
  { id: "source",    n: "01", label: "Source",    q: "Can it find technical builders from public artifacts, without ranking people by prestige or popularity?" },
  { id: "verify",    n: "02", label: "Verify",    q: "Can it reproduce a technical claim against a meaningful baseline, instead of accepting marketing language?" },
  { id: "diligence", n: "03", label: "Diligence", q: "Can it read architecture and code deeply enough to understand the real tradeoffs?" },
  { id: "learn",     n: "04", label: "Learn",     q: "When its own rules fail, does it say so — and improve without rewriting prior results?" },
];

/**
 * The system diagram. Every label and every edge is present in the static SVG;
 * motion only animates a dash offset on the return path. With JS off or reduced
 * motion on, the whole flow is still legible.
 */
export function Pipeline() {
  const reduced = usePrefersReducedMotion();
  return (
    <div className="panel overflow-hidden">
      <div className="scroll-x">
        <svg viewBox="0 0 900 200" className="h-auto w-full min-w-[560px]" role="img"
             aria-label="DAY ZERO pipeline: Source feeds Verify, which feeds Diligence. Learn takes what fails and feeds it back into Source.">
          <defs>
            <marker id="dz-arrow" viewBox="0 0 10 10" refX="9" refY="5"
                    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" fill="#2f7a5e" />
            </marker>
          </defs>

          {[0, 1, 2].map((i) => {
            const x = 40 + i * 290;
            const s = STEPS[i];
            return (
              <g key={s.id}>
                <rect x={x} y="40" width="220" height="66" rx="4"
                      fill="#161a21" stroke="#222833" />
                <text x={x + 16} y="66" fill="#67707f"
                      fontFamily="ui-monospace, monospace" fontSize="11" letterSpacing="1.6">
                  {s.n}
                </text>
                <text x={x + 16} y="90" fill="#e6e9ee"
                      fontFamily="ui-sans-serif, system-ui" fontSize="19" fontWeight="600">
                  {s.label}
                </text>
                {i < 2 && (
                  <line x1={x + 224} y1="73" x2={x + 286} y2="73"
                        stroke="#2f7a5e" strokeWidth="1.5" markerEnd="url(#dz-arrow)" />
                )}
              </g>
            );
          })}

          {/* LEARN: the return path. Failure re-enters sourcing. */}
          <rect x="330" y="146" width="220" height="40" rx="4"
                fill="#111419" stroke="#2f7a5e" strokeDasharray="3 3" />
          <text x="346" y="171" fill="#5fd6a4"
                fontFamily="ui-sans-serif, system-ui" fontSize="14" fontWeight="600">
            04 · Learn
          </text>
          <path d="M620 106 L620 166 L556 166" fill="none" stroke="#2f7a5e"
                strokeWidth="1.5" strokeDasharray="4 4" />
          <path d="M330 166 L150 166 L150 110" fill="none" stroke="#2f7a5e"
                strokeWidth="1.5" markerEnd="url(#dz-arrow)"
                pathLength={1}
                className={reduced ? undefined : "dz-trace"} />
        </svg>
      </div>

      <ol className="grid gap-px border-t border-line bg-line sm:grid-cols-2 lg:grid-cols-4">
        {STEPS.map((s) => (
          <li key={s.id} className="bg-surface px-4 py-4">
            <p className="eyebrow">{s.n} · {s.label}</p>
            <p className="meta mt-2">{s.q}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
