"""No secrets, no personal absolute paths, no raw third-party dumps in tracked files."""
import re
import subprocess
from pathlib import Path

SECRET_PAT = re.compile(
    r"(sk-ant-[A-Za-z0-9_-]{10,}|ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"Bearer\s+[A-Za-z0-9._-]{24,})")
HOME_PAT = re.compile(r"/Users/[a-z0-9._-]+/", re.I)


def _tracked(repo_root: Path) -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=repo_root, capture_output=True,
                         text=True).stdout.split()
    return [repo_root / f for f in out]


def _candidates(repo_root: Path) -> list[Path]:
    """Tracked files plus the files we are about to track."""
    tracked = set(_tracked(repo_root))
    for pattern in ("src/**/*.py", "tests/**/*.py", "config/*.yaml",
                    "outputs/*.json", "outputs/*.md", "data/**/*.yaml",
                    "data/**/*.json", "*.md", "*.toml"):
        tracked |= set(repo_root.glob(pattern))
    return [p for p in sorted(tracked) if p.is_file()]


def test_no_secrets_in_tracked_or_staged_files(repo_root):
    hits = []
    for p in _candidates(repo_root):
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        m = SECRET_PAT.search(text)
        if m:
            hits.append((str(p.relative_to(repo_root)), m.group(0)[:12]))
    assert hits == [], f"possible secret: {hits}"


def test_no_env_file_is_tracked(repo_root):
    names = {p.name for p in _tracked(repo_root)}
    assert ".env" not in names


def test_gitignore_excludes_the_database_and_caches(repo_root):
    gi = (repo_root / ".gitignore").read_text()
    for pattern in ("*.db", "__pycache__/", ".env", "data/raw/"):
        assert pattern in gi, f".gitignore missing {pattern}"


def test_no_personal_absolute_paths_in_source_or_outputs(repo_root):
    """Scoped to the SYSTEM: code, config, data and generated outputs.

    `research/` is excluded deliberately and visibly: the Phase 1 report answers the
    question "what is the git repository root", which necessarily names a local path.
    That is a committed historical record, not a path the engine emits.
    """
    hits = []
    for p in _candidates(repo_root):
        if p.suffix not in (".py", ".yaml", ".json", ".md", ".toml"):
            continue
        if p.relative_to(repo_root).parts[0] == "research":
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for m in HOME_PAT.finditer(text):
            hits.append((str(p.relative_to(repo_root)), m.group(0)))
    assert hits == [], f"personal absolute path leaked: {hits[:5]}"


def test_no_raw_social_dumps_committed(repo_root):
    for p in _tracked(repo_root):
        assert "raw_dumps" not in str(p)
        assert not p.name.endswith(".sqlite")
