"use client";

import { usePointerOffset } from "@/lib/motion";

/**
 * The system diagram: what DAY ZERO actually does, drawn as a workflow.
 *
 *   public artifacts → a builder/team → an evidence gate → the intro queue,
 *   which then splits into the two kinds of work the project claims to do
 *   (reproduce a claim / read an architecture), with LEARN returning a failed
 *   rule to sourcing.
 *
 * STATIC-FIRST, and this is the whole design constraint. Every node, edge and
 * label is rendered opaque in the server HTML. The animation is a highlight
 * that sweeps the stages in order, and it lives *entirely* on decorative accent
 * overlays whose base state is transparent. If the animation never advances —
 * backgrounded tab, frozen currentTime, blocked JS, reduced motion — what
 * remains is the complete graphite diagram with every label legible. Nothing a
 * reader needs is ever gated on motion.
 *
 * The one JS-dependent effect is a 4px pointer parallax between the rails and
 * the node layer, disabled on touch and under reduced motion.
 */

const ART = [
  { x: 76, label: "REPOSITORY" },
  { x: 230, label: "PAPER" },
  { x: 384, label: "DOMAIN" },
];

const VERIFY = ["CLAIM", "BASELINE", "EXPERIMENT", "RESULT"];
const DILIGENCE = ["ARTIFACT", "ARCHITECTURE", "THREAT MODEL", "CONVERSATION"];

const CHAIN_Y = [372, 412, 452, 492];
const LX = 150;   // verify chain x
const RX = 310;   // diligence chain x

const INK = "#14171B";
const LINE = "#C9CFCB";
const EXEC = "#4A7A0F";
const DIM = "#5C646E";

/** Accent overlay: transparent base, lights up on its turn. Decorative only. */
function stage(i: number) {
  return { className: "dz-stage", style: { animationDelay: `${i * 0.82}s` } };
}

