# 0006: The generated repo's lockfile

Date: 2026-09-25. Status: accepted.

## Context

The template's generated CI workflow (`template/.github/workflows/ci.yml.jinja`) runs
`uv sync --locked`, which needs a `uv.lock` that already matches `pyproject.toml`. A
freshly generated repo has no lockfile until someone runs `make setup`. If that repo is
pushed to GitHub before `make setup` has run and its result committed, the very first
CI run fails on a missing lockfile, for a reason that has nothing to do with the new
project's own code.

## Options

1. Have the generated CI run `uv sync` without `--locked`. This always passes, but it
   stops checking that the committed lockfile matches `pyproject.toml`, which is the
   point of `--locked`.
2. Have the generated CI run `uv lock` and then `uv sync --locked`. The second command
   then always passes, because the first command just made it match. This also removes
   the check.
3. Make sure a generated repo already has a correct `uv.lock` the moment `copier copy`
   finishes, so the file exists and matches `pyproject.toml` before the first commit.

## Decision

Option 3. `copier.yml` adds a `_tasks` entry that runs `uv lock` in the new repo right
after Copier writes its files. The generated CI keeps `uv sync --locked` exactly as it
was: a real check that fails if someone edits `pyproject.toml` and forgets to run
`uv lock` again.

`scripts/example.py` renders with `skip_tasks=True`, so this task never runs against
`examples/example-project`. Decision 0005 already ruled that the example commits no
lockfile, and the plain `check` command needs neither `uv` nor a network connection;
running the task there would break both.

`tests/test_template.py` skips the task for its structural checks, to stay fast and
offline, and adds one test, `test_uv_lock_task_writes_lockfile`, that turns the task
back on and checks that `uv sync --locked` passes on the result.

## Consequences

- `copier copy` now needs `uv` on the machine and, the first time, a network
  connection to resolve versions. Both were already needed for `make setup`, so this
  moves a step earlier rather than adding a new requirement.
- `copier update` reruns the task too, so an existing repo's lockfile is refreshed
  whenever the template changes a dependency.
- The one test that exercises the task needs a network connection, marked
  `@pytest.mark.network`. Every other test in the file stays offline.
