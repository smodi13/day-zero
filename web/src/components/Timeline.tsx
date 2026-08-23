"use client";

import { useDrawOnScroll, usePrefersReducedMotion } from "@/lib/motion";

/**
 * The methodology sequence, drawn so the FREEZE-BEFORE-RESULT ordering is the
 * thing you see first.
 *
 * Two node kinds alternate deliberately: a LOCK (rules or a cohort, hashed and
 * committed) and a RESULT (what happened when it was run). The rail between
 * them draws downward as the section enters view, in commit order, which is the
 * whole epistemic argument — the hash existed before the outcome did.
 *
 * It is explicitly not a success staircase: the two failure nodes carry their
 * own tone and the sequence ends on "what broke next", not on a win.
 */

export interface Step {
  kind: "lock" | "result" | "failure";
  label: string;
  detail: string;
  hash?: string;
}

export function Timeline({ steps }: { steps: Step[] }) {
  const reduced = usePrefersReducedMotion();
  const [ref, on] = useDrawOnScroll<HTMLOListElement>();

  return (
    <ol ref={ref} className="relative grid max-w-3xl gap-0">
      {steps.map((s, i) => {
        const last = i === steps.length - 1;
        const delay = 120 + i * 130;
        const tone =
          s.kind === "lock" ? "border-ink bg-paper-card"
          : s.kind === "failure" ? "border-absent bg-absent-pale"
          : "border-exec bg-exec-pale";
        return (
          <li key={s.label} className="relative flex gap-4 pb-7 last:pb-0">
            {/* rail + node */}
            <div className="relative flex w-4 shrink-0 flex-col items-center">
              <span
                className={`z-10 mt-1 h-4 w-4 shrink-0 rounded-full border-[3px] ring-4 ring-paper ${tone}`}
                style={reduced ? undefined : {
                  transform: on ? "scale(1)" : "scale(.4)",
                  opacity: on ? 1 : 0.25,
                  transition: `transform 380ms cubic-bezier(.22,.61,.36,1) ${delay}ms, opacity 380ms ease-out ${delay}ms`,
                }}
                aria-hidden="true"
              />
              {!last && (
                <span aria-hidden="true" className="relative mt-1 w-0.5 flex-1 rounded bg-paper-line">
                  <span className="absolute inset-x-0 top-0 rounded bg-exec/55"
                        style={{
                          height: on ? "100%" : "0%",
                          transition: reduced ? "none"
                            : `height 420ms cubic-bezier(.22,.61,.36,1) ${delay + 120}ms`,
                        }} />
                </span>
              )}
            </div>

            {/* content */}
            <div className="min-w-0 pb-1"
                 style={reduced ? undefined : {
                   transform: on ? "none" : "translateY(10px)",
                   transition: `transform 520ms cubic-bezier(.22,.61,.36,1) ${delay + 60}ms`,
                 }}>
              <p className="flex flex-wrap items-center gap-x-2 gap-y-1">
                <span className={`mono rounded border px-1.5 py-0.5 text-[10px] uppercase tracking-widest ${
                  s.kind === "lock" ? "border-ink/25 bg-paper text-ink"
                  : s.kind === "failure" ? "border-absent/35 bg-absent-pale text-absent"
                  : "border-exec/35 bg-exec-pale text-exec-deep"}`}>
                  {s.kind === "lock" ? "🔒 locked" : s.kind === "failure" ? "✕ failure" : "● result"}
                </span>
                <span className="text-[14px] font-semibold text-ink">{s.label}</span>
              </p>
              <p className="meta mt-1 text-[13px]">{s.detail}</p>
              {s.hash ? (
                <p className="mono mt-1.5 break-all text-[11px] text-ink-faint">{s.hash}</p>
              ) : null}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
