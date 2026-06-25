from abc import ABC, abstractmethod


class WebhookClient(ABC):
	@abstractmethod
	async def send(self, url: str, payload: dict) -> None:
		"""Отправить webhook-уведомление.

		Должен бросать исключение при сетевой ошибке или не-2xx ответе — это сигнал
		вызывающей стороне инициировать повторную попытку.
		"""
		...
