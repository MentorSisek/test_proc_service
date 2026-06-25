## API — примеры (curl)

Все эндпоинты требуют заголовок `X-API-Key` (значение из `.env`, по умолчанию
`secret-api-key`). Базовый URL — `http://localhost:8000`.

## Команды


Аналоги через `docker compose` (то, что Makefile вызывает под капотом):

```bash
docker compose up --build -d           # make up
docker compose logs -f api consumer    # make logs
docker compose down                    # make down
docker compose run --rm migrations     # make migrate-up (применить миграции в контейнере)
```

```bash
make up           # собрать и запустить всё
make logs         # логи api + consumer
make down         # остановить и удалить контейнеры
make migrate-up   # применить миграции локально
make test         # юнит-тесты
make lint         # ruff check
make format       # ruff format + автофиксы
```

### Создание платежа

`POST /api/v1/payments` — заголовки `X-API-Key` и `Idempotency-Key` обязательны.

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H 'X-API-Key: secret-api-key' \
  -H 'Idempotency-Key: order-42' \
  -H 'Content-Type: application/json' \
  -d '{
        "amount": "100.50",
        "currency": "RUB",
        "description": "Оплата заказа #42",
        "metadata": {"order_id": 42},
        "webhook_url": "https://example.com/webhooks/payments"
      }'
```

Ответ `202 Accepted`:

```json
{
  "payment_id": "6c84c701-1aa3-449e-a78e-1299eb147336",
  "status": "pending",
  "created_at": "2026-06-24T11:45:25.095315Z"
}
```

### Идемпотентный повтор

Повтор с тем же `Idempotency-Key` возвращает уже созданный платёж, дубль не создаётся:

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H 'X-API-Key: secret-api-key' \
  -H 'Idempotency-Key: order-42' \
  -H 'Content-Type: application/json' \
  -d '{"amount": "100.50", "currency": "RUB"}'
# -> тот же payment_id, что и в первом запросе
```

### Получение платежа

`GET /api/v1/payments/{payment_id}`

```bash
curl http://localhost:8000/api/v1/payments/6c84c701-1aa3-449e-a78e-1299eb147336 \
  -H 'X-API-Key: secret-api-key'
```

```json
{
  "id": "6c84c701-1aa3-449e-a78e-1299eb147336",
  "amount": "100.50",
  "currency": "RUB",
  "description": "Оплата заказа #42",
  "metadata": {"order_id": 42},
  "status": "succeeded",
  "idempotency_key": "order-42",
  "webhook_url": "https://example.com/webhooks/payments",
  "created_at": "2026-06-24T11:45:25.095315Z",
  "processed_at": "2026-06-24T11:45:29.464005Z"
}
```

### Ошибки

```bash
# Без X-API-Key -> 401 Unauthorized
curl -i -X POST http://localhost:8000/api/v1/payments \
  -H 'Idempotency-Key: x' -H 'Content-Type: application/json' \
  -d '{"amount": "1.00", "currency": "RUB"}'

# Несуществующий платёж -> 404 Not Found
curl -i http://localhost:8000/api/v1/payments/00000000-0000-0000-0000-000000000000 \
  -H 'X-API-Key: secret-api-key'

# Невалидное тело / нет Idempotency-Key -> 422 Unprocessable Entity
curl -i -X POST http://localhost:8000/api/v1/payments \
  -H 'X-API-Key: secret-api-key' -H 'Content-Type: application/json' \
  -d '{"amount": "1.00"}'
```

### Webhook

После обработки сервис делает `POST` на `webhook_url` с телом:

```json
{
  "payment_id": "6c84c701-1aa3-449e-a78e-1299eb147336",
  "status": "succeeded",
  "amount": "100.50",
  "currency": "RUB",
  "metadata": {"order_id": 42},
  "processed_at": "2026-06-24T11:45:29.464005+00:00"
}
```

