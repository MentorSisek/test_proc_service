from dataclasses import dataclass
from decimal import Decimal

from domain.enums.currency import Currency


@dataclass(frozen=True)
class Money:
	"""Денежная сумма с валютой. Сумма всегда строго положительная."""

	amount: Decimal
	currency: Currency

	def __post_init__(self) -> None:
		if not isinstance(self.amount, Decimal):
			raise TypeError('Money amount must be a Decimal')
		if self.amount <= 0:
			raise ValueError('Money amount must be positive')

	@classmethod
	def create(cls, amount: Decimal, currency: Currency) -> 'Money':
		return cls(amount=amount, currency=Currency(currency))

	def __str__(self) -> str:
		return f'{self.amount} {self.currency}'
