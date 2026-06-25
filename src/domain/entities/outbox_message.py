from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from domain.enums.outbox_status import OutboxStatus


@dataclass(kw_only=True)
class OutboxMessageEntity:
	"""Запись transactional outbox.

	Сохраняется в одной транзакции с бизнес-сущностью, а отдельный relay-процесс
	публикует её в брокер и помечает опубликованной. Гарантирует at-least-once доставку.
	"""

	id: str = field(default_factory=lambda: str(uuid4()))

	routing_key: str  # куда публиковать (routing key основного обменника)
	payload: dict  # тело события

	status: OutboxStatus = OutboxStatus.PENDING
	created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
	published_at: datetime | None = None

	@classmethod
	def create(cls, routing_key: str, payload: dict) -> 'OutboxMessageEntity':
		return cls(routing_key=routing_key, payload=payload)

	def mark_published(self) -> None:
		self.status = OutboxStatus.PUBLISHED
		self.published_at = datetime.now(UTC)
