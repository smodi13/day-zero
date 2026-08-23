# Array Ventures — Strategy Research

**Research date:** 2026-08-22
**Method:** public sources only (Array's own site, Array's Substack `insights.array.vc`,
the public job posting, portfolio-company announcements, and third-party press).
Every claim below is tagged **OBSERVED** (stated in a cited public source),
**INFERRED** (my reading, marked as such), or **UNKNOWN**.

---

## 1. Fund overview

| Attribute | Value | Status | Source |
| --- | --- | --- | --- |
| AUM | "$250M+ AUM across 4 funds" | OBSERVED | array.vc/careers/ai-analyst |
| Funds | 4 | OBSERVED | same |
| Portfolio | "80+ portfolio companies" (careers page); "52 active investments" (site portfolio widget) | OBSERVED, and **internally inconsistent** — likely 80+ lifetime vs. 52 active | array.vc |
| Stage | Pre-seed / "at inception" / "Day 0 to Series A" | OBSERVED | array.vc, insights.array.vc |
| Check size | "$250K to $2.5M at inception" (careers); "$250k–$3m checks at formation" (Jan 2026); "actively investing $250K–$2M right now" (Dec 2025) | OBSERVED — the band moves; treat $250K–$3M as the outer envelope | multiple Array posts |
| Pace | "9–10 investments per year" | OBSERVED | careers page |
| Inbound volume | "200–300 inbound deals per month, evaluated with AI-powered tooling" | OBSERVED | careers page |
| Geography | HQ San Francisco; portfolio is not SF-only (HappyRobot founders pitched from Germany; Flamingo is Miami Beach; Wokelo is Seattle-area) | OBSERVED | Array posts, press |
| Investment areas | AI infrastructure, cybersecurity, HealthTech, FinTech, enterprise SaaS; site categories add AI Agents, AI Ops, EdTech, Martech, Collaboration, Robotics, Revtech | OBSERVED | careers page, array.vc |
| Contact | `deals@array.vc` / `arraydeals@array.vc` | OBSERVED | Array posts |
| 2025 activity | 9 new investments, 5 follow-ons; 16 portfolio companies raised in 2025, with Accel, IVP, Menlo, a16z participating | OBSERVED | insights.array.vc "What lies ahead" (2025-12-30) |

**Team (OBSERVED, from array.vc):** Shruti Gandhi (GP; engineer-turned-investor;
described as 100+ investments, 15 exits), Elias Torres (4x founder; Drift acquired for
$1.2B), Katie Jansen (former CMO, AppLovin), Roy Scheer (GTM, 0→$10M ARR).

**Shruti Gandhi (OBSERVED):** solo GP; active AI engineer; Columbia University computer
science professor; Commissioner at the San Francisco Employees' Retirement System;
earlier career as a developer on mainframe security, collaboration tools, and data
analytics; previously invested at True Ventures and Samsung's venture fund; raised
$150M across 3 funds as a solo GP (Money Moves podcast, Jan 2025) before the 4-fund /
$250M+ figure on the current careers page.

---

## 2. What "Day 0" means in practice

Array uses "at inception," "at formation," and "Day 0 to Series A" interchangeably.
Four concrete, source-backed data points define what that means operationally:

1. **Pre-product is explicitly in scope.** "If a company is pre-product, we can often
   relate directly to the underlying challenges through our own building experience."
   (Jan 2026, 15 Themes) — **OBSERVED**
2. **Array led Sapiom's pre-seed**, and Sapiom's founder had left Shopify roughly
   *three weeks* before founding. Accel led the seed; Dragonfly led the Series A.
   (Aug 2026 post + TechCrunch Feb 2026) — **OBSERVED**
3. **Array wrote HappyRobot's first round** when the founders "hadn't raised anything"
   and were pitching from Germany. (Aug 2026 post) — **OBSERVED**
4. **48-hour decision speed** on pitches. (Jan 2026) — **OBSERVED**

**INFERRED:** "Day 0" at Array is not a euphemism for "small seed." It means the
relationship starts before there is a round, sometimes before there is a product, and
frequently before the founder is legible to a database. That is precisely the window
DAY ZERO targets.

---

## 3. What Array appears to value in founders

**OBSERVED:**
- Founder-market fit framed as deep roots in the problem — "living the problem at a
  Fortune 100" or "being a key engineer who saw gaps first-hand."
