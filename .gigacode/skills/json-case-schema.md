# E2E Test Case JSON Schema

This schema defines the machine-readable format for test cases.
Markdown and JSON must be content-identical.

## Top-level fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | ✅ | Unique case ID, e.g. `TC-J01-00` |
| `title` | string | ✅ | Short description of the scenario |
| `goal` | string | ✅ | What the test confirms |
| `priority` | string | ✅ | `Критический`, `Высокий`, `Средний`, `Низкий` |
| `journeyId` | string | ✅ | Associated journey, e.g. `J01-onboarding-first-play` |
| `variantOf` | string or null | ✅ | Main case ID if variant, else `null` |
| `requirements` | string[] | ✅ | REQ anchors, e.g. `["REQ-01", "REQ-02"]` |
| `preconditions` | string[] | ✅ | State before step 1 |
| `testData` | array | ✅ | Concrete test values |
| `steps` | array | ✅ | Ordered actions with expected results |
| `postconditions` | string[] | ✅ | Final state after scenario |
| `gaps` | string[] | ✅ | Uncertainties found during writing |
| `clarifyingQuestions` | string[] | ✅ | Blocking questions for product |

## testData items

| Field | Type | Required |
|---|---|---|
| `name` | string | ✅ | Parameter name |
| `value` | string | ✅ | Concrete value |
| `comment` | string | ❌ | Optional explanation |

## steps items

| Field | Type | Required |
|---|---|---|
| `number` | integer | ✅ | Step number (1-based) |
| `action` | string | ✅ | Single user verb |
| `testData` | string | ❌ | Concrete value or empty |
| `expectedResult` | string | ✅ | Observable result |
| `requirements` | string[] | ❌ | REQ anchors for this step |

## Rules

1. `id`, `journeyId`, `title`, `goal`, `priority` — always non-empty.
2. `steps` must be ordered by `number` ascending.
3. Each step's `number` must be unique.
4. `variantOf` is null for main cases, points to main case ID for variants.
5. All strings are UTF-8, no markdown formatting inside JSON fields.
6. Arrays may be empty (`[]`) but never null.

## Ссылки на тестовые данные в шагах

`steps[].testData` может называть параметр ссылкой вместо того, чтобы вклеивать его значение:

```json
{"number": 1, "testData": "{Базовый URL шлюза}/gateway/admin/api/v1/topologies, {Логин администратора}"}
```

Конвертер подставляет значение из таблицы `testData` на место ссылки, поэтому URL можно
составлять из базового адреса и пути. `{{` и `}}` — литеральные скобки.

Зачем: раньше стодвадцатисимвольный URL приходилось писать дважды — в таблице и в шаге, — потому
что проверка «значение используется» искала подстроку. Со ссылкой проверка точная: имя вне
таблицы — BLOCKER, строка без единой ссылки и без вхождения значения — MAJOR.
