# Sandlock — Reconstructed Architecture

Reconstructed from code, docs and the paper. Source IDs refer to `source_audit.md`.
Every line is tagged **OBSERVED** (present in a cited source), **INFERRED** (my reading),
or **UNKNOWN**. Nothing is assumed because it is common in Linux sandboxing.

## 1. The organising idea

**OBSERVED (S5, paper abstract):** Sandlock is built around one split —

> "static, input-independent policy is compiled into kernel-enforced rules, while a narrow
> supervisor handles runtime-dependent decisions and virtualized effects."

**INFERRED:** this is the whole architecture in one sentence, and it is the right frame
for evaluating it. Anything expressible as a static rule goes to the kernel, where it is
fast and TOCTOU-immune. Anything requiring a runtime decision goes to a userspace
supervisor, which is slower and more trusted. The design question is where that line sits.

## 2. Enforcement mechanisms — what is actually used

| Mechanism | Used for | Evidence |
| --- | --- | --- |
| **Landlock LSM** | Filesystem access, TCP connect/bind ports, IPC scoping (signals, abstract UNIX sockets) | OBSERVED S3, S4, S16 — `landlock.rs` builds rulesets via `SYS_LANDLOCK_CREATE_RULESET`, `LANDLOCK_RULE_PATH_BENEATH`, `LANDLOCK_RULE_NET_PORT`, `LANDLOCK_SCOPE_SIGNAL`, `LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET` |
| **seccomp-bpf** | Syscall filtering; denying UDP/ICMP/raw socket creation when no rule of that protocol exists | OBSERVED S3, S4 |
| **seccomp user notification** (`SECCOMP_USER_NOTIF`, kernel ≥ 5.6) | Runtime decisions: destination-IP enforcement, resource accounting, `/proc` virtualisation, copy-on-write writes | OBSERVED S3, S4; `seccomp/notif.rs` is 130 KB, `cow/seccomp.rs` is 319 KB |
| **`NO_NEW_PRIVS`** | Neutralising setuid binaries; installed before the filter | OBSERVED S6 |
| **`RLIMIT_NOFILE`** and rlimits | Open-file caps, set in the child immediately before `exec` | OBSERVED S4 |
| **`chroot`** | Optional virtual filesystem view with host-directory mounts | OBSERVED S2 (`chroot/dispatch.rs`, 98 KB), S4 |
| **Namespaces** | **Not required.** "no root, no cgroups, no containers"; the OCI shim is described as "namespace-less" | OBSERVED S3 |
| **cgroups** | **Not used.** Resource limits use seccomp notify + `SIGSTOP` | OBSERVED S3, S7 |
| **Hypervisor / KVM** | **Not used.** Shared kernel | OBSERVED S3, S6 |

**Kernel floor (OBSERVED S3):** Linux **6.12+** for the default posture (Landlock ABI v6).
Component floors: seccomp user notification 5.6, Landlock FS 5.13, Landlock TCP ports 6.7,
IPC scoping 6.12.

**INFERRED — this is a real deployment constraint.** Requiring Landlock ABI v6 by default
in 2026 excludes most enterprise LTS fleets. The project handles it explicitly rather than
hiding it (§5), but "runs on your laptop, not on your RHEL 9 estate" is a genuine
go-to-market fact, not a footnote.

## 3. Process and lifecycle model

**OBSERVED (S6):** the workload "never executes an unconfined instruction" —
`NO_NEW_PRIVS`, Landlock and the seccomp filter are all installed **before `exec`**, and
inherited descriptors above stderr are closed first.

**OBSERVED (S3, S5):** startup overhead ~5 ms.
**OBSERVED (S2):** `checkpoint/restore_blob.rs` (47 KB) and a `sandlock-oci/supervisor.rs`
(47 KB) exist — checkpoint/restore is implemented, and the site sells a scheduler that
"places sandboxes by checkpoint and restore" (S8).

**INFERRED:** the supervisor is a parent process that survives the sandbox and services
notifications. It is the single most security-relevant userspace component.

## 4. Component inventory (OBSERVED, S2 + S15)

| Crate / module | Size | Role |
| --- | --- | --- |
| `sandlock-core` | — | Landlock, seccomp, supervisor, COW, pipeline |
| `cow/seccomp.rs` | **319 KB** | Copy-on-write filesystem staging via seccomp notification — the largest single file |
| `sandbox.rs` | 134 KB | Sandbox construction and state |
| `seccomp/notif.rs` | 131 KB | User-notification handling |
| `transaction.rs` | 105 KB | Commit/abort semantics for staged writes |
| `chroot/dispatch.rs` | 99 KB | Virtual filesystem view |
| `network/rules.rs` | 56 KB | Destination IP/CIDR/port rules |
| `procfs.rs` | 50 KB | `/proc` virtualisation |
| `landlock.rs` | 36 KB | Landlock ruleset construction |
| `credential.rs` | 39 KB | Supervisor-held secret injection |
| `sandlock-cli` | 47 KB main | `sandlock run/ps/inspect/learn` |
| `sandlock-oci` | 45 KB + 45 KB policy | OCI runtime shim for containerd, CRI-O, Kubernetes |
| `sandlock-ffi` | 94 KB + 56 KB header | C ABI, consumed by the Python (ctypes) and Go (cgo) SDKs |

