from decimal import Decimal

import pytest

from domain.entities import PaymentEntity
from domain.enums import Currency, PaymentStatus
from domain.value_objects import Money


def _make_payment() -> PaymentEntity:
	return PaymentEntity.create(
		amount=Decimal('100.00'),
		currency=Currency.RUB,
		idempotency_key='key-1',
	)


def test_create_defaults_to_pending():
	payment = _make_payment()
	assert payment.status == PaymentStatus.PENDING
	assert payment.processed_at is None
	assert not payment.is_processed
	assert payment.money == Money(amount=Decimal('100.00'), currency=Currency.RUB)


def test_mark_succeeded_sets_status_and_processed_at():
	payment = _make_payment()
	payment.mark_succeeded()
	assert payment.status == PaymentStatus.SUCCEEDED
	assert payment.processed_at is not None
	assert payment.is_processed


def test_mark_failed_sets_status_and_processed_at():
	payment = _make_payment()
	payment.mark_failed()
	assert payment.status == PaymentStatus.FAILED
	assert payment.processed_at is not None


def test_cannot_process_twice():
	payment = _make_payment()
	payment.mark_succeeded()
	with pytest.raises(ValueError):
		payment.mark_failed()


def test_money_must_be_positive():
	with pytest.raises(ValueError):
		Money(amount=Decimal('0'), currency=Currency.USD)


def test_money_must_be_decimal():
	with pytest.raises(TypeError):
		Money(amount=100, currency=Currency.USD)  # type: ignore[arg-type]
