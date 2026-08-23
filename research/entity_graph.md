# DAY ZERO — Person ↔ Artifact Graph

**Purpose:** answer one question — *what has this person actually built, with whom, and
how is that changing over time?* This is not a social graph and must not be used as one.

---

## 1. Entities

| Entity | Key | Required fields | Notes |
| --- | --- | --- | --- |
| `person` | `person_id` (internal) | `display_name?`, `confidence`, `created_at` | A person may have **no** resolved real name. That is allowed and common. |
| `identity` | `(channel, handle)` | `channel`, `handle`, `profile_url`, `first_seen`, `evidence_status` | The *observable* thing. A `person` is a claim that several `identity` rows are the same human. |
| `repository` | `host/owner/name` | `created_at`, `pushed_at`, `license`, `language`, `owner_type` | Canonical artifact type. |
| `project` | `project_id` | `name`, `homepage?`, `repos[]` | A project may span repos. Never merged on name alone (see §4). |
| `paper` | DOI or arXiv id | `published_at`, `authors[]`, `venue?` | |
| `organization` | `(host, login)` for GitHub orgs; domain otherwise | `created_at`, `type` | GitHub org creation date is a strong formation signal. |
| `lab_or_university` | `ror_id` or canonical name | | Affiliation only — never a ranking input. |
| `hackathon` | `(name, edition, year)` | `official_url`, `dates` | |
| `company` | `company_id` | `name`, `domain`, `first_public_evidence_at` | A `company` is a *state a project reached*, not a starting point. |
| `event` | `event_id` | `name`, `date`, `location`, `official_url` | SF ecosystem module. |
| `signal` | `signal_id` | `type` (from `signal_ontology.md`), `observed_at`, `collected_at`, `channel`, `evidence_status` | |
| `source` | `source_id` | `url`, `publisher`, `quality_tier`, `accessed_at` | Every signal points at ≥1 source. |
| `analyst_review` | `review_id` | human-authored | |

---

## 2. Relationships

```
person        --HAS_IDENTITY-->      identity          [evidence: link_type]
person        --AUTHORED-->          repository        [evidence: commit attribution]
person        --AUTHORED-->          paper             [evidence: author list]
person        --MEMBER_OF-->         organization      [evidence: public org membership]
person        --AFFILIATED_WITH-->   lab_or_university [evidence: self-published / lab page]
person        --PARTICIPATED_IN-->   hackathon         [evidence: official result page]
person        --COLLABORATED_WITH--> person            [derived: co-commit or co-authorship]
person        --FOUNDED-->           company           [evidence: explicit public statement]

repository    --PART_OF-->           project
repository    --OWNED_BY-->          organization
repository    --IMPLEMENTS-->        paper
project       --BECAME-->            company
paper         --FROM_LAB-->          lab_or_university
hackathon     --PRODUCED-->          project

signal        --ABOUT-->             {person|repository|project|organization|company}
signal        --EVIDENCED_BY-->      source
analyst_review--COVERS-->            person | project
```

**`COLLABORATED_WITH` is derived, never asserted.** It requires either (a) both people
having ≥5 commits to the same repository within a 365-day window, or (b) shared
authorship on a paper. It is a working-relationship edge, not a social edge, and it is
never used to reach a person who has no artifact of their own.

---

## 3. Evidence requirements per edge

| Edge | Minimum to create | Minimum to treat as OBSERVED |
| --- | --- | --- |
| `HAS_IDENTITY` | never auto-created (see §4) | an explicit, self-published link between the two profiles |
| `AUTHORED (repo)` | commit attribution to a login | commit attribution **plus** the login being the repo owner or a listed contributor with >5 commits |
| `AUTHORED (paper)` | name on the author list | name on the author list **plus** a matching affiliation or a self-published link |
| `MEMBER_OF` | GitHub public org membership | same (public membership is authoritative) |
| `PARTICIPATED_IN` | official hackathon result page | same |
| `FOUNDED` | explicit first-person public statement | that statement **plus** one of: org creation, domain, or filing |
| `BECAME (project→company)` | ≥2 FORMATION signals | ≥2 FORMATION signals from ≥2 channels |

