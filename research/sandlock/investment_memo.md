# Sandlock (Multikernel Technologies) — Investment Memo

**Prepared 2026-08-23 from public sources only. Nobody was contacted.**
Evidence: `source_audit.md` · Architecture: `architecture.md` · Threat model:
`threat_model.md` · Interview plan: `primary_research_plan.md`

---

# Recommendation

## **ADVANCE TO FOUNDER CONVERSATION**

Not *invest* — that word is unavailable from outside-in public work, and this memo does
not use it.

The recommendation rests on three things that public evidence establishes and one thing it
does not. Established: the technical work is real and unusually well-executed; the threat
model is stated more honestly than most funded security companies state theirs; and the
team's construction pattern looks like durable systems engineering rather than a demo. Not
established: whether anyone has ever tried to break it, and whether anyone pays.

Both unknowns are **conversation-resolvable**, which is precisely what makes this a
founder conversation rather than a pass or a watch.

---

# Why Now

**The honest version, and it cuts both ways.**

Sandboxing untrusted code is a thirty-year-old problem with mature answers. What changed
is not the problem but three properties of the workload:

1. **Volume and latency.** Agents spawn execution constantly. At 200 ms per container the
   isolation layer becomes the dominant cost; at 5 ms it disappears. This is a real
   quantitative change, not vocabulary.
2. **Privilege.** Agents run *on developer machines and in developer accounts*, holding
   real credentials. Requiring root to isolate them is backwards.
3. **The threat is semantic, not just binary.** A prompt-injected agent does not exploit a
   memory bug — it makes a *legitimate* API call with a *legitimate* credential to the
   wrong endpoint. **No namespace, container or microVM addresses that.** An HTTP ACL on
   method/host/path plus a credential the child never sees does.

**The falsification test I set myself:** if AI merely repackaged an old problem, the
right response would be "use Firecracker." Point 3 is the reason that answer is
incomplete — and it is the only one of the three that is genuinely new. Points 1 and 2 are
real but are *performance and ergonomics* arguments, and a sufficiently determined
Firecracker optimisation erodes them.

**Verdict: partially new.** The isolation problem is old. The *policy* problem — expressing
and enforcing what an autonomous agent may do with credentials it legitimately holds — is
new, and Sandlock is one of the few implementations that treats it as the point rather than
an afterthought. Array's own April 2026 security thesis makes the same argument from the
other direction.

---

# What Sandlock Is

A lightweight Linux process sandbox in Rust (Apache-2.0) that confines a command's
filesystem, network, syscalls and resources using **Landlock**, **seccomp-bpf** and
**seccomp user notification** — with no root, no image build, no container runtime and no
hypervisor. Claimed startup overhead ~5 ms.

Distribution: CLI, an OCI runtime shim (containerd / CRI-O / Kubernetes, namespace-less),
a C ABI, and Python and Go SDKs.

# Technical Architecture

One organising idea (paper, S5): **static, input-independent policy compiles into
kernel-enforced rules; a narrow supervisor handles runtime-dependent decisions and
virtualised effects.** Landlock and seccomp-bpf do the static half; seccomp user
notification does the dynamic half — destination-IP enforcement, `/proc` virtualisation,
copy-on-write staging. Full reconstruction in `architecture.md`.

Codebase: 3.3 MB Rust across `sandlock-core`, `-cli`, `-oci`, `-ffi`, plus 503 KB Python
and 75 KB Go SDKs. Integration test files are comparable in size to the modules they test.

# Threat Model

Stated publicly, in three tiers: the host kernel is fully trusted, the supervisor partially
trusted, the workload assumed hostile. Eight named in-scope attacks; five named
out-of-scope. Full analysis in `threat_model.md`.

# What It Does Better

1. **Startup and density.** ~5 ms and no image build; process-level density.
2. **No privilege requirement.** No root, no KVM, no `/etc/subuid`.
3. **Policy expressiveness no competitor matches.** HTTP method/host/path ACL; destination
   IP and CIDR allowlists; credential injection where the secret never enters the child.
4. **Transactional filesystem.** CoW staging with commit/abort — a failed agent run leaves
   the tree untouched.
5. **Programmable interception.** A handler API on any syscall, with built-ins first, so a
   custom handler can extend confinement but never relax it.
