import type { Metadata } from "next";
import Link from "next/link";
import { Section } from "@/components/Chrome";
import { research, DISCLAIMER } from "@/lib/research";

export const metadata: Metadata = {
  title: "About — DAY ZERO",
  description:
    "Why DAY ZERO exists, what it does not claim, its privacy principles, " +
    "AI disclosure, independence disclaimer, and how to reproduce it.",
};

export default function About() {
  return (
    <>
      <Section eyebrow="About" title="Why DAY ZERO exists"
        lead="Early-stage sourcing mostly ranks people by prestige and popularity, because those are the fields that are easy to query. DAY ZERO is an attempt to rank nothing and read everything — to surface builders from what they have verifiably constructed, then do the technical work an introduction deserves before anyone's time is spent.">
        <p className="body max-w-prose">
          It was built as an independent work sample for an AI Analyst application at Array
          Ventures — a role about sourcing technical founders at day zero and interrogating
          their architecture, not tracking announced rounds. The system is the argument:
          sourcing that starts from public artifacts, verification that reruns the claim,
          diligence that reads the code, and a methodology that publishes its own failures.
        </p>
        <p className="body mt-4 max-w-prose">
          What it does <strong className="text-text">not</strong> claim: that its tallies
          are investment performance; that a convergence pass predicts a good company; that
          any person analysed here is or should be raising; that absence of public evidence
          is evidence of absence; or that a system this young has validated its own
          usefulness. The <Link href="/methodology/" className="text-signal underline underline-offset-4">methodology page</Link>{" "}
          is deliberately the load-bearing one.
        </p>
      </Section>

      <Section eyebrow="Principles" title="Privacy">
        <ul className="grid gap-px overflow-hidden rounded border border-line bg-line sm:grid-cols-2">
          {[
            ["Professional artifacts only", "The project analyses repositories, papers, project domains and organisation records — what people build in public. It does not profile people."],
            ["No private identifiers", "No emails, no phone numbers, no precise locations, no personal biography. The export pipeline refuses to emit those fields, and tests enforce it."],
            ["No inferred employment changes", "Nobody is inferred to be leaving a job from silence, inactivity, a deleted post or a bio edit. Only explicit first-person public statements count."],
            ["No enrichment brokers", "No data brokers, people-search sites, facial recognition, WHOIS registrant lookups, or guessed username matching — excluded by written policy, not by omission."],
            ["A small public surface", "The full research universe (267 identities, 102 repositories, 1,586 evidence records) never reaches this site. Only the material needed for the analyses shown here is exported, and a build test verifies the rest stayed home."],
            ["Descriptive, not judgmental", "Attention metrics appear only as description. No person on this site is scored, ranked or labelled a good or bad founder."],
          ].map(([t, d]) => (
            <li key={t} className="bg-surface p-5">
              <h3 className="h3">{t}</h3>
              <p className="meta mt-2">{d}</p>
            </li>
          ))}
        </ul>
      </Section>

      <Section eyebrow="Disclosure" title="AI disclosure">
        <div className="panel-raised max-w-prose border-l-4 border-l-trace/60 p-6">
          <p className="body">
            <strong className="text-text">This project was built with substantial AI
            assistance.</strong> Claude Code assisted with research organisation, software
            implementation, structured extraction from public sources, classification
            assistance, testing, debugging, experiment implementation, drafting and
            synthesis — across every phase, including this website.
          </p>
          <p className="body mt-4">
            The boundaries that keep that honest: public sources are the factual evidence,
            and AI output is never treated as primary evidence. Observed facts are
            structurally distinct from inference in the data model, and every material
            claim carries an evidence state. Final sourcing selections and the
            recommendation on the Sandlock page are analyst judgments. Not every builder in
            the universe received equal manual diligence. And the system contains no global
            founder score — the schema has no column for one, and a test fails if one
            appears.
          </p>
        </div>
      </Section>

      <Section eyebrow="Disclaimer" title="Independence">
        <p className="body max-w-prose border-l-2 border-line pl-5 text-[15px]">
          {DISCLAIMER}
        </p>
        <p className="meta mt-4 max-w-prose">
          Nobody referenced in this research has been contacted about it. No introduction
          has been made. The financing statements on the diligence pages describe what is
          public, never what is true of any company’s actual capitalisation.
        </p>
      </Section>

      <Section eyebrow="System" title="Architecture & reproduction">
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="panel p-5">
            <p className="eyebrow">Architecture</p>
            <div className="mono mt-3 grid gap-1 text-[12.5px] leading-relaxed text-dim">
              <span>Python research pipeline (canonical)</span>
              <span className="text-faint">└─ frozen rules · evidence store · experiments</span>
              <span>scripts/build_frontend_data.py</span>
              <span className="text-faint">└─ validated public export · forbidden-key guard</span>
              <span>Next.js static export (this site)</span>
              <span className="text-faint">└─ no runtime DB · no API · no auth · no AI calls</span>
            </div>
            <p className="meta mt-3 text-[13px]">
              Every research value on this site originates from the canonical export —
              components hard-code no numbers, and drift tests compare the built HTML
              against the export.
            </p>
          </div>
          <div className="panel p-5">
            <p className="eyebrow">Reproduction</p>
            <p className="meta mt-3 text-[13px]">
              The repository contains the frozen rule manifests (hashed), the pre-registered
              experiment protocol, the dataset manifest, all validation outputs, and the
              test suite that guards them. The Headroom experiment reruns from its
              committed protocol; the sourcing validations rerun against the frozen rules;
              the export regenerates deterministically. The commit hashes on the{" "}
              <Link href="/methodology/" className="text-signal underline underline-offset-4">
                methodology page
              </Link>{" "}
              are the audit trail.
            </p>
            <p className="mono mt-3 break-all text-[11px] text-faint">
              export: {research.generatedFrom ?? "outputs/**"}
            </p>
          </div>
        </div>
      </Section>
    </>
  );
}
