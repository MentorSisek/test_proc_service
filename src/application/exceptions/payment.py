from .base import ApplicationException, NotFoundError


class PaymentNotFoundError(NotFoundError):
	def __init__(self):
		super().__init__('Платёж не найден')


class WebhookDeliveryError(ApplicationException):
	"""Не удалось доставить webhook — сигнал к повторной обработке сообщения."""

	def __init__(self, url: str):
		super().__init__(f'Не удалось доставить webhook на {url}')
