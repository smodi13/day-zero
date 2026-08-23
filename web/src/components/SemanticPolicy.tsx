"use client";

import { useState } from "react";

/**
 * The core security insight, made concrete.
 *
 * A prompt-injected agent does not exploit a memory bug. It makes a *correct*
 * API call, with a *real* credential, to the wrong place. This walks that exact
 * request through two boundaries and shows where each one can and cannot answer.
 *
 * Precision matters more than drama here, so the copy is deliberately bounded:
 * a VM boundary is not "weak", it answers a different question; and Sandlock's
 * policy layer is described as *able to express* a constraint, never as solving
 * prompt injection. The full text is present for every step regardless of which
 * one is selected — the buttons change emphasis, not availability.
 */

const REQUEST = [
  { k: "AGENT", v: "the coding agent you deployed", ok: true, note: "legitimate process" },
  { k: "CREDENTIAL", v: "the real API key it was given", ok: true, note: "legitimate secret" },
  { k: "OPERATION", v: "POST /v1/messages", ok: true, note: "legitimate method + path" },
  { k: "DESTINATION", v: "attacker-controlled.example", ok: false, note: "NOT on the policy allowlist" },
];

const BOUNDARIES = [
  {
    id: "vm",
    name: "VM / namespace boundary",
    verdict: "Cannot answer from the boundary alone",
    tone: "claim" as const,
    detail:
      "Every element of the request is legitimate at the level the boundary inspects. The process is permitted to run, permitted to hold the credential, and permitted to open an outbound socket. A hardware or namespace boundary answers “can this process reach the network” — and here the honest answer is yes. Confining the destination is possible outside the VM (an egress firewall, a proxy), but it is not something the isolation boundary itself expresses.",
    stops: null,
  },
  {
    id: "sandlock",
    name: "Sandlock policy layer",
    verdict: "Expressible as policy — destination and credential are separable",
    tone: "exec" as const,
    detail:
      "The HTTP ACL matches on method, host and path, so a rule that permits POST to one host does not permit the same call to another. Separately, the credential stays in the supervisor and is attached after the ACL check, so a request that fails the check never carries the secret. Both are OBSERVED in the code and the docs; neither is independently verified here, and neither is a claim that prompt injection is solved — a policy that grants too much still grants too much, which the project states plainly.",
    stops: 3,
  },
];

export function SemanticPolicy() {
  const [active, setActive] = useState("sandlock");
  const b = BOUNDARIES.find((x) => x.id === active) ?? BOUNDARIES[1];

  return (
    <div className="panel-raised overflow-hidden">
      <div className="grid gap-px bg-paper-line lg:grid-cols-2">
        <div className="bg-paper-card p-6">
          <p className="eyebrow">Traditional isolation asks</p>
          <p className="mt-3 text-xl font-semibold tracking-tight text-ink-dim">
            “Can this process access that resource?”
          </p>
          <p className="meta mt-3">
            Namespaces, microVMs and userspace kernels all answer this, some with a very
            high ceiling. It is a binary, structural question.
          </p>
        </div>
        <div className="bg-paper-card p-6">
          <p className="eyebrow">Agent security also asks</p>
          <p className="mt-3 text-xl font-semibold tracking-tight text-ink">
            “Should this <em className="not-italic text-exec-deep">legitimate</em> agent use this{" "}
            <em className="not-italic text-exec-deep">legitimate</em> credential for this{" "}
            <em className="not-italic text-exec-deep">legitimate</em> operation, against this
            destination, <em className="not-italic text-exec-deep">right now</em>?”
          </p>
          <p className="meta mt-3">
            A prompt-injected agent does not exploit a memory bug. It makes a correct API
            call with a real credential to the wrong place.
          </p>
        </div>
      </div>

      {/* the request, walked through element by element */}
      <div className="border-t border-paper-line px-5 py-6 sm:px-6">
        <p className="eyebrow">One request, four elements</p>
        <ol className="mt-3 grid gap-1.5">
          {REQUEST.map((r, i) => {
            const stopped = b.stops !== null && i === b.stops;
            return (
              <li key={r.k}
                  className={`flex flex-wrap items-center gap-x-3 gap-y-1 rounded border px-3 py-2 transition-colors duration-300 ${
                    r.ok ? "border-paper-line bg-paper"
                         : stopped ? "border-exec/50 bg-exec-pale"
                                   : "border-absent/40 bg-absent-pale"}`}>
                <span className="mono w-28 shrink-0 text-[11px] uppercase tracking-wider text-ink-faint">
                  {r.k}
                </span>
                <span className="mono min-w-0 flex-1 text-[12.5px] text-ink">{r.v}</span>
                <span className={`mono text-[11px] ${
                  r.ok ? "text-ink-dim" : stopped ? "text-exec-deep" : "text-absent"}`}>
                  {r.ok ? "✓ " : stopped ? "◼ " : "✕ "}
                  {stopped ? "policy stops the request here" : r.note}
                </span>
              </li>
            );
          })}
        </ol>
      </div>

      {/* which boundary is being asked */}
      <div className="flex flex-wrap gap-2 border-t border-paper-line px-5 py-3 sm:px-6"
           role="group" aria-label="Which boundary is asked to answer">
        {BOUNDARIES.map((x) => (
          <button key={x.id} type="button" onClick={() => setActive(x.id)}
                  aria-pressed={x.id === active} className="ctl">
            {x.name}
          </button>
        ))}
      </div>
      <div className={`border-t-2 px-5 py-5 sm:px-6 ${
        b.tone === "exec" ? "border-t-exec bg-exec-pale/40" : "border-t-claim bg-claim-pale/40"}`}
           aria-live="polite">
        <p className={`text-[15px] font-semibold ${
          b.tone === "exec" ? "text-exec-deep" : "text-claim"}`}>
          {b.name}: {b.verdict}
        </p>
        <p className="body mt-2 max-w-prose">{b.detail}</p>
      </div>
    </div>
  );
}
