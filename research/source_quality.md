# DAY ZERO — Source Quality Hierarchy

## Tier 1 — Primary artifact
The thing itself, or a first-party statement of record.

- A GitHub repository (code, commit history, contributor list, org membership)
- Official project documentation
- A research paper (arXiv, proceedings, journal)
- A package on an official registry
- An official personal site or academic homepage
- An official company site
- An official hackathon result page
- A mailing-list post authored by the person (LKML, etc.)
- An SEC filing
- A first-person public statement by the builder, on a first-party surface

## Tier 2 — Strong independent source
Someone credible, who is not the subject, reporting on the subject.

- Established technical publications and reputable trade press
- Established general news with a named reporter
- Conference programs and official proceedings listings
- Institutional pages (university lab rosters, official cohort pages)
- A well-sourced funding announcement from a party other than the company

## Tier 3 — Discovery
Points at something. Establishes almost nothing on its own.

- Social posts (X, LinkedIn, Mastodon, Bluesky)
- Aggregators and directories (Crunchbase-style databases, "top N" lists)
- Search-engine results
- Community forums and comment threads
- AI-generated summaries, including this system's own

---

## The distinction that does the real work

> **An X post by THE BUILDER about THEIR OWN project is Tier 1 evidence that they made
> the statement. It is Tier 3 evidence that the statement is true.**

Two separate fields, always:

```yaml
statement_evidence:  {tier: 1, source: "x.com/<handle>/status/<id>", establishes: "the person publicly claimed X on 2026-05-11"}
fact_evidence:       {tier: null, status: UNKNOWN, establishes: null, note: "no independent confirmation of the claim itself"}
```

This applies far beyond X. A README claiming "3x faster" is Tier 1 evidence that the
claim is published and Tier 3 evidence about performance. A company blog post announcing
a customer is Tier 1 for the announcement and Tier 3 for the customer relationship.

**Concrete, verified case:** `scrya-com/rotorquant`'s README states "better PPL (6.91 vs
7.07), 28% faster decode, 5.3x faster prefill, 44x fewer params." That is Tier 1 evidence
of a specific, falsifiable, well-formed claim — which is genuinely a positive signal about
the builder's rigor. It is *zero* evidence that the numbers reproduce. The repo has no
license and no push since 2026-04-23. Both facts belong in the record, and neither cancels
the other.

---

## Rules

1. **Every signal names its source(s) and each source's tier.** No orphan claims.
2. **A FORMATION state requires ≥2 signals from ≥2 independent channels, and at least
   one Tier 1 source.**
3. **Tier 3 alone can never move a person out of UNKNOWN.**
4. **"Independent" means the sources do not derive from each other.** A tweet linking to a
   repo is one channel — the tweet is a pointer to the repo, not a second witness. A paper
   and a repo with overlapping authorship are two.
5. **Tier is a property of the source-claim pair, not of the domain.** TechCrunch is Tier 2
   for a funding round it reported and Tier 3 for a founder's characterization of their own
   technology quoted inside that article.
6. **Aggregator databases are Tier 3 by default**, because their provenance is usually
   opaque. If an aggregator cites a filing, follow the citation and record the filing.
7. **AI output is never above Tier 3 and is never stored as evidence.** It is stored in a
   separate field with `produced_by: model` (see `data_ethics.md` §5).
8. **Archive on access.** Any Tier 1/2 web source used in a Weekly 3 or backtest record is
   recorded with `accessed_at` and, where possible, a Wayback snapshot URL. Pages move.

---

## Downgrade triggers

A source drops a tier when:

- The page is undated and the claim is time-sensitive.
- The publisher is the subject and the claim is about a third party.
- The content is a syndicated rewrite of a press release with no added reporting.
- The URL 404s or redirects to a generic page on re-check.
- The claim in the source contradicts a Tier 1 artifact (record both; do not silently
  prefer one).
