"""Deterministic signal derivation from collected facts.

Every rule here is transparent and testable. Attention metrics (stars, forks,
watchers, followers) are never read by any function in this module — enforced by
`tests/test_no_attention_ranking.py`.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Optional

from ._dates import iso_to_date
from .config import load, signal_family
from .registry import owner_scope
from .urlutil import bare_host, is_product_domain

# ------------------------------------------------------------------ thresholds --
SUSTAINED_MIN_CONTRIBUTIONS = 40     # by the largest human contributor
SUSTAINED_MIN_LONGEVITY_DAYS = 56    # ~8 distinct weeks between first and last activity
ABANDON_STALE_DAYS = 90
ABANDON_SHORT_LIFE_DAYS = 120
CURRENT_SIGNAL_DAYS = 120
CONTRIBUTOR_EXPANSION_MIN = 3

# Language/topic markers used for TECHNICAL DEPTH. Deliberately conservative and
# readable rather than clever: a human can audit exactly why a signal fired.
SYSTEMS_LANGUAGES = {"C", "C++", "Rust", "Go", "Zig", "Assembly", "OCaml", "Swift"}
DEPTH_MARKERS: dict[str, tuple[str, ...]] = {
    "D-01": ("ebpf", "kernel", "syscall", "kvm", "microvm", "micro-vm", "hypervisor",
             "namespace", "seccomp", "lxc", "etw", " esf", "sandbox runtime"),
    "D-02": ("from scratch", "novel", "no vector store", "zero dependencies",
             "single-header", "deterministic", "reversible"),
    "D-03": ("faster", "latency", "throughput", "optimiz", "speedup", "x faster",
             "reduces", "compression", "efficient"),
    "D-04": ("distributed", "consensus", "cluster", "multi-node", "collective",
             "rdma", "p2p", "expert parallel", "load balanc"),
    "D-05": ("security", "prompt injection", "threat", "detection", "malware",
             "zero trust", "zero-trust", "identity", "authorization", "audit",
             "dlp", "yara", "sigma", "red team", "guardrail"),
    "D-06": ("compiler", "parser", "ast", "query engine", "database", "runtime",
             "dsl", "interpreter", "type-safe", "language server", "ir "),
    "D-07": ("inference", "kv cache", "kv-cache", "quantization", "serving",
             "speculative decoding", "cuda", "triton", "mlx", "vllm", "tokeniz"),
    "D-08": ("eval", "benchmark", "test case", "verification", "harness",
             "observability", "trace", "telemetry", "instrument"),
    "D-09": ("data engine", "dataframe", "lakehouse", "multimodal data", "knowledge graph",
             "vector index", "storage engine", "ledger", "fhir"),
    "D-10": ("hipaa", "fhir", "clearing", "freight", "tariff", "medical coding",
             "double entry", "double-entry", "compliance", "gdpr"),
}
INFRA_MARKERS = ("runtime", "kernel", "engine", "proxy", "gateway", "server",
                 "sandbox", "infrastructure", "control plane", "substrate",
                 "index", "compiler", "daemon", "sensor", "layer")

# Array's stated areas, mapped to DAY ZERO themes.
THEME_MARKERS: dict[str, tuple[str, ...]] = {
    # eBPF and kernel-level work is included deliberately: Array's own security thesis
    # names the syscall/kernel layer as the place agent activity becomes visible and
    # enforceable. Added BEFORE the rule freeze; recorded in research/phase2_report.md.
    "agent_execution_isolation": ("sandbox", "microvm", "micro-vm", "isolation", "kvm",
                                  "containment", "fork", "namespace", "seccomp", "lxc",
                                  "ebpf", "kernel", "hypervisor", "syscall"),
    "agent_identity_authority": ("identity", "authorization", "permission", "zero trust",
                                 "zero-trust", "oauth", "credential", "authority",
                                 "approve", "policy", "governance", "control plane"),
    # Deliberately specific. Bare "budget"/"cost"/"usage" matched a plain-text budget
    # tracker during testing, which is not agent economics. Tightened before the freeze.
    "agent_economics": ("token", "llm cost", "ai spend", "agent budget",
                        "token budget", "cost per", "cost across", "spend across",
                        "token usage", "context compression", "prompt cost"),
    "agent_verification": ("verification", "guardrail", "eval", "deterministic",
                           "state machine", "gate", "test", "assert", "rollback"),
    "agent_observability": ("observability", "trace", "telemetry", "monitor",
                            "inspect", "provenance", "audit", "incident"),
    "agent_memory_context": ("memory", "context", "recall", "knowledge graph", "rag"),
    "inference_infra": ("inference", "kv cache", "kv-cache", "quantization", "serving",
                        "gpu", "cuda", "decoding", "collective"),
    "data_infra": ("data engine", "dataframe", "database client", "lakehouse",
                   "query engine", "vector index", "federated"),
    "security": ("security", "threat", "malware", "edr", "detection", "injection",
                 "supply chain", "supply-chain", "zero trust", "zero-trust", "ebpf"),
    "health_infra": ("fhir", "hipaa", "clinical", "health data", "genomic"),
    "fintech_infra": ("ledger", "double entry", "double-entry", "payments",
                      "reconciliation", "accounting"),
}

ARRAY_RELEVANT_THEMES = set(THEME_MARKERS) - set()


@dataclass(frozen=True)
class DerivedSignal:
    signal_type: str
    family: str
    subject_id: str
    subject_type: str
    observed_at: str          # date the underlying fact existed
    channel: str
    evidence_status: str
    basis: str

    @property
    def negative(self) -> bool:
        return self.signal_type == "V-06"


def _text(repo: dict[str, Any]) -> str:
    parts = [repo.get("description") or "", " ".join(repo.get("topics") or []),
             repo.get("full_name") or "", repo.get("homepage") or ""]
    return " ".join(parts).lower()


def themes_for(repo: dict[str, Any]) -> list[str]:
    blob = _text(repo)
    return sorted(t for t, markers in THEME_MARKERS.items()
                  if any(m in blob for m in markers))


def within_array_areas(repo: dict[str, Any]) -> bool:
    return bool(themes_for(repo))


# ------------------------------------------------------------------- BUILD ----
def build_signals(repo: dict[str, Any], releases: list[dict], subject_id: str,
                  as_of: date) -> list[DerivedSignal]:
    out: list[DerivedSignal] = []
    ch = "github"
    created = repo.get("created_at")
    con = repo.get("construction") or {}
    if created and not repo.get("is_fork"):
        out.append(DerivedSignal("B-01", "BUILD", subject_id, "repository", created, ch,
                                 "OBSERVED", f"repository created {created}"))
    rel_dates = [r["published_at"] for r in releases if r.get("published_at")]
    if rel_dates:
        out.append(DerivedSignal("B-02", "BUILD", subject_id, "repository",
                                 min(rel_dates), ch, "OBSERVED",
                                 f"{len(rel_dates)} tagged release(s); first {min(rel_dates)}"))
    top = con.get("top_contributions") or 0
    longevity = con.get("longevity_days")
    if top >= SUSTAINED_MIN_CONTRIBUTIONS and (longevity or 0) >= SUSTAINED_MIN_LONGEVITY_DAYS:
        out.append(DerivedSignal("B-03", "BUILD", subject_id, "repository",
                                 repo.get("pushed_at") or created, ch, "OBSERVED",
                                 f"top human contributor {top} commits over {longevity} days"))
    blob = _text(repo)
    if any(m in blob for m in INFRA_MARKERS) and repo.get("language") in SYSTEMS_LANGUAGES:
        out.append(DerivedSignal("B-09", "BUILD", subject_id, "repository",
                                 created or "", ch, "OBSERVED",
                                 f"infrastructure-layer markers in {repo.get('language')}"))
    if any(w in blob for w in ("benchmark", "vs ", "x faster", "% fewer", "% reduction")):
        out.append(DerivedSignal("B-05", "BUILD", subject_id, "repository",
                                 created or "", ch, "INFERRED",
                                 "benchmark/performance claim present in description"))
    return out


# --------------------------------------------------------- TECHNICAL DEPTH ----
def depth_signals(repo: dict[str, Any], subject_id: str) -> list[DerivedSignal]:
    blob = _text(repo)
    lang = repo.get("language")
    created = repo.get("created_at") or ""
    out: list[DerivedSignal] = []
    for sig, markers in DEPTH_MARKERS.items():
        hits = [m for m in markers if m in blob]
        if not hits:
            continue
        # D-01/D-04/D-06 assert real systems work; require a systems language to
        # call them OBSERVED, otherwise they are INFERRED and cannot support a state.
        strict = sig in {"D-01", "D-04", "D-06"}
        status = "OBSERVED" if (not strict or lang in SYSTEMS_LANGUAGES) else "INFERRED"
        out.append(DerivedSignal(sig, "TECHNICAL_DEPTH", subject_id, "repository",
                                 created, "github", status,
                                 f"markers {hits[:3]} in description/topics; language {lang}"))
    return out


# ---------------------------------------------------------------- VELOCITY ----
def velocity_signals(repo: dict[str, Any], contributors: list[dict],
                     releases: list[dict], subject_id: str, as_of: date) -> list[DerivedSignal]:
    con = repo.get("construction") or {}
    out: list[DerivedSignal] = []
    since_push = con.get("days_since_push")
    longevity = con.get("longevity_days")
    pushed = repo.get("pushed_at") or ""
    if since_push is not None and since_push > ABANDON_STALE_DAYS and \
       (longevity is None or longevity < ABANDON_SHORT_LIFE_DAYS):
        out.append(DerivedSignal("V-06", "VELOCITY", subject_id, "repository", pushed,
                                 "github", "OBSERVED",
                                 f"no push in {since_push} days; total active life {longevity} days"))
    humans = [c for c in contributors if (c.get("contributions") or 0) >= 3]
    if len(humans) >= CONTRIBUTOR_EXPANSION_MIN:
        out.append(DerivedSignal("V-03", "VELOCITY", subject_id, "repository", pushed,
                                 "github", "OBSERVED",
                                 f"{len(humans)} human contributors with >=3 commits"))
    if len(releases) >= 3:
        out.append(DerivedSignal("V-02", "VELOCITY", subject_id, "repository", pushed,
                                 "github", "OBSERVED", f"{len(releases)} tagged releases"))
    return out


def is_current(repo: dict[str, Any]) -> bool:
    since = (repo.get("construction") or {}).get("days_since_push")
    return since is not None and since <= CURRENT_SIGNAL_DAYS


# --------------------------------------------------------------- FORMATION ----
FOUNDER_BIO_RE = ("founder", "co-founder", "cofounder", "ceo @", "building @",
                  "building ", "i'm building", "currently:")


def formation_signals_for_repo(repo: dict[str, Any], org: Optional[dict],
                               subject_id: str) -> list[DerivedSignal]:
    out: list[DerivedSignal] = []
    home = repo.get("homepage") or ""
    if home and is_product_domain(home):
        out.append(DerivedSignal("F-01", "FORMATION", subject_id, "repository",
                                 repo.get("created_at") or "", "web", "OBSERVED",
                                 f"project domain {bare_host(home)}"))
    if org and org.get("created_at"):
        scope = owner_scope(org.get("login") or "", org.get("name") or "",
                            org.get("description") or "", org.get("blog") or "",
                            org.get("public_repos") or 0)
        if scope == "unregistered":
            out.append(DerivedSignal("F-02", "FORMATION", subject_id, "organization",
                                     org["created_at"], "github", "OBSERVED",
                                     f"github org {org['login']} created {org['created_at']}"))
        if (org.get("name") or "").strip().lower().endswith((" inc.", " inc", " ltd", " ltd.",
                                                             " llc", " gmbh", " corp", " corp.")):
            out.append(DerivedSignal("F-06", "FORMATION", subject_id, "organization",
                                     org["created_at"], "github", "OBSERVED",
                                     f"incorporated name: {org['name']}"))
    return out


def founder_statement_signal(user: dict[str, Any], subject_id: str) -> Optional[DerivedSignal]:
    """F-03 requires an EXPLICIT first-person statement in a self-published bio.

    An employer field is never a formation signal, and never a departure signal.
    """
    bio = (user.get("bio") or "").lower()
    if not bio:
        return None
    if not any(m in bio for m in FOUNDER_BIO_RE):
        return None
    return DerivedSignal("F-03", "FORMATION", subject_id, "person",
                         user.get("account_created_at") or "", "github", "OBSERVED",
                         f"self-published bio states: {user.get('bio')!r}")


# ------------------------------------------------------- COMMERCIALIZATION ----
def commercialization_signals(repo: dict[str, Any], subject_id: str) -> list[DerivedSignal]:
    out: list[DerivedSignal] = []
    home = repo.get("homepage") or ""
    blob = _text(repo)
    if home and ("docs." in bare_host(home) or "/docs" in home):
        out.append(DerivedSignal("M-03", "COMMERCIALIZATION", subject_id, "repository",
                                 repo.get("created_at") or "", "web", "OBSERVED",
                                 f"documentation site {home}"))
    if any(w in blob for w in ("pricing", "free tier", "cloud plan", "enterprise")):
        out.append(DerivedSignal("M-04", "COMMERCIALIZATION", subject_id, "repository",
                                 repo.get("created_at") or "", "web", "INFERRED",
                                 "productized/commercial language in description"))
    return out


# ------------------------------------------------------------- CONVERGENCE ----
def channel_of(signal: DerivedSignal) -> str:
    return signal.channel


def convergence(signals: list[DerivedSignal]) -> dict[str, Any]:
    """Cross-source convergence per the frozen ontology.

    Signals published on the same day through surfaces the same actor controls count
    as ONE channel (Phase 1 near-miss NM-1: simultaneity is the tell).
    """
    cfg = load("signal_types.yaml")["convergence"]
    fams = {s.family for s in signals}
    has_build = bool(fams & set(cfg["requires_family_in"]))
    has_form = bool(fams & set(cfg["requires_family_in_2"]))

    buckets: dict[tuple[str, str], list[DerivedSignal]] = {}
    for s in signals:
        buckets.setdefault((s.channel, s.observed_at), []).append(s)
    channels: set[str] = set()
    if cfg.get("same_day_same_actor_counts_as_one_channel"):
        seen_days: dict[str, set[str]] = {}
        for (chan, day), _ in buckets.items():
            seen_days.setdefault(day, set()).add(chan)
        # Channels announced together on one day collapse to a single "coordinated" channel.
        for day, chans in seen_days.items():
            if len(chans) > 1:
                channels.add(f"coordinated:{day}")
            else:
                channels |= chans
    else:
        channels = {s.channel for s in signals}

    ok = (len(signals) >= cfg["min_signals"]
          and len(channels) >= cfg["min_independent_channels"]
          and has_build and has_form)
    return {"converged": ok, "channels": sorted(channels),
            "channel_count": len(channels), "signal_count": len(signals),
            "has_build_or_depth": has_build, "has_collab_or_formation": has_form}
