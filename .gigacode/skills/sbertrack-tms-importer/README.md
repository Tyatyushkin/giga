# SberTrack TMS Importer

> **Импорт E2E тест-кейсов из Markdown в SberTrack TMS через MCP-сервер**

---

## 🚀 Быстрый старт

### 1. Запуск MCP-сервера

Поднимите локальный MCP-сервер `sbertrack-mcp`:

📂 [исходный код](https://sc-ci.sber.ru/sc/InSourceHub_AI/ai_market/src/branch/master/mcp/sbertrack-mcp)

### 2. Настройка подключения

Добавьте конфигурацию в `settings.json`:

```json
{
  "sbertrack_tms": {
    "httpUrl": "http://0.0.0.0:8080/mcp?scopes=issues,test_units,tms"
  }
}
```

### 3. Импорт тест-кейсов

Используйте этот скилл для загрузки тест-кейсов в SberTrack. На вход подайте:

- **Markdown-файлы** E2E тест-кейсов (формат: `ID`, `Название`, `Предусловия`, таблица `Шаги` и т.д.)
- **Код пространства** в SberTrack (например, `TSTQ`, `INSHUB`)

---

## 📚 Документация

| Файл | Описание |
|---|---|
| [SKILL.md](SKILL.md) | Полный workflow, парсинг Markdown → JSON, маппинг полей, примеры |
| [testcase-schema.json](testcase-schema.json) | JSON-схема формата тест-кейса для TMS API |

## Где лежат кейсы этой фабрики

`output/cases/<JOURNEY_ID>/TC-*.md` — порождаются из `.json` рядом скриптом
`scripts/json_to_md.py`. Правкам подлежит `.json`, Markdown перезаписывается.

Формат кейса описан в `docs/format.md`; особенности, которые скилл учитывает отдельно
(«Вариант от», «Трассируемость», «Уточняющие вопросы»), — в разделе «Особенности кейсов
этой фабрики» файла [SKILL.md](SKILL.md).
