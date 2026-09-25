# 0004: How repos score the ML Test Score

Date: 2026-09-25. Status: accepted.

## Context

Plan section 5.1 asks each repo to score itself against Breck et al.'s ML Test Score
in `docs/ml_test_score.md`. The paper gives half a point for a test done by hand and
one point for a test that is automated and runs again on every change. This repo is
not on GitHub yet, so CI has never run. The template's worked example is a toy model
with no live service. The claims check flags decimals such as "0.5" that have no row
in `CLAIMS.md`.

## Options

1. Give a full point to any test that CI is set up to run, even before CI has run.
2. Give a full point only after CI has run the test on GitHub. Until then, a passing
   test run by hand earns half a point.
3. Mark serving and monitoring tests as "not applicable" and leave them out of the
   total.

## Decision

Option 2. Tests that do not apply still score none, as the paper does, so the overall
score stays zero until a project has monitoring. Scores are written as words ("none",
"half a point") because they are judgments against a rubric, not measured results.
The template ships its own copy of the page, scored for the worked example, with a
TODO to raise the scores once CI passes.

## Consequences

- The score is low today: five tests at half a point, and zero overall.
- The score cannot rise without evidence a reader can check, such as a CI run.
- Each new repo must score itself again when it replaces the worked example. The
  page says so at the top.