6. **Fail-closed by default**, with named, auditable, per-protection opt-outs.

# What It Gives Up

1. **The shared kernel.** A kernel LPE in any permitted syscall defeats it. Stated plainly
   by the project, and inherent to the architecture.
2. **A large "partially trusted" supervisor** — `cow/seccomp.rs` alone is 319 KB — handling
   attacker-influenced input outside the sandbox.
3. **Kernel 6.12 / Landlock ABI v6** for the default posture, which excludes most
   enterprise LTS fleets today.
4. **Hardware side channels**, out of scope.
5. **Policy correctness is the operator's problem.** *"Sandlock enforces the policy you
   wrote, not the one you meant."*

# Competitive Alternatives

| | Isolation boundary | Startup | Kernel | Root | Security ceiling | What Sandlock does differently |
| --- | --- | --- | --- | --- | --- | --- |
| **Firecracker** | Hardware virtualisation, separate guest kernel | ~100 ms | Separate | Yes (KVM) | **Highest** | No image, no root, 20× faster start, plus policy-level egress control a VM cannot express |
| **gVisor** | Userspace kernel (Sentry) intercepts every syscall | Moderate | Reimplemented | Varies | High | Native syscall performance and full compatibility; accepts a wider escape surface |
| **Containers** | Namespaces + cgroups | ~200 ms | Shared | Yes* | Comparable-to-lower | Access-control ruleset instead of a constructed namespace; no image; HTTP ACL; CoW rollback |
| **bubblewrap / firejail** | Constructed namespaces | Fast | Shared | user-ns | Comparable | No user-namespace requirement; destination-IP and HTTP rules; credential injection; transactional writes |
| **Raw Landlock + seccomp** | Same primitives | Fast | Shared | No | **Same ceiling** | The supervisor, the CoW engine, the HTTP layer, the protection-posture model, and the distribution — i.e. all the hard parts |

The last row is the real competitive question, and it is answered in
`threat_model.md` §"isn't this just the kernel's feature?"

# Team / Construction Evidence

**OBSERVED:** 8 human contributors; `congwang-mk` 807 commits, `dzerik` 173, `ghazariann`
71, `sachin2605` 20. Twelve-week commit cadence 73/58/31/35/46/31/40/89/64/41/19/10 —
sustained, not bursty. Six releases in three months (v0.8.1 → v0.8.6). Active PR review
with named blockers; multi-architecture work across x86_64, aarch64 and riscv64.

Cong Wang is described on the company site as Founder & CEO, a Linux kernel developer with
16+ years' experience and maintainer of the networking traffic-control subsystem since
2017, with 1,000+ kernel commits.

**This is what "built like a durable system" looks like**: architecture-portability work,
a test surface proportionate to the code, a real review process, and a monthly release
train. Commit *count* is not the evidence — the *shape* is.

# Formation / Company Status

Multikernel Technologies, Inc. GitHub org created 2025-03-08. Company site with three
named products (Private Cloud, Sandbox, LiveUpdate). Sandlock has its own site, an OCI
shim, three SDKs, and a peer-reviewable paper.

**Funding: no public institutional financing was identified in the sources reviewed.** No
round, filing, or investor is named on the company site, the project site, the repository,
or in the searches performed. **This is not a claim that the company is bootstrapped** —
that would require evidence I do not have. It is a statement about what is public.

# Commercialization

**OBSERVED:** two named commercial products beyond the open-source core — a **Sandbox HTTP
API** (remote execution) and a **Sandbox Scheduler** (placement by checkpoint and restore)
— plus an explicit "what is open, what is licensed" page and a "Schedule a Demo" call to
action. The checkpoint/restore machinery that the scheduler needs exists in the repository.

**UNKNOWN:** pricing (no pricing page), customers (no logos, no case studies), revenue,
paid users, deployments, sales motion, team size.

**Open-core is the stated model.** Whether the boundary is defensible is question 7 for the
founder.

# Defensibility

**Proven (OBSERVED):**
- Kernel-subsystem-maintainer expertise applied to a userspace product. Rare, verifiable
  from the kernel record, and not hireable on a normal timeline.
- A working seccomp-user-notification policy engine with CoW transactional semantics. The
  hard part is built and tested, not described.

