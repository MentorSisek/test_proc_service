import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from logger import logger, set_trace_id

_SKIP_PATHS = {'/health', '/docs', '/redoc', '/openapi.json', '/favicon.ico'}


class LoggingMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next) -> Response:
		if request.url.path in _SKIP_PATHS:
			return await call_next(request)

		set_trace_id(str(uuid.uuid4()))

		start = time.perf_counter()
		response = await call_next(request)
		duration_ms = round((time.perf_counter() - start) * 1000)

		if request.scope.get('route') is not None:
			logger.info(
				'Request finished',
				method=request.method,
				path=request.url.path,
				status_code=response.status_code,
				duration_ms=duration_ms,
			)

		return response
