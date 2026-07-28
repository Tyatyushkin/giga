# `output/tests/` — pytest code generation from E2E case files

## Назначение

Каталог `output/tests/` содержит **pytest-тесты**, сгенерированные из E2E-кейсов (`output/cases/`).
Это фаза **4** цикла E2E Test Case Factory — опциональная, запускается по запросу человека.

## Связь с артефактами

| Артефакт | Путь | Роль |
|---|---|---|
| Markdown-кейсы | `output/cases/<JOURNEY_ID>/*.md` | Источник шагов |
| JSON-кейсы | `output/cases/<JOURNEY_ID>/*.json` | Машиночитаемый источник |
| **pytest-файлы** | `output/tests/<JOURNEY_ID>/*.py` | Тесты, 1 функция на 1 шаг |
| Константы | `output/tests/<JOURNEY_ID>/test_data.py` | Типизированные тестовые данные |
| API-заглушка | `output/tests/<JOURNEY_ID>/api_stub.py` | Эмуляция сервиса |
| Фикстуры | `output/tests/<JOURNEY_ID>/conftest.py` | Глобальные фикстуры |
| Конфиг | `pytest.ini` | Маркеры и пути |

## Как это работает

1. Оркестратор завершает цикл дизайн → ревью → отчёт.
2. Спрашивает: «Готово N кейсов. Сгенерировать pytest?»
3. При ответе `да` — запускает `pytest-test-writer`-агента.
4. Агент читает Markdown + JSON, пишет в `output/tests/<JOURNEY_ID>/`.

## Форматное правило

- Один `test_` = один шаг из кейса.
- `@pytest.mark.skip` — если ожидаемый результат не определён требованиями (BLOCKER).
- Константы — из `test_data.py`, **никаких литералов** в теле тестов.
- API-заглушка детерминирована — тесты не flaky.

## Статус на 28 июля 2026

- `output/tests/J01-onboarding-and-first-play/` — написан вручную как демонстрация (18 тестов, 5 skip)
- `output/tests/J02-collection-and-playlists/` — не создан (ждут `--generate`)
- `output/tests/J03-session-resilience/` — не создан (ждут `--generate`)