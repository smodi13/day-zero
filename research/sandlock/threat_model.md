# Sandlock — Threat Model

Two things are kept strictly apart: **what the project states**, and **what I conclude**.

---

## Part 1 — The project's stated threat model (OBSERVED, S6)

Sandlock publishes a threat model at `sandlock.io/security.html`. It is unusually direct,
and its opening line is the right one: *"A sandbox is only useful if you know its edges."*

### Three tiers of trust, verbatim

| Tier | Component | Stated position |
| --- | --- | --- |
| **Fully trusted** | The host kernel | "Landlock rules and the seccomp-bpf filter are evaluated by the kernel. If the kernel is compromised, so is every guarantee on this page. Sandlock shares a kernel with its workload, and that is the fundamental limit of the model." |
| **Partially trusted** | The supervisor | Runs in the parent, outside the sandbox. Decides on syscalls the kernel hands it. "Its handler chain is fixed, with built-ins first, so a custom handler can extend confinement but never relax it." |
| **Untrusted** | The workload | "Assumed hostile. It never executes an unconfined instruction: `NO_NEW_PRIVS`, Landlock, and the seccomp filter are all installed before `exec`, and inherited descriptors above stderr are closed first." |

### In scope — what it claims to stop

1. **Filesystem escape** — only paths reachable through granted Landlock rules; grants are
   recursive, denials override.
2. **Unapproved network egress** — default-deny. With no rules, Landlock refuses every TCP
   connect; UDP, ICMP and raw socket *creation* are refused at the seccomp layer.
3. **Exfiltration on an approved host** — HTTP rules match method, host and path, so "an
   agent allowed one endpoint cannot repurpose the connection."
4. **Credential theft by the workload** — the secret stays in the supervisor and is
   attached after the ACL check; an `env:` source is stripped from the child.
5. **Privilege escalation via setuid** — `NO_NEW_PRIVS` before the filter.
6. **Reaching sibling processes** — Landlock ABI v6 scopes deny abstract UNIX socket
   connections and signals outside the sandbox.
7. **Host resource exhaustion** — memory, process count, open files, CPU share and COW disk
   usage are capped.
8. **Unintended writes** — CoW stages writes and discards them on error.

### Explicitly out of scope — verbatim

- **"Kernel vulnerabilities. The workload runs on your kernel. An escalation bug in a
  permitted syscall defeats the sandbox. This is the price of no hypervisor."**
- **Hardware side channels.** Spectre-class and cache timing. "CPU pinning reduces sharing
  but is not a mitigation."
- **A policy that grants too much.** *"Sandlock enforces the policy you wrote, not the one
  you meant."*
- **A hostile launcher.** "An attacker who already controls the process that starts Sandlock
  controls the policy."
- **The workload starving itself.** "Limits protect the host, not the workload's own
  progress."

### TOCTOU handling (OBSERVED, S4 §4)

Path strings are **never** exposed to `policy_fn` handlers, because seccomp user
notification re-reads user memory after `Continue`. Path-based control must live in static
Landlock rules or `ctx.deny_path()`. `event.argv` **is** exposed and is stated TOCTOU-safe:
"the supervisor freezes peer tasks before exposing it." Landlock rules are described as
"kernel-evaluated and TOCTOU-immune."

### A caveat the project volunteers against itself (OBSERVED, S4)

On `max_open_files`: lowering the hard limit is one-way only for an *unprivileged*
sandlock; a sandbox launched by root or with `CAP_SYS_RESOURCE` can raise it back, because
sandlock does not drop capabilities — **"treat it as a resource budget, not as
confinement."**

---

## Part 2 — Analyst interpretation

### The most important exclusion

**Kernel vulnerabilities**, and it is not close. Everything else on the out-of-scope list
is either physics (side channels) or operator error (over-broad policy, hostile launcher).
Kernel escape is the one exclusion that is *inherent to the architecture* and cannot be
engineered away without abandoning the architecture.

Sandlock's entire value proposition is "no hypervisor, therefore 5 ms and no root."
The cost of that is a shared kernel. A local privilege-escalation bug in any syscall the
policy permits — and a useful policy permits many — defeats confinement completely. The
project says this plainly, in bold, on its own security page. That is the correct posture,
and it does not make the exclusion smaller.

### The core question: escape surface versus a microVM

**This is not "containers bad, microVM good."** They fail differently, and the right answer
depends on the workload.

| Dimension | Sandlock | Firecracker microVM |
| --- | --- | --- |
| **Isolation boundary** | Kernel LSM + syscall filter, *inside* one kernel | Hardware virtualisation; separate guest kernel |
| **What must be bug-free to hold** | The host kernel's Landlock/seccomp implementation **and every permitted syscall path** | KVM, the VMM, and the virtual device models |
| **Attack surface presented to hostile code** | The full host syscall interface, minus what the filter denies — a **large, complex** surface | A far narrower virtio device surface, plus the guest's own kernel (whose compromise is contained) |
| **Escape consequence** | Host compromise | Guest-kernel compromise; a further VMM/KVM bug is needed to reach the host |
| **Startup** | **~5 ms** (S3, S5) | ~100 ms (S7) |
| **Density** | Process-level: thousands per host | VM-level: memory floor per instance |
| **Root required** | **No** | Yes (KVM access) |
| **Image build** | **None** | Required |
| **Filesystem model** | Landlock rules + seccomp CoW on the real tree | Block device, separate FS |
| **Application compatibility** | Anything the syscall policy allows; no re-imaging | Full OS, highest compatibility |
| **Operational burden** | A policy file | Image pipeline, VMM lifecycle, networking |
| **Programmable interception** | **Handler API on any syscall** | Not available |
| **Realistic security ceiling** | Bounded by host-kernel LPE | Materially higher; two boundaries |

