import type { Metadata } from "next";
import Link from "next/link";
import { Section } from "@/components/Chrome";
import { Hash } from "@/components/Evidence";
import { Reveal } from "@/components/Reveal";
import { research } from "@/lib/research";

export const metadata: Metadata = {
  title: "Methodology — DAY ZERO",
  description:
    "The full rule evolution: frozen v1, its failure, the v2 repair, an unseen validation " +
    "cohort — and the new weakness that cohort exposed. Nothing was patched after the fact.",
};

const r = research;
const m = r.methodology;

function Tally({ t, dimZero = false }: { t: Record<string, number>; dimZero?: boolean }) {
  const order = ["PASS", "PARTIAL", "MISS", "UNKNOWN"] as const;
  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {order.map((k) => {
        const v = t[k] ?? 0;
        return (
          <span key={k}
            className={`mono rounded border px-2 py-1 text-[11.5px] ${
              v === 0 && dimZero ? "border-lineSoft text-faint" : "border-line text-dim"}`}>
            <span className={v > 0 && k === "PASS" ? "text-signal" : v > 0 && k === "MISS" ? "text-absent" : "text-text"}>
              {v}
            </span>{" "}{k}
          </span>
        );
      })}
    </div>
  );
}

const TIMELINE = [
  { commit: "phase1", label: "Phase 1 — ontology, evidence philosophy, initial sourcing hypothesis", detail: "Signal ontology, evidence states, privacy rules, the no-score rule. No collection yet." },
  { commit: "commit_a", label: "v1 rules frozen — before any validation ran", detail: "Eligibility, independence and convergence rules hashed into a frozen manifest." },
  { commit: "commit_b", label: "v1 holdout run against the frozen rules", detail: "0 PASS / 2 PARTIAL / 4 MISS / 4 UNKNOWN. The failure is committed, not retried." },
  { commit: "commit_c", label: "Headroom reproduction protocol pre-registered", detail: "Claims, thresholds, baselines and verdict rules hashed before any measurement." },
  { commit: "commit_d", label: "v2 rules designed from the v1 diagnosis and frozen", detail: "Independence redefined as modalities + distinct events; stricter on four axes." },
  { commit: "commit_e", label: "Reproduction + deep diligence executed", detail: "Headroom: PARTIALLY REPRODUCED. Sandlock: advance to founder conversation." },
  { commit: "commit_f", label: "Unseen validation cohort frozen — before evidence retrieval", detail: "Nine cases selected deterministically from portfolio history v2 had never touched." },
  { commit: "commit_g", label: "Unseen validation + identity audit run", detail: "2 PASS / 0 PARTIAL / 1 MISS / 6 UNKNOWN — and a new failure mode found." },
] as const;

