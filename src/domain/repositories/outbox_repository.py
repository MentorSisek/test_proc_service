from abc import ABC, abstractmethod

from domain.entities import OutboxMessageEntity


class OutboxRepository(ABC):
	@abstractmethod
	async def add(self, message: OutboxMessageEntity) -> None:
		"""Добавить запись в outbox (в той же транзакции, что и бизнес-сущность)."""
		...

	@abstractmethod
	async def fetch_pending(self, limit: int) -> list[OutboxMessageEntity]:
		"""Забрать пачку неопубликованных записей с блокировкой строк.

		Использует SELECT ... FOR UPDATE SKIP LOCKED, чтобы несколько relay-воркеров
		не публиковали одно и то же событие дважды.
		"""
		...

	@abstractmethod
	async def mark_published(self, message: OutboxMessageEntity) -> None:
		"""Пометить запись как опубликованную."""
		...
