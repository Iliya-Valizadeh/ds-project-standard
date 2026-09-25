# The house standard

DRAFT: Iliya to edit

These are the rules every repo in my portfolio follows. Each rule has one line on why
it exists and a link to where the idea comes from. The template in this repo makes
the files and sets up the checks. Each new repo still has to fill in its own content.

## In plain words

I want anyone to open one of my projects and see in a minute what it does and how
well it works. Every number must come from code that anyone can run again. I write in
short sentences, and I say what is weak before a reader has to find it.

## The README, in this order

The test is simple. A manager who stops reading after "Result" should know what the
project is, whether it works and how well.

| Section | Why | Source |
|---|---|---|
| Title and one line on what it does | Readers decide in seconds whether to keep reading | [Canada.ca][canada] |
| In plain words: three sentences | Many readers are not technical, and all of them are busy | [Canada.ca][canada] |
| Try it: a live link or three commands | A result you can run yourself needs less trust | [Cookiecutter Data Science][ccds] |
| Result: one number, its interval, a simple baseline, one chart | A number means little without a comparison and its likely range | [Rules of ML, rule 1][rules] |
| How I worked: the evaluation plan and its commit hash, the decision records, the error analysis | The commit shows the test was fixed before I saw any results | [Yan][yan], [Husain][evals] |
| How it works: a Mermaid diagram and five lines | Readers need the shape of the system before its details | [Yan][yan] |
| What's weak, ranked by how much each point could change the result | Limits I state myself are more credible than limits a reader finds | [Model cards][cards] |
| Docs, sorted into tutorial, how-to, reference and explanation | Each kind of reader finds the kind of page they need | [Diátaxis][diataxis] |
| Repo map: each folder and what it does | A known layout lets people find things without asking | [Cookiecutter Data Science][ccds] |

## Files every repo has

| File | Why | Source |
|---|---|---|
| `LICENSE` (MIT) | GitHub cannot add a default license, and without one nobody may reuse the code | [GitHub Docs][gh] |
| `CLAIMS.md` | Maps every number in the docs to its source file and the command that makes it | [Cookiecutter Data Science][ccds] |
| `docs/eval_plan.md`, committed before results | I cannot move the goalposts after I see the numbers | [Yan][yan] |
| `docs/decisions/NNNN-*.md` | A later reader sees what I chose, what I rejected and why | [Yan][yan] |
| `docs/whats_weak.md` and `docs/glossary.md` | The full list of limits, and one plain sentence for each technical term | [Model cards][cards], [Canada.ca][canada] |
| Tutorial, how-to, reference and explanation pages | Four kinds of docs, kept apart | [Diátaxis][diataxis] |
| `MODEL_CARD.md` and `DATASHEET.md`, when there is a model or a dataset | Say what the model or data is for, and where it fails | [Mitchell et al.][cards], [Gebru et al.][sheets] |
| `AI_USAGE.md` | Says what I decided and checked, and what the AI assistant wrote | My own rule |
| `CHANGELOG.md`, tied to tags | Readers see what changed between versions | [Keep a Changelog][changelog] |
| `reports/metrics.json` | My profile and site read numbers from this file, so they never drift from the code | My own rule |
| `Makefile`, `pyproject.toml` and a lockfile | One command per step, with pinned packages, so a rerun gives the same numbers | [Cookiecutter Data Science][ccds] |
| CI workflow and pre-commit config | The same checks run on my machine and on GitHub | [Sculley et al.][debt] |
| `docs/ml_test_score.md` | An honest score of how far the project is from production | [Breck et al.][breck] |

## Checks that must pass in CI

| Check | Why | Source |
|---|---|---|
| Every number in `CLAIMS.md` matches the generated output | A number with no source is a claim nobody can check | [Cookiecutter Data Science][ccds] |
| Reading grade 9 or lower for "In plain words" and notes, 12 or lower elsewhere <!-- not-a-claim --> | Plain text reaches readers whose first language is not English | [Canada.ca][canada] |
| Zero flags from the AI-writing signs check | Those patterns make readers stop trusting the text | [Signs of AI writing][wiki] |
| Links work | A dead link makes a project look abandoned | My own rule |
| ruff, mypy, pytest, data tests, and 80% or more coverage of `src/` in new repos <!-- not-a-claim --> | Model code is a small part of a real system, and the rest needs tests too | [Sculley et al.][debt] |
| `make all` regenerates every number, and `make demo` needs no downloads or keys | Anyone can rerun the work from code and raw data | [Cookiecutter Data Science][ccds], [Rules of ML, rule 4][rules] |

## GitHub settings

Each repo gets a description that matches the README's first line and 5 to 8 topics.
It gets a social preview of the headline chart, 1280 by 640 pixels. <!-- not-a-claim -->
It gets a `v1.0` tag with release notes. Issues stay on, with 3 to 6 real next steps
labelled `roadmap`, and Discussions stay off. Why: search results and shared links
show these things before anyone opens the code. Source: [GitHub Docs][gh].

## Writing rules

| Rule | Why | Source |
|---|---|---|
| Say it simply first, then give the term: "how often the right page is in the top five (hit@5)" | The reader understands the idea before learning its name | [Canada.ca][canada] |
| Short sentences, one idea each, active voice, no idioms | Many of my readers do not speak English as a first language | [Canada.ca][canada] |
| Every chart gets one sentence on what to notice | Readers should not have to guess the point of a chart | [Canada.ca][canada] |
| Every number comes with a comparison, an interval where one exists, and a unit | A number alone cannot tell you if it is good | [Rules of ML, rule 1][rules] |
| Never oversell: "points in a direction" is fine, "proves" almost never is | One exposed overclaim costs more trust than any polish gains | [Signs of AI writing][wiki] |
| Leave out puffery, negative parallelism, bold lead-ins, em dashes and padded lists of three | These are known signs of AI writing | [Signs of AI writing][wiki] |

## Sources

- Zinkevich, [Rules of Machine Learning][rules] (Google)
- Sculley et al., [Hidden Technical Debt in Machine Learning Systems][debt] (NeurIPS 2015)
- Breck et al., [The ML Test Score][breck] (Google, 2017)
- Mitchell et al., [Model Cards for Model Reporting][cards] (2019)
- Gebru et al., [Datasheets for Datasets][sheets] (2018)
- DrivenData, [Cookiecutter Data Science opinions][ccds]
- Procida, [Diátaxis][diataxis]
- Eugene Yan, [How to Write Design Docs for ML Systems][yan]
- Hamel Husain, [Your AI Product Needs Evals][evals]
- [Canada.ca Content Style Guide][canada]
- [GitHub Docs on default community health files][gh]
- [Keep a Changelog][changelog]
- Wikipedia, [Signs of AI writing][wiki]

[rules]: https://developers.google.com/machine-learning/guides/rules-of-ml
[debt]: https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems
[breck]: https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/
[cards]: https://arxiv.org/abs/1810.03993
[sheets]: https://arxiv.org/abs/1803.09010
[ccds]: https://cookiecutter-data-science.drivendata.org/opinions/
[diataxis]: https://diataxis.fr/
[yan]: https://eugeneyan.com/writing/ml-design-docs/
[evals]: https://hamel.dev/blog/posts/evals/
[canada]: https://design.canada.ca/style-guide/
[gh]: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
[changelog]: https://keepachangelog.com/en/1.1.0/
[wiki]: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
