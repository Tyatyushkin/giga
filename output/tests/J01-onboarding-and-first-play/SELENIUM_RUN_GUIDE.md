# Инструкция по запуску Selenium-тестов (J01 — Онбординг)

## Требования

- **Chrome** (не Headless, видимый браузер): установлен в `/Applications/`
- **Сервер**: `https://zvuk.com/` должен быть доступен
- **Python**: `python3.14+`, `pytest`, `selenium`, `webdriver-manager`, `allure-pytest`

## Установка

```bash
pip install selenium webdriver-manager allure-pytest
```

## Запуск всех тестов

```bash
cd output/tests/J01-onboarding-and-first-play/
python3 -m pytest . -v --tb=short
```

**Результат:** 29 passed, 3 skipped (3 — BLOCKER, неопределённое поведение в требованиях)

## Запуск одного кейса

```bash
python3 -m pytest test_J01.py::TestMainHappyPath::test_01_open_app_show_login_screen -v --tb=long
```

## Allure-отчёт

```bash
python3 -m pytest . --alluredir=allure-results
allure serve allure-results
```

## Структура

| Файл | Что тестирует |
|---|---|
| `test_J01.py` | Все 32 шага из TC-J01-00…TC-J01-04 |
| `test_selenium.py` | UI-визуальные тесты (16 сценариев) |
| `conftest.py` | Фикстуры: `driver`, `api_client`, `base_url` |
| `test_data.py` | Константы (номера, коды, названия) |
| `api_stub.py` | Эмуляция API «Звук» (18 методов) |

## Пропущенные тесты (BLOCKER)

| Кейс | Причина | Вопрос |
|---|---|---|
| TC-J01-01, шаг 4 | REQ-01 не определяет UI таймера | Q-02 |
| TC-J01-02, шаг 4 | REQ-01 не определяет поведение при неверном коде | Q-06 |
| TC-J01-04, шаг 8 | REQ-04 не определяет пустой запрос | Q-10 |