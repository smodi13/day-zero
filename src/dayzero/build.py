"""Canonical build: collected facts -> normalized database -> derived signals.

The build is deterministic and idempotent: running it twice from the same collected
data produces byte-identical exports.

The build DOES NOT run the historical holdout, does not produce holdout verdicts,
does not run negative-control verdicts, and does not produce a final Intro Queue.
Those are post-freeze operations gated on the frozen-rules manifest.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any, Optional

import yaml

from . import ids, registry, resolve, signals as sig, technical
from ._dates import iso_to_date
from .adapters import arxiv, manual
from .config import DATA_DIR, load
from .db import connect, reset
from .formation import compute_state, history, mark_stale
from .timeutil import now_utc, to_rfc3339
from .urlutil import bare_host, is_product_domain, normalize_url

COLLECTED = DATA_DIR / "collected"
MANUAL = DATA_DIR / "manual"
DB_PATH = DATA_DIR / "day_zero.db"

GITHUB = "https://github.com"


def _load(name: str) -> Any:
    path = COLLECTED / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_collection_timestamp() -> Optional[str]:
    """Max `collected_at` across collected artifacts, or None if nothing collected."""
    repos = _load("github_repos.json")
    stamps = [r.get("collected_at") for r in repos.values() if r.get("collected_at")]
    return max(stamps) if stamps else None


def _manual(name: str) -> dict:
    path = MANUAL / name
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


class Builder:
    def __init__(self, db_path: Path = DB_PATH, as_of: Optional[date] = None,
                 now: Optional[str] = None) -> None:
        self.db_path = db_path
        self.as_of = as_of or now_utc().date()
        # `now` records WHEN WE LOOKED, never when a fact was true.
        # It defaults to the latest collection timestamp in the evidence base rather
        # than to wall-clock time, so a rebuild from identical collected data is
        # byte-identical and the export is a pure function of its inputs.
        self.now = now or _latest_collection_timestamp() or to_rfc3339(now_utc())
        self.conn = reset(db_path)
        self.counts: dict[str, int] = {}
        self.signal_index: dict[str, list[sig.DerivedSignal]] = {}
        self.repo_index: dict[str, dict] = {}

    # ------------------------------------------------------------- helpers --
    def _bump(self, key: str, n: int = 1) -> None:
        self.counts[key] = self.counts.get(key, 0) + n

    def _source(self, url: str, source_type: str, publisher: str = "",
                accessed_at: Optional[str] = None,
                underlying_event_key: Optional[str] = None) -> str:
        sid = ids.source_id(url)
        tier = load("source_quality.yaml")["default_tier"].get(source_type, 3)
        self.conn.execute(
            "INSERT OR IGNORE INTO sources(source_id,url,publisher,source_type,"
            "default_tier,accessed_at,underlying_event_key) VALUES (?,?,?,?,?,?,?)",
            (sid, normalize_url(url), publisher, source_type, tier,
             accessed_at or self.now, underlying_event_key))
        return sid

    def _authority(self, source_type: str, claim_class: str, first_party: bool) -> int:
        """Source authority is a property of the (source, claim) PAIR."""
        cfg = load("source_quality.yaml")
        for rule in cfg["authority_rules"]:
            w = rule["when"]
            if "first_party" in w and bool(w["first_party"]) != first_party:
                continue
            if "source_type" in w and w["source_type"] != source_type:
                continue
            if "claim_class" in w and w["claim_class"] != claim_class:
                continue
            return int(rule["authority"])
        return int(cfg["default_tier"].get(source_type, 3))

    def _evidence(self, *, entity_id: str, entity_type: str, claim_type: str,
                  claim_class: str, observed_claim: str, source_url: str,
                  source_type: str, evidence_date: str, status: str,
                  first_party: bool = False, notes: str = "") -> str:
        sid = self._source(source_url, source_type)
        eid = ids.evidence_id(entity_id, claim_type, sid, evidence_date)
        tier = load("source_quality.yaml")["default_tier"].get(source_type, 3)
        auth = self._authority(source_type, claim_class, first_party)
        self.conn.execute(
            "INSERT OR IGNORE INTO evidence(evidence_id,entity_id,entity_type,claim_type,"
            "claim_class,observed_claim,source_id,evidence_date,source_accessed_at,"
            "quality_tier,authority_for_claim,evidence_status,first_party,notes)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (eid, entity_id, entity_type, claim_type, claim_class, observed_claim, sid,
             evidence_date, self.now, tier, auth, status, int(first_party), notes))
        self._bump("evidence")
        return eid

    def _rel(self, a: str, at: str, kind: str, b: str, bt: str,
             evidence_id: Optional[str], observed_at: str) -> None:
        rid = ids.relationship_id(a, kind, b)
        self.conn.execute(
            "INSERT OR IGNORE INTO relationships(relationship_id,from_id,from_type,kind,"
            "to_id,to_type,evidence_id,observed_at) VALUES (?,?,?,?,?,?,?,?)",
            (rid, a, at, kind, b, bt, evidence_id, observed_at))
        self._bump("relationships")

    def _signal(self, table: str, s: sig.DerivedSignal, evidence_id: Optional[str],
                stale: bool) -> None:
        sid = ids.signal_id(s.subject_id, s.signal_type, s.observed_at)
        self.conn.execute(
            f"INSERT OR IGNORE INTO {table}(signal_id,subject_id,subject_type,signal_type,"
            "observed_at,collected_at,channel,evidence_id,evidence_status,stale)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (sid, s.subject_id, s.subject_type, s.signal_type, s.observed_at, self.now,
             s.channel, evidence_id, s.evidence_status, int(stale)))
        self._bump(f"signals:{table}")

    # -------------------------------------------------------------- ingest --
    def ingest_github(self) -> None:
        repos = _load("github_repos.json")
        contribs = _load("github_contributors.json")
        releases = _load("github_releases.json")
        users = _load("github_users.json")
        orgs = _load("github_orgs.json")
        papers = _load("arxiv_papers.json")

        # organizations first (referential integrity)
        for login, org in sorted(orgs.items()):
            oid = ids.org_id("github.com", login)
            org_age = None
            d = iso_to_date(org.get("created_at"))
            if d:
                org_age = (self.as_of - d).days
            scope = registry.owner_scope(login, org.get("name") or "",
                                         org.get("description") or "",
                                         org.get("blog") or "",
                                         org.get("public_repos") or 0, org_age)
            self.conn.execute(
                "INSERT OR IGNORE INTO organizations(org_id,host,login,name,blog,location,"
                "description,created_at,public_repos,scope) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (oid, "github.com", login, org.get("name"), org.get("blog"),
                 org.get("location"), org.get("description"), org.get("created_at"),
                 org.get("public_repos"), scope))
            self._bump("organizations")
            if org.get("created_at"):
                self._evidence(entity_id=oid, entity_type="organization",
                               claim_type="org_created", claim_class="formation",
                               observed_claim=f"GitHub organization {login} created {org['created_at']}",
                               source_url=f"{GITHUB}/{login}", source_type="github_org",
                               evidence_date=org["created_at"], status="OBSERVED",
                               first_party=True)

        # identities (people)
        for login, u in sorted(users.items()):
            iid = ids.identity_id("github", login)
            self.conn.execute(
                "INSERT OR IGNORE INTO identities(identity_id,person_id,channel,handle,"
                "profile_url,is_bot,first_seen) VALUES (?,?,?,?,?,?,?)",
                (iid, None, "github", login, f"{GITHUB}/{login}", 0,
                 u.get("account_created_at")))
            self._bump("identities")

        # repositories
        for full_name, r in sorted(repos.items()):
            rid = ids.repo_id(full_name)
            self.repo_index[full_name] = r
            self.conn.execute(
                "INSERT OR IGNORE INTO repositories(repo_id,host,full_name,owner_login,"
                "owner_type,created_at,pushed_at,language,license,homepage,description,"
                "archived,is_fork,collected_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (rid, "github.com", full_name, r.get("owner_login"), r.get("owner_type"),
                 r.get("created_at"), r.get("pushed_at"), r.get("language"),
                 r.get("license"), r.get("homepage"), r.get("description"),
                 int(bool(r.get("archived"))), int(bool(r.get("is_fork"))),
                 r.get("collected_at")))
            self._bump("repositories")

            att = r.get("attention") or {}
            self.conn.execute(
                "INSERT OR IGNORE INTO repo_attention(repo_id,stars,forks,watchers,open_issues)"
                " VALUES (?,?,?,?,?)",
                (rid, att.get("stars"), att.get("forks"), att.get("watchers"),
                 att.get("open_issues")))
            con = r.get("construction") or {}
            self.conn.execute(
                "INSERT OR IGNORE INTO repo_construction(repo_id,human_contributors,"
                "top_contributions,total_contributions,longevity_days,age_days,"
                "days_since_push,release_count,active_window_ratio)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (rid, con.get("human_contributors"), con.get("top_contributions"),
                 con.get("total_contributions"), con.get("longevity_days"),
                 con.get("age_days"), con.get("days_since_push"),
                 con.get("release_count"), con.get("active_window_ratio")))

            repo_url = f"{GITHUB}/{full_name}"
            if r.get("created_at"):
                self._evidence(entity_id=rid, entity_type="repository",
                               claim_type="repo_created", claim_class="construction",
                               observed_claim=f"repository {full_name} created {r['created_at']}",
                               source_url=repo_url, source_type="github_repo",
                               evidence_date=r["created_at"], status="OBSERVED",
                               first_party=True)

            # ---- relationships: contributors ----
            for c in contribs.get(full_name, [])[:6]:
                login = c["login"]
                iid = ids.identity_id("github", login)
                self.conn.execute(
                    "INSERT OR IGNORE INTO identities(identity_id,person_id,channel,handle,"
                    "profile_url,is_bot,first_seen) VALUES (?,?,?,?,?,?,?)",
                    (iid, None, "github", login, f"{GITHUB}/{login}", 0, None))
                ev = self._evidence(
                    entity_id=iid, entity_type="identity",
                    claim_type="contributed_to", claim_class="construction",
                    observed_claim=f"{login} has {c['contributions']} commits in {full_name}",
                    source_url=repo_url, source_type="github_commits",
                    evidence_date=r.get("pushed_at") or r.get("created_at") or "1970-01-01",
                    status="OBSERVED", first_party=True)
                kind = "MAINTAINS" if c["contributions"] >= 40 else "CONTRIBUTED_TO"
                self._rel(iid, "identity", kind, rid, "repository", ev,
                          r.get("pushed_at") or "")

            # ---- relationship: owned by org ----
            if r.get("owner_type") == "Organization":
                oid = ids.org_id("github.com", r["owner_login"])
                self._rel(rid, "repository", "OWNED_BY", oid, "organization", None,
                          r.get("created_at") or "")

            # ---- derived signals ----
            rel_list = releases.get(full_name, [])
            cons = contribs.get(full_name, [])
            org = orgs.get(r.get("owner_login") or "")
            derived: list[sig.DerivedSignal] = []
            derived += sig.build_signals(r, rel_list, rid, self.as_of)
            depth = sig.depth_signals(r, rid)
            derived += depth
            derived += sig.velocity_signals(r, cons, rel_list, rid, self.as_of)
            derived += sig.formation_signals_for_repo(r, org, rid)
            derived += sig.commercialization_signals(r, rid)

            # paper linkage requires EXACT author overlap, not a name match
            paper_linked = self._link_paper(full_name, rid, papers, cons, users, derived)

            stale = mark_stale(derived, self.as_of)
            for s in derived:
                table = {"FORMATION": "formation_signals",
                         "COMMERCIALIZATION": "commercialization_signals"}.get(
                             s.family, "technical_signals")
                ev = self._evidence(
                    entity_id=rid, entity_type="repository",
                    claim_type=s.signal_type, claim_class=(
                        "formation" if s.family == "FORMATION" else
                        "commercial" if s.family == "COMMERCIALIZATION" else
                        "technical_depth" if s.family == "TECHNICAL_DEPTH" else "construction"),
                    observed_claim=s.basis, source_url=repo_url,
                    source_type="github_repo",
                    evidence_date=s.observed_at or r.get("created_at") or "1970-01-01",
                    status=s.evidence_status, first_party=True)
                self._signal(table, s, ev, stale.get(s.signal_type, False))
            self.signal_index[full_name] = derived

            # ---- technical dimensions (rule-derived) ----
            for dv in technical.derive(r, depth, rel_list, paper_linked):
                self.conn.execute(
                    "INSERT OR IGNORE INTO technical_assessments(assessment_id,subject_id,"
                    "subject_type,dimension,value,evidence_status,basis,assessed_at,assessed_by)"
                    " VALUES (?,?,?,?,?,?,?,?,?)",
                    (ids.entity_id("assess", f"{rid}|{dv.dimension}"), rid, "repository",
                     dv.dimension, dv.value, dv.evidence_status, dv.basis, self.now,
                     dv.assessed_by))
                self._bump("technical_assessments")

        self._founder_statements(users, repos, contribs)

    def _link_paper(self, full_name: str, rid: str, papers: dict,
                    contributors: list[dict], users: dict,
                    derived: list[sig.DerivedSignal]) -> bool:
        """Attach a paper only when a paper author EXACTLY matches a contributor's
        self-published name. Title similarity alone never links (ER-2)."""
        entry = papers.get(full_name)
        if not entry:
            return False
        names = []
        for c in contributors[:6]:
            u = users.get(c["login"]) or {}
            if u.get("name"):
                names.append(u["name"])
        linked = False
        for res in entry.get("results", []):
            overlap = arxiv.author_overlaps(res.get("authors", []), names)
            if not overlap:
                continue
            pid = ids.paper_id(res["arxiv_id"])
            self.conn.execute(
                "INSERT OR IGNORE INTO papers(paper_id,arxiv_id,title,published_at,url)"
                " VALUES (?,?,?,?,?)",
                (pid, res["arxiv_id"], res["title"], res["published_at"], res["url"]))
            self._bump("papers")
            for i, a in enumerate(res.get("authors", [])):
                self.conn.execute(
                    "INSERT OR IGNORE INTO paper_authors(paper_id,author_name,position,identity_id)"
                    " VALUES (?,?,?,?)", (pid, a, i, None))
            ev = self._evidence(
                entity_id=rid, entity_type="repository", claim_type="paper_linked",
                claim_class="technical_depth",
                observed_claim=f"arXiv {res['arxiv_id']}: {res['title']} (author overlap: {overlap})",
                source_url=res["url"], source_type="arxiv_paper",
                evidence_date=res["published_at"], status="OBSERVED")
            self._rel(rid, "repository", "IMPLEMENTS", pid, "paper", ev, res["published_at"])
            derived.append(sig.DerivedSignal(
                "C-03", "COLLABORATION", rid, "repository", res["published_at"],
                "research", "OBSERVED",
                f"paper author overlaps repo contributor: {overlap}"))
            derived.append(sig.DerivedSignal(
                "B-08", "BUILD", rid, "repository", res["published_at"],
                "research", "OBSERVED", f"implementation linked to arXiv {res['arxiv_id']}"))
            linked = True
        return linked

    def _founder_statements(self, users: dict, repos: dict, contribs: dict) -> None:
        """F-03 requires an explicit first-person statement in a self-published bio.

        An employer field is never a formation signal and never a departure signal.
        """
        for login, u in sorted(users.items()):
            s = sig.founder_statement_signal(u, ids.identity_id("github", login))
            if not s:
                continue
            iid = ids.identity_id("github", login)
            ev = self._evidence(
                entity_id=iid, entity_type="identity", claim_type="F-03",
                claim_class="formation", observed_claim=s.basis,
                source_url=f"{GITHUB}/{login}", source_type="github_user",
                evidence_date=u.get("account_created_at") or "1970-01-01",
                status="OBSERVED", first_party=True,
                notes="self-published bio; statement authority only")
            self._signal("formation_signals", s, ev, False)

    # --------------------------------------------------------- people/state --
    def resolve_people(self) -> None:
        """Create person records from GitHub identities, conservatively.

        A person is anchored on a single GitHub identity. Cross-channel merges require
        ER-1 evidence, which in this population is almost never present (only 1 of 267
        collected profiles publishes an X link) — so nearly every person has exactly
        one identity, and that is recorded honestly rather than papered over.
        """
        users = _load("github_users.json")
        for login, u in sorted(users.items()):
            iid = ids.identity_id("github", login)
            pid = ids.person_id("github", login)
            blog = u.get("blog") or ""
            conf = resolve.identity_confidence(
                has_real_name=bool(u.get("name")),
                has_self_published_site=bool(blog) and is_product_domain(blog),
                has_org_membership=bool(u.get("company")),
                cross_channel_links=1 if (blog and bare_host(blog) not in ("", "github.com")) else 0)
            career, career_ev = self._career_class(u, login)
            self.conn.execute(
                "INSERT OR IGNORE INTO builders(person_id,display_name,identity_confidence,"
                "career_signal_class,career_signal_evidence_id,created_at)"
                " VALUES (?,?,?,?,?,?)",
                (pid, u.get("name"), conf, career, career_ev, self.now))
            self.conn.execute("UPDATE identities SET person_id=? WHERE identity_id=?",
                              (pid, iid))
            self._bump("builders")

    def _career_class(self, u: dict, login: str) -> tuple[str, Optional[str]]:
        """Optional, evidence-backed, and NEVER a positive ranking factor.

        Forbidden inputs (account age, repo topic, follower count, employer silence)
        are not consulted anywhere in this function.
        """
        bio = (u.get("bio") or "").lower()
        company = (u.get("company") or "").lower()
        iid = ids.identity_id("github", login)
        url = f"{GITHUB}/{login}"

        young = ("phd student", "ph.d. student", "phd candidate", "student",
                 "undergrad", "research assistant", "msc", "postdoc")
        if any(t in bio for t in young):
            ev = self._evidence(entity_id=iid, entity_type="identity",
                                claim_type="career_signal", claim_class="career",
                                observed_claim=f"self-published bio: {u.get('bio')!r}",
                                source_url=url, source_type="github_user",
                                evidence_date=u.get("account_created_at") or "1970-01-01",
                                status="OBSERVED", first_party=True)
            return "YOUNG_BUILDER", ev

        founder = ("founder", "co-founder", "cofounder", "ceo @", "ceo &")
        if any(t in bio for t in founder):
            ev = self._evidence(entity_id=iid, entity_type="identity",
                                claim_type="career_signal", claim_class="career",
                                observed_claim=f"self-published bio: {u.get('bio')!r}",
                                source_url=url, source_type="github_user",
                                evidence_date=u.get("account_created_at") or "1970-01-01",
                                status="OBSERVED", first_party=True)
            return "OPERATOR_TO_FOUNDER", ev

        if bio and company:
            ev = self._evidence(entity_id=iid, entity_type="identity",
                                claim_type="career_signal", claim_class="career",
                                observed_claim=f"self-published role/company: {u.get('company')!r}",
                                source_url=url, source_type="github_user",
                                evidence_date=u.get("account_created_at") or "1970-01-01",
                                status="OBSERVED", first_party=True)
            return "OTHER_EXPLICIT", ev

        return "UNCLASSIFIED", None

    def compute_states(self) -> None:
        for full_name, derived in sorted(self.signal_index.items()):
            rid = ids.repo_id(full_name)
            hist = history(derived, author_resolved=True)
            for h in hist:
                row = ids.entity_id("state", f"{rid}|{h.state}|{h.as_of}")
                self.conn.execute(
                    "INSERT OR IGNORE INTO formation_state_history(row_id,person_id,"
                    "project_id,state,as_of,supporting_signals) VALUES (?,?,?,?,?,?)",
                    (row, None, rid, h.state, h.as_of, json.dumps(list(h.supporting))))
                self._bump("formation_states")

    def ingest_manual(self) -> None:
        for rec in manual.load_yaml(MANUAL / "hackathons.yaml"):
            r = manual.validate_hackathon(rec)
            self.conn.execute(
                "INSERT OR IGNORE INTO hackathons(hackathon_id,name,edition,year,"
                "official_url,start_date,end_date,import_mode) VALUES (?,?,?,?,?,?,?,?)",
                (ids.entity_id("hack", f"{r['name']}|{r['year']}"), r["name"],
                 r.get("edition"), r["year"], r["official_url"], r.get("start_date"),
                 r.get("end_date"), r["import_mode"]))
            self._bump("hackathons")
        for rec in manual.load_yaml(MANUAL / "events.yaml"):
            r = manual.validate_event(rec)
            self.conn.execute(
                "INSERT OR IGNORE INTO events(event_id,name,date,location,official_url,"
                "organizer,theme,why_relevant,sourcing_objective,builder_signal_sought,"
                "attendance_status,import_mode) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (ids.entity_id("event", f"{r['name']}|{r['date']}"), r["name"], r["date"],
                 r.get("location"), r["official_url"], r.get("organizer"), r["theme"],
                 r["why_relevant"], r["sourcing_objective"], r.get("builder_signal_sought"),
                 r["attendance_status"], r["import_mode"]))
            self._bump("events")
        xs = _manual("x_signals.yaml")
        for rec in xs.get("records", []) or []:
            self.conn.execute(
                "INSERT OR IGNORE INTO social_signals(social_id,channel,handle,url,"
                "posted_at,claim_class,observed_claim,ingest_mode,available)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (ids.entity_id("social", rec["url"]), "x", rec.get("handle"), rec["url"],
                 rec.get("posted_at"), rec.get("claim_class"), rec.get("observed_claim"),
                 manual.MANUAL_MODE, 1))
            self._bump("social_signals")
        for rec in (_manual("status_checks.yaml").get("records") or []):
            self.conn.execute(
                "INSERT OR IGNORE INTO status_checks(check_id,subject_id,subject_label,"
                "status,as_of,source_id,notes) VALUES (?,?,?,?,?,?,?)",
                (ids.entity_id("status", rec["subject"]),
                 ids.repo_id(rec["subject"]) if "/" in rec["subject"] else None,
                 rec["subject"], rec["status"], rec.get("as_of"),
                 self._source(rec["source"], "company_site") if rec.get("source") else None,
                 rec.get("notes")))
            self._bump("status_checks")

    def ingest_cost(self) -> None:
        path = DATA_DIR / "cost_ledger.jsonl"
        if not path.exists():
            return
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            e = json.loads(line)
            self.conn.execute(
                "INSERT OR IGNORE INTO cost_ledger(row_id,run_id,source,api,requests,units,"
                "unit_label,estimated_cost_usd,actual_cost_usd,at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (ids.entity_id("cost", f"{e['run_id']}|{e['source']}|{e['at']}|{i}"),
                 e["run_id"], e["source"], e["api"], e["requests"], e["units"],
                 e["unit_label"], e["estimated_cost_usd"], e["actual_cost_usd"], e["at"]))
            self._bump("cost_events")

    def validate(self) -> list[str]:
        """Integrity checks that must hold after every build."""
        problems: list[str] = []
        c = self.conn
        n = c.execute("SELECT COUNT(*) FROM evidence e LEFT JOIN sources s"
                      " ON e.source_id=s.source_id WHERE s.source_id IS NULL").fetchone()[0]
        if n:
            problems.append(f"{n} evidence rows with no source")
        n = c.execute("SELECT COUNT(*) FROM identities WHERE is_bot=1 AND person_id IS NOT NULL").fetchone()[0]
        if n:
            problems.append(f"{n} bot identities attached to a person")
        n = c.execute("SELECT COUNT(*) FROM technical_signals WHERE evidence_id IS NULL").fetchone()[0]
        if n:
            problems.append(f"{n} technical signals with no evidence")
        n = c.execute("SELECT COUNT(*) FROM builders WHERE career_signal_class != 'UNCLASSIFIED'"
                      " AND career_signal_evidence_id IS NULL").fetchone()[0]
        if n:
            problems.append(f"{n} classified builders with no career evidence")
        return problems

    def run(self) -> dict[str, Any]:
        self.ingest_github()
        self.resolve_people()
        self.compute_states()
        self.ingest_manual()
        self.ingest_cost()
        problems = self.validate()
        self.conn.commit()
        return {"as_of": self.as_of.isoformat(), "counts": dict(sorted(self.counts.items())),
                "integrity_problems": problems}
