"use client";

import { useState } from "react";
import { usePrefersReducedMotion } from "@/lib/motion";

/**
 * Interactive trust-boundary comparison.
 *
 * Each architecture is a stack from the hostile workload down to the host
 * kernel. Boundaries are drawn as named, hatched bars because the mechanism IS
 * the security argument — "hardware virtualisation" and "Landlock + seccomp"
 * are not decoration, they are the thing being compared.
 *
 * Switching architecture animates rather than swaps: the layers that persist
 * keep their position and re-flow, so the reader sees WHERE the boundary moves
 * (Firecracker gains a guest kernel above the boundary; gVisor interposes a
 * userspace kernel; raw Landlock loses the supervisor). Every layer carries a
 * text trust label, and the full comparison also exists as a server-rendered
 * dimension table on the page — this diagram is never the sole carrier.
 */

type Trust = "hostile" | "partial" | "trusted" | "contained";

interface Layer { key: string; label: string; sub?: string; trust: Trust }
interface Boundary { key: string; mechanism: string; strength: "kernel" | "hardware" | "userspace" }
type Row = ({ kind: "layer" } & Layer) | ({ kind: "boundary" } & Boundary);

interface Arch {
  id: string; name: string; rows: Row[];
  escape: string; gains: string; cost: string;
}

const ARCHS: Arch[] = [
  {
    id: "sandlock",
    name: "Sandlock",
    rows: [
      { kind: "layer", key: "work", label: "Agent workload", trust: "hostile",
        sub: "assumed hostile — never executes an unconfined instruction" },
      { kind: "boundary", key: "b", strength: "kernel",
        mechanism: "Landlock LSM + seccomp-bpf + seccomp user notification" },
      { kind: "layer", key: "sup", label: "Supervisor", trust: "partial",
        sub: "partially trusted · userspace parent process · runtime decisions, CoW staging, credential injection" },
      { kind: "layer", key: "host", label: "Shared host kernel", trust: "trusted",
        sub: "fully trusted — “if the kernel is compromised, so is every guarantee”" },
    ],
    escape: "a kernel privilege-escalation bug in any syscall the policy permits",
    gains: "~5 ms start (project claim) · no root · no image · HTTP-level policy and supervisor-held credentials",
    cost: "one shared kernel: the workload and the host meet inside the same kernel",
  },
  {
    id: "firecracker",
    name: "Firecracker",
    rows: [
      { kind: "layer", key: "work", label: "Workload", trust: "hostile", sub: "assumed hostile" },
      { kind: "layer", key: "guest", label: "Guest kernel", trust: "contained",
        sub: "separate kernel — its compromise is contained inside the VM" },
      { kind: "boundary", key: "b", strength: "hardware",
        mechanism: "Hardware virtualisation — narrow virtio device surface" },
      { kind: "layer", key: "sup", label: "VMM + KVM", trust: "partial",
        sub: "trusted · requires root / KVM access" },
      { kind: "layer", key: "host", label: "Host kernel", trust: "trusted", sub: "fully trusted" },
    ],
    escape: "a VMM or KVM bug — after first compromising the guest kernel",
    gains: "two boundaries: highest realistic security ceiling of the four",
    cost: "~100 ms start · root required · image build · no semantic (HTTP/credential) policy",
  },
  {
    id: "gvisor",
    name: "gVisor",
    rows: [
      { kind: "layer", key: "work", label: "Workload", trust: "hostile", sub: "assumed hostile" },
      { kind: "boundary", key: "b", strength: "userspace",
        mechanism: "Every syscall intercepted and re-serviced in userspace" },
      { kind: "layer", key: "sup", label: "Sentry — userspace kernel", trust: "partial",
        sub: "reimplements the Linux syscall interface; presents a narrowed surface to the host" },
      { kind: "layer", key: "host", label: "Host kernel", trust: "trusted",
        sub: "fully trusted, but reached only through the Sentry" },
    ],
    escape: "a Sentry bug, or a host-kernel bug reachable through it",
    gains: "host syscall surface shrunk to what the Sentry forwards",
    cost: "per-syscall performance tax · compatibility bounded by how completely the Sentry reimplements Linux",
  },
  {
    id: "raw",
    name: "Raw Landlock / process isolation",
    rows: [
      { kind: "layer", key: "work", label: "Workload", trust: "hostile", sub: "assumed hostile" },
      { kind: "boundary", key: "b", strength: "kernel",
        mechanism: "Landlock + seccomp — the identical kernel primitives" },
      { kind: "layer", key: "host", label: "Shared host kernel", trust: "trusted",
        sub: "fully trusted — same ceiling as Sandlock" },
    ],
    escape: "a kernel privilege-escalation bug — the identical ceiling to Sandlock",
    gains: "no dependency: the primitives are public kernel features anyone can call",
    cost: "no supervisor, no policy engine, no CoW rollback, no HTTP ACL, no credential injection — every hard part is missing",
  },
];

