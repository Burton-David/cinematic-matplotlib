"""README links resolve against the files in this checkout, not a stale tag."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Absolute URLs, because PyPI renders the README too and relative image paths
# break there. The cost is that a link can silently pin an old ref, which is how
# half the README ended up on v0.2.0 while the v3 images tracked main.
REPO_LINK = re.compile(
    r"https://(?:raw\.githubusercontent\.com/Burton-David/cinematic-matplotlib"
    r"|github\.com/Burton-David/cinematic-matplotlib/blob)/([^/]+)/([^)\s]+)"
)


def _repo_links() -> list[tuple[str, str]]:
    return REPO_LINK.findall((ROOT / "README.md").read_text(encoding="utf-8"))


def test_readme_repo_links_track_main() -> None:
    links = _repo_links()
    assert links, "expected the README to link images and docs in this repo"
    pinned = [f"{ref}/{path}" for ref, path in links if ref != "main"]
    assert pinned == []


def test_readme_repo_links_point_at_files_that_exist() -> None:
    missing = [path for _, path in _repo_links() if not (ROOT / path).is_file()]
    assert missing == []
