from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities import PaymentEntity
from domain.enums import Currency, PaymentStatus
from domain.value_objects import Money

from .base import Base, pg_enum


class SQLPayment(Base):
	__tablename__ = 'payments'

	id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)

	amount: Mapped[Decimal] = mapped_column(
		Numeric(precision=18, scale=2), nullable=False
	)
	currency: Mapped[Currency] = mapped_column(
		pg_enum(Currency, 'currency_enum'), nullable=False
	)
	description: Mapped[str | None] = mapped_column(String, nullable=True)
	meta: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, default=dict)

	status: Mapped[PaymentStatus] = mapped_column(
		pg_enum(PaymentStatus, 'payment_status_enum'), nullable=False, index=True
	)
	idempotency_key: Mapped[str] = mapped_column(
		String, nullable=False, unique=True, index=True
	)
	webhook_url: Mapped[str | None] = mapped_column(String, nullable=True)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False
	)
	processed_at: Mapped[datetime | None] = mapped_column(
		DateTime(timezone=True), nullable=True
	)

	@classmethod
	def from_entity(cls, entity: PaymentEntity) -> 'SQLPayment':
		return cls(
			id=entity.id,
			amount=entity.money.amount,
			currency=entity.money.currency,
			description=entity.description,
			meta=entity.metadata,
			status=entity.status,
			idempotency_key=entity.idempotency_key,
			webhook_url=entity.webhook_url,
			created_at=entity.created_at,
			processed_at=entity.processed_at,
		)

	def to_entity(self) -> PaymentEntity:
		return PaymentEntity(
			id=self.id,
			money=Money(amount=self.amount, currency=self.currency),
			description=self.description,
			metadata=self.meta,
			status=self.status,
			idempotency_key=self.idempotency_key,
			webhook_url=self.webhook_url,
			created_at=self.created_at,
			processed_at=self.processed_at,
		)
