from application.exceptions import WebhookDeliveryError
from domain.entities import PaymentEntity
from domain.ports import WebhookClient
from domain.repositories import PaymentRepository
from logger import logger


class DeliverWebhookUseCase:
	"""Доставить результат платежа на webhook_url.

	Выполняется после фиксации статуса. Ошибка доставки пробрасывается как
	WebhookDeliveryError — сигнал вызывающей стороне инициировать повторную попытку.
	"""

	def __init__(self, payment_repo: PaymentRepository, webhook_client: WebhookClient):
		self.payment_repo = payment_repo
		self.webhook_client = webhook_client

	async def execute(self, payment_id: str) -> None:
		payment = await self.payment_repo.get_by_id(payment_id)
		if not payment or not payment.webhook_url:
			return

		try:
			await self.webhook_client.send(
				url=payment.webhook_url,
				payload=self._build_payload(payment),
			)
		except Exception as e:
			logger.warning(
				'Webhook delivery failed',
				payment_id=payment.id,
				webhook_url=payment.webhook_url,
				error=str(e),
			)
			raise WebhookDeliveryError(payment.webhook_url) from e

		logger.info(
			'Webhook delivered',
			payment_id=payment.id,
			webhook_url=payment.webhook_url,
		)

	@staticmethod
	def _build_payload(payment: PaymentEntity) -> dict:
		return {
			'payment_id': payment.id,
			'status': payment.status,
			'amount': str(payment.money.amount),
			'currency': payment.money.currency,
			'metadata': payment.metadata,
			'processed_at': payment.processed_at.isoformat()
			if payment.processed_at
			else None,
		}
