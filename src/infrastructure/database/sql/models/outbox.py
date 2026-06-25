from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities import OutboxMessageEntity
from domain.enums import OutboxStatus

from .base import Base, pg_enum


class SQLOutboxMessage(Base):
	__tablename__ = 'outbox'

	id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True)

	routing_key: Mapped[str] = mapped_column(String, nullable=False)
	payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

	status: Mapped[OutboxStatus] = mapped_column(
		pg_enum(OutboxStatus, 'outbox_status_enum'),
		nullable=False,
		index=True,
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False
	)
	published_at: Mapped[datetime | None] = mapped_column(
		DateTime(timezone=True), nullable=True
	)

	@classmethod
	def from_entity(cls, entity: OutboxMessageEntity) -> 'SQLOutboxMessage':
		return cls(
			id=entity.id,
			routing_key=entity.routing_key,
			payload=entity.payload,
			status=entity.status,
			created_at=entity.created_at,
			published_at=entity.published_at,
		)

	def to_entity(self) -> OutboxMessageEntity:
		return OutboxMessageEntity(
			id=self.id,
			routing_key=self.routing_key,
			payload=self.payload,
			status=self.status,
			created_at=self.created_at,
			published_at=self.published_at,
		)