- Technical origin: HappyRobot's founders were praised for "energy, curiosity,
  willingness to experiment, and relentless optimism" — behavioral, not credential.
- Array's own portfolio-velocity metric is *code*: founders "adding 500k lines of code
  that's from 41k just a couple quarters ago" (Dec 2025).
- Elias Torres and Shruti Gandhi have worked together "more than two decades" since IBM
  — relationships that long predate any round.

**INFERRED:** Array indexes on *demonstrated construction and problem proximity* rather
than institutional pedigree. Note the counter-signal for honesty: Sapiom's founder was a
Shopify director of engineering and HappyRobot went through YC — pedigree is present in
the portfolio, it just does not appear to be the selection *mechanism*.

---

## 4. Technical diligence philosophy

This is the most distinctive and most quotable part of Array's public posture.

> "We don't just review pitch decks — we use the products ourselves. If a company is
> pre-product, we can often relate directly to the underlying challenges through our own
> building experience. **In many cases, we attempt to recreate parts of a product
> ourselves to understand the technical complexity.**"
> — *[Array VC] 15 Themes We're Most Excited to Back*, 2026-01-09 — **OBSERVED**

> "The team dives into technical stacks, reads research papers, and evaluates the actual
> defensibility of what founders are building."
> — array.vc/careers/ai-analyst — **OBSERVED**

> "The team codes daily and tests products in developer environments during due diligence
> to evaluate founder fit."
> — Array Q3 2025 update — **OBSERVED**

**This directly authorizes DAY ZERO's Technical Reproduction Lab.** Array does not
describe reproduction as an aspiration; it describes it as current practice. A sourcing
system that ends at "here is an interesting builder" stops short of what Array already
does manually.

---

## 5. AI / infrastructure thesis

From *The Infrastructure Behind AI's "App Layer"* (2025-03-13) and the 15 Themes list
(2026-01-09). The 15 themes, verbatim — **OBSERVED**:

1. Self-driving operators: "AI suggests" → "AI does"
2. AI Governance Infrastructure: Control Layer Systems
3. AI Economics Infrastructure: Do more with less
4. Edge Intelligence: Inference, Optimization, Efficiency
5. Embodied World Models: Physical AI
6. Symbolic AI: Deterministic Reasoning
7. Knowledge-infused AI: Context Management
8. Energy Infrastructure: Hardware Bottleneck
9. Life Operators: Personal companion
10. Agent Economy: Transaction and commerce
11. Verifiable AI: On-Chain Proofs
12. Agent Learning Systems: RL and Training Loops
13. Vertical AI: Make any industry efficient
14. Content Authenticity: AI Manipulation
15. Boring Email Company: Just make my Inbox better :)

**Relevance weighting for DAY ZERO (INFERRED):** themes 2, 3, 4, 7, 10, 12 are the ones
where *pre-formation open-source artifacts are the dominant public evidence*. Themes 5,
8, 9, 11, 14, 15 are much harder to source from GitHub. DAY ZERO should concentrate on
the former and say so, rather than claiming even coverage.

---

## 6. Cybersecurity thesis

From *Agents broke the security stack* (2026-04-28) — **OBSERVED**:

- Core claim: the security stack built over 20 years assumed a human in the loop. Agents
  are "a process with tokens, admin permissions" that moves data "through syscalls."
- Scale claim: roughly **100 non-human identities per human user** in the average
  enterprise, and most security teams cannot inventory their own.
- Named failure cases: the Vercel breach via a compromised third-party AI assistant
  (OAuth token theft → Google Workspace takeover → internal systems); EchoLeak
  prompt-injection in Microsoft 365 Copilot exfiltrating via approved Microsoft URLs;
  Polyfill.io cross-layer supply-chain compromise; the 2023 MGM incident.
- Why existing tooling fails: "endpoint security watches keyboards and screens, DLP
  writes rules per app, and SaaS security tracks login flows — none of it catches an
  agent."
- **Already backed:** kernel-level data-movement governance treating agents and humans
  equivalently; web-infrastructure impersonation detection; adaptive AI-adversary crisis
  training.
- **Actively seeking:** agent identity and authority management; autonomous SOC /
  incident response; AI red-teaming and pre-deployment security testing; "vibe coding
  security" (securing production code written by agents).

That last list is effectively a published sourcing brief. DAY ZERO should treat those
four categories as named, current, unfilled mandates.