---

## 4. Entity-resolution rules (deliberately conservative)

### Rule ER-0: The default is *do not merge*.
Two identities remain separate unless a merge rule below fires. An unmerged graph with
duplicates is a manageable problem. A wrongly merged graph produces false claims about
real people, and there is no way to detect it downstream.

### Rule ER-1: Accepted merge evidence (any one is sufficient)
1. **Explicit self-published link.** Profile A links to profile B (GitHub blog field →
   personal site → X handle; X bio → GitHub URL; personal site listing both).
2. **Verified organization membership on both sides.** Both identities are public
   members of the same GitHub org, *and* the org is small enough (<25 public members)
   that this is meaningful.
3. **Exact artifact cross-reference.** A paper's author list names a person whose
   self-published homepage links the exact repository, and the repository's commits
   carry that login.
4. **Explicit bio statement.** "I'm @handle on X" or equivalent, on a first-party surface.

### Rule ER-2: Forbidden merge evidence
- Similar or identical **display names**. (There are many people named "Yang Zhou.")
- Similar avatars.
- Same city.
- Same employer.
- Same technical topic.
- Name similarity plus topic similarity. This is the most tempting and the most wrong.

### Rule ER-3: Ambiguous identities stay separate and are flagged
An `identity` with `confidence < high` never enters a Weekly 3 record. A lead whose
identity cannot be resolved to the standard of ER-1 is capped at "watchlist" — you cannot
introduce someone you cannot name.

**Live example from the initial universe:** `brontoguana` — 768 owner-commits on a C++
hybrid LLM runtime (`krasis`), no name, no company, no blog, 10 followers. Technically
one of the more interesting artifacts found. **Identity confidence: LOW.** It stays on
the watchlist and cannot be a Weekly 3 lead until the person publishes something linkable.

### Rule ER-4: Organization names are not project names are not company names
Three separate namespaces. `deeplethe` (GitHub org) ≠ DeepLethe (company name in a bio) ≠
`forkd` (project). Links between them require evidence, not string equality.

### Rule ER-5: Name collision is assumed, not exceptional
Every `project` and `company` merge must check for collisions before merging. Two
verified collisions from Array's own portfolio are stored as permanent regression tests:

| Collision | Entity A | Entity B | Why a naive engine merges them |
| --- | --- | --- | --- |
| "Agency" | Array portfolio co. founded by Elias Torres, acquired by Klaviyo (2026) | AgentOps/Agency — agent observability, Reibman/Silverman/Qiu, $2.6M pre-seed led by 645 Ventures + Afore, **Array did not participate** | identical name, same sector-adjacent space, same era |
| "Eventual" | Eventual/Daft — data engine, $7.5M seed 2024-10-01 (CRV), Array participated | Eventual — climate fintech, $7.5M seed 2025-07 (AlleyCorp, Upfront) | identical name **and** identical round size |

A merge rule that used name + sector + round size would produce, in both cases, a false
statement about who Array backed.

### Rule ER-6: Bots are not people
`github-actions[bot]`, `dependabot[bot]`, `renovate[bot]`, and any login matching
`\[bot\]$` are excluded from `person`, from contributor counts, and from all velocity
signals.

---

## 5. Temporal integrity

Every node and edge carries `observed_at` (when the underlying fact happened) and
`collected_at` (when DAY ZERO recorded it). All backtest queries filter on
`observed_at <= cutoff`. Any field that cannot be given a defensible `observed_at`
(current star count, current follower count, current bio text) is **excluded from
backtest queries entirely** rather than approximated — a current bio is a statement about
today, not about 2024.

This is the mechanism that prevents look-ahead bias, and it is why the ported
`timeutil.py` discipline (aware-UTC only, naive datetimes rejected at boundaries) is a
correctness requirement rather than a style preference.

---

## 6. What the graph is not for

- Not for mapping who knows whom socially.
- Not for reconstructing employment history.
- Not for tracking individuals across time outside of their public technical work.
- Not for inferring anything about a person's plans, intentions, or private life.

The graph's only legitimate query shape is: *given this artifact, who built it, with
whom, and what changed?*
