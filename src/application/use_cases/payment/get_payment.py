from application.exceptions import PaymentNotFoundError
from domain.entities import PaymentEntity
from domain.repositories import PaymentRepository


class GetPaymentUseCase:
	def __init__(self, payment_repo: PaymentRepository):
		self.payment_repo = payment_repo

	async def execute(self, payment_id: str) -> PaymentEntity:
		payment = await self.payment_repo.get_by_id(payment_id)
		if not payment:
			raise PaymentNotFoundError()
		return payment
