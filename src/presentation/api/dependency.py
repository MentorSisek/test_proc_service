from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from application.exceptions import UnauthorizedError
from application.use_cases.payment import CreatePaymentUseCase, GetPaymentUseCase
from config import settings
from domain.repositories import OutboxRepository, PaymentRepository
from infrastructure.database.sql.connection import SessionFactory
from infrastructure.database.sql.repositories import (
	SQLOutboxRepository,
	SQLPaymentRepository,
)
from logger import logger


# DB
async def get_db_session():
	async with SessionFactory() as session:
		logger.debug('DB session opened')
		try:
			yield session
			await session.commit()
			logger.debug('DB session committed')
		except Exception:
			await session.rollback()
			logger.debug('DB session rolled back')
			raise


def get_payment_repository(
	db_session: AsyncSession = Depends(get_db_session),
) -> PaymentRepository:
	return SQLPaymentRepository(session=db_session)


def get_outbox_repository(
	db_session: AsyncSession = Depends(get_db_session),
) -> OutboxRepository:
	return SQLOutboxRepository(session=db_session)


# Use cases
def get_create_payment_use_case(
	payment_repo=Depends(get_payment_repository),
	outbox_repo=Depends(get_outbox_repository),
) -> CreatePaymentUseCase:
	return CreatePaymentUseCase(payment_repo=payment_repo, outbox_repo=outbox_repo)


def get_payment_use_case(
	payment_repo=Depends(get_payment_repository),
) -> GetPaymentUseCase:
	return GetPaymentUseCase(payment_repo=payment_repo)


# Auth
async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
	"""Проверяет статический API-ключ в заголовке X-API-Key для всех эндпоинтов."""
	if x_api_key != settings.api.key:
		raise UnauthorizedError('Неверный или отсутствующий X-API-Key')


# Annotated dependencies
CreatePaymentUseCaseDep = Annotated[
	CreatePaymentUseCase, Depends(get_create_payment_use_case)
]
GetPaymentUseCaseDep = Annotated[GetPaymentUseCase, Depends(get_payment_use_case)]
IdempotencyKeyDep = Annotated[str, Header(alias='Idempotency-Key')]
