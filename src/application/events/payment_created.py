from dataclasses import dataclass


class PaymentEventType:
	NEW = 'payments.new'


@dataclass(kw_only=True)
class PaymentCreatedEvent:
	"""Событие очереди `payments.new`. Несёт только id — сам платёж читается из БД."""

	payment_id: str

	def to_dict(self) -> dict:
		return {'payment_id': self.payment_id}

	@classmethod
	def create(cls, payment_id: str) -> 'PaymentCreatedEvent':
		return cls(payment_id=payment_id)
