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

## Phase 4 — pytest code generation (optional, gated by human)

After the E2E loop finishes (all journeys are `PASS` or `NEEDS_HUMAN`), the orchestrator **asks** the user:

> «Готово N кейсов в Markdown. Сгенерировать pytest-тесты?»

The question is asked **once**, after all journeys are complete — not per-journey.
If the user answers `yes`, the orchestrator launches **one** `pytest-test-writer` subagent per journey
that has **zero BLOCKER** (i.e. `PASS` verdict), and the orchestrator handles `NEEDS_HUMAN` journeys
manually (skipped tests with `@pytest.mark.skip`).

The `pytest-test-writer` agent reads:

- Journey suite plan → `output/suites/<ID>.md`
- All case files → `output/cases/<ID>/TC-*.md`
- All case JSON → `output/cases/<ID>/TC-*.json` (if available)

And writes:

- `tests/helpers/test_data.py` — typed constants from every `## Тестовые данные` table
- `tests/helpers/api_stub.py` — one emulated method per REQ, returns dict
- `tests/helpers/conftest.py` — global fixtures (api_client fixture, project_root)
- `pytest.ini` — markers from the review
- `tests/test_JOURNEY_ID.py` — one class per Case, one `test_` per step

**Contract** (all paths in `tests/`):

| File | Content |
|---|---|
| `tests/conftest.py` | Global fixtures |
| `tests/helpers/test_data.py` | Typed constants |
| `tests/helpers/api_stub.py` | Emulated API client |
| `pytest.ini` | Marker registry |
| `tests/test_JOURNEY_ID.py` | All test cases for one journey |

**Rules:**

1. **One test per step.** A `test_` function tests exactly one step from one case.
2. **Skip blockers.** If the critic marked a step as BLOCKER, the test is `@pytest.mark.skip`.
3. **No invented behavior.** All unobservable expectations are `skip`.
4. **Data from constants.** No literals in test code.
5. **API stub is deterministic.** Returns the same thing for the same input — no flaky tests.

**Allure-разметка:** см. `.gigacode/agents/pytest-test-writer.md` — раздел «Allure-разметка».

**Report in `output/tests/README.md`:**

After generation, the agent **appends** a summary to `output/tests/README.md`:

```markdown
## <JOURNEY_ID> — pytest generation

| Вердикт | Всего | PASS | SKIP | FAIL |
|---|---|---|---|---|
| `PASS` | N | N | M | 0 |
| `NEEDS_HUMAN` | N | N | M | 0 |
```

- **Всего тестов** — количество `test_` функций
- **PASS** — тесты, чей expected result определён в REQ
- **SKIP** — `@pytest.mark.skip` из-за выдуманного поведения (BLOCKER)
- **FAIL** — 0 (детерминированная эмуляция)

Каждый SKIP содержит ссылку на пробел и номер вопроса из уточняющего списка.
Пример:

```python
@pytest.mark.skip(
    reason="BLOCKER: REQ-01 не определяет UI таймера. "
           "Уточняющий вопрос 2: что видит пользователь при неактивной кнопке?"
)
def test_timer_visual():
    ...
```
**Exit:** After all writer agents finish, the orchestrator reports:

> «Сгенерировано N тестов, M пропущено. Нужна доработка от человека по K BLOCKER.»
