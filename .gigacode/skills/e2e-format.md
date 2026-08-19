# E2E Test Case Format Contract

## Mandatory section headers (verbatim, Russian)

```
# E2E тест-кейс

## Общая информация
- **ID:** TC-J<NN>-<NN>
- **Название:** …
- **Цель:** …
- **Приоритет:** Критический | Высокий | Средний | Низкий
- **Journey:** J<NN>-<slug>
- **Вариант от:** — | TC-J<NN>-<NN>
- **Покрываемые требования:** REQ-01, REQ-02, …

## Предусловия
- …

## Тестовые данные
| Параметр | Значение | Комментарий |
|---|---|---|

## Шаги
| № | Действие пользователя | Тестовые данные | Ожидаемый результат |
|---:|---|---|---|

## Постусловия
- …

## Выявленные пробелы
- …

## Уточняющие вопросы
1. …
2. …
```

## Naming rules

| Artifact | Pattern | Example |
|---|---|---|
| Journey | `J<NN>-<slug>` | `J01-onboarding-first-play` |
| Main case | `TC-J<NN>-00` | `TC-J01-00` |
| Variant | `TC-J<NN>-<NN>` | `TC-J01-03` |
| Requirement | `REQ-<NN>` | `REQ-07` |

## Step rules

1. One step = one user action + one verifiable result.
2. Test data column: concrete value from the data table or `—`.
3. Expected result: MUST name an observable — screen name, element, exact text, state, counter, order.
4. Forbidden words in expected result (if not accompanied by an observable): «успешно», «корректно», «работает», «без ошибок», «как ожидается», «выполнено», «нормально».
5. Values created early must be repeated verbatim in later steps.
6. Main case ≥ 8 steps; a 3-step case is not e2e.