---

## 7. Enterprise thesis

**OBSERVED:** Array's site frames the fund as "Your First BD Hire And Partner For 2nd
Wave Of Customers," backed by "500+ industry experts" who act as angels, advisors and
customers. The Mar 2026 post *11 companies cracked 1M ARR in 6 months with DAD*
identifies Distribution as Differentiation, solo founders, and 1–2 person teams as a
recurring pattern in the portfolio. *Churn/Retention in the Era of AI* (Feb 2026) and
*If AI Doesn't Know You Exist* (Jan 2026, AI search optimization) round out a
go-to-market rather than technical thesis.

**INFERRED:** the enterprise thesis is a *post-investment* thesis. It describes how Array
helps after the check. It is not a sourcing signal, and DAY ZERO should not attempt to
source against it.

---

## 8. Data thesis

**OBSERVED:** Array's own site lists "data" as a core area; the fund's history includes
Mozart Data (out-of-the-box data stack, 2020), Integral (privacy-preserving data
quality, 2023), Hotdata (federated data layer), and Eventual/Daft (multimodal data
processing; Array participated in the Oct 2024 seed). Eventual's Daft is described as
"already processing petabytes of multimodal data daily at companies like Amazon,
CloudKitchens, Essential AI, and Together AI."

**INFERRED:** Array's data thesis is *engine-level*, not dashboard-level — query
engines, processing substrates, federated access layers. Every one of those categories
produces a public open-source artifact years before a round. This is the single most
backtestable part of Array's portfolio.

---

## 9. Array AI Labs

**What it verifiably is (OBSERVED):**

- Launched May 2025 ("Launching Array AI Labs at Array Ventures", 2025-05-30).
- **Experiment #1 (2025-05-29):** AI-generated podcasts with no training data,
  synthesizing content from guests' other public interviews. First subject: an interview
  with Ashton Kutcher.
- **Experiment #2:** AI-generated looks and videos (Nano Banana / Gemini 2.5, Kling 2.1,
  Seedance 1.0); a UGC-tools template combining NanoBanana, Seeddream, ElevenLabs,
  InfiniteTalk, and Qwen.
- **Joyce** — an "office hours agent" / "24x7 Office Hours with our AI Analyst Joyce"
  (2025-11-27) that assists prospective founders and answers portfolio questions.
- **Deal evaluation tooling:** "300+ deals in less than 48hrs," using Wokelo.ai (a
  portfolio company) for competitive research and Runable (a portfolio company) for task
  scheduling.
- **An internal 24/7 AI coworker** (2026-02-17) that "replaced half our internal tools":
  persistent structured memory updated by background processes into a searchable
  knowledge base; a "heartbeat" pattern that wakes on schedule to review tasks and flag
  issues; its own filesystem sandbox with isolated execution; on-demand skill/tool
  acquisition rather than loading all integrations at once. It replaced their operations
  dashboard by building and maintaining its own apps against live data.
- **Labs feeds the portfolio:** Array says it identified the problem Sapiom solved
  "while testing agents in Array's own stack at the Array Ventures AI lab."

**INFERRED:** Array AI Labs is two things at once — a *marketing/content* lab
(podcasts, video) and an *internal-operations engineering* lab (Joyce, the AI coworker,
deal triage). The second is the one that generated an investment. It is also a working
demonstration of the exact loop architecture Shruti wrote about in July 2026.

**UNKNOWN:** headcount, whether Labs has a budget separate from the fund, whether any
Labs code is or will be public, and whether an AI Analyst hire would own Labs
experiments or contribute to them.

---

## 10. Sourcing process — what is publicly knowable

**OBSERVED:**
- 200–300 inbound deals/month, triaged with AI tooling; 300+ deals reviewed in <48h in
  one documented instance.
- 9–10 investments/year → an implied inbound-to-investment rate of roughly
  **0.3%** (10 / ~3,000 annual inbound).
- Outbound is explicitly a hiring priority: the AI Analyst is asked to source from two
  pools and attend SF hackathons and community events.
- The target for the role is **2–3 quality founder intros per week**.
- Network sourcing: 500+ industry experts as angels/advisors/customers.
- Relationship-first sourcing: Elias Torres (two decades), HappyRobot pre-raise, Sapiom
  three weeks after the founder left Shopify.
