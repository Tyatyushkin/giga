# E2E Test Case Factory — project context

This project turns product requirements into **connected end-to-end test suites** using a loop of
three subagents inside Qwen Code:

```
requirements  →  [requirements-analyst]  →  suite plans (journeys)
                        ↓
                 [qa-designer]  →  test cases (Markdown + JSON, Russian)
                        ↓
                 [test-critic]  →  review report (BLOCKER / MAJOR / MINOR)
                        ↓
        blockers > 0 and iteration < MAX_ITERATIONS ──→ back to qa-designer
        blockers = 0 ──→ DONE
```

## Directory contract

| Path | Owner | Content |
|---|---|---|
| `input/requirements/*.md` | human | source requirements |
| `output/suites/<JOURNEY_ID>.md` | requirements-analyst | journey / suite plan |
| `output/cases/<JOURNEY_ID>/<CASE_ID>.md` | qa-designer | test case, Markdown (primary) |
| `output/cases/<JOURNEY_ID>/<CASE_ID>.json` | qa-designer | same case, machine-readable |
| `output/reviews/<JOURNEY_ID>-iter<N>.md` | test-critic | review + fix list |
| `output/state.json` | orchestrator | loop state (iteration, blockers, verdict) |
| `output/report.md` | orchestrator | final run summary |

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

## Loop control

- `MAX_ITERATIONS = 3` (override with `--max N` argument to `/e2e:run`).
- Loop exits when the critic reports **zero BLOCKERs**. MAJOR/MINOR findings are recorded in the
  review and in the final report but do not block.
- If blockers remain after `MAX_ITERATIONS`, stop and mark the journey `NEEDS_HUMAN` in
  `output/report.md` with the unresolved list.

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
