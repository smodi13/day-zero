# DAY ZERO

### Founder Formation & Technical Diligence Engine

> ## 🚧 WORK IN PROGRESS — PHASE 1 (RESEARCH & DESIGN) COMPLETE
> No frontend. No deployment. No live ingestion pipeline. No outreach.
> Phase 2 has not begun and will not begin without an explicit decision.

---

## What this is

A working design — and the first real evidence base — for an internal sourcing and
technical-diligence system for a pre-seed deep-tech fund.

It tries to answer two questions:

1. **Can we systematically identify unusually strong technical builders before they become
   obvious venture deals**, using public evidence of what they are actually building rather
   than prestige or social popularity?
2. **Can we technically evaluate the most promising projects deeply enough** to determine
   whether there is real engineering or research defensibility?

The intended output chain:

```
SIGNALS → BUILDERS → TECHNICAL ARTIFACTS → FORMATION EVIDENCE
       → ANALYST REVIEW → WEEKLY 3 → TECHNICAL REPRODUCTION → DILIGENCE
```

## Why it exists

DAY ZERO was built as an independent work sample for an **AI Analyst** application at
**Array Ventures**. The role is unusually specific: source young technical builders and
experienced operators leaving strong technical environments; attend SF hackathons and
technical communities; build sourcing tools programmatically; read papers; interrogate
architecture; test defensibility; and surface roughly **2–3 quality founder introductions
per week**.

Array says of itself: *"We do not vibe-invest."* This project takes that literally.

## The two founder pools

**Pool A — young builders.** Recent graduates, graduate students, hackathon participants,
research engineers, open-source maintainers, university lab researchers.
The question is never *"did they attend Stanford?"* It is *"what have they actually built,
and what evidence shows unusual technical ability or founder formation?"*

**Pool B — operator → founder.** Technical operators who have **publicly stated** they are
leaving to build; new independent projects; new technical collaborations; new GitHub
organizations; early launches.

**Hard rule:** DAY ZERO never infers a private employment change. Not from silence, not
from inactivity, not from a deleted post, not from a bio edit. Only from an explicit
first-person public statement.

## Evidence philosophy

- **No fabricated data.** If something is unknown, it is recorded as **UNKNOWN**.
- **Primary evidence first.** Code, papers, official docs, filings, first-party statements.
- **Every important claim is tagged OBSERVED / INFERRED / UNKNOWN.**
- **Social popularity is not founder quality.** Follower and star counts are barred from
  surfacing logic entirely.
- **Prestige is not a score.** Affiliation is context for identity resolution, never a rank.
- **AI is not evidence.** AI assists extraction, classification and drafting; its output is
  stored separately and must be verified against a source before it counts.
- **There is no total score.** Not on a person, not on a project. The schema forbids it.

## X's role

X is **one discovery channel of eight**, not the project.

> An X post is primary evidence that a person *made a statement*.
> It is never, by itself, evidence that the statement is *true*.

Every X lead must run: `POST → IDENTITY RESOLUTION → TECHNICAL ARTIFACT → INDEPENDENT
CONFIRMATION → ANALYST REVIEW`. **An X post alone can never create a Weekly 3 lead.**
X ingestion is **off by default** in the Phase 2 design.

An earlier X sourcing engine of mine was audited (read-only) to decide what should and
should not carry over — see `research/existing_x_engine_audit.md`.

## The Weekly 3

Three builder or team leads per cycle that survive analyst review and are worth spending
relationship capital on. **If fewer than three genuinely survive, DAY ZERO returns one or
two — or zero.** Filling slots is the fastest way to make the system worthless.

## Accepted Work Unit

> **One Accepted Work Unit = one founder or team lead that survives analyst review and is
> genuinely worth an introduction.**

Borrowed deliberately from Shruti Gandhi's own July 2026 framing of AI work: measure
**cost per accepted work unit**, not tokens. DAY ZERO holds itself to its customer's metric
— including that the dominant cost is *analyst time*, not API spend.

## Technical Reproduction Lab

Selected technical claims get **actually tested** against a real baseline, with a frozen
corpus and a published harness. This automates something Array already does by hand:

> *"In many cases, we attempt to recreate parts of a product ourselves to understand the
> technical complexity."* — Array Ventures, January 2026

Phase 1 selected five candidate experiments and one primary, chosen partly because it runs
on an 8 GB M1 laptop for a few dollars.

## Historical holdout

Ten Array portfolio companies, each with a frozen cutoff date, selected on **evidence
recoverability rather than success** — three of them are expected to be misses, and are
kept deliberately. The signal ontology and acceptance criteria were **frozen before the
cohort was scored**, and the expected outcome for each company is published in advance.

No evidence after a case's cutoff date may inform the decision. Later information appears
only in a field named `OUTCOME`.

## Privacy principles

DAY ZERO researches **what people build**. It does not research people.

No personal addresses, phone numbers, or private emails. No family, demographic, political,
religious, or health information or inference. No location tracking beyond self-published
professional context. No data brokers. No inference that anyone is quitting a job. No
attempt to de-anonymize a pseudonymous builder. Removal on request, no questions asked.

Full rules: `research/data_ethics.md`.

## AI use

Claude Code was used substantially: research organization, source gathering, structured
extraction, classification, drafting, and tooling. See `research/phase1_report.md` §42 and
the AI disclosure section for the specific boundary. In short — **AI never scores a person,
never decides who receives an investment or an introduction, and its output is never stored
as evidence.**

## Limitations (Phase 1)

- No live pipeline, no database, no frontend, no deployment.
- The backtest is **designed, not run**.
- The reproduction experiments are **selected, not run**.
- The builder universe is 45 records — enough to pressure-test an ontology, not a sourcing
  universe.
- Discovery skews to English-language GitHub. Non-GitHub and non-English ecosystems are
  under-covered, and this is measured rather than hidden.
- The hackathon channel is manual-only by policy (Devpost's `robots.txt` disallows AI
  crawlers, verified 2026-08-22).
- Only ~31% of builders could be assigned to Pool A or Pool B from public evidence.

## Repository layout

```
day-zero/
  README.md
  .gitignore
  research/     23 documents — strategy, frameworks, evidence, findings
  sources/      source_registry.csv (50 traceable sources)
  config/       (empty in Phase 1)
  src/          (empty in Phase 1 — no production code written)
```

Start with `research/phase1_report.md`.

## Planned phases

| Phase | Scope | Status |
| --- | --- | --- |
| **1** | Research, ontology, evidence model, cohort selection, initial builder universe | ✅ Complete |
| **2** | GitHub + arXiv ingestion, entity resolution, the frozen backtest, negative-control suite | ⬜ Not started — awaiting review |
| **3** | Reproduction lab (EXP-1 primary), analyst review workflow, first real Weekly 3 cycles | ⬜ |
| **4** | Interface, if and only if the underlying system earns one | ⬜ |

---

> **DAY ZERO is an independent research project and is not affiliated with, sponsored by,
> or endorsed by Array Ventures, Shruti Gandhi, or any person or company referenced in the
> analysis.**

All third-party information is drawn from public sources and is cited in
`sources/source_registry.csv`. No individual named in this repository has been contacted in
connection with it.
