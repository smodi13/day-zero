import type { Metadata } from "next";
import Link from "next/link";
import { Section } from "@/components/Chrome";
import { BoundaryDiagram } from "@/components/BoundaryDiagram";
import { SemanticPolicy } from "@/components/SemanticPolicy";
import { EvidenceBadge, Verdict, type EvidenceState } from "@/components/Evidence";
import { Reveal } from "@/components/Reveal";
import { SourceLedger, SRef } from "@/components/Sources";
import { research } from "@/lib/research";

export const metadata: Metadata = {
  title: "Sandlock — technical diligence",
  description:
    "Outside-in technical diligence on multikernel/sandlock: architecture, trust boundary, " +
    "threat model, competitive alternatives, and what public evidence cannot establish.",
};

const s = research.sandlock;
const lead = research.current3.find((l) => l.subject === "multikernel/sandlock")!;

const IN_SCOPE = [
  ["Filesystem escape", "only paths reachable through granted Landlock rules; grants are recursive, denials override"],
  ["Unapproved network egress", "default-deny: with no rules, Landlock refuses every TCP connect; UDP, ICMP and raw-socket creation are refused at the seccomp layer"],
  ["Exfiltration on an approved host", "HTTP rules match method, host and path — “an agent allowed one endpoint cannot repurpose the connection”"],
  ["Credential theft by the workload", "the secret stays in the supervisor and is attached after the ACL check; an env: source is stripped from the child"],
  ["Privilege escalation via setuid", "NO_NEW_PRIVS before the filter"],
  ["Reaching sibling processes", "Landlock ABI v6 scopes deny abstract UNIX-socket connections and signals outside the sandbox"],
  ["Host resource exhaustion", "memory, process count, open files, CPU share and CoW disk usage are capped"],
  ["Unintended writes", "copy-on-write stages writes and discards them on error"],
] as const;

const OUT_OF_SCOPE = [
  ["Kernel vulnerabilities", "“The workload runs on your kernel. An escalation bug in a permitted syscall defeats the sandbox. This is the price of no hypervisor.” — stated by the project, in bold"],
  ["Hardware side channels", "Spectre-class and cache timing; “CPU pinning reduces sharing but is not a mitigation”"],
  ["A policy that grants too much", "“Sandlock enforces the policy you wrote, not the one you meant”"],
  ["A hostile launcher", "an attacker who already controls the process that starts Sandlock controls the policy"],
  ["The workload starving itself", "limits protect the host, not the workload's own progress"],
] as const;

const SCENARIOS = [
  ["Generated code tries to read ~/.ssh", "BLOCKED", "Landlock, kernel-evaluated"],
  ["Malicious dependency exfiltrates to an attacker host", "BLOCKED", "default-deny egress; on an approved host, the HTTP method/host/path ACL"],
  ["Prompt-injected tool call tries to POST the API key", "BLOCKED", "the key never enters the child's address space — the most agent-specific guarantee in the product"],
  ["Workload attempts setuid escalation", "BLOCKED", "NO_NEW_PRIVS"],
  ["Workload signals a sibling process", "BLOCKED*", "on ABI v6; not blocked on an older kernel unless allow_degraded was chosen deliberately"],
  ["Kernel LPE in a permitted syscall", "NOT DEFENDED", "full host compromise — stated by the project"],
  ["Operator writes --net-allow '*'", "NOT DEFENDED", "stated: policy correctness is the operator's problem"],
  ["Attacker controls the launching process", "NOT DEFENDED", "stated"],
] as const;

function H3({ children }: { children: React.ReactNode }) {
  return <h3 className="h3 mt-8">{children}</h3>;
}

