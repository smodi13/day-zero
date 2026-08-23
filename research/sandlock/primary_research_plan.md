# Sandlock — Primary Research Plan

**Nobody has been contacted, and nobody will be as part of this project.** This is a plan
for conversations that would be needed *before* an investment decision, written so the
gaps in outside-in research are explicit.

Each section states what would **strengthen** and what would **weaken** the thesis, written
before the conversation, so a persuasive answer cannot retroactively become the bar.

---

## 1. Founder / CEO — Cong Wang

**Objective:** resolve the three things public evidence cannot: adversarial-testing
history, the commercial wedge, and whether sandbox is the company or the entry point.

1. Your security page says a kernel LPE in a permitted syscall defeats the sandbox. Which
   customers have accepted that trade, and which have refused it — and what did the ones
   who refused choose instead?
2. `cow/seccomp.rs` is your largest file. What is the hardest correctness problem in the
   copy-on-write path, and what have you got wrong there before?
3. Has anyone outside the team attempted an escape? Audit, bug bounty, red team, a
   customer's security review — what happened, and what did it change?
4. Landlock ABI v6 means kernel 6.12. What fraction of inbound interest dies on that
   requirement, and what does `allow_degraded` actually get used for in the field?
5. Multikernel sells three products. If you had to kill two, which survive, and is Sandlock
   a wedge into the cloud-OS business or the business itself?
6. `branchfs` and `branching` both stopped in Q2 2026 as sandlock accelerated. What did you
   learn that made you consolidate?
7. Sandlock is Apache-2.0. Your site says "what is open, what is licensed." Where is that
   line, and what stops a cloud provider from running the open core as a service?

**Strengthens:** a specific, unflattering war story about a CoW correctness bug; a real
adversarial engagement with a named outcome; a crisp answer on the open/licensed boundary.
**Weakens:** "nobody has tried to break it yet"; a licence boundary drawn after the fact;
three products with no ranking.

## 2. A production user (agent platform or CI operator)

**Objective:** establish whether anyone runs this in production and what it replaced.

1. What were you doing before — containers, gVisor, nothing — and what specifically broke?
2. Did you measure the 5 ms figure yourself? On what kernel?
3. Which sandlock feature would you actually miss: the syscall filtering, the HTTP ACL, the
   credential injection, or the CoW rollback?
4. Have you hit a workload sandlock could not run?
5. Who wrote your policy, and how often is it wrong?
6. Would you pay, and for what — the runtime, the scheduler, or support?

**Strengthens:** the answer to (3) being HTTP ACL or credential injection — those are the
differentiated parts. **Weakens:** "we use it because it's fast", which a microVM
improvement erases.

## 3. A security engineer who does not use it

**Objective:** an adversarial read from someone with no stake.

1. Given a shared kernel and a permitted syscall set, how would you attack this?
2. Is a "partially trusted" supervisor handling attacker-influenced notifications a sound
   boundary, or is it a new attack surface?
3. Would you accept this for untrusted third-party code, or only for semi-trusted agent
   code?
4. What would an audit have to cover before you would deploy it?
5. Where does Landlock itself have sharp edges people underestimate?

**Strengthens:** "sound design, needs an audit". **Weakens:** a concrete escape sketch that
does not require a kernel bug.

## 4. A maintainer of a competing project (gVisor, Firecracker, bubblewrap)

**Objective:** understand the trade honestly from the other side.

1. Where is Sandlock's approach genuinely better than yours?
2. Where do you think it is fooling itself?
3. Has the AI-agent workload changed what people ask you for?
4. Could you add HTTP-level ACLs and credential injection, and why haven't you?
5. What is the real cost of your per-syscall interposition on agent workloads?

**Strengthens:** an admission that policy-level egress control is outside their model.
**Weakens:** "we shipped that last quarter."

## 5. An agent-platform builder (the buyer)

**Objective:** test whether sandboxing is a purchase or a checkbox.

1. What isolates customer code on your platform today, and who chose it?
2. Is startup latency a real constraint at your concurrency, or a benchmark concern?
3. Would you pay for isolation, or expect it from your cloud provider?
4. What does your security review demand before you adopt an isolation layer?
5. If a model writes code that exfiltrates a customer key, who is accountable — and does
   that change what you buy?

**Strengthens:** an existing budget line and a named owner. **Weakens:** "our cloud
provider handles it", which makes this a feature rather than a company.

---

## What would remain unknown even after all five

Revenue, retention, and whether the open-core boundary holds commercially. Those need a
data room, not a conversation.
