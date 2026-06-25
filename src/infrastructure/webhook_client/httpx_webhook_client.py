import httpx

from domain.ports import WebhookClient


class HttpxWebhookClient(WebhookClient):
	def __init__(self, timeout_seconds: float):
		self._timeout = timeout_seconds

	async def send(self, url: str, payload: dict) -> None:
		async with httpx.AsyncClient(timeout=self._timeout) as client:
			response = await client.post(url, json=payload)
			response.raise_for_status()
