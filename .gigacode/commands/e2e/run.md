---
description: Full loop — analyst → N parallel designer/critic loops, repeating until zero blockers (max 3 iterations).
---

You are the orchestrator of a multi-agent e2e test generation run. Follow this procedure exactly and
do not perform the agents' work yourself — delegate through the `agent` tool.

Arguments (may be empty): {{args}}
- a path or glob → requirements source (default `input/requirements/*.md`)
- `--max N` → override MAX_ITERATIONS (default 3)
- `--journey J01` → run the loop for a single journey only
- `--parallel N` → number of concurrent design/review loops; skips the parallelism question
- `--unit journey|area` → what one loop owns; skips the ownership question
- `--yes` → skip the go/no-go pause after analysis
- `--no-ask` → fully autonomous: skip every interactive question and record the answers I would have
  been asked in `output/report.md` under «Требуются решения человека»

## How to ask me things

Several phases below require you to ask me a question. Use the interactive question tool your
runtime exposes (`ask_user_question` / `AskUserQuestion` / equivalent). If no such tool exists,
print the question with numbered options and **stop your turn** — do not choose for me and do not
continue the run until I answer. `--no-ask` is the only thing that lets you skip a question.

Project state right now:

!{ls -1 input/requirements/ 2>/dev/null; echo "--- suites ---"; ls -1 output/suites/ 2>/dev/null; echo "--- cases ---"; ls -1 output/cases/ 2>/dev/null; echo "--- state ---"; ls -1 output/state/ 2>/dev/null}

## Procedure

### Phase 1 — analysis

Call `agent` with `subagent_type: requirements-analyst`.
Task: read the requirements source, produce journey plans into `output/suites/` plus the machine
index `output/suites/_index.json`.
Wait for it to finish. Read `output/suites/_index.json` and every plan it produced. If it produced
zero journeys, stop and report why.

Show me the journey list: id, title, priority, functional areas, stages, variants, gaps, questions.

### Phase 1.5 — requirements gate (mandatory, ask me explicitly)

This gate exists because a gap nobody surfaced becomes an invented expected result three agents
downstream. Never skip it, never soften it, never answer it on my behalf.

From `_index.json` and the plans, collect:

1. **Непокрытые требования** — every `REQ-XX` that lands in no journey stage, with the reason.
2. **Пробелы** — requirements that are silent, contradictory or ambiguous, deduplicated across
   journeys, each with the quoted source text.
3. **Блокирующие вопросы** — clarifying questions, ordered by how many stages/variants they block.
4. **Этапы без требования** — stages carrying the marker `БЕЗ ТРЕБОВАНИЯ`.
5. **Структурные подозрения** — journeys with fewer than 5 stages, fewer than 3 functional areas, or
   with no data carried between stages. These are grouping mistakes, not coverage facts — label them
   as such.

Print all five lists in full. Do not replace a list with its count, and do not summarise items away.
If a list is empty say so explicitly — «непокрытых требований нет» is information I need.

Then ask me, in one question round:

- **Q1 — coverage.** «N требований не покрыто, M пробелов, K блокирующих вопросов. Как поступить?»
  Options: *Продолжить, зафиксировать пробелы как вопросы* / *Я отвечу на блокирующие вопросы
  сейчас* / *Остановиться — я поправлю требования*.
  If I answer the questions, write my answers into `input/requirements/_answers.md` (create it,
  Russian, one numbered answer per question, each quoting its question), then re-run the analyst
  with that file added to its input before continuing. My answers are requirements from then on.
  If I choose to stop, write what is missing into `output/report.md` and end the run.
- **Q2 — parallelism.** «Сколько параллельных циклов designer→critic запускать?»
  Options: *1 (последовательно)* / *2* / *3 (рекомендуется)* / *По одному на каждый journey (N)*.
  Recommend `min(3, journey count)`. Skip this question if `--parallel N` was given.
- **Q3 — ownership unit.** «Что владеет одним циклом?»
  Options: *Один journey на цикл (рекомендуется)* / *Одна функциональная область на цикл*.
  Skip this question if `--unit` was given or if there is only one journey.

Unless `--yes` was passed, also pause here for my go/no-go before Phase 2.

### Phase 2 — parallel design + review loops

Let `P` = the parallelism I chose and `MAX_ITERATIONS` = 3 or `--max N`.

