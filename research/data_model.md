# DAY ZERO — Data Model (design)

**Status: designed, not implemented.** Phase 1 deliberately builds no database. The model
is written down so the ontology can be checked for consistency before code exists.

Target for Phase 2: SQLite first (single file, no server, trivially versioned, and the
audited X engine already proved it is sufficient at this scale), with a documented path to
Postgres if concurrent analysts ever need it.

---

## 1. Principles

1. **Evidence is a first-class table, not a column.** Every assertion points at a source.
2. **No score column exists anywhere.** Not on a person, not on a project, not on a lead.
   This is enforced by the schema, not by convention.
3. **Two timestamps on everything that can have them:** `observed_at` (when the fact was
   true) and `collected_at` (when we recorded it).
4. **Append-mostly.** Signals and evidence are appended. Corrections are new rows with a
   `supersedes` pointer, never in-place edits — the same discipline as the audited engine's
   append-only cost ledger.
5. **Machine output is segregated.** Any AI-produced field carries `produced_by='model'`
   and lives in `ai_annotations`, never in `evidence`.

---

## 2. Core tables

```sql
-- Identity ---------------------------------------------------------------
persons(person_id PK, display_name NULL, identity_confidence CHECK IN ('high','medium','low'),
        created_at, notes)

identities(identity_id PK, person_id FK NULL, channel, handle, profile_url,
           first_seen_at, last_seen_at, is_bot BOOL DEFAULT 0,
           UNIQUE(channel, handle))
-- person_id is NULL until an ER-1 merge rule fires. NULL is the default and is normal.

identity_links(link_id PK, identity_a FK, identity_b FK, rule CHECK IN
               ('self_published_link','shared_small_org','artifact_cross_reference','explicit_bio'),
               source_id FK, created_at, created_by)
-- Every merge records WHICH rule fired and WHICH source proved it. Reversible.

-- Artifacts --------------------------------------------------------------
repositories(repo_id PK, host, owner, name, created_at, pushed_at, license, language,
             owner_type, homepage NULL, collected_at, UNIQUE(host,owner,name))
projects(project_id PK, name, homepage NULL, created_at)
project_repos(project_id FK, repo_id FK, PRIMARY KEY(project_id, repo_id))
papers(paper_id PK, arxiv_id NULL, doi NULL, title, published_at, venue NULL)
paper_authors(paper_id FK, author_name, identity_id FK NULL, position)
packages(package_id PK, registry, name, first_release_at, latest_release_at, repo_id FK NULL)

organizations(org_id PK, host, login, name NULL, created_at, blog NULL, location NULL,
              scope CHECK IN ('unregistered','established_organization','foundation_or_community','unknown'))
companies(company_id PK, name, domain NULL, first_public_evidence_at, org_id FK NULL)
labs(lab_id PK, name, ror_id NULL, url NULL)

hackathons(hackathon_id PK, name, edition, year, official_url, start_date, end_date)
events(event_id PK, name, date, location, official_url, organizer, theme,
       attendance NULL)   -- NEVER system-populated; human entry only

-- Relationships ----------------------------------------------------------
authorship(person_id FK, artifact_type, artifact_id, contribution_count, first_at, last_at,
           evidence_status)
memberships(person_id FK, org_id FK, is_public BOOL, observed_at)
collaborations(person_a FK, person_b FK, basis CHECK IN ('co_commit','co_authorship'),
               artifact_type, artifact_id, window_start, window_end)
affiliations(person_id FK, lab_id FK, observed_at, source_id FK)   -- context only, never ranking
participations(person_id FK, hackathon_id FK, source_id FK)

-- Evidence ---------------------------------------------------------------
sources(source_id PK, url, publisher NULL, source_type, quality_tier CHECK IN (1,2,3),
        publication_date NULL, accessed_at, archive_url NULL)

signals(signal_id PK, signal_type,          -- 'B-01','D-03','C-04','F-02','V-06','M-05','S-01'
        subject_type, subject_id,
        observed_at, collected_at,
        channel, evidence_status CHECK IN ('OBSERVED','INFERRED','UNKNOWN'),
        stale BOOL DEFAULT 0, supersedes FK NULL)

signal_sources(signal_id FK, source_id FK, establishes CHECK IN ('statement','fact'))
-- The statement/fact split from source_quality.md is enforced HERE, in the schema.

-- Assessment -------------------------------------------------------------
technical_assessments(assessment_id PK, artifact_type, artifact_id, assessed_at, assessed_by,
                      tq1_difficulty, tq1_status, tq2_originality, tq2_status,
                      tq3_systems_depth, tq3_status, tq4_research_depth, tq4_status,
                      tq5_reproducibility, tq5_status, tq6_performance, tq6_status,
                      tq7_usage, tq7_status, tq8_architecture, tq8_status,
                      tq9_defensibility_question TEXT)
-- Nine dimensions, nine statuses, one open question. NO total column. By design.

formation_states(state_id PK, person_id FK, state CHECK IN
                 ('BUILDING','COLLABORATING','FORMING','LAUNCHED','FUNDED','UNKNOWN'),
                 computed_at, supporting_signal_ids JSON)

analyst_reviews(review_id PK, subject_type, subject_id, reviewed_at, reviewer,
                what_they_built, why_interesting, what_changed, array_relevance,
                why_missed_by_normal_sourcing, strongest_evidence, weakest_evidence,
                technical_question, commercial_question,
                what_would_make_it_an_intro, what_would_make_us_drop_it, verdict)

weekly3(entry_id PK, cycle_date, rank_within_cycle, person_id FK NULL, project_id FK NULL,
        review_id FK, identity_confidence, contacted BOOL DEFAULT 0)
-- `contacted` exists so the system can never silently imply outreach happened.

-- Lab & backtest ---------------------------------------------------------
experiments(experiment_id PK, artifact_id, claim TEXT, baseline TEXT, method TEXT,
            corpus_hash, artifact_commit_sha, ran_at, result TEXT,
            supports_claim CHECK IN ('supports','weakens','inconclusive'))

backtest_cases(case_id PK, company, array_relationship, milestone, milestone_date,
               cutoff_date, expected_verdict, actual_verdict NULL,
               pre_cutoff_evidence JSON, decided_at NULL, outcome TEXT NULL)
-- `outcome` is post-cutoff information. It is written LAST and referenced by NO rule.

negative_controls(control_id PK, control_type, artifact_id, expected_rejection_rule,
                  actual_result NULL, tested_at NULL)

-- Machine output (segregated) --------------------------------------------
ai_annotations(annotation_id PK, subject_type, subject_id, field, value,
               model, produced_at, verified_by NULL, verified_at NULL)
-- An annotation becomes evidence only when a human verifies it against a source,
-- at which point a real `signals` + `signal_sources` row is created.
```

