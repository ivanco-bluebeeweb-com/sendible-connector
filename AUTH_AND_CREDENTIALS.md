# Sendible Connector — Auth & Credentials Standard

**App ID:** `sendible-connector`  
**Standard Compliance:** AUTH_AND_CREDENTIALS_STANDARD.md (B1–B10)

## Authentication Architecture
- **Тип авторизации:** OAuth 2.0 (Authorization Code Grant)
- **Принцип BYOC:** Пользователь подключает собственный аккаунт/ключи.
- **Хранение секретов:** Зашифрованные переменные окружения / Vault. Токены никогда не логируются и маскируются в ответах API.
- **Верификация подключения:** При сохранении ключа выполняется тестовый запрос `GET /api/v1/profiles.json`.
- **Отключение:** Удаление локальных ключей по команде пользователя без повреждения данных на стороне Sendible.
