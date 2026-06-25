from decimal import Decimal

from application.events import PaymentCreatedEvent, PaymentEventType
from domain.entities import OutboxMessageEntity, PaymentEntity
from domain.enums import Currency
from domain.repositories import OutboxRepository, PaymentRepository
from logger import logger


class CreatePaymentUseCase:
	"""Создать платёж и положить событие в outbox в одной транзакции.

	Защита от дублей по Idempotency-Key: повторный запрос с тем же ключом возвращает
	уже созданный платёж, не создавая новый и не публикуя событие повторно.
	"""

	def __init__(
		self,
		payment_repo: PaymentRepository,
		outbox_repo: OutboxRepository,
	):
		self.payment_repo = payment_repo
		self.outbox_repo = outbox_repo

	async def execute(
		self,
		idempotency_key: str,
		amount: Decimal,
		currency: Currency,
		description: str | None = None,
		metadata: dict | None = None,
		webhook_url: str | None = None,
	) -> PaymentEntity:
		existing = await self.payment_repo.get_by_idempotency_key(idempotency_key)
		if existing:
			logger.info(
				'Idempotent replay, returning existing payment',
				idempotency_key=idempotency_key,
				payment_id=existing.id,
			)
			return existing

		payment = PaymentEntity.create(
			amount=amount,
			currency=currency,
			idempotency_key=idempotency_key,
			description=description,
			metadata=metadata,
			webhook_url=webhook_url,
		)
		await self.payment_repo.create(payment)
		await self.outbox_repo.add(
			OutboxMessageEntity.create(
				routing_key=PaymentEventType.NEW,
				payload=PaymentCreatedEvent.create(payment.id).to_dict(),
			)
		)

		logger.info(
			'Payment created',
			payment_id=payment.id,
			amount=str(payment.money.amount),
			currency=payment.money.currency,
		)
		return payment
