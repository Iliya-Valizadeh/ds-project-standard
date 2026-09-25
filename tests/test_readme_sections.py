from pathlib import Path

import pytest

import ai_signs_check
import readme_sections as rs


def test_skeleton_passes_its_own_check_and_ai_signs() -> None:
    text = rs.skeleton(
        "fraud-review-queue", "Ranks card payments so reviewers see risky ones first."
    )
    assert rs.check_readme(text) == []
    assert ai_signs_check.check_text(text) == []
    headings = [line[3:] for line in text.splitlines() if line.startswith("## ")]
    assert headings == rs.SECTIONS


def test_check_finds_missing_and_out_of_order() -> None:
    text = "# Title\n\nOne line.\n\n" + "".join(
        f"## {name}\n\ntext\n\n" for name in rs.SECTIONS if name != "Docs"
    )
    assert rs.check_readme(text) == ["missing section: ## Docs"]
    swapped = text.replace("## Try it", "## TMP").replace("## Result", "## Try it")
    swapped = swapped.replace("## TMP", "## Result")
    assert "section out of order: ## Result" in rs.check_readme(swapped)


def test_check_needs_title_and_one_line() -> None:
    body = "".join(f"## {name}\n\ntext\n\n" for name in rs.SECTIONS)
    assert rs.check_readme("Intro text.\n\n" + body)[0].startswith("the first line must be")
    assert rs.check_readme("# Title\n\n" + body) == [
        "the title must be followed by a one-line summary"
    ]


def test_check_allows_extra_sections_and_curly_apostrophe() -> None:
    names = [n.replace("'", "’") for n in rs.SECTIONS]
    names.insert(3, "Limits of the data")
    text = "# T\n\nOne line.\n\n" + "".join(f"## {n}\n\nx\n\n" for n in names)
    assert rs.check_readme(text) == []


def make_repo(root: Path) -> None:
    for name in ("src", "tests", "docs", ".github", ".git", "mystery", "__pycache__"):
        (root / name).mkdir()
    (root / "CLAIMS.md").write_text("x", encoding="utf-8")
    (root / "notes.txt").write_text("x", encoding="utf-8")


def test_repo_map_lists_real_folders(tmp_path: Path) -> None:
    make_repo(tmp_path)
    text = rs.skeleton("t", "One line.")
    new = rs.update_repo_map(text, tmp_path)
    table = new[new.find(rs.MAP_START) : new.find(rs.MAP_END)]
    assert "| `.github/` | CI workflows" in table
    assert "| `mystery/` | TODO: describe |" in table
    assert "| `CLAIMS.md` |" in table
    for skipped in (".git/", "__pycache__", "notes.txt"):
        assert skipped not in table
    assert rs.update_repo_map(new, tmp_path) == new  # running twice changes nothing


def test_repo_map_keeps_hand_written_descriptions(tmp_path: Path) -> None:
    make_repo(tmp_path)
    new = rs.update_repo_map(rs.skeleton("t", "One line."), tmp_path)
    edited = new.replace("| `mystery/` | TODO: describe |", "| `mystery/` | Odd bits |")
    (tmp_path / "extra").mkdir()
    again = rs.update_repo_map(edited, tmp_path)
    assert "| `mystery/` | Odd bits |" in again
    assert "| `extra/` | TODO: describe |" in again


def test_repo_map_needs_markers(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="markers"):
        rs.update_repo_map("# T\n", tmp_path)


def test_cli_new_check_and_repo_map(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    readme = tmp_path / "README.md"
    args = ["new", "--title", "t", "--one-line", "One line.", "--out", str(readme)]
    assert rs.main(args) == 0
    assert rs.main(args) == 1  # will not overwrite
    assert rs.main(args + ["--force"]) == 0
    assert rs.main(["check", str(readme)]) == 0
    (tmp_path / "src").mkdir()
    assert rs.main(["repo-map", str(readme), "--check"]) == 1  # out of date
    assert rs.main(["repo-map", str(readme)]) == 0
    assert rs.main(["repo-map", str(readme), "--check"]) == 0
    (tmp_path / "mystery").mkdir()
    rs.main(["repo-map", str(readme)])
    assert rs.main(["repo-map", str(readme), "--check"]) == 1  # a TODO row remains
    readme.write_text("# T\n", encoding="utf-8")
    assert rs.main(["check", str(readme)]) == 1
    assert rs.main(["repo-map", str(readme)]) == 1
    capsys.readouterr()


def test_cli_new_prints(capsys: pytest.CaptureFixture[str]) -> None:
    assert rs.main(["new", "--title", "t", "--one-line", "One line."]) == 0
    assert capsys.readouterr().out.startswith("# t\n\nOne line.\n")
