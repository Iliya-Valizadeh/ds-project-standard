from pathlib import Path

import pytest

import links_check as lc
from _markdown import anchors, github_slug


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("heading", "slug"),
    [
        ("What's weak", "whats-weak"),
        ("How I worked", "how-i-worked"),
        ("Docs (Diátaxis)", "docs-diátaxis"),
        ("Using `make demo`", "using-make-demo"),
        ("Step 1: set up", "step-1-set-up"),
    ],
)
def test_github_slug(heading: str, slug: str) -> None:
    assert github_slug(heading) == slug


def test_anchors_number_repeats_and_read_ids() -> None:
    text = '# Notes\n## Notes\n<a id="custom"></a>\n```\n# not a heading\n```\n'
    assert anchors(text) == {"notes", "notes-1", "custom"}


def test_extract_links_kinds() -> None:
    text = (
        'See [a](docs/a.md) and ![img](img/x.png "title").\n'
        "[ref]: docs/ref.md\n"
        '<img src="img/y.png"> and `[not](a-link.md)`\n'
        "```\n[skip](nope.md)\n```\n"
    )
    assert [t for _, t in lc.extract_links(text)] == [
        "docs/a.md",
        "img/x.png",
        "docs/ref.md",
        "img/y.png",
    ]


def test_good_links_pass(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "guide.md", "# Guide\n\n## Set up\n")
    write(tmp_path / "docs" / "img" / "chart.png", "")
    readme = write(
        tmp_path / "README.md",
        (
            "# Top\n\n## Try it\n\n"
            "[guide](docs/guide.md#set-up), [folder](docs/), [chart](docs/img/chart.png),\n"
            "[here](#try-it), [root](/docs/guide.md), [web](https://example.com/x),\n"
            "[mail](mailto:a@b.c), [spaced](docs/guide.md?plain=1).\n"
        ),
    )
    assert lc.check([str(readme)], tmp_path) == []
    assert lc.main(["--root", str(tmp_path), str(readme)]) == 0


def test_broken_links_fail(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(tmp_path / "docs" / "guide.md", "# Guide\n")
    readme = write(
        tmp_path / "README.md",
        ("[a](docs/missing.md)\n[b](docs/guide.md#no-such-part)\n[c](#nowhere)\n"),
    )
    problems = lc.check([str(tmp_path)], tmp_path)
    assert len(problems) == 3
    assert problems[0].endswith("README.md:1: missing file: docs/missing.md")
    assert "missing section: docs/guide.md#no-such-part" in problems[1]
    assert "missing section: #nowhere" in problems[2]
    assert lc.main(["--root", str(tmp_path), str(readme)]) == 1
    assert "3 broken link(s)" in capsys.readouterr().out
