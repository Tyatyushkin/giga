# E2E Test Case Factory — project context

This project turns product requirements into **connected end-to-end test suites** using a loop of
three subagents inside Qwen Code:

```
requirements  →  [requirements-analyst]  →  suite plans (journeys) + _index.json
                        ↓
              requirements gate: the human is shown every gap, every uncovered REQ,
              every blocking question, and chooses how many loops run in parallel
                        ↓
   ┌────────────────────┼────────────────────┐        P loops, one per journey/area,
   ▼                    ▼                    ▼        running concurrently
 [qa-designer J01]   [qa-designer J02]   [qa-designer J03]
   ▼                    ▼                    ▼
 [test-critic J01]   [test-critic J02]   [test-critic J03]  → output/state/<J>.json
   │                    │                    │
   └── blockers > 0 and iteration < MAX_ITERATIONS ──→ back to that journey's designer
       blockers = 0 ──→ that journey is DONE, the others keep running
                        ↓
              coverage gate: the human is shown what the run could not settle
                        ↓
                     output/report.md
```

## Directory contract

| Path | Owner | Content |
|---|---|---|
| `input/requirements/*.md` | human | source requirements |
| `input/requirements/_answers.md` | human, written by the orchestrator | answers to clarifying questions; ranks as a requirement |
| `output/suites/<JOURNEY_ID>.md` | requirements-analyst | journey / suite plan |
| `output/suites/_index.json` | requirements-analyst | machine index: journeys, areas, gaps, questions, uncovered REQ |
| `output/cases/<JOURNEY_ID>/<CASE_ID>.md` | qa-designer | test case, Markdown (primary) |
| `output/cases/<JOURNEY_ID>/<CASE_ID>.json` | qa-designer | same case, machine-readable |
| `output/reviews/<JOURNEY_ID>-iter<N>.md` | test-critic | review + fix list |
| `output/state/<JOURNEY_ID>.json` | test-critic | that journey's loop state — one writer per file |
| `output/state.json` | orchestrator | aggregate snapshot across journeys |
| `output/report.md` | orchestrator | final run summary |

**One writer per path.** Parallel loops make this a correctness rule, not a convention: a designer
writes only its own `output/cases/<JOURNEY_ID>/`, a critic only its own review and
`output/state/<JOURNEY_ID>.json`, and only the orchestrator writes `output/state.json` and
`output/report.md`. Any file two agents could write concurrently is a bug in the prompt.

## Non-negotiable rules (apply to every agent)

1. **Output language of artifacts is Russian.** Section headings must match `docs/format.md` character
   for character. Agent reasoning and commit messages may be English.
2. **No invented behaviour.** If a system reaction is not in the requirements, it does not exist.
   Write it into `## Выявленные пробелы` / `## Уточняющие вопросы` instead of assuming it.
   Inventing behaviour is a BLOCKER at review.
3. **No vague expected results.** «Успешно», «корректно», «работает», «без ошибок», «как ожидается»
   are forbidden as the substance of an expected result. Every result must name an observable:
   screen, element, text, state, counter, order of items. Vague result is a BLOCKER at review.
4. **One action per step.** A step contains exactly one user action and exactly one checkable result.
5. **State continuity.** Data created in an early step must be referenced by its concrete value in
   later steps (playlist name, track title, phone number). A journey is a chain, not a list.
6. **Traceability.** Every stage of a journey and every step of a case carries a requirement anchor
   (`REQ-XX`). A step with no anchor must be justified as an obvious UI navigation step.
7. **Reusability.** Nothing in the templates or agent prompts may hardcode the «Звук» domain.
   The domain lives only in `input/requirements/`.
8. **Journey isolation.** A design/review loop owns exactly one journey (or, in `area` mode, one
   functional area) and reads and writes nothing outside it. Plans must therefore be self-sufficient:
   no cross-references between journeys, no shared fixtures created by another journey's steps.
9. **Gaps are shown to the human, not absorbed.** Uncovered requirements, contradictions and blocking
   questions are surfaced as explicit lists with items — never as a count, never buried in a file the
   human has to go find. The orchestrator asks before designing and again before reporting.

## Loop control

- `MAX_ITERATIONS = 3` (override with `--max N` argument to `/e2e:run`).
- Each journey iterates independently. A journey exits its loop when its critic reports **zero
  BLOCKERs**. MAJOR/MINOR findings are recorded in the review and in the final report but do not block.
- If blockers remain after `MAX_ITERATIONS`, that journey stops and is marked `NEEDS_HUMAN` in
  `output/report.md` with the unresolved list. Other journeys keep running.
- A journey whose subagent errors or writes no state is `FAILED` — recorded, not fatal to the run.

## Parallelism

- The analyst runs once, over all requirements — journeys can only be found by looking at everything.
- After the requirements gate, the human chooses `P`, the number of concurrent design/review loops
  (`--parallel N` to skip the question; default recommendation `min(3, journeys)`), and the ownership
  unit (`--unit journey|area`).
- The orchestrator dispatches a wave by emitting `P` `agent` calls **in a single message**; agents in
  one wave run concurrently and share no context. Every prompt therefore carries explicit paths and
  an explicit ownership boundary.
- Waves are lockstep: all designers of a wave finish, then all critics of that wave run, then the
  orchestrator reads `output/state/*.json`, drops finished journeys, and refills from the queue.

## Deterministic gate

Before any semantic review the critic must run:

```bash
python3 scripts/validate_cases.py output/cases/<JOURNEY_ID> --json output/reviews/<JOURNEY_ID>-lint.json
```

The linter checks structure, placeholders, step numbering, vague wording and step atomicity.
Its findings are merged into the review report. Linter exit code 1 = blockers present.

## Reference documents

- `docs/format.md` — mandatory output format (Russian) and JSON schema
- `docs/quality-criteria.md` — 12 quality criteria the result is graded against
- `docs/critic-rubric.md` — severity rules for the critic
- `docs/examples.md` — bad → good rewrites for expected results, actions, data, questions
- `templates/` — copyable skeletons
- `examples/J01-onboarding-first-play/` — a fully worked plan + case that passes the linter
