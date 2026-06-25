from domain.ports import PaymentGateway
from domain.repositories import PaymentRepository
from logger import logger


class ProcessPaymentUseCase:
	"""Провести платёж через шлюз и зафиксировать итоговый статус.

	Идемпотентен: уже обработанный платёж (повторная доставка сообщения) повторно
	через шлюз не проводится. Статус фиксируется отдельно от доставки webhook, чтобы
	сбой webhook не откатывал результат обработки.
	"""

	def __init__(self, payment_repo: PaymentRepository, gateway: PaymentGateway):
		self.payment_repo = payment_repo
		self.gateway = gateway

	async def execute(self, payment_id: str) -> None:
		payment = await self.payment_repo.get_by_id(payment_id)
		if not payment:
			logger.warning('Payment not found, skipping', payment_id=payment_id)
			return

		if payment.is_processed:
			return

		success = await self.gateway.charge(payment)
		if success:
			payment.mark_succeeded()
		else:
			payment.mark_failed()
		await self.payment_repo.update(payment)
		logger.info(
			'Payment processed',
			payment_id=payment.id,
			status=payment.status,
		)
