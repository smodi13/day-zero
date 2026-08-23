# Array Ventures — Portfolio Map

**Research date:** 2026-08-22
**Purpose:** (a) understand what Array actually backs at the artifact level, and
(b) select a cohort for the historical holdout in `backtest_methodology.md`.

**Evidence rules applied here:** a company appears in this table only if a public source
associates Array Ventures with it. Where a source only says "Array Ventures portfolio"
without a round, the round is UNKNOWN. Where Array's own writing names the round, it is
OBSERVED. Nothing in the "Array round" column is inferred from co-investor lists.

---

## 1. Disclosed portfolio — companies with a source-backed Array association

| Company | What it built | Layer | Array round (if public) | Later financing / outcome | Source type |
| --- | --- | --- | --- | --- | --- |
| **Eventual** (Daft) | Rust-native distributed engine for multimodal data (text/image/audio/video) | Data engine | Participated in **$7.5M seed, 2024-10-01** (led by CRV/Brittany Walker; also YC, Essence VC) | **$20M Series A, 2025-06-24** led by Felicis; M12, Citi Ventures. Total $30M raised | Press + Array insights |
| **Sapiom** | Infrastructure layer between agents and the services they consume — budgets and permissions enforced *before* execution, full audit trail, cost per step | Agent economics / governance | **Led the pre-seed** | **$15M seed, 2026-02-05** (Accel); **$35M Series A, 2026-08** (Dragonfly). ~$50M total <1yr from founding. Reported 270M transactions across 100k+ agents daily | Array post + TechCrunch |
| **HappyRobot** | AI agents for freight/logistics ops (calls, email, paperwork) → "AI-native OS" | Vertical AI | **First round** (pre-institutional; founders "hadn't raised anything") | $500K seed 2023 → **$15.6M Series A 2024-12** (a16z) → **$44M Series B 2025-09** (Base10) → **$150M Series C** at $1.2B | Array post + press |
| **Meibel** | Runtime confidence + decision traceability for enterprise generative AI | Agent reliability | UNKNOWN | **$7M, 2025-05-28** | Array insights |
| **Flamingo** | OpenFrame — AI + open-source operating system for MSPs; agents "Fae" and "Mingo" automate password resets, disk alerts, patching, threat detection | Vertical AI / IT ops | **$2.2M pre-seed co-led** (Focal VC + Array VC) | Launched from stealth 2025-10-28 | Businesswire, TFN, ChannelBuzz |
| **Wokelo** | AI-generated due-diligence research reports | Vertical AI (finance) | UNKNOWN | **$4M, 2024-10** | GeekWire |
| **Integral** | AI agents automating HIPAA expert determination and privacy-preserving data prep | HealthTech data infra | UNKNOWN | **$6.9M seed, 2023-09-05** | Businesswire |
| **Perspective AI** | Customer-truth discovery (founder: Guy Nirpaz, ex-Totango) | Enterprise SaaS | UNKNOWN | **$4M seed, emerged from stealth 2025-01-30** | Business Wire |
| **CandorIQ** | Compensation and workforce-spend planning for HR/Finance | FinTech / people spend | UNKNOWN | **$4.8M seed, 2025-07-22** | Array insights |
| **Wabi** | "YouTube of apps" — AI app platform (founder of Replika) | Consumer/prosumer AI | UNKNOWN | **$20M pre-seed, 2025-11** (a16z) | TechCrunch |
| **Blumira** | Automated threat detection and response | Cybersecurity | UNKNOWN | — | array.vc portfolio |
| **Mozart Data** | Out-of-the-box modern data stack (founders Peter Fishman, Dan Silberman) | Data infra | UNKNOWN | **$4M seed, 2020-11-11** | TechCrunch |
| **Runable** | Agent that automates daily/repeated tasks; used inside Array's own deal flow | Agent product | UNKNOWN | Launch exceeded 1M views | Array insights |
| **Hotdata** | Federated data layer | Data infra | UNKNOWN | — | Array insights |
| **Precanto** | AI financial planning & analysis | FinTech | UNKNOWN | — | Array insights |
| **Zingly** | Customer-experience transformation | Enterprise SaaS | UNKNOWN | — | Array insights |
| **FinanceOps** | Accounts-receivable automation | FinTech | UNKNOWN | — | Array insights |
| **MokSa.ai** | Retail theft/fraud detection from security cameras | Vertical AI / vision | UNKNOWN | **$1.5M pre-seed, 2024-04** | Business Insider |
| **Blaze (BlazeAI)** | Automated LinkedIn/X marketing content | Martech | UNKNOWN | — | Array insights |
| **AnswersAI** | One-click answers (EdTech) | EdTech | UNKNOWN | — | array.vc |
| **Sotto** | Omni-channel SMS platform | Martech | UNKNOWN | — | array.vc |
| **Blendid** | Autonomous food platform (robotics) | Robotics | UNKNOWN | — | array.vc |
| **Capsule** | Collaborative video / video Q&A platform | Collaboration | UNKNOWN | **$2M seed, 2021-01** | TechCrunch |
| **Cast (Cast AI)** | Agent for account management / customer success | Revtech | UNKNOWN | — | array.vc |
| **Retina Robotics** | Robotics | Robotics | UNKNOWN | — | Array insights |
| **ORO** | Enterprise procurement | Enterprise SaaS | UNKNOWN | **$25M Series A, 2022-11** | Business Wire |
| **Tumble** | Smart laundry platform | Consumer ops | UNKNOWN | **$7M seed, 2022-10** | Business Wire |

