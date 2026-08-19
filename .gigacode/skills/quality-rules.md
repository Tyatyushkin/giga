# E2E Quality Rules (from GIGACODE.md)

## Non-negotiable rules

1. **No invented behaviour.** If a system reaction is not defined in the requirements, it does not exist. Write it to `## Выявленные пробелы` / `## Уточняющие вопросы`. Invented behaviour = BLOCKER.

2. **No vague expected results.** «Successfully», «correctly», «works», «without errors», «as expected» are prohibited. Each result MUST name an observable: screen name, element, text, state, counter, element order. Vague result = BLOCKER.

3. **One action per step.** A step contains exactly one user action and exactly one verifiable result.

4. **State continuity.** Data created in an early step must be mentioned by its concrete value in later steps (playlist name, track title, phone number). A journey is a chain, not a list.

5. **Traceability.** Each journey stage and each case step carries a requirement anchor (`REQ-XX`). A step without an anchor must be justified as an obvious UI navigation step.

6. **Reusability.** Nothing in templates or agent prompts should hardcode the "Sound" domain. The domain lives only in `input/requirements/`.

7. **Journey isolation.** The design/review cycle owns exactly one journey (or one functional area in `area` mode) and reads/writes only within it. Plans must be self-sufficient: no cross-journey links, no shared fixtures created by another journey's steps.

8. **Gaps shown to human, not swallowed.** Uncovered requirements, contradictions, and blocking questions are output as explicit itemised lists — never as a count, never buried in a file the human must hunt for.

## Severity quick reference

| Level | When to use |
|---|---|
| **BLOCKER** | Invented behaviour (no observable result) — the two most common: (a) expected result names nothing observable, (b) expected result describes a system reaction not defined in requirements. |
| **MAJOR** | Coverage gap (REQ in scope not checked by any step), broken chain (step needs state nobody created), variant improperly linked. |
| **MINOR** | Style deviations: non-verbatim section header, missing changelog comment, redundant step grouping. |
