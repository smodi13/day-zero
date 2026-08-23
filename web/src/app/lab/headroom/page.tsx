import type { Metadata } from "next";
import Link from "next/link";
import { Section } from "@/components/Chrome";
import { HeadroomExplorer } from "@/components/HeadroomExplorer";
import { BaselineReveal } from "@/components/BaselineReveal";
import { Hash, Stat, Verdict } from "@/components/Evidence";
import { Reveal } from "@/components/Reveal";
import { research } from "@/lib/research";

export const metadata: Metadata = {
  title: "Token compression reproduction — DAY ZERO",
  description:
    "A pre-registered reproduction of headroom-ai's published token-compression claims " +
    "against real baselines, on 35 samples the author did not choose.",
};

const hr = research.headroom;
const json = hr.categories.structured_json;
const coding = hr.categories.coding_context;
const agent = hr.categories.agent_context;

const CLAIM_TEXT: Record<string, string> = {
  "CLAIM-A": "Reduces tokens relative to raw input (structured JSON)",
  "CLAIM-B": "Reduction exceeds trivial minification (structured JSON)",
  "CLAIM-C": "Task-relevant information survives — “same answers”",
  "CLAIM-D": "JSON reduction reaches the published 60–95% band",
  "CLAIM-E": "Coding-agent reduction reaches the published 15–20% band",
};

