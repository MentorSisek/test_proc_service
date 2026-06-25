from sqlalchemy.ext.asyncio import AsyncSession

from application.use_cases.processing import (
	DeliverWebhookUseCase,
	ProcessPaymentUseCase,
)
from config import settings
from domain.ports import PaymentGateway, WebhookClient
from infrastructure.database.sql.repositories import SQLPaymentRepository
from infrastructure.payment_gateway import EmulatedPaymentGateway
from infrastructure.webhook_client import HttpxWebhookClient


def get_payment_gateway() -> PaymentGateway:
	return EmulatedPaymentGateway(
		min_delay_seconds=settings.processing.min_delay_seconds,
		max_delay_seconds=settings.processing.max_delay_seconds,
		success_rate=settings.processing.success_rate,
	)


def get_webhook_client() -> WebhookClient:
	return HttpxWebhookClient(
		timeout_seconds=settings.processing.webhook_timeout_seconds
	)


def get_process_payment_use_case(
	session: AsyncSession,
	gateway: PaymentGateway,
) -> ProcessPaymentUseCase:
	return ProcessPaymentUseCase(
		payment_repo=SQLPaymentRepository(session=session),
		gateway=gateway,
	)


def get_deliver_webhook_use_case(
	session: AsyncSession,
	webhook_client: WebhookClient,
) -> DeliverWebhookUseCase:
	return DeliverWebhookUseCase(
		payment_repo=SQLPaymentRepository(session=session),
		webhook_client=webhook_client,
	)
