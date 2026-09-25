# tools

Checks that keep every repo in this portfolio honest and easy to read.

## In plain words

These small programs read the text files in a project. Each one looks for one kind of
problem, such as a number with no source or a sentence that is hard to read. If it
finds a problem, it prints where it is and the build stops.

## What each tool checks

| Tool | What it checks | Needs |
|---|---|---|
| `ai_signs_check.py` | Common signs of AI writing: puffery words, em dashes, bold lead-ins, title-case headings | Python only |
| `claims_check.py` | Every number in `CLAIMS.md` matches its source file, and every number in the docs is listed in `CLAIMS.md` | Python only |
| `readability_check.py` | Reading grade of the "In plain words" section and notes, reading grade of the rest, and glossary links on first use | `textstat` |
| `links_check.py` | Links between local files and to sections inside them, with no network access | Python only |
| `lychee.toml` | Settings for lychee, which checks links to other websites | lychee |
| `readme_sections.py` | Writes the README skeleton, checks the section order, and keeps the repo map table up to date | Python only |

The grade limits come from section 3.3 of the portfolio plan. The limits and the
number rules are written at the top of each script, so the script is the single
source for how it works.

## How to run them

From the root of a project:

```bash
uv run python tools/ai_signs_check.py README.md docs
uv run python tools/claims_check.py README.md docs
uv run python tools/readability_check.py --glossary docs/glossary.md README.md docs
uv run python tools/links_check.py README.md docs
uv run python tools/readme_sections.py check README.md
uv run python tools/readme_sections.py repo-map README.md --check
lychee --config tools/lychee.toml './**/*.md'
```

Each command exits with code 0 when there is nothing to fix and code 1 when there is.
Add `--help` to any Python tool to see its options.

## Limits of these checks

- The AI-signs check only finds patterns that a regular expression can find. Lists of
  three used for rhythm and empty praise in new words still need a person to read
  the text.
- The claims check skips small whole numbers (0 to 10) and years, because most are
  counts or dates. A claim such as "7 of 10 cases" needs its own row in `CLAIMS.md`
  anyway, and the check will not remind you.
- A reading grade is a rough guide. Short sentences with long technical words can
  still score high, and simple words can still hide an unclear idea.

## Tests

```bash
uv run pytest
```
