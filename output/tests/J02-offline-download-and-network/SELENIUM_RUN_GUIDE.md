# Инструкция по запуску Selenium-тестов (J02 — Офлайн и обрыв сети)

## Требования

- **Chrome** (не Headless): установлен в `/Applications/`
- **Сервер**: `https://zvuk.com/` доступен
- **Python**: `selenium`, `webdriver-manager`, `allure-pytest`

## Установка

```bash
pip install selenium webdriver-manager allure-pytest
```

## Запуск

```bash
cd output/tests/J02-offline-download-and-network/
python3 -m pytest . -v --tb=short
```

**Результат:** 32 passed, 4 skipped

## Пропущенные тесты

| Кейс | Причина | Вопрос |
|---|---|---|
| TC-J02-03, шаг 2 | Q-13 не определяет UI кнопки «Закрыть» | Q-13 |
| TC-J02-06, шаги 1,3,4 | BR-015 не определяет поведение дубликата | BR-015 |