from pathlib import Path

import pytest

import writing_style_check as ws

REPO = Path(__file__).resolve().parents[1]


def names(text: str) -> list[str]:
    return [name for _, name, _ in ws.check_text(text)]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("We leverage a robust model.", "puffery word"),
        ("This is a key finding.", "key as adjective"),
        ("The table serves as a guide.", "copula avoidance"),
        ("It is not just fast but also cheap.", "negative parallelism"),
        ("The score rose, highlighting the gain.", "superficial -ing tail"),
        ("Experts say this works.", "weasel attribution"),
        ("Overall, the model works.", "didactic / summary"),
        ("Certainly! Here it is.", "chatty address"),
        ("Fraud is associated with night hours.", "vague association"),
        ("The model — a tree — works.", "em dash"),
        ("He said “yes”.", "curly quote"),
        ("Done ✅", "emoji"),
        ("---", "thematic break"),
        ("- **Speed:** fast", "inline-header list item"),
        ("**Note** this is bold.", "bold lead-in paragraph"),
        ("## Model Training Results", "title-case heading"),
    ],
)
def test_flags_each_sign(text: str, expected: str) -> None:
    assert expected in names(text)


def test_plain_text_has_no_flags() -> None:
    text = (
        "# Fraud review queue\n\n"
        "## How it works\n\n"
        "The model ranks card payments by risk. A person reviews the top 100 each day.\n"
        "- Speed: the queue updates every hour.\n"
    )
    assert ws.check_text(text) == []


def test_code_links_and_comments_are_skipped() -> None:
    text = (
        "Run `robust_fit()` first.\n"
        "See [the notes](https://example.com/landscape-report).\n"
        "<!-- a robust comment -->\n"
        "```python\n"
        "x = 'leverage'  # —\n"
        "```\n"
        "~~~\n"
        "robust\n"
        "~~~\n"
    )
    assert ws.check_text(text) == []


def test_front_matter_is_skipped() -> None:
    assert ws.check_text("---\ntitle: A Robust Title\n---\n\nPlain text.\n") == []


def test_line_numbers_match_the_file() -> None:
    hits = ws.check_text("Line one.\n\nWe delve into it.\n")
    assert hits == [(3, "puffery word", "delve")]


def test_main_exit_codes_and_folders(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = tmp_path / "good.md"
    good.write_text("The model ranks payments by risk.\n", encoding="utf-8")
    assert ws.main([str(good)]) == 0
    bad = tmp_path / "sub" / "bad.md"
    bad.parent.mkdir()
    bad.write_text("A seamless and **bold** flow.\n", encoding="utf-8")
    assert ws.main([str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "bad.md: 1 flags, 1 bold spans" in out
    assert ws.main([]) == 2


def test_repo_docs_pass() -> None:
    assert ws.main([str(REPO / "tools" / "README.md")]) == 0
