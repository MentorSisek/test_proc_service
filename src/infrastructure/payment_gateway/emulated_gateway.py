import asyncio
import random

from domain.entities import PaymentEntity
from domain.ports import PaymentGateway
from logger import logger


class EmulatedPaymentGateway(PaymentGateway):
	"""Эмуляция внешнего платёжного шлюза.

	Имитирует сетевую задержку (min..max секунд) и исход платежа с заданной
	вероятностью успеха.
	"""

	def __init__(
		self,
		min_delay_seconds: float,
		max_delay_seconds: float,
		success_rate: float,
	):
		self._min_delay = min_delay_seconds
		self._max_delay = max_delay_seconds
		self._success_rate = success_rate

	async def charge(self, payment: PaymentEntity) -> bool:
		delay = random.uniform(self._min_delay, self._max_delay)
		await asyncio.sleep(delay)
		success = random.random() < self._success_rate
		logger.debug(
			'Gateway charge emulated',
			payment_id=payment.id,
			delay=round(delay, 2),
			success=success,
		)
		return success
