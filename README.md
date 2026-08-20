# E2E Test Case Factory — Gigacode project

Three subagents turn product requirements into connected end-to-end test suites in the mandatory
Russian format: an analyst finds the journeys, then one design→review loop per journey runs — several
of them **in parallel**, as many as you choose — until nothing blocking is left. You are asked twice
about what the requirements do not say: before any case is written, and before the report.

```
input/requirements/*.md
        │
        ▼
[requirements-analyst] ──► output/suites/J01-….md + _index.json   journeys, stages, gaps
        │
        ▼
  ❓ requirements gate — you see every uncovered REQ, gap and blocking question,
     and choose how many loops run in parallel and what one loop owns
        │
        ├──────────────────┬──────────────────┐   P concurrent loops, one journey each
        ▼                  ▼                  ▼
[qa-designer J01]   [qa-designer J02]   [qa-designer J03]  ──► output/cases/J0N-…/
        ▼                  ▼                  ▼
[test-critic J01]   [test-critic J02]   [test-critic J03]  ──► output/reviews/, output/state/J0N.json
        │                  │                  │
        ├── blockers > 0 and iteration < 3 ──► back to that journey's designer
        └── blockers = 0 ──────────────────► that journey is done, the rest keep going
        │
        ▼
  ❓ [optional] pytest generation — orchestrator asks if you want pytest tests
        │
        ├── yes ──► pytest-stub-writer per PASS journey → output/tests/<J>/
        └── no  ──► continue to coverage gate
        │
        ▼
  ❓ coverage gate — requirements no case checks, questions still open
        │
        ▼
   output/report.md
```

## Requirements

- Gigacode CLI (subagents + Markdown custom commands)
- Python 3.9+ for the linter (standard library only)

## Quick start

```bash
cd zvuk-e2e-agents
gigacode                       # start the CLI in the project root
/agents                    # confirm the five project subagents are loaded
/e2e:run                   # full loop over input/requirements/*.md
```

Put your own requirements into `input/requirements/` and delete the sample.

## Commands

| Command | What it does |
|---|---|
| `/e2e:run [path] [--max N] [--parallel N] [--unit journey\|area] [--journey J01] [--yes] [--no-ask] [--generate-pytest]` | Full run: analyse → parallel design/review loops → [optional pytest generation] → report |
| `/e2e:analyze [path]` | Journey plans only, then the gap report and the gap question |
| `/e2e:design J01 [J02 …] [review-path]` | Test cases; several journey ids run in parallel |
| `/e2e:review J01 [J02 …] [N]` | Review only, one critic per journey, in parallel |
| `/e2e:status` | Current artefacts, per-journey verdicts, open questions, linter output |
| `/e2e:profile <log dir>` | Where a finished run spent its tokens and turns, and which requests failed, truncated or returned nothing |

## Parallel loops

The analyst runs once — journeys can only be found by looking at all the requirements at once. After
that, each journey gets its own designer→critic loop, and the loops run concurrently.

You decide how many. `/e2e:run` asks:

- **how many parallel loops** — 1, 2, 3, or one per journey (`--parallel N` answers it in advance)
- **what one loop owns** — one journey, or one functional area with its journeys done in sequence
  (`--unit journey|area`)

A loop is exclusive: it reads and writes only its own journey's suite plan, case directory, reviews
and `output/state/<JOURNEY_ID>.json`. Nothing is shared, so nothing races — the orchestrator alone
writes the aggregate `output/state.json`. Journeys finish independently: one hitting `NEEDS_HUMAN`
after three iterations does not hold up the others.

## Being asked about missing requirements

Silence in the requirements is the failure mode this project is built around, so it is escalated to
you rather than absorbed:

- **After analysis** you get the full lists — uncovered `REQ-XX`, contradictions and ambiguities with
  the conflicting text quoted, blocking questions ordered by how many stages they block, stages with
  no requirement anchor, and journeys whose shape looks like a grouping mistake. Items, never counts.
  You choose: proceed and record the gaps, answer the questions now, or stop and fix the requirements.
- **Answering now** writes `input/requirements/_answers.md` and re-runs the analyst with it. From
  that point every agent treats your answers as requirements, so a case built on them is no longer
  "invented behaviour".
- **After the loops** you get what the run could not settle — requirements no case checks, questions
  still open, journeys needing a human — and can answer and re-run just those journeys.

`--yes` skips only the go/no-go pause. `--no-ask` makes the run fully autonomous and accumulates
every question it would have asked in `output/pending.md`; the final phase folds that file into
`output/report.md` under «Требуются решения человека».

## Layout

```
.gigacode/agents/       requirements-analyst.md, qa-designer.md, test-critic.md,
                        pytest-stub-writer.md, browser-test-writer.md
.gigacode/commands/e2e/ run.md, analyze.md, design.md, review.md, status.md
.gigacode/skills/       human-gate.md, subagent-briefing.md, requirements-gate.md,
                        journey-pipeline.md, pytest-generation.md — procedures shared by
                        several commands, inlined with
                        `!{python3 scripts/include_skill.py <name> --level N}`
conftest.py             registers the J<NN> journey markers from output/tests/ dirs
GIGACODE.md             project context loaded into every session
.gigacode/skills/       procedure skills as flat .md, injected by include_skill.py;
                        capability skills as directories with SKILL.md (sbertrack-tms-importer)
docs/                   format.md, quality-criteria.md, critic-rubric.md, examples.md
templates/              suite-plan.md, test-case.md, test-case.json, review-report.md
input/requirements/     your source requirements (sample «Звук» included) + _answers.md
input/requirements-*/   additional corpora, one directory each (knox, kuper)
output/                 suites/, cases/, reviews/, tests/, state/<journey>.json, state.json,
                        report.md, pending.md (skipped questions), .run (run identity),
                        .previous/ (last run's artefacts)
scripts/                run: validate_cases.py, check_state.py, review_scope.py, extract_reqs.py,
                        build_gate_questions.py, gate_check.py, include_skill.py,
                        start_run.py, check_artifacts.py, validate_plans.py,
                        json_to_md.py, extract_journey_context.py, patch_case.py
                        profiling: analyze_logs_v2.py, profile_qwen_logs.py
                        migration: build_case_json.py (pre-JSON-primary cases)
examples/               a fully worked journey plan + case, useful as a reference and smoke test
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
  silently drop a stage. It is also what makes the loops parallelisable: one writer per path, no
  shared mutable state, so concurrent loops cannot clobber each other.
- **One loop, one journey.** A loop that owned two journeys would start borrowing facts between them
  — which is exactly how invented behaviour spreads. Isolation is a correctness property here, not a
  scheduling detail.
- **Missing requirements are your decision, not the model's.** The run stops and asks rather than
  guessing, both before writing cases and before reporting. Answers you give become requirements.
- **Domain-free templates.** «Звук» exists only in `input/requirements/`. Point the project at other
  requirements and nothing else changes.

## Adapting to another product

1. Replace `input/requirements/`.
2. If the target team's case format differs, edit `docs/format.md`, `templates/test-case.md` and the
   section list at the top of `scripts/validate_cases.py` — the agents read the contract, they do not
   hardcode it.
3. Nothing in `.gigacode/agents/` needs to change.
