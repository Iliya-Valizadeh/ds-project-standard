"""The committed example must equal a fresh render of the template."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parent.parent


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("example_script", REPO / "scripts/example.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_committed_example_matches_template() -> None:
    assert load_script().check(run_eval=False) == 0


def test_diff_finds_hand_edits_and_extra_files(tmp_path: Path) -> None:
    script = load_script()
    fresh = script.render(tmp_path / "fresh")
    edited = tmp_path / "edited"
    script.shutil.copytree(fresh, edited)
    assert script.diff_trees(fresh, edited) == []

    (edited / "README.md").write_text("changed\n", encoding="utf-8")
    (edited / "extra.txt").write_text("x\n", encoding="utf-8")
    (edited / "LICENSE").unlink()
    (edited / "src" / "__pycache__").mkdir()
    (edited / "src" / "__pycache__" / "x.pyc").write_bytes(b"\0")
    problems = script.diff_trees(fresh, edited)
    assert [p.splitlines()[0] for p in problems] == [
        "missing from examples/: LICENSE",
        "not made by the template: extra.txt",
        "differs: README.md",
    ]


@pytest.mark.parametrize("line", ["_commit:", "C:\\", "/tmp/"])
def test_answers_file_has_no_machine_details(line: str) -> None:
    answers = (REPO / "examples/example-project/.copier-answers.yml").read_text(encoding="utf-8")
    assert line not in answers