**Potential (INFERRED):**
- The **agent-specific policy layer** — HTTP ACL, credential injection, deterministic
  execution. This is the piece a competitor would have to *decide* to build, not just
  port. It is also the piece most connected to the buyer's actual fear.
- Accumulated hardening, if adversarial contact ever happens.
- The scheduler and checkpoint/restore, if density becomes the commercial axis.

**Not a moat:**
- Landlock and seccomp. Public kernel features.
- Speed alone. A number competitors can chase.
- 358 stars.

**Could a strong security team reproduce it?** The architecture, yes — in six to twelve
months with two or three engineers who genuinely understand seccomp notification. What
stays hard: the CoW correctness surface, the TOCTOU discipline, and the kernel-maintainer
judgement about which primitives will exist in two years' time. **That is a real head start
and a thin moat, and both statements are true at once.**

# Key Risks

1. **No evidence of adversarial contact.** For a security product this is the single
   biggest gap. Absence of an audit is not evidence of weakness — it is absence of
   evidence, in the category where evidence matters most.
2. **Absorption.** AWS, Google or an agent platform could ship "isolated execution" as a
   feature. Open primitives make the *mechanism* copyable; the policy layer is the only
   part that is not.
3. **Kernel 6.12 floor** materially shrinks the near-term enterprise market.
4. **Feature-versus-company.** If agent platforms treat isolation as table stakes they
   bundle rather than buy.
5. **Focus.** Three company products, sixteen repositories, one founder writing most of
   the code.
6. **Supervisor complexity** as a trusted-ish component under attacker-influenced input.

# What Is Proven

Rust codebase of 3.3 MB with proportionate tests · Landlock/seccomp/user-notification
mechanisms present in code · fail-closed default with named opt-outs · a published,
specific, self-limiting threat model · a peer-reviewable paper · a sustained 12-week
build cadence and monthly releases · multi-architecture support · two named commercial
products · founder identity and kernel record.

# What Is Inferred

That the CoW/notification path is the hardest engineering · that consolidating away from
`branchfs`/`branching` reflects learning · that the policy layer is the durable
differentiator · that the shared-kernel ceiling is acceptable for semi-trusted agent code
and not for hostile multi-tenant code.

# What Is Unknown

Revenue · customers · pricing · team size · funding · any independent security audit ·
production deployments · whether the 5 ms and Redis-throughput figures reproduce on
third-party hardware · whether the open/licensed boundary holds.

# Questions For Founder

Seven, in `primary_research_plan.md` §1. The two that matter most:

- **Technical:** *"Your security page says a kernel LPE in a permitted syscall defeats the
  sandbox. Has anyone outside the team ever tried — audit, bounty, red team, a customer's
  security review — and what did it change?"*
- **Commercial:** *"Sandlock is Apache-2.0 and your site says 'what is open, what is
  licensed.' Where is that line, and what stops a cloud provider from running the open core
  as a service?"*

# What Would Change My View

**Upgrade** — an independent audit or a real adversarial engagement with a published
outcome; two or more named production users who chose it over a container runtime; evidence
that the HTTP-ACL and credential-injection layer is why they chose it; a defensible
open/licensed boundary; a second senior systems engineer with material ownership.

**Downgrade** — an escape that does not require a kernel bug; "nobody has tried to break
it"; discovery that adoption is driven by speed alone; a major platform shipping equivalent
policy-level egress control; continued three-product spread with no ranking; or evidence
of an institutional round already closed at a price that removes the Day-0 window.

---

## Thematic-mirroring guard

*Would Sandlock be interesting if Array had never published "Agents broke the security
stack"?*

**Yes**, and the test is easy to apply here because the artifact is verifiable independent
of the thesis: a 3.3 MB Rust codebase, a kernel maintainer's record, a paper, an OCI shim
and three SDKs would be interesting to any infrastructure investor. The mechanism —
Landlock, seccomp, user notification — was not chosen to match anyone's vocabulary; it is
what the problem requires.

Where the guard **does** bite: I should not treat "agent" framing as evidence of an agent
market. The strongest verifiable buyers today may be CI and FaaS operators, both of which
the project names, and neither of which needs an AI thesis. **Sandlock passes the guard,
but its Array relevance rests on the security thesis being right about *buyers*, not just
about threats.**
