import type { Config } from "tailwindcss";

/** DAY ZERO's own system. Graphite base, one verification accent, status tones
 *  that are always paired with a text label and a glyph — never colour alone. */
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0b0d11",
        surface: "#111419",
        raised: "#161a21",
        line: "#222833",
        lineSoft: "#1a1f27",
        text: "#e6e9ee",
        dim: "#98a2b3",
        faint: "#67707f",
        // single high-signal accent: verification / execution
        signal: "#5fd6a4",
        signalDim: "#2f7a5e",
        // evidence states
        observed: "#5fd6a4",
        claim: "#e0b354",
        inferred: "#e0b354",
        unknown: "#7b8494",
        absent: "#c07a6b",
        trace: "#7aa2f7",
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "SF Mono", "Menlo", "Consolas", "monospace"],
        sans: ["ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Inter", "sans-serif"],
      },
      maxWidth: { content: "70rem", prose: "44rem" },
      fontSize: {
        eyebrow: ["11px", { lineHeight: "1.4", letterSpacing: "0.14em" }],
      },
    },
  },
  plugins: [],
};
export default config;
