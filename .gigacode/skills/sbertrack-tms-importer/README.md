## 1. Настроить и поднять mcp сервер sbertrack-mcp
https://sc-ci.sber.ru/sc/InSourceHub_AI/ai_market/src/branch/master/mcp/sbertrack-mcp


## 2. Пример подключения к sbertrack-mcp в settings.json:

```json
   "sbertrack_tsm": {
   "httpUrl": "http://0.0.0.0:8080/mcp?scopes=issues,test_units,tms"
   }
   ```

## 3. Для импорта тестов в тест культура использовать скилл: [sbertrack-tms-importer](.gigacode%2Fskills%2Fsbertrack-tms-importer)
На вход скиллу дать md файл с тестами и код пространства в sbertrack