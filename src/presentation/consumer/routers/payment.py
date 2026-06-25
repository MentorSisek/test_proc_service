from faststream.rabbit.annotations import RabbitMessage

from application.events import PaymentCreatedEvent
from config import settings
from infrastructure.database.sql.connection import SessionFactory
from infrastructure.messaging import (
	RETRY_COUNT_HEADER,
	dlq_queue,
	new_queue,
	payments_exchange,
	retry_queue,
)
from logger import logger
from presentation.consumer.broker import broker
from presentation.consumer.dependency import (
	get_deliver_webhook_use_case,
	get_payment_gateway,
	get_process_payment_use_case,
	get_webhook_client,
)

_gateway = get_payment_gateway()
_webhook_client = get_webhook_client()


@broker.subscriber(new_queue, payments_exchange)
async def handle_payment_new(event: PaymentCreatedEvent, msg: RabbitMessage) -> None:
	"""Обработать платёж. При ошибке — отложенный повтор, после исчерпания попыток — DLQ.

	Сообщение всегда подтверждается (ack), а повтор реализуется явной переотправкой в
	`payments.retry` с экспоненциальной задержкой — это исключает «горячий» requeue.
	"""
	try:
		await _process(event.payment_id)
	except Exception as exc:
		await _route_failure(event, msg, exc)


async def _process(payment_id: str) -> None:
	# Этап 1 — провести платёж и зафиксировать статус (отдельная транзакция).
	async with SessionFactory() as session:
		try:
			use_case = get_process_payment_use_case(session=session, gateway=_gateway)
			await use_case.execute(payment_id)
			await session.commit()
		except Exception:
			await session.rollback()
			raise

	# Этап 2 — доставить webhook. Сбой здесь не откатывает статус и уводит сообщение
	# в retry/DLQ; повторная обработка пройдёт только доставку (статус уже зафиксирован).
	async with SessionFactory() as session:
		use_case = get_deliver_webhook_use_case(
			session=session,
			webhook_client=_webhook_client,
		)
		await use_case.execute(payment_id)


async def _route_failure(
	event: PaymentCreatedEvent,
	msg: RabbitMessage,
	exc: Exception,
) -> None:
	retry_count = int(msg.headers.get(RETRY_COUNT_HEADER, 0) or 0)

	if retry_count < settings.processing.max_retries:
		delay = settings.processing.retry_base_delay_seconds * (2**retry_count)
		await broker.publish(
			event.to_dict(),
			queue=retry_queue,
			headers={RETRY_COUNT_HEADER: retry_count + 1},
			expiration=delay,
		)
		logger.warning(
			'Payment processing failed, retry scheduled',
			payment_id=event.payment_id,
			attempt=retry_count + 1,
			delay=delay,
			error=str(exc),
		)
		return

	await broker.publish(
		event.to_dict(),
		queue=dlq_queue,
		headers={RETRY_COUNT_HEADER: retry_count},
	)
	logger.error(
		'Payment processing exhausted retries, moved to DLQ',
		payment_id=event.payment_id,
		attempts=retry_count,
		error=str(exc),
	)
