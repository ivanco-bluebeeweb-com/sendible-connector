# Sendible Connector — Discovery & API Specification

**Vendor:** Sendible  
**Catalog URL:** https://sendible.com  
**API Base URL:** `https://api.sendible.com/api/v1`  
**Authentication:** OAuth 2.0 (Authorization Code Grant)

## Core Entities & Endpoints
социальные профили (/profiles), сообщения и посты (/messages), входящие активности (/activities), отчеты аналитики

## Verified Read Operation
- **Эндпоинт проверки:** `GET /api/v1/profiles.json`
- **Метод:** GET
- **Ожидаемый ответ:** HTTP 200 OK со структурой метаданных сущности.

## Rate Limits & Pagination
- Стандартная курсорная или offset/limit пагинация вендора.
- Обработка HTTP 429 Too Many Requests с экспоненциальным backoff.
- Защита от тайм-аутов: ограничение на сетевые запросы 15-30 секунд.
