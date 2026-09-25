"""lychee is not installed on every machine, so these tests check the config file itself:
it parses, it uses only known settings, and its patterns are valid regular expressions."""

import re
import tomllib
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "tools" / "lychee.toml"

# Settings from lychee's example config (lychee.example.toml on the master branch,
# read on 2026-09-25).
KNOWN_KEYS = {
    "accept",
    "cache",
    "exclude",
    "exclude_all_private",
    "exclude_link_local",
    "exclude_loopback",
    "exclude_path",
    "exclude_private",
    "include_fragments",
    "max_cache_age",
    "max_concurrency",
    "max_redirects",
    "max_retries",
    "no_progress",
    "retry_wait_time",
    "scheme",
    "timeout",
    "user_agent",
}


def load() -> dict[str, object]:
    with CONFIG.open("rb") as f:
        return tomllib.load(f)


def test_config_uses_known_keys() -> None:
    assert set(load()) <= KNOWN_KEYS


def test_patterns_are_valid_regex() -> None:
    config = load()
    for key in ("exclude", "exclude_path"):
        patterns = config[key]
        assert isinstance(patterns, list) and patterns
        for pattern in patterns:
            re.compile(pattern)


def test_linkedin_and_placeholders_skipped_but_real_sites_checked() -> None:
    patterns = [re.compile(p) for p in load()["exclude"]]  # type: ignore[attr-defined]

    def skipped(url: str) -> bool:
        return any(p.search(url) for p in patterns)

    assert skipped("https://www.linkedin.com/in/someone")
    assert skipped("https://example.com/page")
    assert not skipped("https://github.com/Iliya-Valizadeh")
    assert not skipped("https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests")


def test_success_codes_accepted() -> None:
    accept = load()["accept"]
    assert isinstance(accept, str)
    assert [a.strip() for a in accept.split(",")] == ["200..=299", "429"]
