"""Топология RabbitMQ для процессинга платежей.

relay ──publish──▶ (exchange: payments / rk: payments.new) ──▶ [payments.new] ──▶ consumer
                                                                      │ ошибка обработки
                                        attempt < 3                   ▼
                      [payments.retry]◀──── republish (per-message TTL, exp. backoff)
                              │ TTL истёк (dead-letter)
                              └──▶ (exchange: payments / rk: payments.new) ──▶ [payments.new]
                                        attempt == 3
                                             ▼
                                       [payments.dlq]
"""

from faststream.rabbit import ExchangeType, RabbitExchange, RabbitQueue

from application.events import PaymentEventType

EXCHANGE_NAME = 'payments'
QUEUE_NEW = 'payments.new'
QUEUE_RETRY = 'payments.retry'
QUEUE_DLQ = 'payments.dlq'

RETRY_COUNT_HEADER = 'x-retry-count'

payments_exchange = RabbitExchange(
	EXCHANGE_NAME,
	type=ExchangeType.DIRECT,
	durable=True,
)

# Рабочая очередь — её слушает consumer.
new_queue = RabbitQueue(
	QUEUE_NEW,
	durable=True,
	routing_key=PaymentEventType.NEW,
)

# Очередь отложенного повтора: сообщения лежат здесь до истечения per-message TTL,
# после чего dead-letter возвращает их в рабочую очередь через основной обменник.
retry_queue = RabbitQueue(
	QUEUE_RETRY,
	durable=True,
	arguments={
		'x-dead-letter-exchange': EXCHANGE_NAME,
		'x-dead-letter-routing-key': PaymentEventType.NEW,
	},
)

# Терминальная очередь для сообщений, не обработанных после всех попыток.
dlq_queue = RabbitQueue(QUEUE_DLQ, durable=True)
