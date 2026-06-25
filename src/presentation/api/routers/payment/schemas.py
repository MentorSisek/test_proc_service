from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl

from domain.entities import PaymentEntity
from domain.enums import Currency, PaymentStatus


class CreatePaymentRequest(BaseModel):
	amount: Decimal = Field(gt=0)
	currency: Currency
	description: str | None = Field(default=None, max_length=1024)
	metadata: dict = Field(default_factory=dict)
	webhook_url: HttpUrl | None = None


class CreatePaymentResponse(BaseModel):
	payment_id: str
	status: PaymentStatus
	created_at: datetime

	@classmethod
	def create(cls, payment: PaymentEntity) -> 'CreatePaymentResponse':
		return cls(
			payment_id=payment.id,
			status=payment.status,
			created_at=payment.created_at,
		)


class PaymentResponse(BaseModel):
	id: str
	amount: Decimal
	currency: Currency
	description: str | None
	metadata: dict
	status: PaymentStatus
	idempotency_key: str
	webhook_url: str | None
	created_at: datetime
	processed_at: datetime | None

	@classmethod
	def create(cls, payment: PaymentEntity) -> 'PaymentResponse':
		return cls(
			id=payment.id,
			amount=payment.money.amount,
			currency=payment.money.currency,
			description=payment.description,
			metadata=payment.metadata,
			status=payment.status,
			idempotency_key=payment.idempotency_key,
			webhook_url=payment.webhook_url,
			created_at=payment.created_at,
			processed_at=payment.processed_at,
		)
