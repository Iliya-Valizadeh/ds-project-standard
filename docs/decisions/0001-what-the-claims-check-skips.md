# 0001: What the claims check skips

Date: 2026-09-25. Status: accepted.

## Context

The house rule says every number in a Markdown file traces to a committed script
through `CLAIMS.md`. A check that flags every digit would also flag years, dates,
version numbers, list markers and small counts such as "three commands" or
"5 to 8 topics". A check that flags too much gets ignored or switched off.

## Options

1. Flag every number, and ask authors to mark each non-claim by hand.
2. Skip numbers that are almost never results: years, dates, versions, numbers glued
   to letters (F1, p95, hit@5) and whole numbers from 0 to 10 without a percent sign.
3. Flag only numbers with a decimal point or a percent sign.

## Decision

Option 2. Any line can also opt out with the comment `<!-- not-a-claim -->`.

## Consequences

- Most results (decimals, percentages, large counts) are checked.
- A small whole-number claim such as "7 of 10 cases" is not flagged. It still needs a
  row in `CLAIMS.md`, and a reviewer has to catch it. The tool's docstring and
  `tools/README.md` say this openly.
- If this gap causes a missed claim, lower the limit in `is_claim_like` and record a
  new decision.