### Exits / acquisitions publicly associated with Array

| Company | Outcome | Date |
| --- | --- | --- |
| **Agency** (founded by Elias Torres) | Acquired by **Klaviyo** | 2026 |
| **Simility** | Acquired by **PayPal** (~$120M) — AI fraud/risk | 2018-06 |
| **Passage AI** | Acquired by **ServiceNow** — conversational AI | 2020-01 |
| **Era Software** | Acquired by **ServiceNow** — observability/log management | 2022-10 |
| **ZecOps** | Acquired by **Jamf** — mobile security research | 2022-11 |
| **Art19** | Acquired by **Amazon** — podcast hosting/ads | 2021-06 |
| **Managed by Q** | Acquired by **WeWork** | 2019-04 |
| **Xwing** (autonomy division) | Acquired by **Joby Aviation** | 2024-06 |
| **PrecisionGx** | Acquired by **TREND Health Partners** | 2023-10 |

---

## 2. Two entity-resolution traps found in this portfolio (important)

These are real, and both would break a naive name-matching sourcing engine. They are
carried into `entity_graph.md` as test cases and into `negative_controls.md`.

**Trap 1 — two companies named "Agency."**
- *Agency* (Array portfolio, founded by Elias Torres, acquired by Klaviyo in 2026).
- *Agency* / AgentOps (Alex Reibman, Adam Silverman, Shawn Qiu) — agent observability,
  born from SF AI hackathons in summer 2023, raised a **$2.6M pre-seed led by 645
  Ventures and Afore Capital**, **Array Ventures did not participate** (TechCrunch,
  2024-08-28).
Merging these would produce a false claim that Array backed a company it did not.

**Trap 2 — two companies named "Eventual."**
- *Eventual* (Daft) — data processing, seed 2024-10-01, CRV-led, Array participated.
- *Eventual* — a climate fintech that raised $7.5M from AlleyCorp and Upfront Ventures
  in July 2025 (Fortune).
Both are "Eventual," both raised $7.5M, and the amounts collide. Name + amount matching
would merge them.

---

## 3. What the portfolio tells us about Array's actual selection behavior

**OBSERVED patterns:**

1. **Infrastructure-with-an-open-artifact recurs.** Eventual/Daft (Apache-2.0 Rust
   engine), Flamingo (open-source MSP platform), Integral (privacy tooling). These are
   companies whose core work was publicly inspectable before or at the round.
2. **Operator→founder is a real, repeated pattern.** Sapiom (Shopify director of
   engineering → founded 3 weeks later), Perspective AI (Guy Nirpaz, ex-Totango CEO),
   Flamingo (Michael Assraf, cybersecurity/MSP veteran), Mozart Data (two operators who
   had worked together 20 years).
3. **Young-builder is also real.** HappyRobot (YC S23, robotics undergrads, sibling
   co-founders, pivoted post-YC).
4. **Array is frequently the *first* institutional money** and then hands off to Accel,
   a16z, CRV, Felicis, Dragonfly, Base10.
5. **Security is a persistent thread** across a decade: Simility (2018), ZecOps (2022),
   Blumira, and now the agent-security thesis.

**INFERRED:** Array's edge is timing plus technical legibility. They commit before the
company is a legible database row, and they can do that because they can read the
artifact. Any sourcing system built for them must be able to read the artifact too.

---

## 4. Backtest cohort selection (design only — not yet run)

Selection criterion is **evidence recoverability**, not success. Specifically: did
meaningful *public* evidence plausibly exist before a known financing milestone, and can
that evidence still be retrieved today with a cutoff filter?

I deliberately included companies where I expect DAY ZERO to **fail**, and companies
where the pre-round evidence was probably private.

### Selected cohort (10 companies)