export default function Methodology() {
  return (
    <>
      <Section eyebrow="Method" title="Rules that freeze before they run"
        lead="Every rule set and every cohort in this project was hashed and committed before the outcome it governs existed. That ordering is what makes a failure a result instead of an embarrassment — and this page is the story of one real failure and what it changed.">
        <p className="body max-w-prose">
          A caution before any numbers: the tallies below measure whether frozen sourcing
          rules would have surfaced known Array portfolio companies from public evidence
          available before their announcement dates. Every case is a company with a known
          outcome, so hindsight bias is structural.{" "}
          <strong className="text-text">None of these figures is investment performance,
          precision, recall, or a win rate</strong> — and the three runs below are not
          comparable to each other as performance, because each answers a different
          question.
        </p>
      </Section>

      {/* ── THREE RESULTS ────────────────────────────────────────────────── */}
      <Section eyebrow="The record" title="Three runs, three different questions">
        <div className="grid gap-4 lg:grid-cols-3">
          <Reveal>
            <div className="panel h-full p-5">
              <p className="eyebrow">Phase 2 · v1 · FROZEN, THEN RUN</p>
              <h3 className="h3 mt-2">The system failed</h3>
              <Tally t={m.v1.tally} />
              <p className="meta mt-3">
                Ten historical cases; the rules had never seen any of them.{" "}
                <strong className="text-dim">Zero passes.</strong> The diagnosis: v1 defined
                independence as <em>different hostnames</em>, so a builder whose entire
                verifiable life is on GitHub — organisation creation, sustained construction,
                collaborators, releases — collapsed into “one source” and could never
                converge.
              </p>
            </div>
          </Reveal>
          <Reveal delay={60}>
            <div className="panel h-full p-5">
              <p className="eyebrow">Phase 3 · v2 · POST-HOC EXPLORATORY</p>
              <h3 className="h3 mt-2">The rules changed</h3>
              <Tally t={m.v2Exploratory.tally} />
              <p className="meta mt-3">
                v2 was frozen <em>before</em> this rerun — but the cohort is the same ten
                cases that motivated the redesign, so this result is labelled exploratory
                and can prove nothing on its own. It is shown because hiding it would
                misstate how the repair was developed.
              </p>
            </div>
          </Reveal>
          <Reveal delay={120}>
            <div className="panel h-full border-l-2 border-l-signalDim p-5">
              <p className="eyebrow">Phase 4A · v2 · UNSEEN COHORT</p>
              <h3 className="h3 mt-2">The real test</h3>
              <Tally t={m.unseen.tally} />
              <p className="meta mt-3">
                {m.unseen.cohortSize} cases v2’s design had never touched, selected
                deterministically and committed before any evidence was retrieved.
                Out-of-sample with respect to <em>rule development</em> — not to venture
                outcomes, since every case is still a known portfolio company.
              </p>
            </div>
          </Reveal>
        </div>
      </Section>

      {/* ── V1 → V2 ─────────────────────────────────────────────────────── */}
      <Section eyebrow="The repair" title="What v2 actually changed"
        lead="The failure was not that v1 was too strict. It was that v1 measured independence on the wrong axis — and the repair had to get stricter, not looser, to be defensible.">
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="panel p-5">
            <p className="eyebrow">v1 · independence = hostnames</p>
            <p className="body mt-2 text-[14.5px]">
              Two pieces of evidence were independent if they came from different hostnames.
              GitHub org creation in 2024, a shipped system in 2025, and outside
              collaborators in 2026 all counted as <em>one</em> channel — while a repo plus
              a tweet about the repo counted as two.
            </p>
            <p className="mono mt-4 break-all text-[11px] text-faint">
              v1 {r.hashes.v1Frozen}
            </p>
          </div>
          <div className="panel border-l-2 border-l-signalDim p-5">
            <p className="eyebrow">v2 · independence = modalities + events</p>
            <p className="body mt-2 text-[14.5px]">
              Independence became <em>evidence modalities</em> (construction, formation,
              identity, collaboration) counted over <em>distinct dated events</em> — while
              tightening four other axes at once: a minimum modality count, a minimum event
              count, mandatory construction evidence, and mandatory temporal spread.
            </p>
            <p className="mono mt-4 break-all text-[11px] text-faint">
              v2 {r.hashes.v2Rules}
            </p>
          </div>
        </div>
        <p className="body mt-5 max-w-prose">
          The check that keeps the repair honest: <strong className="text-text">negative
          controls</strong>. All {m.negativeControls.v2Controls.length} v1-rejected control
          repositories — curated lists, hype repos, thin wrappers — were re-run under v2.{" "}
          <span className="mono text-text">{m.negativeControls.v2Regressions}</span> were
          incorrectly promoted. Loosening that let junk through would have been a worse
          failure than the one being fixed.
        </p>
      </Section>

      {/* ── UNSEEN VALIDATION ────────────────────────────────────────────── */}
      <Section eyebrow="Phase 4A" title="The unseen test"
        lead="Nine eligible portfolio companies v2 had never seen, ordered by a deterministic rule — SHA-256 of the v2 rule hash joined with the case ID, sorted ascending — frozen in a commit, and only then researched. Binding the ordering to the v2 hash means it could not be chosen after the fact without visibly changing v2 itself. Case-by-case:">
        <div className="scroll-x rounded border border-line">
          <table className="text-[13px]">
            <thead>
              <tr className="border-b border-line bg-raised">
                <th className="px-4 py-2.5">Case</th>
                <th className="px-4 py-2.5">Company</th>
                <th className="px-4 py-2.5">Cutoff</th>
                <th className="px-4 py-2.5">Verdict</th>
                <th className="px-4 py-2.5">Why</th>
              </tr>
            </thead>
            <tbody>
              {[...(m.unseen.cases as { case_id: string; company: string; cutoff_date: string;
                  verdict: string; reason: string; modalities?: string[] }[])]
                .sort((a, b) => a.case_id.localeCompare(b.case_id))
                .map((c) => (
                <tr key={c.case_id} className="border-b border-lineSoft align-top last:border-b-0">
                  <td className="mono px-4 py-2.5 text-faint">{c.case_id}</td>
                  <td className="px-4 py-2.5 font-semibold text-text">{c.company}</td>
                  <td className="mono whitespace-nowrap px-4 py-2.5 text-dim">{c.cutoff_date}</td>
                  <td className={`mono whitespace-nowrap px-4 py-2.5 text-[11.5px] ${
                    c.verdict === "PASS" ? "text-signal" : c.verdict === "MISS" ? "text-absent" : "text-unknown"}`}>
                    {c.verdict === "PASS" ? "● " : c.verdict === "MISS" ? "✕ " : "○ "}{c.verdict}
                  </td>
                  <td className="px-4 py-2.5 text-dim">{c.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="meta mt-4 max-w-prose">
          {m.unseen.noStatistic} The six UNKNOWNs are themselves a finding: under v2’s
          conservative identity rules, no GitHub organisation could be verifiably linked to
          those companies pre-announcement — name-only matches may not merge. That is the
          structural blindness of a GitHub-led system stated as data: companies that form
          without a public construction trail are invisible to it, and pretending otherwise
          would require exactly the fuzzy matching the rules forbid.
        </p>
      </Section>

      {/* ── PERSPECTIVE AI ───────────────────────────────────────────────── */}
      <Section eyebrow="What broke next" title="The unseen test found a new weakness">
        <Reveal>
          <div className="panel-raised border-l-4 border-l-claim p-6">
            <p className="eyebrow">Perspective AI · U01 · PASS — and that is the problem</p>
            <p className="body mt-3 max-w-prose">
              Perspective AI passed the v2 convergence gate on a{" "}
              <strong className="text-text">marketing/content repository</strong> — SCSS, no
              licence, no meaningful engineering surface. Every convergence check was
              legitimately satisfied: the evidence was independent, multi-modal, temporally
              spread, and included construction events. The pass is valid under the frozen
              rules, and the rules are wrong.
            </p>
            <p className="body mt-3 max-w-prose">
              The diagnosis: v2 repaired evidence <em>independence</em>, but it does not
              require the evidence to be <em>technically deep</em> at the convergence
              stage. Depth signals exist elsewhere in the system — they are simply not
              wired into this gate.
            </p>
            <p className="body mt-3 max-w-prose">
              <strong className="text-text">The rule was not changed after seeing the
              result.</strong> A technical-depth eligibility requirement at the convergence
              gate is the leading candidate for a future v3 — and no v3 has been designed,
              frozen or validated, so none is claimed. The weakness stands in the record
              exactly as the v1 failure does.
            </p>
          </div>
        </Reveal>
      </Section>

      {/* ── GIT TIMELINE ─────────────────────────────────────────────────── */}
      <Section eyebrow="Proof" title="The commit history is the argument"
        lead="Freeze-before-measure only means something if the ordering is verifiable. Every step below is a real commit in the repository, in this order.">
        <ol className="grid gap-0">
          {TIMELINE.map((t, i) => (
            <li key={t.commit} className="relative flex gap-4 pb-6 last:pb-0">
              <div className="flex flex-col items-center">
                <span className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full border-2 ${
                  i === 1 || i === 3 || i === 6 ? "border-signal bg-signal/20" : "border-line bg-raised"}`}
                  aria-hidden="true" />
                {i < TIMELINE.length - 1 && <span className="w-px flex-1 bg-line" aria-hidden="true" />}
              </div>
              <div className="min-w-0 pb-1">
                <p className="text-[14px] font-semibold text-text">{t.label}</p>
                <p className="meta mt-1 text-[13px]">{t.detail}</p>
                <p className="mono mt-1.5 break-all text-[11px] text-faint">
                  {r.commits[t.commit] ?? "—"}
                </p>
              </div>
            </li>
          ))}
        </ol>
        <div className="panel mt-6 p-5">
          <p className="eyebrow">The three hashes that matter</p>
          <div className="mt-3 grid gap-2 text-[13px]">
            <Hash label="v1 rules (frozen before v1 holdout)" value={r.hashes.v1Frozen} />
            <Hash label="v2 rules (frozen before v2 rerun and Phase 4)" value={r.hashes.v2Rules} />
            <Hash label="unseen cohort freeze commit" value={m.unseen.freezeCommit} />
          </div>
        </div>
      </Section>

      {/* ── HONESTY LEDGER ───────────────────────────────────────────────── */}
      <Section eyebrow="Accounting" title="What was and wasn't measured">
        <div className="grid gap-3 lg:grid-cols-2">
          <div className="panel p-5">
            <p className="eyebrow">Human analyst active time</p>
            <p className="mono mt-2 text-lg text-text">NOT_MEASURED</p>
            <p className="meta mt-2 text-[13px]">
              No human ran the review timer during Phase 4, so no number is reported.
              Claude Code and tool wall-clock time is machine time, and it is never
              relabelled as human analyst time. The timer instrument exists and is tested;
              it produces a figure only when a human actually starts and stops it.
            </p>
          </div>
          <div className="panel p-5">
            <p className="eyebrow">What a defensible v2 means</p>
            <p className="meta mt-2 text-[13px]">
              v2 survives Phase 4A as a design: it converged in two of the three cases
              where identity could be resolved, promoted zero negative controls, and
              failed in a way that is documented, diagnosed and left unpatched — including
              one of its own two passes being the failure. It does
              not survive as a finished system — the Perspective AI gap and the six
              identity-unresolvable cases bound what it can currently claim. Both statements
              belong in the record; see also{" "}
              <Link href="/signals/" className="text-signal underline underline-offset-4">
                the identity audit
              </Link>{" "}
              for the assumption Phase 4 revised.
            </p>
          </div>
        </div>
      </Section>
    </>
  );
}
