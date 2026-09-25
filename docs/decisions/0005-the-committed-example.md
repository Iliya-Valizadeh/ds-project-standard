# 0005: The committed example project

Date: 2026-09-25. Status: accepted.

## Context

PORTFOLIO_PLAN.md section 5.1 asks for an example project under `examples/`, made from
the template and tested in CI. It proves that the template works. The example must stay
equal to what the template makes today. If someone changes the template and forgets
the example, or edits the example by hand, a check has to fail.

## Options

1. Render the example in CI only and commit nothing. Readers then have no example to
   browse on GitHub.
2. Commit the rendered example and trust people to update it. It drifts without
   anyone noticing.
3. Commit the rendered example. Add a script that renders the template again into a
   temporary folder and fails on any difference.

## Decision

Option 3. `scripts/example.py write` renders the template into
`examples/example-project`. `scripts/example.py check` renders it again and compares
every file byte for byte. It exits 1 on any difference. `check --eval` also installs the
example's packages and runs its evaluation, then compares `reports/metrics.json` with
the committed file. `tests/test_example.py` runs the plain check with the other tests.

The answers are fixed in the script: the project name `example-project`, one line, and
the year 2026. Every other answer uses the default in `copier.yml`. A change to a
default then shows up as drift, which is what we want.

Two lines in `.copier-answers.yml` are changed after rendering:

- `_src_path` becomes `gh:Iliya-Valizadeh/ds-project-standard`. Copier writes the local
  path, which differs on each machine and would leak a home folder name.
- `_commit` is removed. With uncommitted edits, Copier writes a temporary commit that
  exists nowhere else. It also changes with every commit to this repo.

## Consequences

- The example has no `_commit`, so `copier update` does not work inside it. That is
  fine, because the example is rendered again with `write`, not updated.
- The example has no `uv.lock`. A lockfile would change whenever a package releases a
  new version, and the check would fail for reasons that have nothing to do with the
  template. A real repo still commits its lockfile.
- The check skips caches and virtual environments (`__pycache__`, `.venv`, `uv.lock`
  and similar), so running the example locally does not cause false failures.
- `check --eval` needs uv and a network connection. The plain check needs neither.