export default function Sandlock() {
  return (
    <>
      {/* ── VERDICT ──────────────────────────────────────────────────────── */}
      <Section eyebrow="Diligence · multikernel/sandlock" title="Sandlock">
        <Verdict label={s.recommendation.replaceAll("_", " ")} kind="signal"
          sub={<>
            <strong className="text-ink">{s.financingWording}</strong>{" "}
            <EvidenceBadge state="NOT_FOUND" /> That is a statement about what is public —
            not a claim that the company is bootstrapped, which would require evidence this
            research does not have. <em>Invest</em> is deliberately absent from the verdict
            vocabulary ({s.recommendationVocabulary.map((v) => v.replaceAll("_", " ")).join(" / ")}):
            it is unavailable from outside-in public work. Array has not reviewed this
            company; this is an independent research exercise.
          </>} />
        <p className="body mt-6 max-w-prose">
          The recommendation rests on three things public evidence establishes and one it
          does not. Established: the technical work is real and unusually well-executed;
          the threat model is stated more honestly than most funded security companies
          state theirs; and the construction pattern looks like durable systems engineering
          rather than a demo. Not established: whether anyone has ever tried to break it,
          and whether anyone pays. Both unknowns are conversation-resolvable — which is
          exactly what makes this a founder conversation rather than a pass or a watch.
        </p>
      </Section>

      {/* ── WHY IT SURFACED ──────────────────────────────────────────────── */}
      <Section eyebrow="01" title="Why it surfaced">
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="panel p-5">
            <p className="eyebrow">Why the system saw it</p>
            <p className="body mt-2 text-[14.5px]">{lead.whyNow}</p>
            <p className="meta mt-3">{lead.strongestPositive}</p>
          </div>
          <div className="panel p-5">
            <p className="eyebrow">Why company-first sourcing misses it</p>
            <p className="body mt-2 text-[14.5px]">{lead.whyMissed}</p>
            <p className="meta mt-3">
              Carried as <span className="mono">WATCH · analyst override</span>:{" "}
              {lead.strongestNegative}
            </p>
          </div>
        </div>
      </Section>

      {/* ── WHAT SANDLOCK IS + ARCHITECTURE ─────────────────────────────── */}
      <Section eyebrow="02" title="What Sandlock is"
        lead="A lightweight Linux process sandbox in Rust (Apache-2.0) that confines a command's filesystem, network, syscalls and resources using Landlock, seccomp-bpf and seccomp user notification — no root, no image build, no container runtime, no hypervisor.">
        <p className="body max-w-prose">
          Distribution is unusually complete for a project this young: a CLI, an OCI runtime
          shim for containerd / CRI-O / Kubernetes, a C ABI, and Python and Go SDKs{" "}
          <SRef id="S2" />. The codebase is 3.3&nbsp;MB of Rust <SRef id="S15" />, and the
          integration-test files are comparable in size to the modules they test{" "}
          <SRef id="S2" /> — an unusual and good sign in a security project.
        </p>

        <H3>The organising idea</H3>
        <blockquote className="panel-raised mt-3 max-w-prose border-l-2 border-l-exec px-5 py-4">
          <p className="body italic">
            “Static, input-independent policy is compiled into kernel-enforced rules, while
            a narrow supervisor handles runtime-dependent decisions and virtualized
            effects.”
          </p>
          <footer className="meta mt-2">— the paper’s abstract, arXiv:2605.26298 <SRef id="S5" /></footer>
        </blockquote>
        <p className="body mt-4 max-w-prose">
          That sentence is the whole architecture, and it is the right frame for evaluating
          it. Anything expressible as a static rule goes to the kernel, where it is fast and
          TOCTOU-immune. Anything requiring a runtime decision goes to a userspace
          supervisor, which is slower and more trusted. The design question is where that
          line sits — and the hard engineering lives on the supervisor side:{" "}
          <span className="mono">cow/seccomp.rs</span> alone is 319&nbsp;KB, the largest
          file in the repository <SRef id="S2" />.
        </p>

        <H3>Beyond a conventional sandbox</H3>
        <p className="body mt-3 max-w-prose">
          Filesystem and syscall confinement is table stakes. The differentiated surface{" "}
          <SRef id="S3" /> <SRef id="S4" />: an HTTP-level ACL on method + host + path via a
          transparent proxy; destination-IP and CIDR allowlists with no DNS; credential
          injection where the secret stays in the supervisor and is attached{" "}
          <em>after</em> the ACL check; a copy-on-write working directory with transactional
          commit/abort; deterministic execution (frozen time, seeded randomness); and a
          handler API on any syscall where a custom handler “can extend confinement but
          never relax it” <SRef id="S6" />.
        </p>
      </Section>

      {/* ── TRUST BOUNDARY ───────────────────────────────────────────────── */}
      <Section eyebrow="03" title="The trust boundary"
        lead="Sandlock publishes its own three-tier trust model: the host kernel is fully trusted, the supervisor partially trusted, the workload assumed hostile. Compare where the boundary actually sits in each architecture.">
        <Reveal>
          <BoundaryDiagram />
        </Reveal>
        <p className="meta mt-4 max-w-prose">
          The diagram is a summary; the dimension-by-dimension table below carries the same
          comparison in full, and the project’s own comparison page <SRef id="S7" /> was one
          of its sources. There is deliberately no “security score” anywhere on this page —
          the architectures fail differently, and a single number would erase exactly the
          information that matters.
        </p>
      </Section>

      {/* ── THREAT MODEL ─────────────────────────────────────────────────── */}
      <Section eyebrow="04" title="The stated threat model"
        lead="Published at sandlock.io/security.html, and unusually direct — its opening line: “A sandbox is only useful if you know its edges.”">
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="panel overflow-hidden">
            <p className="eyebrow border-b border-paper-line px-5 py-3">
              In scope — what it claims to stop <SRef id="S6" />
            </p>
            <ul>
              {IN_SCOPE.map(([t, d]) => (
                <li key={t} className="border-b border-paper-line px-5 py-3 last:border-b-0">
                  <p className="text-[13.5px] font-semibold text-ink">{t}</p>
                  <p className="meta mt-0.5 text-[12.5px]">{d}</p>
                </li>
              ))}
            </ul>
          </div>
          <div className="panel overflow-hidden">
            <p className="eyebrow border-b border-paper-line px-5 py-3">
              Explicitly out of scope <SRef id="S6" />
            </p>
            <ul>
              {OUT_OF_SCOPE.map(([t, d]) => (
                <li key={t} className="border-b border-paper-line px-5 py-3 last:border-b-0">
                  <p className="text-[13.5px] font-semibold text-ink">{t}</p>
                  <p className="meta mt-0.5 text-[12.5px]">{d}</p>
                </li>
              ))}
            </ul>
            <p className="meta border-t border-paper-line px-5 py-3 text-[12.5px]">
              The most important exclusion is the first, and it is not close. Side channels
              are physics and over-broad policy is operator error — kernel escape is the one
              exclusion <em>inherent to the architecture</em>, and it cannot be engineered
              away without abandoning the architecture.
            </p>
          </div>
        </div>

        <H3>What a hostile workload actually does</H3>
        <div className="scroll-x mt-3 rounded border border-paper-line">
          <table className="text-[13px]">
            <thead>
              <tr className="border-b border-paper-line bg-paper">
                <th className="px-4 py-2.5">Scenario</th>
                <th className="px-4 py-2.5">Outcome</th>
                <th className="px-4 py-2.5">Mechanism / caveat</th>
              </tr>
            </thead>
            <tbody>
              {SCENARIOS.map(([sc, out, note]) => (
                <tr key={sc} className="border-b border-paper-line last:border-b-0">
                  <td className="px-4 py-2.5 text-ink-dim">{sc}</td>
                  <td className={`mono whitespace-nowrap px-4 py-2.5 text-[11.5px] ${
                    out.startsWith("BLOCKED") ? "text-exec-deep" : "text-absent"}`}>
                    {out.startsWith("BLOCKED") ? "● " : "✕ "}{out}
                  </td>
                  <td className="px-4 py-2.5 text-ink-dim">{note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* ── THE CORE INSIGHT ─────────────────────────────────────────────── */}
      <Section eyebrow="05" title="The question a VM boundary cannot answer">
        <Reveal>
          <SemanticPolicy />
        </Reveal>
        <p className="body mt-5 max-w-prose">
          This is why the interesting layer of Sandlock is not the sandbox. It is the{" "}
          <strong className="text-ink">semantic execution policy</strong>: an HTTP ACL on
          method/host/path, a credential the child process can use but never read, and
          transactional writes that make a failed run leave no trace. The syscall
          confinement underneath is competent; the policy layer is the part a competitor
          would have to <em>decide</em> to build, not just port.
        </p>
      </Section>

      {/* ── COMPARISON TABLE ─────────────────────────────────────────────── */}
      <Section eyebrow="06" title="Against the alternatives, dimension by dimension"
        lead="No aggregate score, deliberately. Isolation boundary, kernel relationship, startup model, trust assumptions and operational burden are different axes, and collapsing them into one number would hide the trade each architecture makes.">
        <div className="scroll-x rounded border border-paper-line">
          <table className="text-[12.5px]">
            <thead>
              <tr className="border-b border-paper-line bg-paper">
                <th className="px-3 py-2.5">Alternative</th>
                <th className="px-3 py-2.5">Isolation boundary</th>
                <th className="px-3 py-2.5">Kernel</th>
                <th className="px-3 py-2.5">Startup</th>
                <th className="px-3 py-2.5">Root</th>
                <th className="px-3 py-2.5">Escape requires</th>
                <th className="px-3 py-2.5">Security ceiling</th>
                <th className="px-3 py-2.5">What Sandlock does differently</th>
              </tr>
            </thead>
            <tbody>
              {s.competitors.map((c) => (
                <tr key={c.name} className="border-b border-paper-line align-top last:border-b-0">
                  <td className="whitespace-nowrap px-3 py-2.5 font-semibold text-ink">{c.name}</td>
                  <td className="px-3 py-2.5 text-ink-dim">{c.isolation_boundary}</td>
                  <td className="px-3 py-2.5 text-ink-dim">{c.kernel}</td>
                  <td className="mono whitespace-nowrap px-3 py-2.5 text-ink-dim">{c.startup ?? "—"}</td>
                  <td className="px-3 py-2.5 text-ink-dim">{String(c.root_required ?? "—")}</td>
                  <td className="px-3 py-2.5 text-ink-dim">{c.escape_requires ?? "—"}</td>
                  <td className="px-3 py-2.5 text-ink-dim">{c.security_ceiling ?? "—"}</td>
                  <td className="px-3 py-2.5 text-ink-dim">{c.sandlock_difference}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="meta mt-4 max-w-prose">
          The last row is the sharpest challenge — “isn’t this just the kernel’s feature?”
          Landlock <em>is</em> a public kernel feature. What sits on top: the seccomp
          user-notification policy engine (the 319&nbsp;KB CoW path), the HTTP ACL and
          credential injection, transactional filesystem semantics, the resolved
          per-protection posture model, and the distribution. Identical ceiling; almost none
          of the product.
        </p>
      </Section>

      {/* ── FAIRNESS: THE TRADE ──────────────────────────────────────────── */}
      <Section eyebrow="07" title="The trade, stated plainly"
        lead="The shared kernel is not a footnote. It is the price of everything Sandlock gains, and the project prices it honestly.">
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="panel border-l-2 border-l-exec p-5">
            <p className="eyebrow">Sandlock gains</p>
            <ul className="mt-3 grid gap-2">
              {["~5 ms claimed startup and no VM image — the isolation layer stops being the dominant cost at agent volumes",
                "no root, no KVM, no /etc/subuid — it can confine an agent on the developer laptop where the agent actually runs",
                "full native compatibility: the host kernel stays in the syscall path",
                "policy expressiveness no competitor matches: HTTP ACL, credential injection, CoW rollback, deterministic execution",
                "fail-closed by default, with named, auditable, per-protection opt-outs",
              ].map((t) => (
                <li key={t} className="body flex gap-2 text-[14px]">
                  <span aria-hidden="true" className="mt-0.5 text-exec-deep">+</span>{t}
                </li>
              ))}
            </ul>
          </div>
          <div className="panel border-l-2 border-l-absent p-5">
            <p className="eyebrow">Sandlock gives up</p>
            <ul className="mt-3 grid gap-2">
              {["a separate guest kernel — a kernel LPE in any permitted syscall defeats it, stated plainly by the project itself",
                "the VM/hardware boundary and with it the highest attainable isolation ceiling",
                "a large “partially trusted” supervisor handles attacker-influenced input outside the sandbox",
                "kernel 6.12 / Landlock ABI v6 for the default posture — which excludes most enterprise LTS fleets today",
                "hardware side channels are out of scope entirely",
              ].map((t) => (
                <li key={t} className="body flex gap-2 text-[14px]">
                  <span aria-hidden="true" className="mt-0.5 text-absent">−</span>{t}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </Section>

      {/* ── CODE REVIEW ──────────────────────────────────────────────────── */}
      <Section eyebrow="08" title="Code review — construction evidence"
        lead="Commit count is not the evidence. The shape is: sustained cadence, proportionate tests, a real review process, multi-architecture work, and a monthly release train.">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="panel px-4 py-3">
            <div className="font-mono text-lg text-ink">{s.construction.human_contributors}</div>
            <div className="eyebrow mt-1">Human contributors</div>
            <div className="meta mt-1 text-[12px]">top contributor {s.construction.top_contributions} commits <SRef id="S9" /></div>
          </div>
          <div className="panel px-4 py-3">
            <div className="font-mono text-lg text-ink">3.3 MB</div>
            <div className="eyebrow mt-1">Rust</div>
            <div className="meta mt-1 text-[12px]">+ 503 KB Python, 75 KB Go SDKs <SRef id="S15" /></div>
          </div>
          <div className="panel px-4 py-3">
            <div className="font-mono text-lg text-ink">{s.construction.releases.length} releases</div>
            <div className="eyebrow mt-1">In 3 months</div>
            <div className="meta mt-1 text-[12px]">{s.construction.releases[0].split(" ")[0]} → {s.construction.releases.at(-1)!.split(" ")[0]} <SRef id="S11" /></div>
          </div>
          <div className="panel px-4 py-3">
            <div className="font-mono text-lg text-ink">{s.construction.architectures.join(" ")}</div>
            <div className="eyebrow mt-1">Architectures</div>
            <div className="meta mt-1 text-[12px]">active PR review with named blockers <SRef id="S12" /></div>
          </div>
        </div>
        <div className="panel mt-4 p-5">
          <p className="eyebrow">Weekly commits, last 12 weeks <SRef id="S10" /></p>
          <div className="mt-3 flex h-16 items-end gap-1.5" role="img"
               aria-label={`Weekly commits over the last twelve weeks: ${s.construction.weekly_commits_last_12.join(", ")}`}>
            {s.construction.weekly_commits_last_12.map((v, i) => (
              <div key={i} className="flex-1 rounded-sm bg-exec"
                   style={{ height: `${Math.max(6, (v / 89) * 100)}%` }} title={`${v} commits`} />
            ))}
          </div>
          <p className="mono mt-2 text-[11px] text-ink-faint">
            {s.construction.weekly_commits_last_12.join(" · ")} — sustained, not bursty
          </p>
        </div>
        <p className="body mt-5 max-w-prose">
          The founder is described on the company site as a Linux kernel developer with 16+
          years’ experience, maintainer of the networking traffic-control subsystem since
          2017 <SRef id="S14" />. Kernel-subsystem-maintainer expertise applied to a
          userspace product is rare, verifiable from the public kernel record, and not
          hireable on a normal timeline. The test files being comparable in size to the
          modules they test <SRef id="S2" /> is what a durable system looks like from
          outside.
        </p>
      </Section>

      {/* ── CLAIMS LEDGER ────────────────────────────────────────────────── */}
      <Section eyebrow="09" title="Claims ledger — performance, security, commercial"
        lead="Every material claim, with its evidence state. A project's own benchmark is authoritative that the project claims the number — never that the number is true.">
        <div className="scroll-x rounded border border-paper-line">
          <table className="text-[13px]">
            <thead>
              <tr className="border-b border-paper-line bg-paper">
                <th className="px-4 py-2.5">ID</th>
                <th className="px-4 py-2.5">Claim</th>
                <th className="px-4 py-2.5">State</th>
                <th className="px-4 py-2.5">Source / note</th>
              </tr>
            </thead>
            <tbody>
              {s.claims.map((c) => (
                <tr key={c.id} className="border-b border-paper-line align-top last:border-b-0">
                  <td className="mono whitespace-nowrap px-4 py-2.5 text-ink-faint">{c.id}</td>
                  <td className="px-4 py-2.5 text-ink">{c.claim}</td>
                  <td className="whitespace-nowrap px-4 py-2.5">
                    <EvidenceBadge state={c.status as EvidenceState} />
                  </td>
                  <td className="px-4 py-2.5 text-ink-dim">
                    {c.note ? <>{c.note}. </> : null}
                    <span className="mono text-[11.5px] text-ink-faint">{c.source}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="meta mt-4 max-w-prose">
          The 5&nbsp;ms startup figure and the Redis-throughput result were <em>not</em>{" "}
          reproduced here: the pre-registered reproduction budget went to the Headroom
          experiment, and Sandlock’s default posture needs Linux&nbsp;6.12 while the test
          machine is macOS. They are carried as project claims, not as verified numbers —
          and nothing on this page treats them as verified.
        </p>
        <p className="body mt-4 max-w-prose">
          <strong className="text-ink">The biggest gap in the record:</strong>{" "}
          {s.biggestRisk} For a security product, <em>survived adversarial contact</em> is
          the evidence that matters most, and it is absent from public sources. Absence of
          an audit is not evidence of weakness — it is absence of evidence, in the category
          where evidence matters most.
        </p>
      </Section>

      {/* ── COMMERCIAL STATUS ────────────────────────────────────────────── */}
      <Section eyebrow="10" title="Commercial status">
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="panel p-5">
            <p className="eyebrow">Observed <SRef id="S8" /> <SRef id="S14" /></p>
            <ul className="mt-2 grid gap-1.5">
              <li className="body text-[14px]">Entity: {s.companyStatus.entity as string}; GitHub org created {s.companyStatus.github_org_created as string}</li>
              <li className="body text-[14px]">Open-core model, stated: “what is open, what is licensed”</li>
              <li className="body text-[14px]">Two named commercial products beyond the core: {(s.companyStatus.products as string[]).join(", ")}</li>
              <li className="body text-[14px]">A “Schedule a Demo” call to action; the checkpoint/restore machinery the scheduler needs exists in the repository</li>
            </ul>
          </div>
          <div className="panel p-5">
            <p className="eyebrow">Unknown / not found</p>
            <ul className="mt-2 grid gap-1.5">
              <li className="body flex items-center gap-2 text-[14px]">Pricing <EvidenceBadge state="UNKNOWN" /></li>
              <li className="body flex items-center gap-2 text-[14px]">Customers, revenue <EvidenceBadge state="UNKNOWN" /></li>
              <li className="body flex items-center gap-2 text-[14px]">Team size <EvidenceBadge state="UNKNOWN" /></li>
              <li className="body flex items-center gap-2 text-[14px]">Institutional financing <EvidenceBadge state="NOT_FOUND" /></li>
              <li className="body flex items-center gap-2 text-[14px]">Independent security audit <EvidenceBadge state="NOT_FOUND" /></li>
            </ul>
            <p className="meta mt-3 text-[12.5px]">
              “Not found” means the searches performed found nothing public — it never means
              “does not exist”.
            </p>
          </div>
        </div>
      </Section>

      {/* ── PROJECT GRAPH + AGENTSIGHT ───────────────────────────────────── */}
      <Section eyebrow="11" title="The Multikernel project graph"
        lead="Sixteen repositories, one coherent stack, three clusters — this is an infrastructure organisation with a consistent thesis, not a technical studio spraying experiments.">
        <div className="grid gap-3 lg:grid-cols-3">
          {[
            ["Kernel research & infrastructure", "linux (multikernel-enabled kernel) · kernelscript (OCaml eBPF DSL) · kexec-tools · kmorph · tcp_splice · mkbench …", "The thesis: per-application kernels."],
            ["Filesystem & state", "daxfs (CXL disaggregated FS) · branchfs (FUSE CoW branching) · branching (CoW for agents)", "branchfs and branching — both CoW-for-agents — went quiet in Q2 2026 as sandlock accelerated. Inferred: consolidation onto the mechanism that worked. DAY ZERO's own rules dropped both as ABANDONED."],
            ["AI-facing product", "sandlock (pushed daily) · sandlock.io · kerf · the company site", "The piece of the stack that AI agents made urgent — and the one that got a website, an OCI shim, three SDKs and a paper."],
          ].map(([t, repos, note]) => (
            <div key={t} className="panel p-5">
              <p className="eyebrow">{t}</p>
              <p className="mono mt-2 text-[12px] leading-relaxed text-ink-dim">{repos}</p>
              <p className="meta mt-3 text-[12.5px]">{note}</p>
            </div>
          ))}
        </div>
        <p className="mono mt-3 text-[11.5px] text-ink-faint">Source: org repository listing <SRef id="S13" /></p>

        <H3>The AgentSight relationship — stated precisely</H3>
        <div className="mt-3 grid gap-3 lg:grid-cols-2">
          <div className="panel border-l-2 border-l-exec p-5">
            <p className="eyebrow">Established</p>
            <p className="body mt-2 text-[14px]">{s.agentsight.established} <SRef id="S5" /> <SRef id="S17" /></p>
          </div>
          <div className="panel p-5">
            <p className="eyebrow">Not established — and not inferred</p>
            <p className="body mt-2 text-[14px]">{s.agentsight.not_established}.</p>
          </div>
        </div>
        <p className="body mt-4 max-w-prose">
          Why this matters to the sourcing system itself: {s.agentsight.sourcing_consequence}
        </p>
      </Section>

      {/* ── DEFENSIBILITY ────────────────────────────────────────────────── */}
      <Section eyebrow="12" title="Defensibility — proven, potential, not a moat">
        <div className="grid gap-3 lg:grid-cols-3">
          {([
            ["Proven", s.defensibility.proven, "signal"],
            ["Potential", s.defensibility.potential, "claim"],
            ["Not a moat", s.defensibility.not_a_moat, "absent"],
          ] as const).map(([t, items, tone]) => (
            <div key={t} className={`panel h-full border-t-2 p-5 ${
              tone === "signal" ? "border-t-exec" : tone === "claim" ? "border-t-claim" : "border-t-absent"}`}>
              <p className="eyebrow">{t}</p>
              <ul className="mt-3 grid gap-2">
                {items.map((it) => <li key={it} className="body text-[13.5px]">{it}</li>)}
              </ul>
            </div>
          ))}
        </div>
        <p className="body mt-5 max-w-prose">
          Could a strong security team reproduce it? The architecture, yes — in six to
          twelve months with two or three engineers who genuinely understand seccomp
          notification. What stays hard: the CoW correctness surface, the TOCTOU discipline,
          and the kernel-maintainer judgement about which primitives will exist in two
          years. <strong className="text-ink">That is a real head start and a thin moat,
          and both statements are true at once.</strong>
        </p>
      </Section>

      {/* ── FOUNDER QUESTIONS ────────────────────────────────────────────── */}
      <Section eyebrow="13" title="Questions for the founder"
        lead="Written before any conversation, with what would strengthen and weaken the thesis pre-registered — so a persuasive answer cannot retroactively become the bar. Nobody has been contacted.">
        <ol className="grid gap-3">
          {[
            "Your security page says a kernel LPE in a permitted syscall defeats the sandbox. Which customers have accepted that trade, which have refused it — and what did the ones who refused choose instead?",
            "cow/seccomp.rs is your largest file. What is the hardest correctness problem in the copy-on-write path, and what have you got wrong there before?",
            "Has anyone outside the team attempted an escape? Audit, bug bounty, red team, a customer's security review — what happened, and what did it change?",
            "Landlock ABI v6 means kernel 6.12. What fraction of inbound interest dies on that requirement, and what does allow_degraded actually get used for in the field?",
            "Multikernel sells three products. If you had to kill two, which survive — and is Sandlock a wedge into the cloud-OS business, or the business itself?",
            "branchfs and branching both stopped in Q2 2026 as sandlock accelerated. What did you learn that made you consolidate?",
            "Sandlock is Apache-2.0 and your site says “what is open, what is licensed.” Where is that line, and what stops a cloud provider from running the open core as a service?",
          ].map((q, i) => (
            <li key={i} className="panel flex gap-4 p-4">
              <span className="mono pt-0.5 text-ink-faint">{String(i + 1).padStart(2, "0")}</span>
              <p className="body text-[14.5px]">{q}</p>
            </li>
          ))}
        </ol>
        <p className="meta mt-4 max-w-prose">
          Pre-registered evaluation: a specific, unflattering war story about a CoW
          correctness bug strengthens; “nobody has tried to break it yet” weakens — and
          those bars were written down before any answer could exist.
        </p>
      </Section>

      {/* ── WHAT CHANGES THE VIEW ────────────────────────────────────────── */}
      <Section eyebrow="14" title="What would change this view">
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="panel border-l-2 border-l-exec p-5">
            <p className="eyebrow">Upgrade</p>
            <p className="body mt-2 text-[14px]">
              An independent audit or a real adversarial engagement with a published
              outcome; two or more named production users who chose it over a container
              runtime; evidence that the HTTP-ACL and credential-injection layer is{" "}
              <em>why</em> they chose it; a defensible open/licensed boundary; a second
              senior systems engineer with material ownership.
            </p>
          </div>
          <div className="panel border-l-2 border-l-absent p-5">
            <p className="eyebrow">Downgrade</p>
            <p className="body mt-2 text-[14px]">
              An escape that does not require a kernel bug; “nobody has tried to break it”;
              discovery that adoption is driven by speed alone; a major platform shipping
              equivalent policy-level egress control; continued three-product spread with no
              ranking; or evidence of an institutional round already closed at a price that
              removes the Day-0 window.
            </p>
          </div>
        </div>
        <p className="meta mt-5 max-w-prose">
          Related on this site: how the same system{" "}
          <Link href="/lab/headroom/" className="text-exec-deep underline underline-offset-4">
            pressure-tests a quantitative claim
          </Link>{" "}
          when reproduction <em>is</em> feasible, and{" "}
          <Link href="/methodology/" className="text-exec-deep underline underline-offset-4">
            what happens when its own rules fail
          </Link>.
        </p>
      </Section>

      {/* ── SOURCES ──────────────────────────────────────────────────────── */}
      <Section eyebrow="Provenance" title="Source ledger"
        lead="Every claim above traces to one of these sources. All evidence gathered 2026-08-23 from public material; nobody was contacted.">
        <SourceLedger sources={s.sources} />
        <p className="meta mt-4 max-w-prose">
          One defect found on the way: the project site’s own navigation links to
          /security-model/ and /comparison/, which 404 — the real paths are security.html
          and comparison.html. Noted because a careful reader reports that rather than
          silently working around it.
        </p>
      </Section>
    </>
  );
}
