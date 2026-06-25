from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import OutboxMessageEntity
from domain.enums import OutboxStatus
from domain.repositories import OutboxRepository
from infrastructure.database.sql.models import SQLOutboxMessage


class SQLOutboxRepository(OutboxRepository):
	def __init__(self, session: AsyncSession):
		self._session = session

	async def add(self, message: OutboxMessageEntity) -> None:
		model = SQLOutboxMessage.from_entity(message)
		self._session.add(model)
		await self._session.flush()

	async def fetch_pending(self, limit: int) -> list[OutboxMessageEntity]:
		stmt = (
			select(SQLOutboxMessage)
			.where(SQLOutboxMessage.status == OutboxStatus.PENDING)
			.order_by(SQLOutboxMessage.created_at)
			.limit(limit)
			.with_for_update(skip_locked=True)
		)
		result = await self._session.execute(stmt)
		return [m.to_entity() for m in result.scalars().all()]

	async def mark_published(self, message: OutboxMessageEntity) -> None:
		message.mark_published()
		stmt = (
			update(SQLOutboxMessage)
			.where(SQLOutboxMessage.id == message.id)
			.values(status=message.status, published_at=message.published_at)
		)
		await self._session.execute(stmt)
