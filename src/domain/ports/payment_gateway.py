from abc import ABC, abstractmethod

from domain.entities import PaymentEntity


class PaymentGateway(ABC):
	@abstractmethod
	async def charge(self, payment: PaymentEntity) -> bool:
		"""Провести платёж через внешний шлюз.

		Возвращает True при успехе и False при отказе шлюза.
		"""
		...
