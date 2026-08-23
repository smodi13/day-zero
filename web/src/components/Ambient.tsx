/**
 * Ambient technical ground for the hero band.
 *
 * Faint graph edges and branch lines drifting behind the content — the visual
 * suggestion of a system running, kept far below the threshold where it would
 * compete with reading. Everything here is decorative: `aria-hidden`, no text,
 * no information, opacities in the 0.03–0.09 range, and a mask that fades it
 * out entirely before it reaches the copy column.
 *
 * Server component: pure SVG + CSS keyframes, zero client JavaScript.
 */
export function Ambient() {
  return (
    <div aria-hidden="true"
         className="pointer-events-none absolute inset-0 overflow-hidden select-none">
      <svg viewBox="0 0 1440 620" preserveAspectRatio="xMidYMid slice"
           className="h-full w-full" role="presentation">
        <defs>
          {/* The execution grid lives inside this layer rather than on the
              section, so grid and geometry fade together and no seam appears
              where the mask releases. */}
          <pattern id="dz-amb-grid" width="46" height="46" patternUnits="userSpaceOnUse">
            <path d="M46 0H0V46" fill="none" stroke="#14171B" strokeWidth="0.6"
                  opacity="0.055" />
          </pattern>
          {/* A soft, wide ramp — opaque across the copy column, releasing only
              well past it. Painted in the hero's own background colour so the
              transition itself is invisible. */}
          <linearGradient id="dz-amb-fade" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="1" />
            <stop offset="34%" stopColor="#FFFFFF" stopOpacity="0.98" />
            <stop offset="56%" stopColor="#FFFFFF" stopOpacity="0.78" />
            <stop offset="78%" stopColor="#FFFFFF" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
          </linearGradient>
        </defs>

        <rect width="1440" height="620" fill="url(#dz-amb-grid)" />

        {/* Branch lines — a commit graph read sideways. */}
        <g className="dz-drift" fill="none" stroke="#14171B" strokeWidth="1">
          {[
            "M-40 120 H 380 Q 430 120 460 158 H 900 Q 950 158 980 196 H 1500",
            "M-40 258 H 300 Q 350 258 380 300 H 760 Q 810 300 840 342 H 1500",
            "M-40 430 H 520 Q 570 430 600 392 H 1010 Q 1060 392 1090 356 H 1500",
            "M-40 556 H 240 Q 290 556 320 514 H 880 Q 930 514 960 476 H 1500",
          ].map((d, i) => (
            <path key={d} d={d} opacity={0.07 - i * 0.008} />
          ))}
        </g>

        {/* Execution traces travelling along two of those branches. */}
        <g fill="none" stroke="#4A7A0F" strokeWidth="1.2" strokeDasharray="2 12">
          <path d="M-40 120 H 380 Q 430 120 460 158 H 900 Q 950 158 980 196 H 1500"
                opacity="0.28" className="dz-flow" />
          <path d="M-40 430 H 520 Q 570 430 600 392 H 1010 Q 1060 392 1090 356 H 1500"
                opacity="0.22" className="dz-flow" style={{ animationDelay: "-6s" }} />
        </g>

        {/* Commit nodes at the branch points. */}
        <g className="dz-drift">
          {[[460, 158], [980, 196], [380, 300], [840, 342], [600, 392], [1090, 356]].map(
            ([cx, cy], i) => (
              <g key={`${cx}-${cy}`}>
                <circle cx={cx} cy={cy} r="3" fill="#F7F8F7" stroke="#14171B"
                        strokeWidth="1" opacity="0.16" />
                <circle cx={cx} cy={cy} r="3" fill="none" stroke="#4A7A0F"
                        strokeWidth="1" opacity="0" className="dz-ping"
                        style={{ animationDelay: `${i * 1.3}s` }} />
              </g>
            ),
          )}
        </g>

        {/* Sandbox boundary geometry, far right. */}
        <g fill="none" stroke="#14171B" opacity="0.06">
          <rect x="1120" y="96" width="250" height="150" rx="6" strokeDasharray="6 6" />
          <rect x="1152" y="128" width="186" height="86" rx="4" />
        </g>

        {/* Mask last: everything above it fades toward the copy column. */}
        <rect width="1440" height="620" fill="url(#dz-amb-fade)" />
      </svg>
    </div>
  );
}