**My assessment:** *A microVM has a meaningfully higher security ceiling, and Sandlock does
not dispute it.* What Sandlock is arguing is that for the AI-agent workload the ceiling is
often not the binding constraint, and the binding constraints — 5 ms instead of 100 ms, no
root, no image build, and policy that can express "this agent may POST to exactly this
endpoint and may never see the API key" — are things a microVM does not address at all.

That is a coherent position. It is also a *product* argument rather than a *security*
argument, and it should be tested as one.

### Versus gVisor

**OBSERVED (S7), the project's own framing:** gVisor is "a userspace kernel that
reimplements the Linux syscall interface… every syscall is serviced by the Sentry, and
compatibility depends on how completely it reimplements the interface. Sandlock leaves the
host kernel in the syscall path and intercepts only the calls that carry a policy
decision." It recommends gVisor "when you are running a full untrusted OS image and can
absorb the per-syscall cost."

**INFERRED:** gVisor sits between the two. It shrinks the host attack surface by
interposing a userspace kernel, at a real per-syscall performance cost and a real
compatibility cost. Sandlock keeps native performance and full compatibility and accepts
the full host syscall surface, narrowed by policy. **Sandlock's escape surface is wider
than gVisor's**; its compatibility and latency are better. Neither dominates.

### Versus Landlock/bubblewrap/firejail — "isn't this just the kernel's feature?"

This is the sharpest challenge, and it deserves a real answer rather than a dismissal.

Landlock **is** a kernel feature, and anyone can call it. What Sandlock adds on top:

1. **seccomp user notification as a policy engine**, not just a filter — runtime
   destination-IP decisions, `/proc` virtualisation, CoW write staging. This is where the
   319 KB `cow/seccomp.rs` and 131 KB `seccomp/notif.rs` live, and it is the part that is
   genuinely hard.
2. **HTTP-level ACL and credential injection**, which no namespace-based tool provides.
3. **Transactional filesystem semantics** — commit/abort on exit.
4. **A resolved protection-posture model** with per-protection `Active/Degraded/Disabled/
   Unavailable` states, checkpointed with the sandbox.
5. **Distribution**: CLI, OCI shim, C ABI, Python, Go, MCP.

Against bubblewrap/firejail specifically, the project's own line is accurate: "Sandlock's
policy is an access-control ruleset, not a constructed namespace." Different primitive,
different failure modes, no user-namespace requirement.

### What a hostile workload actually does

| Scenario | Outcome |
| --- | --- |
| Malicious generated code tries to read `~/.ssh` | **Blocked** — Landlock, kernel-evaluated (OBSERVED S6) |
| Malicious dependency exfiltrates to an attacker host | **Blocked** by default-deny egress; **blocked** on an approved host by the HTTP method/host/path ACL |
| Prompt-injected tool call tries to POST the API key | **Key never enters the child's address space** (OBSERVED S6). Strong, and the most agent-specific guarantee in the product |
| Workload attempts setuid escalation | **Blocked** — `NO_NEW_PRIVS` |
| Workload signals a sibling process | **Blocked** on ABI v6; **not blocked** on an older kernel unless `allow_degraded` was chosen deliberately |
| Workload exploits a kernel LPE in a permitted syscall | **Not defended.** Full host compromise. Stated |
| Operator writes `--net-allow '*'` | **Not defended.** Stated |
| Attacker controls the launching process | **Not defended.** Stated |

### Where I would push hardest

1. **The supervisor is "partially trusted" and very large.** `cow/seccomp.rs` alone is
   319 KB. A memory-safety or logic bug in the notification path is a bug in a component
   that is, by design, outside the sandbox and handling attacker-influenced input. Rust
   removes a class of these, not the class of logic errors. **No independent security audit
   was found.**
2. **No public adversarial-testing evidence.** The test suite is substantial and
   proportionate — but it is the authors' own. I found no third-party audit, no bug bounty,
   no CTF result, no published escape attempt. For a security product, *survived adversarial
   contact* is the evidence that matters, and it is absent from public sources.
3. **The Landlock ABI v6 / kernel 6.12 floor** is a deployment constraint that the security
   posture depends on. `allow_degraded` is the honest escape hatch, and it is also the knob
   that quietly converts a strict sandbox into a weaker one on an older fleet.
4. **HTTPS MITM with an ephemeral CA spliced into trust bundles** is powerful and is also a
   deliberately weakened TLS path. Memory-only keys are the right design; the residual
   question is what the proxy does on certificate errors and whether the child can reach
   the proxy's control surface.