export default function Headroom() {
  return (
    <>
      {/* ── VERDICT ──────────────────────────────────────────────────────── */}
      <Section eyebrow="Lab · technical verification" title="Token compression reproduction">
        <Verdict label={hr.verdict.replaceAll("_", " ")} kind="mixed"
          sub={<>
            Three of five pre-registered claims supported at their thresholds; two not.
            Probe retention <span className="mono text-ink">{hr.retention.toFixed(4)}</span>,{" "}
            <span className="mono text-ink">{hr.errors}</span> transformation errors —
            the compression is genuinely lossless. Both halves of this verdict matter, and
            neither is a statement about the project’s honesty.
          </>} />
        <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Stat value={`${json.vsRaw.median.toFixed(2)}%`} label="JSON vs raw" note="median savings" />
          <Stat value={`${json.vsMinified.median.toFixed(2)}%`} label="JSON vs minified" note="the pre-registered decisive comparison" />
          <Stat value={`${coding.vsRaw.median.toFixed(2)}%`} label="Coding vs raw" note="at every quantile — min, median, max" />
          <Stat value={`${agent.vsRaw.median.toFixed(2)}%`} label="Agent context vs raw" note="median — but bimodal, see below" />
        </div>
      </Section>

      {/* ── THE CLAIM ────────────────────────────────────────────────────── */}
      <Section eyebrow="01" title="The published claims, verbatim"
        lead="Two public descriptions of the same project differ. Both are recorded exactly; the discrepancy was resolved against the experiment, not in it — the protocol tests the lower coding bound (15%).">
        <div className="grid gap-3 lg:grid-cols-2">
          {hr.sourceClaims.map((c) => (
            <blockquote key={c.id} className="panel p-5">
              <p className="body text-[14.5px]">“{c.text}”</p>
              <footer className="mono mt-3 text-[11.5px] text-ink-faint">
                {c.id} — {c.source}
              </footer>
            </blockquote>
          ))}
        </div>
        <p className="body mt-5 max-w-prose">
          The repository description says <strong className="text-ink">20%</strong> for
          coding agents; the README says{" "}
          <strong className="text-ink">15–20%</strong>. Where a published range and a
          published point differ, the experiment tested against the lower bound — a
          deliberately generous reading.
        </p>
      </Section>

      {/* ── DESIGN ───────────────────────────────────────────────────────── */}
      <Section eyebrow="02" title="Experiment design"
        lead="The protocol — dataset, baselines, thresholds and verdict rules — was committed and hashed before any measurement was taken. The dataset was constructed by the analyst, not chosen by the project.">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Stat value={String(hr.dataset.sampleCount)} label="Samples"
            note={`${(hr.dataset.totalBytes / 1_000_000).toFixed(2)} MB total`} />
          <Stat value="12 · 12 · 11" label="JSON · coding · agent"
            note="structured JSON, coding context, agent context" />
          <Stat value="2 tokenizers" label="o200k_base · cl100k_base"
            note={`primary: ${hr.dataset.primaryTokenizer}`} />
          <Stat value="4 baselines" label="RAW · MINIFIED · COMPACT_JSON · GZIP_B64"
            note="primary comparison: HEADROOM vs MINIFIED" />
        </div>
        <p className="body mt-5 max-w-prose">
          Why MINIFIED is the primary baseline: pretty-printed JSON is largely whitespace,
          and stripping whitespace costs one line of code. A compression tool earns its
          place by what it saves <em>beyond</em> that. Defaulting the comparison to RAW
          would make every result look stronger than it is — so this page defaults to
          MINIFIED everywhere, and shows RAW as the labelled marketing comparison.
        </p>
        <div className="mono mt-4 grid gap-1.5 text-[12px]">
          <Hash label="protocol sha256" value={research.hashes.experimentProtocol} />
          <Hash label="dataset manifest sha256" value={research.hashes.experimentDataset} />
        </div>
      </Section>

      {/* ── EXPLORER ─────────────────────────────────────────────────────── */}
      <Section eyebrow="03" title="Results, by category and baseline"
        lead="Every dot is one sample. Switch the category and the baseline — the default is the decisive one, HEADROOM vs MINIFIED. Negative values mean headroom's output tokenised larger than the baseline.">
        <Reveal>
          <HeadroomExplorer samples={hr.samples} categories={hr.categories}
            primaryTokenizer={hr.dataset.primaryTokenizer} />
        </Reveal>

        <h3 className="h3 mt-8">Canonical distributions (o200k_base, pre-registered quantiles)</h3>
        <div className="scroll-x mt-3 rounded border border-paper-line">
          <table className="text-[12.5px]">
            <thead>
              <tr className="border-b border-paper-line bg-paper">
                <th className="px-4 py-2.5">Category</th>
                <th className="px-4 py-2.5">n</th>
                <th className="px-4 py-2.5">vs raw — median (p25 · p75)</th>
                <th className="px-4 py-2.5">vs minified — median (p25 · p75)</th>
                <th className="px-4 py-2.5">minify alone vs raw</th>
                <th className="px-4 py-2.5">retention</th>
              </tr>
            </thead>
            <tbody>
              {([["Structured JSON", json], ["Coding context", coding], ["Agent context", agent]] as const)
                .map(([label, d]) => (
                <tr key={label} className="border-b border-paper-line last:border-b-0">
                  <td className="px-4 py-2.5 font-semibold text-ink">{label}</td>
                  <td className="mono px-4 py-2.5 text-ink-dim">{d.vsRaw.n}</td>
                  <td className="mono px-4 py-2.5 text-ink-dim">
                    <span className="text-ink">{d.vsRaw.median?.toFixed(2)}%</span>{" "}
                    ({d.vsRaw.p25?.toFixed(2)} · {d.vsRaw.p75?.toFixed(2)})
                  </td>
                  <td className="mono px-4 py-2.5 text-ink-dim">
                    <span className="text-ink">{d.vsMinified.median?.toFixed(2)}%</span>{" "}
                    ({d.vsMinified.p25?.toFixed(2)} · {d.vsMinified.p75?.toFixed(2)})
                  </td>
                  <td className="mono px-4 py-2.5 text-ink-dim">{d.minifyOnlyVsRaw.median?.toFixed(2)}%</td>
                  <td className="mono px-4 py-2.5 text-ink-dim">{d.retention.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="meta mt-3 max-w-prose">
          Agent context is the interesting distribution: a median of{" "}
          <span className="mono">{agent.vsRaw.median.toFixed(2)}%</span> hides a bimodal
          split — structured-ish agent outputs (API pages, log streams) compressed by as
          much as <span className="mono">{agent.vsRaw.max?.toFixed(2)}%</span>, while
          code-like agent outputs were routed to a protected class and left untouched.
          The router’s protectiveness is a defensible design choice; it is also why the
          headline coding claim does not show up here.
        </p>
      </Section>

      {/* ── CLAIM SCOREBOARD ─────────────────────────────────────────────── */}
      <Section eyebrow="04" title="Pre-registered claims, scored">
        <div className="scroll-x rounded border border-paper-line">
          <table className="text-[13px]">
            <thead>
              <tr className="border-b border-paper-line bg-paper">
                <th className="px-4 py-2.5">Claim</th>
                <th className="px-4 py-2.5">Threshold</th>
                <th className="px-4 py-2.5">Measured</th>
                <th className="px-4 py-2.5">Result</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(hr.claims).map(([id, c]) => (
                <tr key={id} className="border-b border-paper-line align-top last:border-b-0">
                  <td className="px-4 py-2.5">
                    <span className="mono text-[11.5px] text-ink-faint">{id}</span>
                    <span className="ml-2 text-ink">{CLAIM_TEXT[id]}</span>
                  </td>
                  <td className="mono whitespace-nowrap px-4 py-2.5 text-ink-dim">{c.threshold}</td>
                  <td className="mono whitespace-nowrap px-4 py-2.5 text-ink-dim">
                    {c.value === null ? "—" : id === "CLAIM-C" ? c.value.toFixed(4) : `${c.value.toFixed(2)}%`}
                  </td>
                  <td className={`mono whitespace-nowrap px-4 py-2.5 text-[11.5px] ${
                    c.supported ? "text-exec-deep" : "text-absent"}`}>
                    {c.supported ? "● SUPPORTED" : "✕ NOT SUPPORTED"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="meta mt-3 max-w-prose">
          The verdict rule was itself pre-registered: PARTIALLY REPRODUCED means at least
          one claim supported at threshold and at least one not.
        </p>
      </Section>

      {/* ── THE FINDING ──────────────────────────────────────────────────── */}
      <Section eyebrow="05" title="The baseline is part of the claim"
        lead="Step through the three comparisons. The measured data never changes — the same tokens, the same samples, the same run. What changes is the zero point.">
        <Reveal>
          <BaselineReveal
            vsRaw={json.vsRaw.median}
            minifyOnly={json.minifyOnlyVsRaw.median}
            vsMinified={json.vsMinified.median}
          />
        </Reveal>
        <Reveal>
          <div className="panel-raised mt-5 border-l-4 border-l-exec p-6">
            <p className="body max-w-prose text-[16px]">
              For structured JSON, headroom saves a median{" "}
              <span className="mono text-ink">{json.vsRaw.median.toFixed(2)}%</span>{" "}
              against pretty-printed input — but trivial whitespace minification alone
              saves <span className="mono text-ink">{json.minifyOnlyVsRaw.median.toFixed(2)}%</span>{" "}
              (median) on the same samples. Measured against minified input, headroom’s own
              contribution is a median{" "}
              <span className="mono text-ink">{json.vsMinified.median.toFixed(2)}%</span>.
            </p>
            <p className="body mt-4 max-w-prose text-[16px]">
              That remaining {json.vsMinified.median.toFixed(2)}% is real, lossless, and
              worth having. But a majority of the <em>headline</em> number is supplied by a
              baseline choice, not by the compressor — which is why any compression claim
              is unevaluable until you know what it was measured against.{" "}
              <strong className="text-ink">The baseline is part of the claim.</strong>
            </p>
          </div>
        </Reveal>
      </Section>

      {/* ── CODING RESULT + FALSIFICATION ATTEMPTS ───────────────────────── */}
      <Section eyebrow="06" title="The coding claim, and three attempts to rescue it"
        lead="All 12 coding samples produced 0.00% savings versus raw — at the minimum, median and maximum. Before concluding anything, the experiment tried to prove itself wrong three ways.">
        <div className="grid gap-3 lg:grid-cols-3">
          {hr.supplementary.map((sp) => (
            <div key={sp.id} className="panel flex h-full min-w-0 flex-col break-words p-5">
              <p className="eyebrow">{sp.id}</p>
              <p className="body mt-2 text-[13.5px]"><em>{sp.hypothesis}</em></p>
              <p className="meta mt-2 flex-1 text-[12.5px]">{sp.method}</p>
              <p className="mono mt-3 border-t border-paper-line pt-3 text-[11.5px] text-claim">
                {sp.conclusion}
              </p>
            </div>
          ))}
        </div>
        <p className="body mt-5 max-w-prose">
          The mechanism is visible in the router traces: recent code and user messages are
          routed to a <span className="mono">protected</span> class and passed through
          untouched. On this benchmark, the published coding-agent savings did not
          materialise under the library’s default entry point — including with the{" "}
          <span className="mono">[code]</span> extra installed, under context pressure, and
          in multi-turn framing. Versus minified, the coding median was{" "}
          <span className="mono text-ink">{coding.vsMinified.median.toFixed(2)}%</span> —
          negative, because headroom’s structural wrapping adds tokens it cannot recover on
          content it declines to compress.
        </p>
      </Section>

      {/* ── FAIRNESS ─────────────────────────────────────────────────────── */}
      <Section eyebrow="07" title="What this result is — and is not">
        <ul className="grid gap-px overflow-hidden rounded border border-paper-line bg-paper-line sm:grid-cols-2">
          {[
            ["Headroom is real engineering", "The structured-data path is a genuine, working, content-aware compressor with reversible transforms — not a fake wrapper. Retention 1.0000 across 35 samples and zero transformation errors is a strong engineering result."],
            ["The structured-data result is strong", "A median 28.41% beyond minification, lossless, reaching 86.85% on compatible schema structure. On the right workload this is significant, real savings."],
            ["The coding claim did not reproduce here", "0.00% at every quantile versus raw, on all 12 coding samples, under the library's default entry point — with three pre-registered rescue attempts falsified."],
            ["This benchmark is limited", "One environment, one entry point, 35 samples, and several untested configurations (proxy, wrap, MCP, the prose model, cross-agent memory). It is a reproducible data point about claim scope — not a universal verdict on the project, and not an accusation of dishonesty."],
          ].map(([t, d]) => (
            <li key={t} className="bg-paper-card p-5">
              <h3 className="h3">{t}</h3>
              <p className="meta mt-2">{d}</p>
            </li>
          ))}
        </ul>
        <details className="panel mt-4">
          <summary className="cursor-pointer px-5 py-3 text-[13px] text-ink-dim hover:text-ink">
            Untested configurations ({hr.untested.length})
          </summary>
          <ul className="border-t border-paper-line px-5 py-3">
            {hr.untested.map((u) => (
              <li key={u} className="meta py-1 text-[13px]">— {u}</li>
            ))}
          </ul>
        </details>
        <p className="meta mt-5 max-w-prose">
          Environment: headroom-ai {String(hr.environment.headroom_ai)}, tiktoken{" "}
          {String(hr.environment.tiktoken)}, Python {String(hr.environment.python)},{" "}
          {String(hr.environment.platform)}. Zero paid API calls.
          The protocol, dataset manifest and results are committed in the repository —
          see the{" "}
          <Link href="/methodology/" className="text-exec-deep underline underline-offset-4">
            methodology timeline
          </Link>{" "}
          for the commit ordering.
        </p>
      </Section>
    </>
  );
}