**Test surface (OBSERVED, S2):** integration tests of 86 KB (transaction), 78 KB (chroot),
61 KB (landlock), 56 KB (COW), 55 KB (network), plus FFI smoke tests at 87 KB and a
Python suite at 49 KB. **The test files are comparable in size to the modules they test** —
an unusual and good sign in a security project.

## 5. Policy model

**OBSERVED (S4):** every Landlock protection has a resolved status of `Active`,
`Degraded`, `Disabled` or `Unavailable`. The default is **strict: enforce everything the
kernel supports and refuse to start when a required protection is unavailable.** Two
explicit opt-outs exist — `allow_degraded(Protection::P)` (skip where unsupported) and
`disable(Protection::P)` (never enforce). Protection posture is part of the checkpoint, so
a restored sandbox restores its exact posture.

**INFERRED:** fail-closed-by-default with named, per-protection, auditable escape hatches
is the correct design. It is also the honest one: the alternative — silently degrading on
older kernels — is how sandboxes end up providing less than operators believe.

## 6. Capabilities beyond a conventional sandbox (OBSERVED, S3, S4)

These are the parts that are not simply "namespaces reimplemented":

- **Destination-IP and CIDR allowlists**, matched by containment, no DNS.
- **HTTP-level ACL** on method + host + path, via a transparent proxy; HTTP rules with
  concrete hosts auto-extend the TCP allowlist.
- **HTTPS MITM with an ephemeral CA** whose private key is memory-only and never written to
  disk, spliced into named trust bundles at open time.
- **Credential injection**: the secret stays in the supervisor and is attached in the proxy
  **after** the ACL check; the child never sees it, and an `env:` source is stripped. Over
  cleartext HTTP the tool warns that the secret would be exposed on the wire.
- **Copy-on-write working directory** with transactional commit/abort on exit or error.
- **Port virtualisation** so several sandboxes can bind the same port.
- **Deterministic execution**: frozen time and seeded randomness.
- **GPU scoping**: `--gpu 0` is a hard Landlock boundary on `/dev/nvidiaN` nodes.
- **`policy_fn` handler API**: a custom handler on any syscall, with a fixed chain and
  built-ins first, so a handler "can extend confinement but never relax it" (S6).

**INFERRED:** the HTTP ACL, credential injection and COW rollback are the differentiated
surface. Filesystem and syscall confinement is table stakes; *an agent that is allowed to
call one endpoint and cannot repurpose the connection, with the API key never entering its
address space* is a materially different product from a container.

## 7. The Multikernel project graph (OBSERVED, S13)

16 repositories, one coherent stack, three clusters:

**Kernel research and infrastructure** — `linux` (multikernel-enabled kernel, 90★, active),
`kernelscript` (OCaml eBPF DSL, 502★), `kexec-tools`, `kmorph`, `lazy_cma`, `tcp_splice`,
`kbi`, `will-it-scale`, `mkbench`.

**Filesystem and state** — `daxfs` (CXL/shared-memory disaggregated FS, 93★, active),
`branchfs` (FUSE CoW branching, 106★, **last pushed 2026-05-23**), `branching`
(BranchContext CoW for agents, **last pushed 2026-03-14**).

**AI-facing product** — `sandlock` (358★, pushed daily), `sandlock.io`, plus `kerf`
(orchestrating multiple kernel instances) and the company site.

**INFERRED — what kind of organisation is this?** Not a technical studio spraying
experiments, and not one product. It is an **infrastructure stack with a consistent
thesis**: per-application kernels, and the filesystem and isolation primitives that a
per-application-kernel world needs. Sandlock is the piece of that stack that AI agents
made urgent, and it is the one that got a website, an OCI shim, SDKs in three languages,
and a paper. `branchfs` and `branching` — both CoW-for-agents — went quiet in Q2 2026,
around when sandlock accelerated; **INFERRED**, that reads as consolidation onto the
mechanism that worked, and DAY ZERO's own rules dropped both as `ABANDONED`.

## 8. The AgentSight relationship — stated precisely

**OBSERVED (S5):** arXiv:2605.26298 is co-authored by **Cong Wang and Yusheng Zheng**.
Yusheng Zheng is the author of AgentSight (arXiv:2508.02736) and the `eunomia-bpf` lead.
**OBSERVED (S9):** `yunwei37` is **not** a contributor to the sandlock repository.
**OBSERVED (S17):** 49 code-search hits for "sandlock" inside the `eunomia-bpf` org,
including `docs/tmp/2026-07-01-branchfs-sandlock-workload-reproduction.md` and a
`2026-07-02-sandlock-workload-evidence-summary.md` — i.e. the eunomia-bpf side has been
*reproducing sandlock/branchfs workloads*.

**What this supports:** a real research collaboration between two people who each lead
their own project, plus evidence that one side independently reproduced the other's
workloads.

**What it does NOT support, and is not claimed:** any organisational, employment,
equity or corporate relationship between Multikernel Technologies and eunomia-bpf. There
is no evidence of one and none is inferred.

**Why it matters to DAY ZERO:** Phase 2 surfaced Multikernel and AgentSight as two
independent leads. They are not independent *as evidence*. Two leads sharing an author is
one intellectual cluster, and a sourcing system that counts them as two overstates its own
coverage. This is now a v2 requirement (`v2_methodology.md`).
