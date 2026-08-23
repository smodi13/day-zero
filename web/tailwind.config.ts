import type { Config } from "tailwindcss";

/**
 * DAY ZERO's design tokens.
 *
 * The paper base is deliberately the same neutral ground as the sibling
 * research project (#F7F8F7 / #FFFFFF / #DFE3E1) — a shared, unbranded surface
 * that reads as a document rather than a product. Everything above the ground
 * is DAY ZERO's own: graphite near-black instead of blue-black ink, and a
 * single execution/verification accent in the yellow-green band rather than
 * teal. Status tones are always paired with a glyph and a text label, so colour
 * is never the sole carrier of meaning.
 */
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // ── ground ────────────────────────────────────────────────────────
        paper: { DEFAULT: "#F7F8F7", card: "#FFFFFF", line: "#DFE3E1", soft: "#EFF1EF" },
        // ── type: graphite, not blue-black ────────────────────────────────
        ink: { DEFAULT: "#14171B", soft: "#3A4048", dim: "#5C646E", faint: "#878E97" },
        // ── the one high-signal accent: execution / verification ──────────
        exec: {
          DEFAULT: "#4A7A0F",   // links, active state, verified marks
          deep: "#35590A",      // hover, emphasis
          pale: "#EDF3E1",      // washes and chips
          bright: "#7CB518",    // small live marks only — never body text
        },
        // ── evidence states (always with glyph + label) ───────────────────
        claim: { DEFAULT: "#8A6209", pale: "#F7F0DF" },   // project claim / inferred
        absent: { DEFAULT: "#A32B32", pale: "#F9E9E9" },  // not found
        unknown: { DEFAULT: "#66707C", pale: "#EFF1F2" }, // unknown
        trace: { DEFAULT: "#44505F", pale: "#ECEEF1" },   // graph edges, neutral technical
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "SF Mono", "Menlo", "Consolas", "monospace"],
        sans: ["ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Inter", "sans-serif"],
      },
      maxWidth: { content: "72rem", prose: "68ch" },
    },
  },
  plugins: [],
};
export default config;
