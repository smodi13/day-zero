# DAY ZERO — Data Ethics & Privacy

This project analyzes real people. That obligates a written, enforceable boundary, not a
disclaimer.

**The one-line rule:**
> **DAY ZERO researches what people build. It does not research people.**

---

## 1. Hard prohibitions

Never collected, stored, inferred, or displayed:

- Home or personal addresses
- Personal phone numbers
- Personal email addresses obtained from anywhere other than a first-party professional
  surface the person published themselves (e.g. a `mailto:` on their own project site)
- Family information, relationships, or dependents
- Age, gender, race, ethnicity, nationality, or any demographic inference
- Political affiliation, religion, health, sexuality, or any inference toward them
- Location beyond a self-published professional location field or voluntarily public
  participation in a public professional event
- Any data from a data broker, people-search service, or employment-history vendor
- Any content behind a login, a paywall, or an access control
- Any content from a source whose `robots.txt` or terms prohibit our access
- Deleted, edited, or otherwise retracted content
- Private repositories, private org membership, or private contribution graphs

## 2. Prohibited inferences

Some inferences are technically possible from public data and are still forbidden.

| Forbidden inference | Why |
| --- | --- |
| "This person is leaving their job" from silence, inactivity, a deleted post, a bio edit, or a follower change | This is surveillance, and it is usually wrong. Only an explicit first-person public statement counts (`x_channel.md` §4). |
| "This person will start a company" | DAY ZERO classifies evidence; it does not predict people's decisions. |
| "This person is unhappy / looking / recruitable" | Not our business and not observable. |
| Anything from posting-time patterns, timezone drift, or activity gaps | Behavioral surveillance dressed as analytics. |
| Anything from a person's *network* rather than their *work* | The graph exists to answer "what did they build, with whom" — not "who do they know." |
| Identity merges from name similarity | Produces false statements about real people (`entity_graph.md` ER-2). |

## 3. What IS in scope

- Public code and its commit history
- Public repositories, organizations, and org membership that the person made public
- Published research papers and their author lists
- Public package registry entries
- A person's own professional website, blog, and self-published bio
- Public first-person statements on public platforms
- Official hackathon and accelerator result pages
- Public company sites, documentation, and product surfaces
- Public regulatory filings
- Public professional events the person chose to participate in publicly

## 4. Operating rules

1. **Minimum necessary.** If a field is not needed to answer "what did they build, with
   whom, and how is it changing," it is not collected.
2. **No raw social dumps in the repository.** `.gitignore` excludes caches, databases, and
   raw payloads. Derived, cited records only.
3. **Public professional context only.** Everything stored should be something the person
   would recognize as part of their public professional record.
4. **Correction and removal.** If a person asks to be removed from DAY ZERO's records,
   they are removed, without argument and without asking why.
5. **No contact as part of the research.** Phase 1 contacts nobody. Outreach, if it ever
   happens, is a human decision made outside this system.
6. **Attendance is never assumed.** DAY ZERO does not record the operator as having
   attended any event. Attendance is recorded only when explicitly entered by a human.
7. **No re-identification.** Anonymous or pseudonymous builders stay that way. If someone
   ships as `brontoguana` with no name and no links, DAY ZERO records `brontoguana` and
   stops — it does not attempt to determine who they are.
8. **Adverse findings stay internal.** A failed reproduction or a weak technical assessment
   is diligence material. It is never published as criticism of a named builder.
9. **Every record is a record about work.** If a field would be uncomfortable to show the
   person it describes, it does not belong in the system.

## 5. AI use boundary

- AI may **assist** with extraction, classification, entity-candidate generation,
  summarization, source prioritization, and drafting.
- AI output is **never evidence.** It is stored in fields marked `produced_by: model`,
  rendered separately from sourced facts, and must be verified against a source before it
  can be marked OBSERVED.
- **AI never decides who receives an investment or an introduction.** Weekly 3 selections
  are analyst judgments.
- **AI never scores a person.** There is no model call anywhere in this system whose output
  is a rating of a human being.

## 6. The test I apply before adding any field

> *If this builder read their own DAY ZERO record, would they recognize it as a fair
> description of their public work — or would they feel surveilled?*

If it is the second, the field does not go in.
