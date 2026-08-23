import type { Metadata } from "next";
import Link from "next/link";
import { Section } from "@/components/Chrome";
import { Stat } from "@/components/Evidence";
import { Reveal } from "@/components/Reveal";
import { AttentionConstruction, IdentityStates } from "@/components/SignalViz";
import { research } from "@/lib/research";

export const metadata: Metadata = {
  title: "Signals — DAY ZERO",
  description:
    "What actually feeds DAY ZERO: GitHub-led discovery with multi-modal evidence, " +
    "an honest identity audit, and why presence is not the same as signal.",
};

const sig = research.signals;
const ident = sig.identity;
const dom = sig.domain;

const CHANNEL_NOTES: Record<string, { label: string; role: string; state: string }> = {
  github: { label: "GitHub", role: "The discovery channel. Every one of the 102 repositories in the universe entered through it.", state: "LIVE — 100% of discovery" },
  research: { label: "Research papers", role: "Evidence enrichment: papers corroborate depth and collaboration on already-surfaced leads (e.g. the Sandlock arXiv paper). Not a discovery source in the current run.", state: "LIVE — enrichment only" },
  web: { label: "Domains / web", role: "Formation evidence: project domains, company sites, organisation records attached to existing leads.", state: "LIVE — formation evidence" },
  x: { label: "X", role: "Ingestion is off by default and no credentials were present. Nothing in the current dataset came from X.", state: "DISABLED" },
  hackathon: { label: "Hackathon automation", role: "Manual only, by robots policy. No automated adapter exists.", state: "NOT USED" },
  events: { label: "Manual event layer", role: "Designed (schema and adapter interface exist) but not populated in the current run.", state: "DESIGNED, NOT POPULATED" },
};

