"""Render the Copier template and check the generated project.

These tests prove that the template renders without Jinja errors, that it makes every
file in PORTFOLIO_PLAN.md section 3.2, and that the new project passes its own docs
checks before anyone edits it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from copier import run_copy

REPO = Path(__file__).resolve().parent.parent
TOOLS = [
    "_markdown.py",
    "ai_signs_check.py",
    "claims_check.py",
    "links_check.py",
    "lychee.toml",
    "readability_check.py",
    "readme_sections.py",
]
# Files every generated repo must have (PORTFOLIO_PLAN.md section 3.2). The lockfile is
# written by `make setup` in the new repo, so it is not in this list.
REQUIRED = [
    "README.md",
    "LICENSE",
    "CLAIMS.md",
    "docs/eval_plan.md",
    "docs/decisions/0000-template.md",
    "docs/whats_weak.md",
    "docs/glossary.md",
    "docs/tutorial.md",
    "docs/how-to/run-the-checks.md",
    "docs/reference.md",
    "docs/explanation.md",
    "AI_USAGE.md",
    "CHANGELOG.md",
    "reports/metrics.json",
    "reports/figures/mae_by_model.png",
    "Makefile",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    ".pre-commit-config.yaml",
    ".copier-answers.yml",
    ".gitignore",
    ".gitattributes",
    *[
        f"src/demo_project/{name}.py"
        for name in ("__init__", "data", "models", "metrics", "plots", "evaluate", "demo")
    ],
    "tests/test_pipeline.py",
    *[f"tools/{name}" for name in TOOLS],
]
BASE = {"project_name": "demo-project", "one_line": "Scores a demo dataset and shows its work."}


def render(dest: Path, **answers: Any) -> Path:
    run_copy(
        str(REPO),
        dest,
        data={**BASE, **answers},
        defaults=True,
        vcs_ref="HEAD",
        quiet=True,
        unsafe=False,
    )
    return dest


@pytest.fixture(scope="module")
def project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return render(tmp_path_factory.mktemp("default") / "demo-project")


def doc_paths(root: Path) -> list[str]:
    """The Markdown that `make check-docs` scans, as the Makefile lists it."""
    tops = [
        "README.md",
        "CLAIMS.md",
        "CHANGELOG.md",
        "AI_USAGE.md",
        "MODEL_CARD.md",
        "DATASHEET.md",
    ]
    return [p for p in tops if (root / p).exists()] + ["docs"]


def run_tool(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=root, capture_output=True, text=True, check=False
    )


@pytest.mark.parametrize("name", REQUIRED)
def test_required_file_exists(project: Path, name: str) -> None:
    assert (project / name).is_file(), name


def test_no_template_syntax_left(project: Path) -> None:
    for path in project.rglob("*"):
        if not path.is_file() or path.suffix == ".png":
            continue
        assert path.suffix != ".jinja", path
        text = path.read_text(encoding="utf-8")
        assert "{{" not in text and "{%" not in text, path


@pytest.mark.parametrize("name", TOOLS)
def test_tools_are_exact_copies(project: Path, name: str) -> None:
    assert (project / "tools" / name).read_bytes() == (REPO / "tools" / name).read_bytes()


def test_answers_are_filled_in(project: Path) -> None:
    readme = (project / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("# demo-project\n\nScores a demo dataset and shows its work.\n")
    assert 'name = "demo-project"' in (project / "pyproject.toml").read_text(encoding="utf-8")
    assert "Iliya Valizadeh" in (project / "LICENSE").read_text(encoding="utf-8")
    assert "\tuv sync" in (project / "Makefile").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "args",
    [
        ["tools/ai_signs_check.py"],
        ["tools/claims_check.py"],
        ["tools/readability_check.py", "--glossary", "docs/glossary.md"],
        ["tools/links_check.py"],
    ],
    ids=["ai-signs", "claims", "readability", "links"],
)
def test_docs_checks_pass(project: Path, args: list[str]) -> None:
    result = run_tool(project, *args, *doc_paths(project))
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("args", [["check"], ["repo-map", "--check"]])
def test_readme_checks_pass(project: Path, args: list[str]) -> None:
    cmd, *flags = args
    result = run_tool(project, "tools/readme_sections.py", cmd, "README.md", *flags)
    assert result.returncode == 0, result.stdout + result.stderr


def test_model_and_dataset_files_follow_answers(tmp_path: Path) -> None:
    root = render(tmp_path / "data-project", has_model=False, has_dataset=True)
    assert not (root / "MODEL_CARD.md").exists()
    assert (root / "DATASHEET.md").is_file()
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "DATASHEET.md" in readme and "MODEL_CARD.md" not in readme
    result = run_tool(root, "tools/links_check.py", *doc_paths(root))
    assert result.returncode == 0, result.stdout + result.stderr


def test_bad_project_name_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        render(tmp_path / "bad", project_name="Bad Name")
