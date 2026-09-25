# 0003: The worked example inside the template

Date: 2026-09-25. Status: accepted.

## Context

The template needs a small example that runs from end to end, so a new repo passes
`make all` on its first day and `examples/` has real output to test. The example must
need no downloads and no keys. Every number it writes must come from running the code.

## Options

1. Keep empty placeholders. A new repo then has no working `make eval`, and nothing
   proves that the chart and `reports/metrics.json` steps work.
2. Use a public dataset. That needs a download, which breaks the `make demo` rule.
3. Make a seeded synthetic regression problem. Fit a baseline that predicts the
   training mean and a least squares linear model. Report mean absolute error with a
   percentile bootstrap interval, plus the gap between the two with a paired bootstrap.

## Decision

Option 3, with numpy and matplotlib as the only runtime packages. scikit-learn was
left out, because numpy's least squares solver is enough here and keeps installs small.

The rendered `reports/metrics.json` and `reports/figures/mae_by_model.png` are
committed in the template. They came from running `python -m <package>.evaluate` in a
freshly rendered project. A test in each generated repo runs the evaluation again and
fails if the committed metrics differ by more than the rounding step (0.0001).

## Consequences

- A new repo starts with real, reproducible numbers and one chart. They describe
  made-up data, so the `about` field in metrics.json says to replace them.
- The example is easy on purpose: the data comes from a linear rule, so the linear
  model is the right shape. It shows the workflow, and says nothing about real data.
- The chart PNG can differ by a few bytes across matplotlib versions. Only the JSON is
  checked for an exact match.
- The docs keep their TODO lines. The example numbers stay out of the README, so a new
  repo does not start with claims about data it does not use.
