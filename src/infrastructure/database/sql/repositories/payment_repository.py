from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import PaymentEntity
from domain.repositories import PaymentRepository
from infrastructure.database.sql.models import SQLPayment


class SQLPaymentRepository(PaymentRepository):
	def __init__(self, session: AsyncSession):
		self._session = session

	async def create(self, payment: PaymentEntity) -> None:
		model = SQLPayment.from_entity(payment)
		self._session.add(model)
		await self._session.flush()

	async def get_by_id(self, payment_id: str) -> PaymentEntity | None:
		stmt = select(SQLPayment).where(SQLPayment.id == payment_id)
		result = await self._session.execute(stmt)
		model = result.scalar_one_or_none()
		return model.to_entity() if model else None

	async def get_by_idempotency_key(
		self, idempotency_key: str
	) -> PaymentEntity | None:
		stmt = select(SQLPayment).where(SQLPayment.idempotency_key == idempotency_key)
		result = await self._session.execute(stmt)
		model = result.scalar_one_or_none()
		return model.to_entity() if model else None

	async def update(self, payment: PaymentEntity) -> None:
		model = SQLPayment.from_entity(payment)
		await self._session.merge(model)
		await self._session.flush()