export function HeroFlow() {
  const [ref, off] = usePointerOffset<HTMLDivElement>();

  return (
    <div ref={ref} className="dz-art relative" aria-hidden="true">
      <svg viewBox="0 0 460 560" className="h-auto w-full" role="presentation">
        <defs>
          <marker id="dz-a" viewBox="0 0 10 10" refX="8.5" refY="5"
                  markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill={LINE} />
          </marker>
          <marker id="dz-ae" viewBox="0 0 10 10" refX="8.5" refY="5"
                  markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill={EXEC} />
          </marker>
        </defs>

        {/* ── rails layer (parallax back) ─────────────────────────────── */}
        <g style={{ transform: `translate(${off.x * -3}px, ${off.y * -3}px)` }}>
          {/* LEARN return rail: bottom → far left → back into the artifact row */}
          <path d="M150 512 L150 534 L22 534 L22 44 L54 44"
                fill="none" stroke={LINE} strokeWidth="1.2" strokeDasharray="4 4"
                markerEnd="url(#dz-a)" />
          <path d="M150 512 L150 534 L22 534 L22 44 L54 44"
                fill="none" stroke={EXEC} strokeWidth="1.4" strokeDasharray="4 4"
                markerEnd="url(#dz-ae)" {...stage(6)} />
          <text x="30" y="548" fontSize="10" fill={DIM} fontFamily="ui-monospace, monospace"
                letterSpacing="0.1em">
            04 · LEARN — a failed rule re-enters sourcing
          </text>
        </g>

        {/* ── graph layer (parallax front) ────────────────────────────── */}
        <g style={{ transform: `translate(${off.x * 4}px, ${off.y * 4}px)` }}>
          {/* stage 01 — artifacts converge on a builder/team */}
          <text x="14" y="18" fontSize="10.5" fill={DIM}
                fontFamily="ui-monospace, monospace" letterSpacing="0.12em">
            01 · SOURCE
          </text>
          {ART.map((a, i) => (
            <g key={a.label}>
              <text x={a.x} y="40" fontSize="10" fill={INK} textAnchor="middle"
                    fontFamily="ui-monospace, monospace" letterSpacing="0.05em">
                {a.label}
              </text>
              <rect x={a.x - 26} y="50" width="52" height="22" rx="3"
                    fill="#FFFFFF" stroke={LINE} strokeWidth="1.1" />
              <rect x={a.x - 26} y="50" width="52" height="22" rx="3"
                    fill={EXEC} fillOpacity="0.10" stroke={EXEC} strokeWidth="1.3"
                    {...stage(0)} />
              {/* converging edge to the builder node */}
              <path d={`M${a.x} 72 Q ${a.x} 108 230 128`} fill="none"
                    stroke={LINE} strokeWidth="1.1" />
              <path d={`M${a.x} 72 Q ${a.x} 108 230 128`} fill="none"
                    stroke={EXEC} strokeWidth="1.4" strokeDasharray="3 5"
                    className="dz-flow" opacity="0.5"
                    style={{ animationDelay: `${i * 1.1}s` }} />
            </g>
          ))}

          {/* builder / team node */}
          <circle cx="230" cy="140" r="13" fill="#FFFFFF" stroke={INK} strokeWidth="1.3" />
          <circle cx="230" cy="140" r="13" fill={EXEC} fillOpacity="0.14"
                  stroke={EXEC} strokeWidth="1.6" {...stage(1)} />
          <circle cx="230" cy="140" r="13" fill="none" stroke={EXEC} strokeWidth="1"
                  className="dz-ping" opacity="0" />
          <text x="252" y="144" fontSize="10.5" fill={INK}
                fontFamily="ui-monospace, monospace" letterSpacing="0.05em">
            BUILDER / TEAM
          </text>
          <path d="M230 153 L230 186" stroke={LINE} strokeWidth="1.1" markerEnd="url(#dz-a)" />

          {/* stage 02 — the evidence gate */}
          <rect x="86" y="192" width="288" height="30" rx="4"
                fill="#FFFFFF" stroke={LINE} strokeWidth="1.1" strokeDasharray="5 4" />
          <rect x="86" y="192" width="288" height="30" rx="4"
                fill={EXEC} fillOpacity="0.08" stroke={EXEC} strokeWidth="1.4"
                strokeDasharray="5 4" {...stage(2)} />
          <text x="230" y="211" fontSize="10.5" fill={INK} textAnchor="middle"
                fontFamily="ui-monospace, monospace" letterSpacing="0.08em">
            EVIDENCE GATE
          </text>
          <g className="dz-gate">
            <path d="M104 207 l5 5 l9 -10" fill="none" stroke={EXEC} strokeWidth="1.8"
                  strokeLinecap="round" strokeLinejoin="round" />
            <path d="M344 202 l10 10 M354 202 l-10 10" fill="none" stroke="#A32B32"
                  strokeWidth="1.6" strokeLinecap="round" />
          </g>
          <path d="M230 222 L230 258" stroke={LINE} strokeWidth="1.1" markerEnd="url(#dz-a)" />

          {/* intro queue */}
          <rect x="160" y="264" width="140" height="28" rx="4"
                fill="#FFFFFF" stroke={INK} strokeWidth="1.3" />
          <rect x="160" y="264" width="140" height="28" rx="4"
                fill={EXEC} fillOpacity="0.12" stroke={EXEC} strokeWidth="1.5" {...stage(3)} />
          <text x="230" y="282" fontSize="10.5" fill={INK} textAnchor="middle"
                fontFamily="ui-monospace, monospace" letterSpacing="0.06em">
            INTRO QUEUE
          </text>

          {/* the split */}
          <path d={`M230 292 L230 316 L${LX} 316 L${LX} 344`} fill="none"
                stroke={LINE} strokeWidth="1.1" markerEnd="url(#dz-a)" />
          <path d={`M230 292 L230 316 L${RX} 316 L${RX} 344`} fill="none"
                stroke={LINE} strokeWidth="1.1" markerEnd="url(#dz-a)" />
          <path d={`M230 292 L230 316 L${LX} 316 L${LX} 344`} fill="none"
                stroke={EXEC} strokeWidth="1.4" {...stage(4)} />
          <path d={`M230 292 L230 316 L${RX} 316 L${RX} 344`} fill="none"
                stroke={EXEC} strokeWidth="1.4" {...stage(5)} />

          <text x={LX} y="338" fontSize="10.5" fill={DIM} textAnchor="middle"
                fontFamily="ui-monospace, monospace" letterSpacing="0.12em">
            02 · VERIFY
          </text>
          <text x={RX} y="338" fontSize="10.5" fill={DIM} textAnchor="middle"
                fontFamily="ui-monospace, monospace" letterSpacing="0.12em">
            03 · DILIGENCE
          </text>

          {/* the two chains */}
          {CHAIN_Y.map((y, i) => (
            <g key={y}>
              {i < 3 && (
                <>
                  <path d={`M${LX} ${y + 5} L${LX} ${CHAIN_Y[i + 1] - 5}`}
                        stroke={LINE} strokeWidth="1.1" />
                  <path d={`M${RX} ${y + 5} L${RX} ${CHAIN_Y[i + 1] - 5}`}
                        stroke={LINE} strokeWidth="1.1" />
                </>
              )}
              <circle cx={LX} cy={y} r="4.5" fill="#FFFFFF" stroke={INK} strokeWidth="1.2" />
              <circle cx={LX} cy={y} r="4.5" fill={EXEC} stroke={EXEC} strokeWidth="1.2"
                      {...stage(4)} />
              <text x={LX - 12} y={y + 3.5} fontSize="10" fill={INK} textAnchor="end"
                    fontFamily="ui-monospace, monospace" letterSpacing="0.04em">
                {VERIFY[i]}
              </text>
              <circle cx={RX} cy={y} r="4.5" fill="#FFFFFF" stroke={INK} strokeWidth="1.2" />
              <circle cx={RX} cy={y} r="4.5" fill={EXEC} stroke={EXEC} strokeWidth="1.2"
                      {...stage(5)} />
              <text x={RX + 12} y={y + 3.5} fontSize="10" fill={INK}
                    fontFamily="ui-monospace, monospace" letterSpacing="0.04em">
                {DILIGENCE[i]}
              </text>
            </g>
          ))}
        </g>
      </svg>
    </div>
  );
}

/**
 * Mobile/tablet variant. The graph above is dense by design; below `lg` it is
 * replaced by this four-step summary rather than shrunk into illegibility.
 * Plain HTML text, no SVG, no motion beyond the shared entrance transform.
 */
export function HeroFlowCompact() {
  const steps = [
    ["01", "Source", "Public artifacts — repository, paper, domain — converge on a builder, and the evidence has to clear a gate."],
    ["02", "Verify", "The claim is reproduced against a real baseline: claim → baseline → experiment → result."],
    ["03", "Diligence", "The artifact is read at the level of its architecture and threat model, up to a founder conversation."],
    ["04", "Learn", "A rule that fails re-enters sourcing instead of being quietly patched."],
  ];
  return (
    <ol className="panel divide-y divide-paper-line overflow-hidden">
      {steps.map(([n, label, note], i) => (
        <li key={n} className="flex gap-4 p-4">
          <span className="mono pt-0.5 text-ink-faint">{n}</span>
          <div className="min-w-0">
            <p className="flex items-center gap-2 text-[14.5px] font-semibold">
              {label}
              {i < 3 ? <span aria-hidden="true" className="text-exec">↓</span>
                     : <span aria-hidden="true" className="text-exec">↺</span>}
            </p>
            <p className="meta mt-1">{note}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
