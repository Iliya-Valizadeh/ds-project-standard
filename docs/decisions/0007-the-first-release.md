# 0007: The first release

Date: 2026-09-25. Status: accepted.

## Context

The house standard asks every repo for a description that matches the README's first
line, a social preview image of the headline chart, and a `v1.0` tag with notes. This
repo went public without a README, a license file or a changelog. It also lacks a
headline chart, because it has no model result of its own.

The tag matters more here than in other repos. `copier copy` and `copier update` pick
the newest git tag of a template when no `--vcs-ref` is given. So the first tag decides
what every new repo gets.

## Options

1. Tag `main` as it is and set only the GitHub settings.
2. Add a README, the MIT license file that `pyproject.toml` already names, and a
   changelog first, then tag.

For the social preview:

1. Use the worked example's chart. It is a toy on synthetic data, so putting it on the
   repo's card could read as a real result.
2. Use a plain card with the repo name and its one line.

## Decision

Add the README, license and changelog first, set the version in `pyproject.toml` to
1.0.0, and then tag `v1.0` on `main`. Use a plain text card for the social preview.

## Why

A public repo with no README and no license file is hard to judge and unclear to reuse.
The description must match a README line that did not exist. A text card cannot be
mistaken for a result.

## Consequences

- From now on, a template change reaches new repos only after a new tag. Tag each
  release on `main` after CI is green, and add a changelog entry for it.
- The drift check in `scripts/example.py` and the template tests pass
  `vcs_ref="HEAD"`, so they keep testing the working copy, not the last tag.
- `docs/img/social-preview.png` has to be uploaded by hand in the repo settings. The
  GitHub API has no way to set it.
