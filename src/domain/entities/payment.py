from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from domain.enums.currency import Currency
from domain.enums.payment_status import PaymentStatus
from domain.value_objects.money import Money


@dataclass(kw_only=True)
class PaymentEntity:
	id: str = field(default_factory=lambda: str(uuid4()))

	money: Money
	description: str | None = None
	metadata: dict = field(default_factory=dict)  # произвольная доп. информация

	status: PaymentStatus = PaymentStatus.PENDING
	idempotency_key: str  # уникальный ключ для защиты от дублей
	webhook_url: str | None = None  # куда уведомить о результате

	created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
	processed_at: datetime | None = None  # момент завершения обработки

	@classmethod
	def create(
		cls,
		amount: Decimal,
		currency: Currency,
		idempotency_key: str,
		description: str | None = None,
		metadata: dict | None = None,
		webhook_url: str | None = None,
	) -> 'PaymentEntity':
		return cls(
			money=Money.create(amount=amount, currency=currency),
			description=description,
			metadata=metadata or {},
			idempotency_key=idempotency_key,
			webhook_url=webhook_url,
		)

	def mark_succeeded(self) -> None:
		"""Платёж успешно обработан шлюзом."""
		if self.status != PaymentStatus.PENDING:
			raise ValueError('Обработать можно только платёж в статусе pending')
		self.status = PaymentStatus.SUCCEEDED
		self.processed_at = datetime.now(UTC)

	def mark_failed(self) -> None:
		"""Шлюз отклонил платёж."""
		if self.status != PaymentStatus.PENDING:
			raise ValueError('Обработать можно только платёж в статусе pending')
		self.status = PaymentStatus.FAILED
		self.processed_at = datetime.now(UTC)

	@property
	def is_processed(self) -> bool:
		return self.status in (PaymentStatus.SUCCEEDED, PaymentStatus.FAILED)