---

## 3. Schema-level guarantees

| Guarantee | Mechanism |
| --- | --- |
| No person is ever scored | No numeric column on `persons`; `technical_assessments` has no total |
| Look-ahead bias is preventable | Every signal has `observed_at`; backtests filter on it; current-state fields are not stored as signals |
| Evidence is always traceable | `signals` has no meaning without `signal_sources` |
| Statements ≠ facts | `signal_sources.establishes` |
| Merges are auditable and reversible | `identity_links` records the rule and the source |
| AI output is not evidence | Separate table; requires human verification to promote |
| Outreach is never implied | `weekly3.contacted` defaults to 0 and is human-set |
| Attendance is never fabricated | `events.attendance` defaults NULL and is human-set |
| Bots are excluded | `identities.is_bot` set on `[bot]`-suffixed logins |

---

## 4. What is deliberately absent

- No `score`, `rank`, `rating`, or `probability` column on any entity.
- No `founding_likelihood`, `intent`, or `is_looking` column.
- No employment-history table. DAY ZERO does not model where people work.
- No follower/star columns on `persons`. Star and follower counts live on the
  `repositories` row as context and are barred from surfacing logic.
- No raw social-media payload storage in-repo.

---

## 5. Phase 2 prototype scope

The smallest thing that validates the model:
`identities`, `repositories`, `signals`, `sources`, `signal_sources`, `formation_states`.
If those six tables can hold the 56 verified builder records in `initial_builders.csv`
without needing a score column or a fabricated field, the model is sound enough to build on.
