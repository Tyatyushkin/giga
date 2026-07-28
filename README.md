# E2E Test Case Factory — Qwen Code project

Three subagents in a loop turn product requirements into connected end-to-end test suites in the
mandatory Russian format: an analyst finds the journeys, a QA designer writes the cases, a critic
compares them back against the requirements and sends fixes until nothing blocking is left.

```
input/requirements/*.md
        │
        ▼
[requirements-analyst] ──► output/suites/J01-….md        journeys, stages, state transitions, gaps
        │
        ▼
[qa-designer] ──────────► output/cases/J01-…/TC-J01-00.md + .json
        │
        ▼
[test-critic] ──────────► output/reviews/J01-…-iter1.md   BLOCKER / MAJOR / MINOR + fix list
        │
        ├── blockers > 0 and iteration < 3 ──► back to qa-designer with the review
        └── blockers = 0 ──────────────────► output/report.md
```

## Requirements

- Gigacode
- Python 3.9+ for the linter (standard library only)

## Quick start

```bash
cd zvuk-e2e-agents
gigacode                       # start the CLI in the project root
/agents                    # confirm the three project subagents are loaded
/e2e:run                   # full loop over input/requirements/*.md
```

Put your own requirements into `input/requirements/` and delete the sample.

## Commands

| Command | What it does |
|---|---|
| `/e2e:run [path] [--max N] [--journey J01] [--yes]` | Full loop: analyse → design → review → fix → report |
| `/e2e:analyze [path]` | Journey plans only |
| `/e2e:design J01 [review-path]` | Test cases for one journey, or a fix iteration |
| `/e2e:review J01 [N]` | Review only, produces the fix list and verdict |
| `/e2e:status` | Current artefacts, last verdict, open questions, linter output |

The loop pauses after analysis for your confirmation unless you pass `--yes`.

## Layout

```
.qwen/agents/         requirements-analyst.md, qa-designer.md, test-critic.md
.qwen/commands/e2e/   run.md, analyze.md, design.md, review.md, status.md
QWEN.md               project context loaded into every session
docs/                 format.md, quality-criteria.md, critic-rubric.md, examples.md
templates/            suite-plan.md, test-case.md, test-case.json, review-report.md
input/requirements/   your source requirements (sample «Звук» included)
output/               suites/, cases/, reviews/, state.json, report.md
scripts/              validate_cases.py — deterministic linter
examples/             a fully worked journey plan + case, useful as a reference and smoke test
```

## The linter

The critic runs it before any semantic review, so structural defects never consume model attention:

```bash
python3 scripts/validate_cases.py output/cases
python3 scripts/validate_cases.py examples/J01-onboarding-first-play --json /tmp/lint.json
```

It flags as **BLOCKER**: missing or empty mandatory sections, placeholder values, broken step
numbering, vague expected results («успешно», «корректно», «работает»…), main-path cases shorter
than 8 steps, cases whose steps never touch their own test data, Markdown/JSON divergence.
As **MAJOR**: non-atomic steps, unused test data, weak state continuity across the second half of a
scenario, variant cases not linked to their main case, missing JSON.
Exit code 1 means blockers are present.

## Design decisions

- **Journeys, not features.** The analyst is forbidden from producing single-area paths; a journey
  crosses at least three functional areas and carries data from early stages into late ones. This is
  the part a plain agent gets wrong most often — it produces a pile of atomic checks instead.
- **Blocker list is closed.** Invented behaviour and vague results are blockers; everything else is
  advisory. That keeps the loop from spinning on taste disagreements.
- **Requirements are the only source of truth.** Silence in the requirements produces a gap and a
  question, never a plausible-sounding expected result.
- **Files, not context.** Agents hand off through disk, so context loss between iterations cannot
  silently drop a stage.
- **Domain-free templates.** «Звук» exists only in `input/requirements/`. Point the project at other
  requirements and nothing else changes.

## Adapting to another product

1. Replace `input/requirements/`.
2. If the target team's case format differs, edit `docs/format.md`, `templates/test-case.md` and the
   section list at the top of `scripts/validate_cases.py` — the agents read the contract, they do not
   hardcode it.
3. Nothing in `.qwen/agents/` needs to change.
