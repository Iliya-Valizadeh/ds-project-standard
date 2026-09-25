from pathlib import Path

import pytest

import readability_check as rc

REPO = Path(__file__).resolve().parents[1]

EASY = (
    "The model looks at each card payment. It gives the payment a score. "
    "A person checks the payments with the top scores. Most payments are fine. "
    "We count how many bad ones the person finds."
)
HARD = (
    "Notwithstanding considerable methodological heterogeneity, the proposed "
    "probabilistic classification architecture demonstrates substantially improved "
    "discriminative performance characteristics relative to conventional "
    "logistic regression specifications, particularly regarding minority-class "
    "identification under severe distributional imbalance conditions."
)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_clean_prose_drops_markup() -> None:
    lines = [
        "# Title",
        "Some **bold** text with `code` and a [link](http://x.org).",
        "| a | b |",
        "- a list item",
        "- another item",
        "![chart](img.png)",
        "<br>",
    ]
    text = rc.clean_prose(lines)
    assert text == "Some bold text with code and a link. a list item. another item."


def test_split_sections_finds_plain_words() -> None:
    text = f"# T\n\n## In plain words\n\n{EASY}\n\n### Detail\n\nmore\n\n## Result\n\n{HARD}\n"
    plain, rest = rc.split_sections(text)
    assert EASY in plain and "more" in plain
    assert HARD in rest and EASY not in rest


def test_easy_plain_section_passes(tmp_path: Path) -> None:
    f = write(tmp_path / "README.md", f"# T\n\n## In plain words\n\n{EASY}\n\n## Other\n\n{EASY}\n")
    scores = rc.check_file(f, 9, 12, 20, rc.DEFAULT_PLAIN_GLOBS)
    assert [s.label for s in scores] == ["In plain words", "rest of file"]
    assert all(s.ok for s in scores)
    assert rc.main([str(f)]) == 0


def test_hard_plain_section_fails(tmp_path: Path) -> None:
    f = write(tmp_path / "README.md", f"# T\n\n## In plain words\n\n{HARD}\n")
    plain = rc.check_file(f, 9, 12, 20, rc.DEFAULT_PLAIN_GLOBS)[0]
    assert plain.grade is not None and plain.grade > 9 and not plain.ok
    assert rc.main([str(f)]) == 1


def test_hard_rest_fails_at_grade_12(tmp_path: Path) -> None:
    f = write(tmp_path / "docs" / "ref.md", f"# Ref\n\n{HARD}\n")
    assert rc.main([str(f)]) == 1
    assert rc.main(["--max", "60", str(f)]) == 0


def test_notes_must_be_plain_as_a_whole(tmp_path: Path) -> None:
    f = write(tmp_path / "notes" / "week1.md", f"# Week 1\n\n{HARD}\n")
    scores = rc.check_file(f, 9, 60, 20, rc.DEFAULT_PLAIN_GLOBS)
    assert scores[0].label == "whole file (plain)" and not scores[0].ok


def test_short_text_is_skipped(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    f = write(tmp_path / "a.md", "# A\n\nToo short to score.\n")
    assert rc.main([str(f)]) == 0
    assert "skipped" in capsys.readouterr().out


GLOSSARY = "# Glossary\n\n## Baseline\n\nA simple method.\n\n## Area under the curve (AUC)\n\nX.\n"


def test_glossary_terms_parsed(tmp_path: Path) -> None:
    g = write(tmp_path / "docs" / "glossary.md", GLOSSARY)
    assert rc.glossary_terms(g) == ["Baseline", "Area under the curve", "AUC"]


def test_glossary_first_use_linked(tmp_path: Path) -> None:
    g = write(tmp_path / "docs" / "glossary.md", GLOSSARY)
    good = write(
        tmp_path / "README.md",
        "## Result\n\nWe beat the [baseline](docs/glossary.md#baseline). "
        "The baseline is simple. The [AUC](docs/glossary.md#area-under-the-curve-auc) "
        "is shown. Run `baseline` here.\n",
    )
    assert rc.check_glossary_links(good, rc.glossary_terms(g)) == []


def test_glossary_first_use_unlinked_fails(tmp_path: Path) -> None:
    g = write(tmp_path / "docs" / "glossary.md", GLOSSARY)
    bad = write(
        tmp_path / "README.md",
        "## Baseline\n\nThe baseline is simple. See the [baseline](docs/glossary.md).\n"
        "The auc word in lower case is not the term. The AUC is 0.5.\n",
    )
    problems = rc.check_glossary_links(bad, rc.glossary_terms(g))
    assert len(problems) == 2
    assert "README.md:3: first use of 'Baseline'" in problems[0]
    assert "README.md:4: first use of 'AUC'" in problems[1]
    assert rc.main(["--glossary", str(g), "--min-words", "999", str(tmp_path)]) == 1


def test_repo_docs_pass() -> None:
    assert rc.main([str(REPO / "tools" / "README.md")]) == 0