| # | Company | Array relationship | Milestone used as "obvious" | Proposed cutoff | Pre-cutoff evidence likely recoverable? | Expected difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | **Eventual / Daft** | Participated in seed | Seed announced 2024-10-01 | **2024-09-30** | **Yes, strongly.** `Eventual-Inc` GitHub org created 2022-02-03; `Eventual-Inc/Daft` repo created 2022-04-25; sustained multi-contributor commits from 2022 (verified via GitHub API this session). Founders Sammy Sidhu, Jay Chia (ex-Lyft). | Should be a PASS. If DAY ZERO misses this, the ontology is broken. |
| B2 | **Sapiom** | **Led pre-seed** | Seed 2026-02-05 (Accel) | **2026-02-04** | Partially. Founder Ilan Zerbib (5 yrs Shopify director of engineering, payments). Founded 2025 in SF. Pre-seed date itself is UNKNOWN. | Hard. Tests whether the FORMING state can be reached from an operator transition with little public artifact. |
| B3 | **HappyRobot** | First round, pre-institutional | Series A 2024-12-04 (a16z) | **2024-12-03** | Yes. YC S23 public batch page; company site; product content. | Should be PASS via the accelerator channel, but tests whether DAY ZERO over-weights YC (a prestige risk). |
| B4 | **Flamingo** | Co-led $2.2M pre-seed | Stealth exit 2025-10-28 | **2025-10-27** | Uncertain. Company launched *from stealth* — by construction, evidence may not exist pre-cutoff. Founder Michael Assraf has a prior public record. Waitlist of 1,000 MSPs was built pre-launch via a community tool. | Likely PARTIAL or MISS. **Kept deliberately** as an honest hard case. |
| B5 | **Meibel** | UNKNOWN | $7M, 2025-05-28 | **2025-05-27** | Unknown. | Likely UNKNOWN. Kept to measure how often the method simply cannot decide. |
| B6 | **Integral** | UNKNOWN | $6.9M seed 2023-09-05 | **2023-09-04** | Possible. HealthTech privacy tooling; may have public docs/standards work. | PARTIAL expected. Tests HealthTech coverage, Array's weakest channel. |
| B7 | **Mozart Data** | UNKNOWN | $4M seed 2020-11-11 | **2020-11-10** | Likely thin. Founders Peter Fishman & Dan Silberman had 20-year public track records. Pre-2021 GitHub/X archives are recoverable but the product was closed-source. | Likely MISS. Kept as a pre-LLM-era control — DAY ZERO's channels are 2023+ biased and should admit it. |
| B8 | **ZecOps** | UNKNOWN (acquired by Jamf 2022-11) | Acquisition 2022-11-17 | **2020-01-01** (pre-Series A era) | Yes. Founder Zuk Avraham published mobile-security research publicly for years. Research-artifact channel. | PASS expected via the *papers/research* channel rather than GitHub. Tests channel diversity. |
| B9 | **Era Software** | UNKNOWN (acquired by ServiceNow 2022-10) | Acquisition 2022-10-05 | **2021-10-05** | Uncertain — observability/log-management, likely closed-source. | Likely MISS or UNKNOWN. |
| B10 | **Wokelo** | UNKNOWN | $4M, 2024-10-09 | **2024-10-08** | Uncertain. Seattle-area, vertical AI, likely no OSS. | Likely MISS. **Kept deliberately**: if DAY ZERO can only find open-source infrastructure builders, that is a real and important limitation to publish. |

### Cohort composition check

- Expected PASS: 3 (B1, B3, B8)
- Expected PARTIAL: 2 (B4, B6)
- Expected MISS: 3 (B7, B9, B10)
- Expected UNKNOWN: 2 (B2, B5)

That is deliberately a **~30% expected hit rate.** A cohort designed to score 90% would
be a cohort of open-source infrastructure companies, which is exactly the retrofitting
the mandate forbids. These expectations are written down *before* the backtest runs so
they can be checked against the result.

### Companies deliberately excluded from the cohort

- **Agency (Klaviyo exit)** — founded by an Array team member; sourcing it would be
  circular.
- **Wabi** — a $20M pre-seed by the founder of Replika is not a discovery problem.
- **Simility, Passage AI, Art19, Managed by Q, Tumble, ORO, Capsule** — pre-2021, before
  the public artifact channels DAY ZERO relies on were meaningful. Including them would
  manufacture misses as easily as excluding hard cases would manufacture hits.
- **Blumira, Hotdata, Precanto, Zingly, FinanceOps, MokSa, Blaze, AnswersAI, Sotto,
  Blendid, Cast, Retina Robotics** — no publicly-sourced financing date found, so no
  defensible cutoff can be set.

---

## 5. Open questions / UNKNOWNs to resolve before Phase 2

1. Sapiom's pre-seed announcement date (needed for a tighter B2 cutoff).
2. Whether Array's participation in B5–B10 was at the named round or earlier.
3. Whether array.vc's full 52-company portfolio widget can be enumerated (the
   `/portfolio` path 404s; only 10 companies render on the homepage).
4. Blumira's, Hotdata's, and Retina Robotics' financing history.
