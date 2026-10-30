# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and each release matches a
git tag.

## [Unreleased]

## [1.1] - 2026-10-29

### Removed

- `AI_USAGE.md` from the standard, the template and the example. New repos no longer
  get it, and `make check-docs` no longer lists it.

### Changed

- The template and the example tell GitHub to leave the Makefile out of the language
  bar (`.gitattributes`).
- The docs, CI step names and the repo map call `ai_signs_check.py` the writing-style
  check.

## [1.0] - 2026-09-25

The first release. `copier copy` without `--vcs-ref` now uses this tag.

### Added

- Checks in `tools/`: writing style, claims, readability, local links, README
  sections, and a lychee config for web links, each with tests.
- A Copier template in `template/` with every file the house standard asks for,
  including CI, docs, a decision record folder and an ML Test Score page.
- A worked example on synthetic data: a mean baseline against a linear model, with
  bootstrap intervals and one chart.
- `STANDARD.md`, the house rules on one page (a draft I still have to edit).
- `examples/example-project/`, rendered from the template and checked for drift in CI.
- CI for this repo: tool tests, the example check with a fresh evaluation, the
  example's own gates, and a web link check.
- A README, an MIT license file and this changelog.
