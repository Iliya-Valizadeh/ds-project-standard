"""Keep examples/example-project equal to what the template makes today.

    python scripts/example.py write        # render the template into examples/
    python scripts/example.py check        # render to a temp folder, fail on any difference
    python scripts/example.py check --eval # also rerun the evaluation, compare metrics.json

`check` exits 1 when the committed example has drifted from the template, so CI can
catch a template change that was not regenerated, or a hand edit inside examples/.
`--eval` needs uv and a network connection, because it installs the example's
packages into a throwaway environment.
"""

from __future__ import annotations

import argparse
import difflib
import shutil
import subprocess
import tempfile
from pathlib import Path

from copier import run_copy

REPO = Path(__file__).resolve().parent.parent
EXAMPLE = REPO / "examples" / "example-project"
PACKAGE = "example_project"
ANSWERS_FILE = ".copier-answers.yml"
# Only answers that differ from the copier.yml defaults, plus the year, which would
# otherwise change every January.
ANSWERS: dict[str, object] = {
    "project_name": "example-project",
    "one_line": "An example repo made from the ds-project-standard template.",
    "copyright_year": 2026,
}
# Copier writes the local template path in the answers file. The public source is the
# same template and does not leak a path from one machine. Copier also writes `_commit`,
# the template commit it rendered. With uncommitted edits that is a temporary commit
# that exists nowhere else, and it changes with every commit to this repo, so the
# example leaves it out (see docs/decisions/0005-the-committed-example.md).
PUBLIC_SRC = "gh:Iliya-Valizadeh/ds-project-standard"
# Files that tools make when someone works inside the example. They are not template
# output, so the comparison skips them.
SKIP_PARTS = {
    "__pycache__",
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".lycheecache",
    "htmlcov",
}
SKIP_NAMES = {"uv.lock", ".coverage", "coverage.xml"}


def render(dest: Path) -> Path:
    """Render the template at this repo's HEAD (plus any uncommitted edits) into dest."""
    run_copy(
        str(REPO),
        dest,
        data=ANSWERS,
        defaults=True,
        vcs_ref="HEAD",
        quiet=True,
        unsafe=False,
        # Skip the template's `uv lock` task (see docs/decisions/0006). The example
        # intentionally has no uv.lock (decision 0005), and the plain `check` command
        # needs neither uv nor a network connection.
        skip_tasks=True,
    )
    answers = dest / ANSWERS_FILE
    lines = answers.read_text(encoding="utf-8").splitlines()
    fixed = [
        f"_src_path: {PUBLIC_SRC}" if ln.startswith("_src_path:") else ln
        for ln in lines
        if not ln.startswith("_commit:")
    ]
    answers.write_text("\n".join(fixed) + "\n", encoding="utf-8", newline="\n")
    return dest


def files_under(root: Path) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if not path.is_file() or SKIP_PARTS.intersection(rel.parts) or rel.name in SKIP_NAMES:
            continue
        out[rel.as_posix()] = path.read_bytes()
    return out


def diff_trees(expected: Path, actual: Path) -> list[str]:
    """Return one message per difference, with a short unified diff for text files."""
    want, have = files_under(expected), files_under(actual)
    problems: list[str] = []
    for name in sorted(want.keys() - have.keys()):
        problems.append(f"missing from examples/: {name}")
    for name in sorted(have.keys() - want.keys()):
        problems.append(f"not made by the template: {name}")
    for name in sorted(want.keys() & have.keys()):
        if want[name] == have[name]:
            continue
        message = f"differs: {name}"
        try:
            lines = difflib.unified_diff(
                have[name].decode("utf-8").splitlines(),
                want[name].decode("utf-8").splitlines(),
                f"examples/{name}",
                f"template/{name}",
                lineterm="",
            )
            message += "\n" + "\n".join(list(lines)[:40])
        except UnicodeDecodeError:
            message += " (binary)"
        problems.append(message)
    return problems


def write() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        fresh = render(Path(tmp) / "example-project")
        if EXAMPLE.exists():
            shutil.rmtree(EXAMPLE)
        shutil.copytree(fresh, EXAMPLE)
    print(f"Wrote {EXAMPLE.relative_to(REPO).as_posix()}")
    return 0


def rerun_eval(project: Path) -> list[str]:
    """Run the example's evaluation in a fresh environment and compare metrics.json."""
    out = project / "fresh-reports"
    subprocess.run(
        ["uv", "run", "--quiet", "python", "-m", f"{PACKAGE}.evaluate", "--reports-dir", str(out)],
        cwd=project,
        check=True,
    )
    committed = (EXAMPLE / "reports" / "metrics.json").read_bytes()
    if (out / "metrics.json").read_bytes() != committed:
        return ["differs: reports/metrics.json does not match a fresh run of the evaluation"]
    return []


def check(run_eval: bool) -> int:
    if not EXAMPLE.is_dir():
        print(f"FAIL: {EXAMPLE.relative_to(REPO).as_posix()} does not exist.")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        fresh = render(Path(tmp) / "example-project")
        problems = diff_trees(fresh, EXAMPLE)
        if run_eval and not problems:
            problems = rerun_eval(fresh)
    if problems:
        print("FAIL: examples/example-project has drifted from the template.")
        print("\n".join(problems))
        print("Fix: run `python scripts/example.py write` and commit the result.")
        return 1
    extra = " and a fresh evaluation run" if run_eval else ""
    print(f"OK: examples/example-project matches the template{extra}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("write", help="render the template into examples/")
    check_cmd = sub.add_parser("check", help="fail if examples/ differs from a fresh render")
    check_cmd.add_argument("--eval", action="store_true", help="also rerun the evaluation")
    args = parser.parse_args(argv)
    if args.command == "write":
        return write()
    return check(args.eval)


if __name__ == "__main__":
    raise SystemExit(main())