const TRUST_STYLE: Record<Trust, string> = {
  hostile: "border-absent/45 bg-absent-pale",
  partial: "border-claim/40 bg-claim-pale",
  trusted: "border-paper-line bg-paper",
  contained: "border-trace/35 bg-trace-pale",
};

const TRUST_TAG: Record<Trust, string> = {
  hostile: "HOSTILE",
  partial: "PARTIALLY TRUSTED",
  trusted: "FULLY TRUSTED",
  contained: "CONTAINED IF COMPROMISED",
};

const BOUNDARY_TONE: Record<Boundary["strength"], string> = {
  hardware: "border-trace/60 text-trace",
  kernel: "border-exec/60 text-exec-deep",
  userspace: "border-claim/60 text-claim",
};

export function BoundaryDiagram() {
  const reduced = usePrefersReducedMotion();
  const [active, setActive] = useState("sandlock");
  const arch = ARCHS.find((a) => a.id === active) ?? ARCHS[0];

  return (
    <div className="panel-raised overflow-hidden">
      <div className="flex flex-wrap gap-2 border-b border-paper-line p-3 sm:p-4"
           role="group" aria-label="Choose an isolation architecture to inspect">
        {ARCHS.map((a) => (
          <button key={a.id} type="button" onClick={() => setActive(a.id)}
                  aria-pressed={a.id === active} className="ctl">
            {a.name}
          </button>
        ))}
      </div>

      <div className="px-4 py-5 sm:px-6" aria-live="polite">
        <div className="mx-auto flex max-w-xl flex-col gap-1.5">
          {arch.rows.map((row, i) => {
            /* Keying by `arch.id + key` re-mounts a layer only when it genuinely
               changes role, so shared layers (workload, host kernel) transition
               in place instead of flashing. */
            const enter = reduced ? undefined : {
              animation: `dz-layer-in 420ms cubic-bezier(.22,.61,.36,1) both`,
              animationDelay: `${i * 55}ms`,
            };
            if (row.kind === "boundary") {
              return (
                <div key={`${arch.id}-${row.key}`} style={enter}
                     className={`relative border-y-2 border-dashed px-3 py-1.5 text-center ${BOUNDARY_TONE[row.strength]}`}>
                  <span className="mono text-[11px] uppercase tracking-wider">
                    ▚ {row.mechanism} ▞
                  </span>
                </div>
              );
            }
            return (
              <div key={`${arch.id}-${row.key}`} style={enter}
                   className={`rounded border px-4 py-3 ${TRUST_STYLE[row.trust]}`}>
                <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
                  <span className="text-[14.5px] font-semibold text-ink">{row.label}</span>
                  <span className="mono text-[10px] uppercase tracking-widest text-ink-faint">
                    {TRUST_TAG[row.trust]}
                  </span>
                </div>
                {row.sub ? <p className="meta mt-1 text-[12.5px]">{row.sub}</p> : null}
              </div>
            );
          })}
        </div>

        <dl className="mx-auto mt-5 grid max-w-xl gap-3 text-[13.5px]">
          <div className="trace-rule">
            <dt className="eyebrow">Escape requires</dt>
            <dd className="body mt-1">{arch.escape}</dd>
          </div>
          <div className="trace-rule trace-rule-signal">
            <dt className="eyebrow">What this buys</dt>
            <dd className="body mt-1">{arch.gains}</dd>
          </div>
          <div className="trace-rule">
            <dt className="eyebrow">What it costs</dt>
            <dd className="body mt-1">{arch.cost}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
