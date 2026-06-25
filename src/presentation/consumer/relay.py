import asyncio

from faststream.rabbit import RabbitBroker

from infrastructure.database.sql.connection import SessionFactory
from infrastructure.database.sql.repositories import SQLOutboxRepository
from infrastructure.messaging import payments_exchange
from logger import logger


class OutboxRelay:
	"""Опрашивает таблицу outbox и публикует неотправленные события в брокер.

	Запускается фоновой задачей рядом с consumer. Берёт записи через
	SELECT ... FOR UPDATE SKIP LOCKED, публикует и помечает опубликованными в одной
	транзакции — гарантия at-least-once доставки. Дубликаты безопасны: обработчик
	платежа идемпотентен.
	"""

	def __init__(self, broker: RabbitBroker, poll_interval: float, batch_size: int):
		self._broker = broker
		self._poll_interval = poll_interval
		self._batch_size = batch_size

	async def run(self) -> None:
		logger.info('[Outbox relay] started')
		while True:
			try:
				published = await self._publish_batch()
				if published:
					logger.info('[Outbox relay] batch published', count=published)
			except Exception as exc:
				logger.error('[Outbox relay] batch failed', error=str(exc))
			await asyncio.sleep(self._poll_interval)

	async def _publish_batch(self) -> int:
		async with SessionFactory() as session:
			try:
				repo = SQLOutboxRepository(session=session)
				messages = await repo.fetch_pending(self._batch_size)
				for message in messages:
					await self._broker.publish(
						message.payload,
						exchange=payments_exchange,
						routing_key=message.routing_key,
					)
					await repo.mark_published(message)
				await session.commit()
				return len(messages)
			except Exception:
				await session.rollback()
				raise
