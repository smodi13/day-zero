"""Publication gate: the ENTIRE public Git history must stay privacy-clean.

Frontend tests check what the site ships. These check what the *repository* ships,
across every reachable object rather than just the working tree — because the
pre-publication audit found bulk third-party profile data sitting in history while
`HEAD` and the built site were both clean.

If any of these fail, the repository must not be published or pushed.
"""
import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True).stdout


def is_repo() -> bool:
    return (ROOT / ".git").exists()


pytestmark = pytest.mark.skipif(not is_repo(), reason="not a git checkout")


# Paths removed from all history before first publication. They must never return.
FORBIDDEN_PATHS = {
    "data/collected/github_users.json",
    "data/collected/github_orgs.json",
    "experiments/headroom/datasets/samples/json_users_120.txt",
}

# Addresses that may legitimately appear. Everything else that looks like an email
# fails the test rather than being judged case-by-case at review time.
#   - the author's own GitHub noreply address, present in commit metadata anyway
#   - Anthropic's co-author trailer
#   - a documentation example inside a quoted third-party README
#   - a venture firm's published deal-flow address, cited as OBSERVED evidence
ALLOWED_EMAIL_SUFFIXES = ("@users.noreply.github.com", "@anthropic.com")
ALLOWED_EMAILS = {"user@github.com", "deals@array.vc", "arraydeals@array.vc"}

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Case-SENSITIVE on purpose: macOS home directories are "/Users/<name>", whereas
# "https://api.github.com/users/<login>" is lowercase and appears legitimately in
# collected API error logs. Matching case-insensitively flags every such URL.
HOME_PATH = re.compile(r"/Users/[a-z][a-z0-9_-]*")
SECRETS = {
    "anthropic key": re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    "openai key": re.compile(r"sk-[A-Za-z0-9]{32,}"),
    "github token": re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    "aws key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "slack token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
    "assigned secret": re.compile(
        r"(?i)\b(?:api[_-]?key|secret|password|passwd|token)\s*[:=]\s*[\"'][A-Za-z0-9_\-]{16,}[\"']"),
}

# Profile fields that mark a file as a bulk person cache rather than research prose.
BULK_PERSON_FIELDS = {"location", "bio", "blog", "followers", "hireable", "twitter_username"}


def reachable_blobs():
    """Every (sha, path) blob reachable from any ref — not merely HEAD."""
    out = []
    for line in git("rev-list", "--objects", "--all").splitlines():
        sha, _, path = line.partition(" ")
        if not path:
            continue
        if git("cat-file", "-t", sha).strip() != "blob":
            continue
        raw = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-p", sha],
                             capture_output=True).stdout
        out.append((sha, path, raw))
    return out


@pytest.fixture(scope="module")
def blobs():
    b = reachable_blobs()
    assert b, "no reachable blobs — is this a real checkout?"
    return b


def test_forbidden_paths_absent_from_all_history(blobs):
    present = {p for _, p, _ in blobs} & FORBIDDEN_PATHS
    assert present == set(), f"raw profile cache present in history: {present}"


def test_no_unexpected_email_addresses_in_history(blobs):
    bad = {}
    for _, path, raw in blobs:
        for m in set(EMAIL.findall(raw.decode("utf-8", "ignore"))):
            if m in ALLOWED_EMAILS or m.endswith(ALLOWED_EMAIL_SUFFIXES):
                continue
            bad.setdefault(m, set()).add(path)
    # Report the paths, never the addresses themselves.
    assert not bad, f"unexpected email address(es) in {sorted({p for v in bad.values() for p in v})}"


def test_no_personal_filesystem_paths_in_history(blobs):
    bad = {p for _, p, raw in blobs
           if HOME_PATH.search(raw.decode("utf-8", "ignore"))}
    assert bad == set(), f"personal filesystem paths in: {sorted(bad)}"


def test_no_secrets_in_history(blobs):
    bad = []
    for _, path, raw in blobs:
        txt = raw.decode("utf-8", "ignore")
        for name, pat in SECRETS.items():
            if pat.search(txt):
                bad.append((name, path))
    assert not bad, f"credential-shaped content: {bad}"


def test_no_bulk_person_caches_in_history(blobs):
    """A JSON file of many records carrying profile fields is a person cache."""
    bad = []
    for _, path, raw in blobs:
        if not path.endswith(".json"):
            continue
        try:
            d = json.loads(raw.decode("utf-8", "ignore"))
        except Exception:
            continue
        recs = d if isinstance(d, list) else (list(d.values()) if isinstance(d, dict) else [])
        dicts = [r for r in recs if isinstance(r, dict)]
        if len(dicts) < 20:
            continue
        fields = {k for r in dicts for k in r}
        if fields & BULK_PERSON_FIELDS:
            bad.append((path, sorted(fields & BULK_PERSON_FIELDS)))
    assert not bad, f"bulk person cache: {bad}"


# Image assets the site legitimately ships. Anything else binary is unexpected in a
# repository that is otherwise entirely text, and worth failing on: stray binaries
# are how databases, archives and browser state get published by accident.
ALLOWED_BINARY_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".ico", ".woff", ".woff2")


def test_no_unexpected_binary_or_oversized_blobs(blobs):
    heavy = [(p, len(raw)) for _, p, raw in blobs if len(raw) > 2_000_000]
    binary = [p for _, p, raw in blobs
              if b"\x00" in raw[:2048] and not p.lower().endswith(ALLOWED_BINARY_SUFFIXES)]
    assert not heavy, f"oversized blobs: {heavy}"
    assert not binary, f"unexpected binary blobs: {binary}"


def test_privacy_disclosures_are_published():
    """The rewrite must stay documented; silently scrubbing is not acceptable."""
    for rel in ("research/prepublication_privacy_audit.md",
                "data/collected/README.md",
                "experiments/headroom/datasets/withheld/json_users_120.md",
                "research/headroom_public_subset_sensitivity.md"):
        assert (ROOT / rel).exists(), f"missing disclosure: {rel}"


def test_removed_paths_are_gitignored():
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for p in FORBIDDEN_PATHS:
        assert p in ignored, f"{p} must be gitignored so a rerun cannot stage it"
