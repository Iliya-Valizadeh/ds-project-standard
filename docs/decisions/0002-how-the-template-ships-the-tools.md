# 0002: How the template ships the tools

Date: 2026-09-25. Status: accepted.

## Context

Every generated repo runs the checks in `tools/` in its own CI. The plan says the
template carries these tools, and that `copier update` keeps all repos in sync. Copier
only copies files from `template/`, but the tools and their tests live in `tools/` and
`tests/` at the root of this repo.

## Options

1. Keep a second copy of each tool in `template/tools/`. Two copies can drift apart.
2. Have each generated repo download the tools from GitHub in CI. CI then needs the
   network for a basic check, and a local run needs the same download.
3. Put a one-line Jinja file in `template/tools/` for each tool, such as
   `{% include 'tools/claims_check.py' %}`. Copier reads templates from the root of
   this repo, so the include pulls in the tested file at render time.

## Decision

Option 3. `tools/` stays the only source. A test renders the template and checks that
each copied tool is byte for byte the same as the one in `tools/`. The same test fails
if a tool ever contains Jinja syntax that the include would change.

## Consequences

- Each generated repo holds its own copy of the tools, so its checks run offline.
- `copier update` in a generated repo brings in new versions of the tools.
- Generated repos leave `tools/` out of ruff, because the code is checked here.
- A generated repo gets its own `tools/README.md`, which says not to edit the tools
  there. This repo's `tools/README.md` describes the tests and the plan, which a
  generated repo does not have.
- `uv.lock` is not in the template, because it depends on the project name. `make
  setup` in a new repo writes it, and CI runs `uv sync --locked`, so CI fails until
  the lockfile is committed.
