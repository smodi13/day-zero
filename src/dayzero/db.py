"""SQLite schema.

Normalized entities. The schema deliberately contains NO score column on any
entity — that constraint is enforced by `tests/test_no_score.py`, which inspects
every column name in the live schema.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------- identity --
CREATE TABLE IF NOT EXISTS builders (
  person_id           TEXT PRIMARY KEY,
  display_name        TEXT,
  identity_confidence TEXT NOT NULL CHECK (identity_confidence IN ('high','medium','low')),
  career_signal_class TEXT NOT NULL DEFAULT 'UNCLASSIFIED',
  career_signal_evidence_id TEXT,
  created_at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS identities (
  identity_id  TEXT PRIMARY KEY,
  person_id    TEXT REFERENCES builders(person_id),
  channel      TEXT NOT NULL,
  handle       TEXT NOT NULL,
  profile_url  TEXT,
  is_bot       INTEGER NOT NULL DEFAULT 0,
  first_seen   TEXT,
  UNIQUE (channel, handle)
);

CREATE TABLE IF NOT EXISTS identity_links (
  link_id     TEXT PRIMARY KEY,
  identity_a  TEXT NOT NULL REFERENCES identities(identity_id),
  identity_b  TEXT NOT NULL REFERENCES identities(identity_id),
  rule        TEXT NOT NULL,
  status      TEXT NOT NULL CHECK (status IN ('MERGED','POSSIBLE_MATCH','REJECTED')),
  evidence_id TEXT,
  created_at  TEXT NOT NULL
);

-- --------------------------------------------------------------- artifacts --
CREATE TABLE IF NOT EXISTS repositories (
  repo_id     TEXT PRIMARY KEY,
  host        TEXT NOT NULL,
  full_name   TEXT NOT NULL UNIQUE,
  owner_login TEXT,
  owner_type  TEXT,
  created_at  TEXT,
  pushed_at   TEXT,
  language    TEXT,
  license     TEXT,
  homepage    TEXT,
  description TEXT,
  archived    INTEGER DEFAULT 0,
  is_fork     INTEGER DEFAULT 0,
  collected_at TEXT
);

-- Attention and construction are stored in SEPARATE tables so they can never be
-- accidentally combined. Phase 1 finding 2.
CREATE TABLE IF NOT EXISTS repo_attention (
  repo_id  TEXT PRIMARY KEY REFERENCES repositories(repo_id),
  stars    INTEGER, forks INTEGER, watchers INTEGER, open_issues INTEGER
);

CREATE TABLE IF NOT EXISTS repo_construction (
  repo_id             TEXT PRIMARY KEY REFERENCES repositories(repo_id),
  human_contributors  INTEGER,
  top_contributions   INTEGER,
  total_contributions INTEGER,
  longevity_days      INTEGER,
  age_days            INTEGER,
  days_since_push     INTEGER,
  release_count       INTEGER,
  active_window_ratio REAL
);

CREATE TABLE IF NOT EXISTS projects (
  project_id TEXT PRIMARY KEY, name TEXT NOT NULL, homepage TEXT, anchor TEXT
);
CREATE TABLE IF NOT EXISTS project_repos (
  project_id TEXT NOT NULL REFERENCES projects(project_id),
  repo_id    TEXT NOT NULL REFERENCES repositories(repo_id),
  PRIMARY KEY (project_id, repo_id)
);
CREATE TABLE IF NOT EXISTS papers (
  paper_id TEXT PRIMARY KEY, arxiv_id TEXT UNIQUE, title TEXT, published_at TEXT, url TEXT
);
CREATE TABLE IF NOT EXISTS paper_authors (
  paper_id TEXT NOT NULL REFERENCES papers(paper_id),
  author_name TEXT NOT NULL, position INTEGER,
  identity_id TEXT REFERENCES identities(identity_id),
  PRIMARY KEY (paper_id, author_name)
);
CREATE TABLE IF NOT EXISTS organizations (
  org_id TEXT PRIMARY KEY, host TEXT, login TEXT, name TEXT, blog TEXT,
  location TEXT, description TEXT, created_at TEXT, public_repos INTEGER,
  scope TEXT NOT NULL DEFAULT 'unknown',
  UNIQUE (host, login)
);
CREATE TABLE IF NOT EXISTS companies (
  company_id TEXT PRIMARY KEY, name TEXT, domain TEXT,
  first_public_evidence_at TEXT, org_id TEXT REFERENCES organizations(org_id)
);
CREATE TABLE IF NOT EXISTS hackathons (
  hackathon_id TEXT PRIMARY KEY, name TEXT, edition TEXT, year INTEGER,
  official_url TEXT, start_date TEXT, end_date TEXT, import_mode TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY, name TEXT, date TEXT, location TEXT, official_url TEXT,
  organizer TEXT, theme TEXT, why_relevant TEXT, sourcing_objective TEXT,
  builder_signal_sought TEXT,
  attendance_status TEXT NOT NULL DEFAULT 'NOT_ATTENDED'
    CHECK (attendance_status IN ('NOT_ATTENDED','PLANNED','ATTENDED')),
  import_mode TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS social_signals (
  social_id TEXT PRIMARY KEY, channel TEXT NOT NULL, handle TEXT, url TEXT,
  posted_at TEXT, claim_class TEXT, observed_claim TEXT,
  ingest_mode TEXT NOT NULL, available INTEGER NOT NULL DEFAULT 1
);

-- ---------------------------------------------------------------- evidence --
CREATE TABLE IF NOT EXISTS sources (
  source_id TEXT PRIMARY KEY, url TEXT NOT NULL UNIQUE, publisher TEXT,
  source_type TEXT NOT NULL, default_tier INTEGER, accessed_at TEXT,
  underlying_event_key TEXT           -- source lineage / dedup (same_underlying_event)
);
CREATE TABLE IF NOT EXISTS evidence (
  evidence_id       TEXT PRIMARY KEY,
  entity_id         TEXT NOT NULL,
  entity_type       TEXT NOT NULL,
  claim_type        TEXT NOT NULL,
  claim_class       TEXT NOT NULL,
  observed_claim    TEXT NOT NULL,
  source_id         TEXT NOT NULL REFERENCES sources(source_id),
  evidence_date     TEXT NOT NULL,     -- when the underlying fact existed
  source_accessed_at TEXT NOT NULL,    -- when we retrieved it
  quality_tier      INTEGER NOT NULL,
  authority_for_claim INTEGER NOT NULL,
  evidence_status   TEXT NOT NULL CHECK (evidence_status IN ('OBSERVED','INFERRED','UNKNOWN')),
  first_party       INTEGER NOT NULL DEFAULT 0,
  notes             TEXT
);
-- AI output is stored HERE, never in `evidence`.
CREATE TABLE IF NOT EXISTS ai_classifications (
  ai_id TEXT PRIMARY KEY, entity_id TEXT, entity_type TEXT, field TEXT, value TEXT,
  model TEXT, produced_at TEXT, verified_by TEXT, verified_at TEXT
);

-- ------------------------------------------------------------- graph edges --
CREATE TABLE IF NOT EXISTS relationships (
  relationship_id TEXT PRIMARY KEY,
  from_id   TEXT NOT NULL, from_type TEXT NOT NULL,
  kind      TEXT NOT NULL,
  to_id     TEXT NOT NULL, to_type   TEXT NOT NULL,
  evidence_id TEXT REFERENCES evidence(evidence_id),
  observed_at TEXT
);

-- ------------------------------------------------------------------ signals --
CREATE TABLE IF NOT EXISTS formation_signals (
  signal_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, subject_type TEXT NOT NULL,
  signal_type TEXT NOT NULL, observed_at TEXT NOT NULL, collected_at TEXT NOT NULL,
  channel TEXT NOT NULL, evidence_id TEXT REFERENCES evidence(evidence_id),
  evidence_status TEXT NOT NULL, stale INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS technical_signals (
  signal_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, subject_type TEXT NOT NULL,
  signal_type TEXT NOT NULL, observed_at TEXT NOT NULL, collected_at TEXT NOT NULL,
  channel TEXT NOT NULL, evidence_id TEXT REFERENCES evidence(evidence_id),
  evidence_status TEXT NOT NULL, stale INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS commercialization_signals (
  signal_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, subject_type TEXT NOT NULL,
  signal_type TEXT NOT NULL, observed_at TEXT NOT NULL, collected_at TEXT NOT NULL,
  channel TEXT NOT NULL, evidence_id TEXT REFERENCES evidence(evidence_id),
  evidence_status TEXT NOT NULL, stale INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS formation_state_history (
  row_id TEXT PRIMARY KEY, person_id TEXT, project_id TEXT,
  state TEXT NOT NULL, as_of TEXT NOT NULL, supporting_signals TEXT
);

-- ------------------------------------------------- assessment and workflow --
CREATE TABLE IF NOT EXISTS technical_assessments (
  assessment_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, subject_type TEXT NOT NULL,
  dimension TEXT NOT NULL, value TEXT NOT NULL, evidence_status TEXT NOT NULL,
  basis TEXT, assessed_at TEXT, assessed_by TEXT,
  UNIQUE (subject_id, dimension)
);
CREATE TABLE IF NOT EXISTS analyst_reviews (
  review_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, subject_type TEXT NOT NULL,
  reviewed_at TEXT, reviewer TEXT, workflow_state TEXT NOT NULL,
  drop_reason TEXT, payload TEXT
);
CREATE TABLE IF NOT EXISTS intro_queue (
  entry_id TEXT PRIMARY KEY, person_id TEXT, project_id TEXT, review_id TEXT,
  workflow_state TEXT NOT NULL, added_at TEXT,
  contacted INTEGER NOT NULL DEFAULT 0,
  current3_rank INTEGER
);
CREATE TABLE IF NOT EXISTS watchlist (
  entry_id TEXT PRIMARY KEY, person_id TEXT, project_id TEXT,
  reason TEXT NOT NULL, added_at TEXT
);
CREATE TABLE IF NOT EXISTS status_checks (
  check_id TEXT PRIMARY KEY, subject_id TEXT, subject_label TEXT,
  status TEXT NOT NULL, as_of TEXT, source_id TEXT, notes TEXT
);

-- -------------------------------------------------- validation and metering --
CREATE TABLE IF NOT EXISTS holdout_cases (
  case_id TEXT PRIMARY KEY, company TEXT, founder_or_team TEXT,
  cutoff_date TEXT NOT NULL, permitted_source_types TEXT, expected_availability TEXT
);
CREATE TABLE IF NOT EXISTS holdout_evidence (
  row_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES holdout_cases(case_id),
  claim_type TEXT, claim_class TEXT, observed_claim TEXT, evidence_date TEXT NOT NULL,
  source_type TEXT, source_url TEXT, artifact_available_at_cutoff INTEGER NOT NULL,
  evidence_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS holdout_predictions (
  row_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES holdout_cases(case_id),
  verdict TEXT NOT NULL, criteria TEXT, rules_hash TEXT NOT NULL, decided_at TEXT
);
CREATE TABLE IF NOT EXISTS negative_controls (
  control_id TEXT PRIMARY KEY, name TEXT, subject TEXT,
  expected_drop_reason TEXT, actual_state TEXT, actual_drop_reason TEXT,
  result TEXT, tested_at TEXT
);
CREATE TABLE IF NOT EXISTS experiments (
  experiment_id TEXT PRIMARY KEY, subject TEXT, claim TEXT, baseline TEXT,
  status TEXT NOT NULL, result TEXT
);
CREATE TABLE IF NOT EXISTS source_runs (
  run_id TEXT PRIMARY KEY, source TEXT NOT NULL, started_at TEXT, finished_at TEXT,
  raw_signals INTEGER, resolved_entities INTEGER, notes TEXT
);
CREATE TABLE IF NOT EXISTS cost_ledger (
  row_id TEXT PRIMARY KEY, run_id TEXT, source TEXT, api TEXT, requests INTEGER,
  units INTEGER, unit_label TEXT, estimated_cost_usd TEXT, actual_cost_usd TEXT, at TEXT
);

CREATE INDEX IF NOT EXISTS ix_ev_entity ON evidence(entity_id);
CREATE INDEX IF NOT EXISTS ix_ev_date   ON evidence(evidence_date);
CREATE INDEX IF NOT EXISTS ix_fs_subj   ON formation_signals(subject_id);
CREATE INDEX IF NOT EXISTS ix_ts_subj   ON technical_signals(subject_id);
CREATE INDEX IF NOT EXISTS ix_rel_from  ON relationships(from_id);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def reset(path: Path) -> sqlite3.Connection:
    if path.exists():
        path.unlink()
    return connect(path)


def all_column_names(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    out = []
    for (table,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall():
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall():
            out.append((table, row["name"]))
    return out
