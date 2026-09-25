import json
from decimal import Decimal
from pathlib import Path

import pytest

import claims_check as cc

CLAIMS = """# Claims

| Claim | Value | Source | Command |
|---|---|---|---|
| Test AUC | 0.58 (0.55 to 0.61) | `reports/metrics.json#auc` | `make eval` |
| Rows | 12,345 | `reports/metrics.json#rows` | `make eval` |
| Recall | 71% | `reports/metrics.json#recall` | `make eval` |
| Lift | 2.4 | `reports/eval.txt` | `make eval` |
"""


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "reports").mkdir()
    metrics = {
        "auc": {"value": 0.5812, "ci_low": 0.5489, "ci_high": 0.6071},
        "rows": 12345,
        "recall": 0.7093,
        "flag": True,
    }
    (tmp_path / "reports" / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    (tmp_path / "reports" / "eval.txt").write_text("lift at 5%: 2.41\n", encoding="utf-8")
    (tmp_path / "CLAIMS.md").write_text(CLAIMS, encoding="utf-8")
    return tmp_path


def write(path: Path, text: str) -> str:
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_numbers_found_and_filtered() -> None:
    text = (
        "AUC is 0.58, against 0.50 for a coin flip, on 12,345 rows.\n"
        "Recall is 71%. We ran 3 folds in 2026 on 2026-09-25.\n"
        "Uses Python 3.11.2, v1.0, F1, hit@5, top-20 and p95.\n"
        "1. First step\n"
        "Run `make eval 0.99` or see [the page](docs/42.md).\n"
        "Speed-up of 15 over the old job. <!-- not-a-claim -->\n"
        "```\n77.7\n```\n"
    )
    found = [(n, num.text) for n, num in cc.prose_numbers(text)]
    assert found == [(1, "0.58"), (1, "0.50"), (1, "12,345"), (2, "71%")]


def test_number_forms_and_rounding() -> None:
    pct = cc.parse_numbers("58%")[0]
    assert Decimal("0.58") in pct.forms()
    assert cc.matches(pct, Decimal("0.5812"))
    assert cc.matches(pct, Decimal("58.2"))
    two = cc.parse_numbers("0.12")[0]
    assert cc.matches(two, Decimal("0.125"))  # half-even rounding, as Python prints it
    assert cc.matches(cc.parse_numbers("0.13")[0], Decimal("0.125"))  # half-up
    assert not cc.matches(two, Decimal("0.14"))


def test_all_claims_match_sources(repo: Path) -> None:
    readme = write(
        repo / "README.md", "AUC is 0.58 (0.55 to 0.61) on 12,345 rows. Recall is 71%, lift 2.4.\n"
    )
    assert cc.run(repo / "CLAIMS.md", None, [readme]) == []
    assert cc.main(["--claims", str(repo / "CLAIMS.md"), readme]) == 0


def test_number_missing_from_claims_fails(repo: Path) -> None:
    readme = write(repo / "README.md", "Precision is 0.44.\n")
    errors = cc.run(repo / "CLAIMS.md", None, [readme])
    assert len(errors) == 1
    assert errors[0].endswith("README.md:1: 0.44 is not in CLAIMS.md")


def test_percent_in_docs_matches_fraction_in_claims(repo: Path) -> None:
    readme = write(repo / "README.md", "The AUC was 58% on the test split.\n")
    assert cc.run(repo / "CLAIMS.md", None, [readme]) == []


def test_claim_not_in_source_fails(repo: Path) -> None:
    bad = CLAIMS.replace("| 71% |", "| 75% |")
    write(repo / "CLAIMS.md", bad)
    errors = cc.run(repo / "CLAIMS.md", None, [])
    assert errors == ["CLAIMS.md line 7: 75% not found in reports/metrics.json#recall"]


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("| X | 0.1 | `reports/missing.json` | `make eval` |", "source file not found"),
        ("| X | 0.1 | `reports/metrics.json#nope` | `make eval` |", "key 'nope' not found"),
        ("| X | 2.4 | `reports/eval.txt#k` | `make eval` |", "only works for JSON"),
        ("| X | 0.1 | `reports/metrics.json` |  |", "needs a Source and a Command"),
        ("| X | none | `reports/metrics.json` | `make eval` |", "no number in Value"),
    ],
)
def test_bad_rows_fail(repo: Path, row: str, message: str) -> None:
    write(
        repo / "CLAIMS.md", "| Claim | Value | Source | Command |\n|---|---|---|---|\n" + row + "\n"
    )
    errors = cc.run(repo / "CLAIMS.md", None, [])
    assert len(errors) == 1 and message in errors[0]


def test_json_list_index_and_whole_file(repo: Path) -> None:
    (repo / "reports" / "folds.json").write_text('{"auc": [0.61, 0.57]}', encoding="utf-8")
    write(
        repo / "CLAIMS.md",
        "| Claim | Value | Source | Command |\n|---|---|---|---|\n"
        "| Fold 2 | 0.57 | reports/folds.json#auc.1 | make eval |\n"
        "| Any fold | 0.61 | reports/folds.json | make eval |\n",
    )
    assert cc.run(repo / "CLAIMS.md", None, []) == []


def test_table_without_command_column_fails(repo: Path) -> None:
    write(repo / "CLAIMS.md", "| Value | Source |\n|---|---|\n| 0.58 | reports/metrics.json |\n")
    errors = cc.run(repo / "CLAIMS.md", None, [])
    assert errors and "no column(s): command" in errors[0]


def test_other_tables_are_ignored(repo: Path) -> None:
    text = CLAIMS + "\n| Name | Note |\n|---|---|\n| a | b |\n"
    write(repo / "CLAIMS.md", text)
    assert cc.run(repo / "CLAIMS.md", None, []) == []


def test_missing_claims_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cc.main(["--claims", str(tmp_path / "CLAIMS.md")]) == 1
    assert "not found" in capsys.readouterr().out


def test_claims_file_is_not_scanned_for_coverage(repo: Path) -> None:
    assert cc.run(repo / "CLAIMS.md", None, [str(repo)]) == []
