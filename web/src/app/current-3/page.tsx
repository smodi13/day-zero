import type { Metadata } from "next";
import Link from "next/link";
import { Section } from "@/components/Chrome";
import { Reveal } from "@/components/Reveal";
import { research, type Lead } from "@/lib/research";

export const metadata: Metadata = {
  title: "Current 3 — DAY ZERO",
  description: "The three builder leads that currently survive evidence review.",
};

const r = research;

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="eyebrow">{label}</dt>
      <dd className="body mt-1.5 text-[14.5px]">{children}</dd>
    </div>
  );
}

function StateBadge({ lead }: { lead: Lead }) {
  const intro = lead.systemState === "INTRO_READY";
  return (
    <span className={`mono inline-flex items-center gap-1.5 rounded border px-2 py-0.5 text-[11px] uppercase tracking-wider ${
      intro ? "border-exec/45 bg-exec-pale text-exec-deep"
            : "border-paper-line bg-paper text-ink-dim"}`}>
      <span aria-hidden="true">{intro ? "▸" : "◔"}</span>
      {lead.systemState.replaceAll("_", " ")}
      {lead.analystOverride ? " · analyst override" : ""}
    </span>
  );
}

function LeadRecord({ lead, index }: { lead: Lead; index: number }) {
  return (
    <Reveal>
      <article className="panel overflow-hidden" aria-labelledby={`lead-${index}`}>
        <header className="border-b border-paper-line px-5 py-4 sm:px-7 sm:py-5">
          <div className="flex flex-wrap items-center gap-3">
            <p className="eyebrow">{String(index + 1).padStart(2, "0")}</p>
            <StateBadge lead={lead} />
            <span className="mono text-ink-faint">
              {lead.formationState} · {lead.channels.join(" + ")}
            </span>
          </div>
          <h2 id={`lead-${index}`} className="h2 mt-3 break-words">{lead.subject}</h2>
          <p className="body mt-2 max-w-prose">{lead.project}</p>
        </header>

        <dl className="grid gap-x-8 gap-y-5 px-5 py-5 sm:px-7 sm:py-6 lg:grid-cols-2">
          <Field label="Builder / team">{lead.builder}</Field>
          <Field label="Actual artifact">
            <span className="mono break-words text-[13px] text-ink-dim">{lead.artifact}</span>
          </Field>
          <Field label="Why it surfaced — and why company-first sourcing misses it">
            {lead.whyMissed}
          </Field>
          <Field label="Why now">{lead.whyNow}</Field>
          <Field label="Formation evidence">{lead.formationEvidence}</Field>
          <Field label="Technical-depth evidence">{lead.technicalDepth}</Field>
          <Field label="Strongest positive">{lead.strongestPositive}</Field>
          <Field label="Strongest negative">{lead.strongestNegative}</Field>
          <Field label="Array relevance">{lead.arrayRelevance}</Field>
          <Field label="What must be verified before an introduction">{lead.mustVerify}</Field>
        </dl>

        <div className="grid gap-px border-t border-paper-line bg-paper-line sm:grid-cols-2">
          <div className="bg-paper px-5 py-4 sm:px-7">
            <p className="eyebrow">The technical question</p>
            <p className="body mt-1.5 text-[14.5px]">{lead.technicalQuestion}</p>
          </div>
          <div className="bg-paper px-5 py-4 sm:px-7">
            <p className="eyebrow">The commercial / formation question</p>
            <p className="body mt-1.5 text-[14.5px]">{lead.commercialQuestion}</p>
          </div>
        </div>

        <p className="mono border-t border-paper-line px-5 py-3 text-[11.5px] text-ink-faint sm:px-7">
          signals {lead.signals.join(" · ")}
        </p>
      </article>
    </Reveal>
  );
}

export default function Current3() {
  return (
    <>
      <Section eyebrow="Source → output" title="Current 3"
        lead="Everything that currently survives evidence review — presented in the order the system surfaced it. This is not a global ranking: no case has a score, and the numbering carries no meaning beyond page order.">
        <p className="meta -mt-2 max-w-prose">
          The unit here is <span className="mono">INTRO_READY_AWU</span> — one builder or
          team lead that survives evidence review and is genuinely worth spending
          relationship capital on. The current count is{" "}
          <span className="mono text-ink">{r.introQueue.count}</span>. No introduction has
          been made and nobody named below has been contacted. One lead
          (multikernel/sandlock) is carried as <span className="mono">WATCH</span> with an
          explicit analyst override rather than <span className="mono">INTRO_READY</span>,
          because the company is further along than the Day-0 model assumes — the flag is
          preserved, not hidden.
        </p>
        <div className="mt-8 grid gap-8">
          {r.current3.map((lead, i) => <LeadRecord key={lead.subject} lead={lead} index={i} />)}
        </div>
        <p className="meta mt-8 max-w-prose">
          Public presentation is limited to professional artifacts: repositories, papers,
          project domains and organisation records. No emails, phones, locations or
          employment inferences appear anywhere in this product — see{" "}
          <Link href="/about/" className="text-exec-deep underline underline-offset-4">
            the privacy principles
          </Link>.
        </p>
      </Section>
    </>
  );
}
