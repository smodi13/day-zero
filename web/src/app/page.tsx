import Link from "next/link";
import { Section } from "@/components/Chrome";
import { Ambient } from "@/components/Ambient";
import { EvidenceBadge, Hash, Stat, Verdict } from "@/components/Evidence";
import { HeroFlow, HeroFlowCompact } from "@/components/HeroFlow";
import { Reveal, RevealStagger } from "@/components/Reveal";
import { research } from "@/lib/research";

const r = research;

function Tally({ t }: { t: Record<string, number> }) {
  const order = ["PASS", "PARTIAL", "MISS", "UNKNOWN"];
  return (
    <div className="mono mt-3 flex flex-wrap gap-x-4 gap-y-1 text-ink-dim">
      {order.map((k) => (
        <span key={k}>
          <span className="text-ink">{t[k] ?? 0}</span>&nbsp;{k}
        </span>
      ))}
    </div>
  );
}

export default function Home() {
  const hr = r.headroom;
  const m = r.methodology;
  const json = hr.categories.structured_json;
  const coding = hr.categories.coding_context;

  return (
    <>
      {/* ── HERO ─────────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden border-b border-paper-line bg-paper-card">
        <Ambient />
        <div className="relative mx-auto grid max-w-content items-center gap-10 px-4 pb-14 pt-14 sm:px-6 sm:pb-20 sm:pt-20 lg:grid-cols-[minmax(0,1fr)_minmax(340px,440px)] lg:gap-12">
          {/* copy column — transform-only entrance over an opaque base */}
          <div>
            <p className="eyebrow dz-enter dz-d1">
              Founder Formation &amp; Technical Diligence Engine
            </p>
            <h1 className="h1 dz-enter dz-d2 mt-4">
              Find the builder before the round.<br />
              <span className="text-exec-deep">Test the hard claim</span> before the meeting.
            </h1>
            <p className="lede dz-enter dz-d3 mt-6 max-w-prose">
              DAY ZERO turns public technical artifacts into a small queue of
              founder-introduction candidates, then pressure-tests what actually matters:
              it reproduces the technical claim against a real baseline, and reads the
              architecture closely enough to say what is genuinely hard and what is only
              implementation work.
            </p>
            <p className="meta dz-enter dz-d4 mt-5 max-w-prose">
              It assigns no founder score, keeps no leaderboard, and has contacted nobody.
              When its own sourcing rules failed, the failure was published rather than
              patched over.
            </p>
            <div className="dz-enter dz-d5 mt-8 flex flex-wrap gap-3">
              <Link href="/diligence/sandlock/"
                    className="card-interactive rounded bg-exec px-4 py-2 text-[14px] font-medium text-white hover:bg-exec-deep">
                Read the flagship diligence <span className="arrow" aria-hidden="true">→</span>
              </Link>
              <Link href="/methodology/"
                    className="card-interactive rounded border border-paper-line bg-paper-card px-4 py-2 text-[14px] font-medium">
                See where it failed <span className="arrow" aria-hidden="true">→</span>
              </Link>
            </div>
            <dl className="dz-enter dz-d6 mt-10 grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4">
              {[
                [String(r.scale.repositories), "repositories in the universe"],
                [String(r.introQueue.count), "INTRO_READY_AWU"],
                [`${hr.dataset.sampleCount}`, "reproduction samples"],
                [String(m.unseen.cohortSize), "unseen validation cases"],
              ].map(([v, l]) => (
                <div key={l}>
                  <dt className="font-mono text-lg font-semibold tabular-nums text-exec-deep">{v}</dt>
                  <dd className="meta">{l}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* system diagram — its own column, so it can never sit under the copy */}
          <div className="dz-enter dz-d7 lg:pl-2">
            <div className="hidden lg:block"><HeroFlow /></div>
            <div className="lg:hidden"><HeroFlowCompact /></div>
          </div>
        </div>
      </section>

      {/* ── CURRENT 3 ────────────────────────────────────────────────────── */}
      <Section eyebrow="Stage · Source" title="Current 3"
        lead="Three builders that survived evidence review and are worth spending relationship capital on. Not a ranking, not a top-N list — this is everything that cleared the bar, and the bar is not lowered to reach three.">
        <RevealStagger className="grid gap-3 md:grid-cols-3" step={80}>
          {r.current3.map((lead, i) => (
            <article key={lead.subject} className="panel card-interactive h-full p-5">
              <p className="eyebrow">{String(i + 1).padStart(2, "0")}</p>
              <h3 className="h3 mt-2 break-words">{lead.subject}</h3>
              <p className="meta mt-2">{lead.project}</p>
              <p className="mono mt-3 text-ink-faint">
                {lead.formationState} · {lead.channels.join(" + ")}
              </p>
            </article>
          ))}
        </RevealStagger>
        <p className="meta mt-4">
          <span className="mono text-ink">{r.introQueue.count}</span> INTRO_READY_AWU —
          the operating unit is one lead that survives review, not one profile processed.
          No introduction has been made.{" "}
          <Link href="/current-3/" className="font-medium text-exec-deep underline decoration-exec/30 underline-offset-4 hover:decoration-exec">
            Full records <span className="arrow" aria-hidden="true">→</span>
          </Link>
        </p>
      </Section>

      {/* ── SANDLOCK ─────────────────────────────────────────────────────── */}
      <Section eyebrow="Stage · Diligence" title="Flagship: sandlock"
        lead="A Linux process sandbox that confines untrusted agent code with Landlock, seccomp-bpf and seccomp user notification — no root, no image, no hypervisor. Read at the level of its trust boundary, not its README.">
        <Reveal>
          <Verdict label={r.sandlock.recommendation.replaceAll("_", " ")} kind="signal"
            sub={<>
              {r.sandlock.financingWording}{" "}
              <EvidenceBadge state="NOT_FOUND" /> — and that is a statement about what is
              public, not a claim that the company is bootstrapped.
            </>} />
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <Stat value="Landlock + seccomp" label="Isolation boundary" note="Shared host kernel" />
            <Stat value="Kernel vulnerabilities" label="Excluded from threat model"
              note="Stated by the project itself" />
            <Stat value={r.sandlock.attention.stars.toLocaleString()} label="GitHub stars"
              note="Descriptive only — never a surfacing input" />
          </div>
          <p className="body mt-5 max-w-prose">
            The interesting layer is not the sandbox. Traditional isolation answers{" "}
            <em>can this process reach that resource</em>. A prompt-injected agent asks a
            different question: <em>should this legitimate agent use this legitimate
            credential for this legitimate operation, against this destination, right now?</em>{" "}
            A VM boundary does not answer that. sandlock&rsquo;s HTTP-level policy and
            supervisor-held credentials try to.
          </p>
          <Link href="/diligence/sandlock/"
            className="mt-5 inline-block font-medium text-exec-deep underline decoration-exec/30 underline-offset-4 hover:decoration-exec">
            Full diligence — architecture, threat model, competitive alternatives{" "}
            <span className="arrow" aria-hidden="true">→</span>
          </Link>
        </Reveal>
      </Section>

      {/* ── HEADROOM ─────────────────────────────────────────────────────── */}
      <Section eyebrow="Stage · Verify" title="The baseline is part of the claim"
        lead="A published compression claim, tested against a pre-registered protocol on 35 samples the author did not choose. The protocol was committed before any measurement was taken.">
        <Reveal>
          <Verdict label={hr.verdict.replaceAll("_", " ")} kind="mixed"
            sub="Three of five pre-registered claims supported, two not. Both halves matter." />
          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Stat value={`${json.vsRaw.median.toFixed(2)}%`} label="JSON vs raw" note="median" />
            <Stat value={`${json.vsMinified.median.toFixed(2)}%`} label="JSON vs minified"
              note="the comparison that matters" />
            <Stat value={`${coding.vsRaw.median.toFixed(2)}%`} label="Coding context vs raw"
              note="every quantile" />
            <Stat value={hr.retention.toFixed(4)} label="Probe retention"
              note={`${hr.errors} transformation errors`} />
          </div>
          <p className="body mt-5 max-w-prose">
            Measured against pretty-printed input the saving looks large. Measured against
            trivial whitespace minification — which costs nothing and takes one line —
            most of it is still there, but not all: minification alone supplies{" "}
            <span className="mono text-ink">{json.minifyOnlyVsRaw.median.toFixed(2)}%</span> of the{" "}
            <span className="mono text-ink">{json.vsRaw.median.toFixed(2)}%</span> headline.
            The compression is real, lossless, and narrower than the marketing.
          </p>
          <Link href="/lab/headroom/"
            className="mt-5 inline-block font-medium text-exec-deep underline decoration-exec/30 underline-offset-4 hover:decoration-exec">
            Full reproduction — claims, baselines, distributions, failures{" "}
            <span className="arrow" aria-hidden="true">→</span>
          </Link>
        </Reveal>
      </Section>

      {/* ── LEARN ────────────────────────────────────────────────────────── */}
      <Section eyebrow="Stage · Learn" title="The system failed, then the rules changed"
        lead="Most sourcing projects publish the run that worked. This one publishes the run that did not, and keeps it published beside the repair.">
        <RevealStagger className="grid gap-4 lg:grid-cols-3" step={80}>
          {[
            <div key="v1" className="panel h-full p-5">
              <p className="eyebrow">v1 · frozen, then run</p>
              <h3 className="h3 mt-2">Zero passes</h3>
              <Tally t={m.v1.tally} />
              <p className="meta mt-3">
                The strongest true positive in the cohort failed on a rule built to stop
                false positives: all of its evidence lived on GitHub, and v1 counted that
                as one source.
              </p>
              <p className="mono mt-3 text-ink-faint">v1 {r.hashes.v1Frozen.slice(0, 12)}…</p>
            </div>,
            <div key="v2" className="panel h-full p-5">
              <p className="eyebrow">v2 · post-hoc exploratory</p>
              <h3 className="h3 mt-2">Independence redefined</h3>
              <Tally t={m.v2Exploratory.tally} />
              <p className="meta mt-3">
                Independence became evidence <em>modalities and distinct events</em> rather
                than distinct hostnames — while getting stricter on four of five axes.
                Same cohort, so this proves nothing on its own.
              </p>
              <p className="mono mt-3 text-ink-faint">v2 {r.hashes.v2Rules.slice(0, 12)}…</p>
            </div>,
            <div key="unseen" className="panel h-full border-l-2 border-l-exec p-5">
              <p className="eyebrow">Unseen cohort · out-of-sample</p>
              <h3 className="h3 mt-2">Nine cases v2 never saw</h3>
              <Tally t={m.unseen.tally} />
              <p className="meta mt-3">
                Selected deterministically and committed <em>before</em> any evidence was
                retrieved. Out-of-sample with respect to rule design — not to venture
                performance, since every case is a known portfolio company.
              </p>
              <p className="mono mt-3 text-ink-faint">
                freeze {m.unseen.freezeCommit.slice(0, 12)}…
              </p>
            </div>,
          ]}
        </RevealStagger>

        <Reveal>
          <div className="panel-raised mt-6 border-l-4 border-l-claim p-5 sm:p-6">
            <p className="eyebrow">What the unseen test broke next</p>
            <h3 className="h3 mt-2">
              Perspective AI passed the v2 gate on a marketing repository
            </h3>
            <p className="body mt-3 max-w-prose">
              It cleared convergence using a content repo — SCSS, no licence. v2 verifies
              that evidence is <em>independent</em>; it does not require that the evidence
              is <em>technically deep</em> at the convergence stage. That is a real design
              weakness, and it was found by the very cohort meant to test the repair.
            </p>
            <p className="meta mt-3 max-w-prose">
              The rule was not changed after seeing the result. A depth requirement at the
              convergence gate is a candidate for a future v3 — and no v3 has been
              validated, so none is claimed.
            </p>
          </div>
        </Reveal>
      </Section>

      {/* ── PRINCIPLES ───────────────────────────────────────────────────── */}
      <Section eyebrow="Method" title="Six rules the system runs on">
        <RevealStagger className="grid gap-3 sm:grid-cols-2" step={60}>
          {[
            ["No global score", "No founder score, no probability of founding, no leaderboard. Nine technical dimensions are assessed separately and never combined. The database schema has no score column, and a test enforces it."],
            ["Attention is not construction", "Stars, forks and followers are recorded as description and are barred from every surfacing decision. The measured spread between attention and construction runs four orders of magnitude."],
            ["Evidence has a state", "Observed, project claim, inferred, unknown, not found. A builder's own post is authoritative that they said something — never that it is true."],
            ["Freeze before you measure", "Rules and cohorts are hashed and committed before the results they govern exist. The git history is the proof, not the prose."],
            ["Career stage is optional", "Two thirds of builders cannot be classified as young builder or operator-founder without guessing, so they are left unclassified. The eligibility rules cannot read the field at all."],
            ["No inferred departures", "Nobody is ever inferred to be leaving a job from silence, inactivity, a deleted post or a bio edit. Only an explicit public statement counts."],
          ].map(([t, d]) => (
            <div key={t} className="panel card-quiet h-full p-5">
              <h3 className="h3">{t}</h3>
              <p className="meta mt-2">{d}</p>
            </div>
          ))}
        </RevealStagger>
      </Section>

      <Section>
        <Reveal>
          <div className="panel p-5 sm:p-6">
            <p className="eyebrow">Verify the sequence yourself</p>
            <div className="mt-3 grid gap-2 text-[13px]">
              <Hash label="v1 rules frozen" value={r.hashes.v1Frozen} />
              <Hash label="v2 rules frozen" value={r.hashes.v2Rules} />
              <Hash label="unseen cohort freeze commit" value={m.unseen.freezeCommit} />
            </div>
            <p className="meta mt-4 max-w-prose">
              Each hash predates the result it governs, and the commit order shows it.
              {" "}<Link href="/methodology/" className="font-medium text-exec-deep underline decoration-exec/30 underline-offset-4 hover:decoration-exec">
                See the full timeline <span className="arrow" aria-hidden="true">→</span>
              </Link>
            </p>
          </div>
        </Reveal>
      </Section>
    </>
  );
}