function pctBar(pct: number) {
  return (
    <div className="mt-2 h-2 overflow-hidden rounded-full bg-paper-soft ring-1 ring-paper-line" role="presentation">
      <div className="h-full rounded-full bg-exec" style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function Signals() {
  const gh = sig.channels.find((c) => c.channel === "github")!;
  const order = ["github", "research", "web", "x", "hackathon", "events"];

  return (
    <>
      <Section eyebrow="Inputs" title="What actually feeds DAY ZERO"
        lead="The honest description is GitHub-led discovery with multi-modal evidence — not “multi-channel sourcing”. One channel discovers; the others corroborate. Overstating that would be exactly the kind of claim this project exists to test.">
        <div className="grid gap-px overflow-hidden rounded border border-paper-line bg-paper-line md:grid-cols-2 lg:grid-cols-3">
          {order.map((id) => {
            const ch = sig.channels.find((c) => c.channel === id);
            const meta = CHANNEL_NOTES[id];
            if (!ch || !meta) return null;
            const live = String(meta.state).startsWith("LIVE");
            return (
              <div key={id} className="bg-paper-card p-5">
                <div className="flex items-baseline justify-between gap-3">
                  <h3 className="h3">{meta.label}</h3>
                  <span className={`mono text-[10px] uppercase tracking-widest ${
                    live ? "text-exec-deep" : "text-ink-faint"}`}>
                    {live ? "● " : "○ "}{meta.state}
                  </span>
                </div>
                <p className="meta mt-2 text-[13px]">{meta.role}</p>
                {ch.evidence_records > 0 ? (
                  <p className="mono mt-3 text-[11.5px] text-ink-faint">
                    {ch.evidence_records.toLocaleString()} evidence records · {ch.raw_records} artifacts
                  </p>
                ) : ch.formation_signals > 0 ? (
                  <p className="mono mt-3 text-[11.5px] text-ink-faint">
                    {ch.formation_signals} formation signals
                  </p>
                ) : null}
              </div>
            );
          })}
        </div>
        <p className="meta mt-4 max-w-prose">
          GitHub: {gh.api_requests?.toLocaleString()} API requests, {gh.raw_records}{" "}
          repositories, {gh.evidence_records.toLocaleString()} evidence records, at an API
          cost of $0. The scale numbers on the{" "}
          <Link href="/methodology/" className="text-exec-deep underline underline-offset-4">
            methodology page
          </Link>{" "}
          all trace back to these channels.
        </p>
      </Section>

      {/* ── IDENTITY AUDIT ───────────────────────────────────────────────── */}
      <Section eyebrow="Audit · Phase 4" title="The identity audit — an assumption, revised"
        lead="Phase 1 assumed identity resolution was the bottleneck of the whole system. Phase 4 measured it. The assumption was wrong in an instructive way.">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Stat value={ident.total_identities.toLocaleString()} label="Live identities"
            note="Phase 2 collected universe, unchanged" />
          <Stat value={`${ident.mergeable_identities} · ${ident.mergeable_pct.toFixed(2)}%`}
            label="Mergeable" note="under conservative v2 rules" />
          <Stat value={String(ident.x_linkable_count)} label="Verified X-linkable"
            note={`${ident.x_linkable_pct.toFixed(2)}% of the universe`} />
          <Stat value={String(ident.context.identities_with_an_at_handle_in_bio as number)}
            label="Bio @handles" note="deliberately NOT counted as X identities" />
        </div>

        <div className="mt-6">
          <IdentityStates
            total={ident.total_identities}
            mergeable={ident.mergeable_identities}
            mergeablePct={ident.mergeable_pct}
            xLinkable={ident.x_linkable_count}
            xPct={ident.x_linkable_pct}
          />
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <Reveal>
            <div className="panel h-full p-5">
              <p className="eyebrow">Resolution states</p>
              <div className="mt-3 grid gap-2.5">
                {([
                  ["VERIFIED_CROSS_LINK", "two-way verified link between platforms"],
                  ["STRONG_ARTIFACT_MATCH", "same artifact referenced from both sides"],
                  ["POSSIBLE_MATCH", "suggestive but unverified — never merged"],
                  ["UNRESOLVED", "no cross-platform evidence at all"],
                ] as const).map(([state, desc]) => {
                  const n = ident.states[state] ?? 0;
                  return (
                    <div key={state}>
                      <div className="flex items-baseline justify-between gap-3">
                        <span className="mono text-[11.5px] text-ink-dim">{state}</span>
                        <span className="mono text-[12px] text-ink">{n}</span>
                      </div>
                      {pctBar((n / ident.total_identities) * 100)}
                      <p className="meta mt-1 text-[12px]">{desc}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </Reveal>
          <Reveal delay={60}>
            <div className="panel h-full p-5">
              <p className="eyebrow">The revised conclusion</p>
              <p className="body mt-3 text-[14.5px]">
                General identity resolution is <em>not</em> the bottleneck any more:{" "}
                <span className="mono text-ink">{ident.mergeable_pct.toFixed(2)}%</span> of
                live identities are mergeable under rules that forbid fuzzy matching.
                What remains broken is <strong className="text-ink">X-specific identity
                linkage</strong>: exactly{" "}
                <span className="mono text-ink">{ident.x_linkable_count}</span> identity in{" "}
                {ident.total_identities} could be verifiably linked to an X account.
              </p>
              <p className="body mt-3 text-[14.5px]">
                {ident.context.identities_with_an_at_handle_in_bio as number} GitHub bios
                contain an @handle — and none was counted.{" "}
                {ident.context.why_at_handles_are_not_counted as string} The handles are not
                exposed here, or anywhere in this product.
              </p>
              <p className="meta mt-3 text-[12.5px]">
                Methods excluded by policy: {ident.methods_excluded.join(", ").replaceAll("_", " ")}.
              </p>
            </div>
          </Reveal>
        </div>
      </Section>

      {/* ── DOMAIN SIGNAL ────────────────────────────────────────────────── */}
      <Section eyebrow="Audit · Phase 4" title="Presence is not signal: the domain example"
        lead="Most projects have a domain. That is precisely why having one proves little — the question is whether the domain adds a formation event the evidence graph did not already contain.">
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="panel p-5">
            <div className="flex items-baseline justify-between">
              <p className="eyebrow">Repositories with a project domain</p>
              <span className="mono text-lg text-ink">{dom.with_a_project_domain_pct.toFixed(2)}%</span>
            </div>
            {pctBar(dom.with_a_project_domain_pct)}
            <div className="mt-5 flex items-baseline justify-between">
              <p className="eyebrow">Domain adds a distinct formation event</p>
              <span className="mono text-lg text-exec-deep">{dom.domain_adds_distinct_pct.toFixed(2)}%</span>
            </div>
            {pctBar(dom.domain_adds_distinct_pct)}
            <p className="mono mt-4 text-[11.5px] text-ink-faint">
              {dom.with_a_project_domain_pct}% presence → {dom.domain_adds_distinct_pct}% independent signal,
              measured on {dom.repositories_measured} repositories
            </p>
          </div>
          <div className="panel p-5">
            <p className="eyebrow">Why the gap</p>
            <p className="body mt-2 text-[14px]">{dom.interpretation}</p>
            <p className="meta mt-3 text-[12.5px]">
              Excluded by policy: {dom.methods_excluded.join(", ").replaceAll("_", " ")}.
            </p>
          </div>
        </div>
      </Section>

      {/* ── ATTENTION VS CONSTRUCTION ────────────────────────────────────── */}
      <Section eyebrow="The core separation" title="Attention and construction are different axes"
        lead="Stars measure attention. Commits by the people who own the work measure construction. Across the universe the ratio between them spans four orders of magnitude — which is why attention is barred from every surfacing decision.">
        <Reveal>
          <AttentionConstruction
            high={sig.attentionVsConstruction.high}
            low={sig.attentionVsConstruction.low}
          />
        </Reveal>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div className="panel overflow-hidden">
            <p className="eyebrow border-b border-paper-line px-5 py-3">
              High attention · low construction
            </p>
            <ul>
              {sig.attentionVsConstruction.high.slice(0, 4).map((row) => (
                <li key={row.repo} className="border-b border-paper-line px-5 py-3 last:border-b-0">
                  <div className="flex flex-wrap items-baseline justify-between gap-x-3">
                    <span className="mono break-all text-[12.5px] text-ink">{row.repo}</span>
                    <span className="mono text-[11.5px] text-ink-faint">
                      {row.stars.toLocaleString()}★ · {row.top_contributions} commits
                    </span>
                  </div>
                  <p className="mono mt-1 text-[11px] text-claim">
                    {row.stars_per_commit?.toLocaleString()} stars per commit
                  </p>
                </li>
              ))}
            </ul>
          </div>
          <div className="panel overflow-hidden">
            <p className="eyebrow border-b border-paper-line px-5 py-3">
              High construction · low attention
            </p>
            <ul>
              {sig.attentionVsConstruction.low.slice(0, 4).map((row) => (
                <li key={row.repo} className="border-b border-paper-line px-5 py-3 last:border-b-0">
                  <div className="flex flex-wrap items-baseline justify-between gap-x-3">
                    <span className="mono break-all text-[12.5px] text-ink">{row.repo}</span>
                    <span className="mono text-[11.5px] text-ink-faint">
                      {row.stars.toLocaleString()}★ · {row.top_contributions.toLocaleString()} commits
                    </span>
                  </div>
                  <p className="mono mt-1 text-[11px] text-exec-deep">
                    {row.stars_per_commit?.toLocaleString()} stars per commit
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <p className="meta mt-4 max-w-prose">
          {sig.attentionVsConstruction.note} A curated list at ~1,900 stars per commit and a
          working system at 0.1 stars per commit are not a ranking of their authors — they
          are proof that the two measurements capture different things, and that a system
          surfacing builders must read construction directly.
        </p>
      </Section>

      {/* ── ACCEPTED WORK UNIT ───────────────────────────────────────────── */}
      <Section eyebrow="Output unit" title="What the funnel produces">
        <div className="panel-raised max-w-prose border-l-4 border-l-exec p-6">
          <p className="mono text-[12px] uppercase tracking-widest text-ink-faint">INTRO_READY_AWU</p>
          <p className="body mt-2 text-[15px]">
            One builder or team lead that survives evidence review and is genuinely worth
            spending relationship capital on. The current count is{" "}
            <span className="mono text-ink">{research.scale.introReadyAwu}</span> — from{" "}
            {research.scale.repositories} repositories, {research.scale.evidence.toLocaleString()}{" "}
            evidence records and {research.scale.sources} registered sources.
          </p>
          <p className="meta mt-3">
            Three leads is the honest number, not a vanity metric: no introduction has been
            made, and the count measures review survival, not conversions. The full records
            are on{" "}
            <Link href="/current-3/" className="text-exec-deep underline underline-offset-4">
              Current&nbsp;3
            </Link>.
          </p>
        </div>
      </Section>
    </>
  );
}
