import uuid
from types import TracebackType

from faststream import BaseMiddleware

from application.exceptions import ApplicationException
from logger import logger, set_trace_id


class ErrorMiddleware(BaseMiddleware):
	async def on_receive(self) -> None:
		set_trace_id(str(uuid.uuid4()))

		raw = self.msg
		self._routing_key = getattr(
			getattr(raw, 'raw_message', None), 'routing_key', 'unknown'
		)
		body = getattr(raw, 'body', None)
		self._body = (
			body.decode() if isinstance(body, bytes) else str(body) if body else None
		)
		return await super().on_receive()

	async def after_processed(
		self,
		exc_type: type[BaseException] | None = None,
		exc_val: BaseException | None = None,
		exc_tb: TracebackType | None = None,
	) -> bool | None:
		if exc_type is not None and not issubclass(exc_type, ApplicationException):
			logger.critical(
				'Unhandled consumer exception',
				routing_key=self._routing_key,
				body=self._body,
				error=str(exc_val),
			)
		return await super().after_processed(exc_type, exc_val, exc_tb)