- Public front door: `deals@array.vc`, restated at the bottom of most posts.

**INFERRED:** the fund is inbound-saturated and outbound-constrained. AI tooling is
already applied to *triage* (reducing 300 inbound to a shortlist). It is not evident that
AI tooling is applied to *discovery* (finding people who never send an inbound). That gap
is the entire premise of DAY ZERO.

**UNKNOWN:** what Array's internal CRM is, whether they maintain a watchlist of
pre-formation builders, and whether Joyce touches outbound at all.

---

## 11. Shruti Gandhi's current technical themes

Ordered by recency. These are the themes DAY ZERO should be able to speak to.

### Loop → Graph engineering (2026-07-22) — most important for this project

**OBSERVED:**
- The shift from prompt engineering to **loop design**: define a goal, tools,
  verification checks, and stop conditions; the agent iterates without a human at each turn.
- Five loop steps: **discover → plan → execute → verify → iterate.** Real loops need
  state tracking, hard exit conditions, and objective verification to avoid "soft
  completion."
- **Accepted Work Units (AWU):** each loop produces measurable, accept/reject-able
  output. Replaces token counting with **cost per accepted work unit**. Zendesk's
  outcome-based pricing (pay when tickets resolve) is the cited analogue.
- Named failure modes: the **Ralph Wiggum failure** (agent declares completion without
  hard gates), **goal drift** (loops decide "done enough"; self-grading bias compounds),
  and **flawed loop accumulation** (bad assumptions propagate; review debt and token
  waste pile up silently).
- The investable layer is named **LoopOps**: job specifications, state ledgers, tool
  envelopes, completion gates, budget policies, escalation queues.
- Defensibility comes from **vertical loops** — narrow, high-quality domain automation
  (password resets before full support replacement), not wholesale job replacement.

DAY ZERO adopts AWU as its own productivity metric (see `accepted_work_unit.md`). This
is not a coincidence of vocabulary — it is the correct frame for a sourcing loop, and
using Array's own published metric is the most direct way to show the system was designed
for them.

### Agent security (2026-04-28)
Non-human identity explosion, agents as processes with tokens, cross-layer web trust
attacks, incident-response chaos. Four explicitly-wanted categories (§6 above).

### AI economics / "do more with less" (Theme 3, Jan 2026; Loop post, Jul 2026)
Cost per accepted outcome, budget policies, token waste as a silent liability.

### Context management / knowledge-infused AI (Theme 7, Jan 2026)
Also visible in the internal AI coworker's persistent structured memory design.

### Governance / control layer (Theme 2, Jan 2026)
Policy enforcement, permissions, and audit as an infrastructure category.

### Web world models (2026-01-23) and embodied world models (Theme 5)
Present in the writing; hard to source from public artifacts. Noted, not prioritized.

**Explicitly NOT retrofitted:** I found no public Array writing on MCP-specific security
as a named category, on agent evaluation as a standalone thesis, or on RL environments
as a sourcing target — despite all three being adjacent to themes they do name. Where
DAY ZERO surfaces builders in those areas it should say "adjacent to Array's stated
themes," not "matches Array's thesis."

---

## 12. Implications for DAY ZERO

1. **Array already reproduces products manually.** DAY ZERO's reproduction lab is not a
   novelty; it is automation of an existing Array practice.
2. **Array publishes what it wants to fund and cannot find.** The four "actively seeking"
   security categories are a live sourcing brief.
3. **Array measures AI work in Accepted Work Units.** DAY ZERO should be measured the
   same way, and should report cost per accepted lead honestly, including the misses.
4. **Array's constraint is outbound discovery, not triage.** A tool that ranks the 300
   inbound better is worth little to them. A tool that finds the builder who never sends
   an inbound is worth a lot.
5. **2–3 intros/week × ~48 working weeks ≈ 100–150 intros/year against 9–10
   investments.** DAY ZERO's acceptance bar has to be calibrated to that ratio, not to
   a demo-friendly hit rate.

---

## Sources

All URLs recorded with access date in `../sources/source_registry.csv`.
Primary: array.vc, array.vc/careers/ai-analyst, insights.array.vc (12 posts read),
array.vc/insights (index of ~70 items).
Secondary: TechCrunch, Business Insider, SiliconANGLE, FinSMEs, Fortune, Businesswire,
ChannelBuzz, pmf.show, linuxiac.
