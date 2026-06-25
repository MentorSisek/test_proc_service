from abc import ABC, abstractmethod

from domain.entities import PaymentEntity


class PaymentRepository(ABC):
	@abstractmethod
	async def create(self, payment: PaymentEntity) -> None:
		"""Создать платёж."""
		...

	@abstractmethod
	async def get_by_id(self, payment_id: str) -> PaymentEntity | None:
		"""Вернуть платёж по ID или None если не найден."""
		...

	@abstractmethod
	async def get_by_idempotency_key(
		self, idempotency_key: str
	) -> PaymentEntity | None:
		"""Вернуть платёж по idempotency-ключу или None."""
		...

	@abstractmethod
	async def update(self, payment: PaymentEntity) -> None:
		"""Сохранить изменения платежа."""
		...