**Ownership is exclusive.** One loop owns exactly one work unit and writes only inside it:

| Unit mode | A loop owns | Paths it may write |
|---|---|---|
| `journey` (default) | one journey | `output/cases/<J>/`, `output/reviews/<J>-*`, `output/state/<J>.json` |
| `area` | all journeys of one functional area, one after another inside that loop | the same paths, for its own journeys only |

In `area` mode, group journeys by the first entry of their «Функциональные области» line; a loop
starts the next journey of its area only after the previous one reaches PASS or NEEDS_HUMAN.
Two loops must never write the same path — that is why the critic writes `output/state/<J>.json`
and never the aggregate `output/state.json`. You are the only writer of `output/state.json`.

Build the worklist from the journeys (or the one named in `--journey`), ordered by risk — `J01`
first. Take the first `P` units as the **active batch**; the rest wait in a queue.

Then run lockstep waves:

```
wave:
  1. emit one agent(qa-designer) call per ACTIVE journey — all of them in a SINGLE message,
     so they execute concurrently. Never send them one per message.
  2. when every call has returned, emit one agent(test-critic) call per ACTIVE journey,
     again all in a single message.
  3. read output/state/<J>.json for each active journey and decide:
       blockers == 0                → PASS,        journey leaves the batch
       iteration >= MAX_ITERATIONS  → NEEDS_HUMAN, journey leaves the batch
       subagent errored / no state  → FAILED,      journey leaves the batch, record the error
       otherwise                    → stays active, iteration += 1
  4. refill the batch from the queue up to P
  5. repeat until batch and queue are both empty
```

Rules for the loops:

- Pass explicit file paths in every subagent prompt. Subagents share neither your context nor each
  other's — each one must be told its suite file, its requirement files, its case directory, its
  review path and its state path. A prompt that says «the journey» instead of a path is a bug.
- Every prompt must state the loop's boundary: "you own `<J>` only; do not read or write any other
  journey's directory".
- On iteration ≥ 2 the designer prompt must say: "fix iteration N, address every BLOCKER in
  `<that journey's review path>`, keep diffs minimal".
- The critic's blocker count is authoritative. Do not re-judge it and do not talk it down.
- Never fix cases yourself. If one loop stalls, mark that journey FAILED and let the others finish —
  one bad journey does not abort the run.
- After every wave print one line per active journey:
  `J01 iter2: BLOCKER 1, MAJOR 3, MINOR 2 → FIX` / `→ PASS` / `→ NEEDS_HUMAN`.
- Aggregate `output/state/*.json` into `output/state.json` after each wave:
  `{ "maxIterations": N, "parallel": P, "unit": "journey|area", "journeys": { "J01": {…} }, "verdict": "…" }`.

### Phase 3 — coverage gate (mandatory, ask me explicitly)

Before writing the report, read every final review and collect what the run could **not** settle:

1. requirements in scope of a journey that no case checks — the critics' coverage MAJORs,
2. clarifying questions still open in cases and plans, deduplicated, ordered by cases blocked,
3. gaps the designers hit while writing steps that the analyst had not found,
4. journeys that ended NEEDS_HUMAN or FAILED, with their unresolved blockers verbatim.

Print all four lists in full, then ask me:

«Прогон закончен: X требований без проверки, Y открытых вопросов, Z journey требуют человека.
Что дальше?» Options: *Записать отчёт как есть* / *Я отвечу на вопросы — прогнать блокирующие
journey ещё раз* / *Показать непокрытые требования подробно*.

If I choose the re-run, append my answers to `input/requirements/_answers.md` and repeat Phase 2 for
the affected journeys only, with their iteration counters reset.

### Phase 4 — report

Write `output/report.md` (Russian) containing:

- run header: requirements source, journeys, parallelism used, ownership unit, iterations per journey
- table: journey, verdict, iterations used, blockers left, majors, minors, case count, step count
- consolidated **Выявленные пробелы** across all journeys, deduplicated
- consolidated **Уточняющие вопросы**, numbered, grouped by journey, ordered by how many cases they
  block, each marked answered / open
- **Непокрытые требования** — every `REQ-XX` no case checks, with the reason
- **Требуются решения человека** — for `NEEDS_HUMAN`/`FAILED` journeys the unresolved blockers
  verbatim, plus every question skipped under `--no-ask`

Then print an English summary of what happened, how the parallel loops were distributed, and what
needs a human decision.
