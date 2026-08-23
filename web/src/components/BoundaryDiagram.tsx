"use client";

import { useState } from "react";

/**
 * Interactive trust-boundary comparison. Each architecture is a stack of layers
 * from the hostile workload down to hardware. Boundaries are drawn as named,
 * hatched bars — the mechanism is written on the boundary, because the mechanism
 * IS the security argument. Trust levels are labelled in text on every layer;
 * colour is only reinforcement.
 *
 * The full four-way comparison also exists as a server-rendered dimension table
 * on the page, so nothing here is the sole carrier of the information.
 */

type Trust = "hostile" | "partial" | "trusted" | "contained";

interface Layer { label: string; sub?: string; trust: Trust }
interface Boundary { mechanism: string; strength: "kernel" | "hardware" | "userspace" }
type Row = { kind: "layer"; layer: Layer } | { kind: "boundary"; boundary: Boundary };

interface Arch {
  id: string;
  name: string;
  rows: Row[];
  escape: string;
  gains: string;
  cost: string;
}

const ARCHS: Arch[] = [
  {
    id: "sandlock",
    name: "Sandlock",
    rows: [
      { kind: "layer", layer: { label: "Agent workload", sub: "assumed hostile — never executes an unconfined instruction", trust: "hostile" } },
      { kind: "boundary", boundary: { mechanism: "Landlock LSM + seccomp-bpf + seccomp user notification", strength: "kernel" } },
      { kind: "layer", layer: { label: "Supervisor", sub: "partially trusted · userspace parent process · runtime decisions, CoW staging, credential injection", trust: "partial" } },
      { kind: "layer", layer: { label: "Shared host kernel", sub: "fully trusted — “if the kernel is compromised, so is every guarantee”", trust: "trusted" } },
    ],
    escape: "a kernel privilege-escalation bug in any syscall the policy permits",
    gains: "~5 ms start (project claim) · no root · no image · HTTP-level policy and supervisor-held credentials",
    cost: "one shared kernel: the workload and the host meet inside the same kernel",
  },
  {
    id: "firecracker",
    name: "Firecracker",
    rows: [
      { kind: "layer", layer: { label: "Workload", sub: "assumed hostile", trust: "hostile" } },
      { kind: "layer", layer: { label: "Guest kernel", sub: "separate kernel — its compromise is contained inside the VM", trust: "contained" } },
      { kind: "boundary", boundary: { mechanism: "Hardware virtualisation — narrow virtio device surface", strength: "hardware" } },
      { kind: "layer", layer: { label: "VMM + KVM", sub: "trusted · requires root / KVM access", trust: "partial" } },
      { kind: "layer", layer: { label: "Host kernel", sub: "fully trusted", trust: "trusted" } },
    ],
    escape: "a VMM or KVM bug — after first compromising the guest kernel",
    gains: "two boundaries: highest realistic security ceiling of the four",
    cost: "~100 ms start · root required · image build · no semantic (HTTP/credential) policy",
  },
  {
    id: "gvisor",
    name: "gVisor",
    rows: [
      { kind: "layer", layer: { label: "Workload", sub: "assumed hostile", trust: "hostile" } },
      { kind: "boundary", boundary: { mechanism: "Every syscall intercepted and re-serviced in userspace", strength: "userspace" } },
      { kind: "layer", layer: { label: "Sentry — userspace kernel", sub: "reimplements the Linux syscall interface; presents a narrowed surface to the host", trust: "partial" } },
      { kind: "layer", layer: { label: "Host kernel", sub: "fully trusted, but reached only through the Sentry", trust: "trusted" } },
    ],
    escape: "a Sentry bug, or a host-kernel bug reachable through it",
    gains: "host syscall surface shrunk to what the Sentry forwards",
    cost: "per-syscall performance tax · compatibility bounded by how completely the Sentry reimplements Linux",
  },
  {
    id: "raw",
    name: "Raw Landlock / process isolation",
    rows: [
      { kind: "layer", layer: { label: "Workload", sub: "assumed hostile", trust: "hostile" } },
      { kind: "boundary", boundary: { mechanism: "Landlock + seccomp — the identical kernel primitives", strength: "kernel" } },
      { kind: "layer", layer: { label: "Shared host kernel", sub: "fully trusted — same ceiling as Sandlock", trust: "trusted" } },
    ],
    escape: "a kernel privilege-escalation bug — the identical ceiling to Sandlock",
    gains: "no dependency: the primitives are public kernel features anyone can call",
    cost: "no supervisor, no policy engine, no CoW rollback, no HTTP ACL, no credential injection — every hard part is missing",
  },
];

const TRUST_STYLE: Record<Trust, string> = {
  hostile: "border-absent/50 bg-absent/10",
  partial: "border-claim/40 bg-claim/5",
  trusted: "border-line bg-raised",
  contained: "border-trace/40 bg-trace/5",
};

const TRUST_TAG: Record<Trust, string> = {
  hostile: "HOSTILE",
  partial: "PARTIALLY TRUSTED",
  trusted: "FULLY TRUSTED",
  contained: "CONTAINED IF COMPROMISED",
};

function BoundaryBar({ b }: { b: Boundary }) {
  const tone = b.strength === "hardware" ? "border-trace/60 text-trace"
    : b.strength === "kernel" ? "border-signal/60 text-signal"
    : "border-claim/60 text-claim";
  return (
    <div className={`relative border-y-2 border-dashed px-3 py-1.5 text-center ${tone}`}
         role="presentation">
      <span className="mono text-[11px] uppercase tracking-wider">
        ▚ {b.mechanism} ▞
      </span>
    </div>
  );
}

export function BoundaryDiagram() {
  const [active, setActive] = useState("sandlock");
  const arch = ARCHS.find((a) => a.id === active) ?? ARCHS[0];

  return (
    <div className="panel overflow-hidden">
      <div className="flex flex-wrap gap-2 border-b border-line p-3 sm:p-4"
           role="group" aria-label="Choose an isolation architecture to inspect">
        {ARCHS.map((a) => (
          <button key={a.id} type="button" onClick={() => setActive(a.id)}
            aria-pressed={a.id === active}
            className={`rounded border px-3 py-1.5 text-[13px] transition-colors ${
              a.id === active
                ? "border-signal/60 bg-signal/10 text-signal"
                : "border-line bg-raised text-dim hover:text-text"}`}>
            {a.name}
          </button>
        ))}
      </div>

      <div className="px-4 py-5 sm:px-6" aria-live="polite">
        <div className="mx-auto flex max-w-xl flex-col gap-1.5">
          {arch.rows.map((row, i) =>
            row.kind === "boundary" ? (
              <BoundaryBar key={i} b={row.boundary} />
            ) : (
              <div key={i}
                   className={`rounded border px-4 py-3 ${TRUST_STYLE[row.layer.trust]}`}>
                <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
                  <span className="text-[14.5px] font-semibold text-text">{row.layer.label}</span>
                  <span className="mono text-[10px] uppercase tracking-widest text-faint">
                    {TRUST_TAG[row.layer.trust]}
                  </span>
                </div>
                {row.layer.sub ? <p className="meta mt-1 text-[12.5px]">{row.layer.sub}</p> : null}
              </div>
            ),
          )}
        </div>

        <dl className="mx-auto mt-5 grid max-w-xl gap-3 text-[13.5px] sm:grid-cols-1">
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
