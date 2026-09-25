# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and each release matches a
git tag.

## [Unreleased]

## [1.0] - 2026-09-25

The first release. `copier copy` without `--vcs-ref` now uses this tag.

### Added

- Checks in `tools/`: AI-writing signs, claims, readability, local links, README
  sections, and a lychee config for web links, each with tests.
- A Copier template in `template/` with every file the house standard asks for,
  including CI, docs, a decision record folder and an ML Test Score page.
- A worked example on synthetic data: a mean baseline against a linear model, with
  bootstrap intervals and one chart.
- `STANDARD.md`, the house rules on one page (draft for Iliya to edit).
- `examples/example-project/`, rendered from the template and checked for drift in CI.
- CI for this repo: tool tests, the example check with a fresh evaluation, the
  example's own gates, and a web link check.
- A README, an MIT license file and this changelog.

[Unreleased]: https://github.com/Iliya-Valizadeh/ds-project-standard/compare/v1.0...HEAD
[1.0]: https://github.com/Iliya-Valizadeh/ds-project-standard/releases/tag/v1.0
