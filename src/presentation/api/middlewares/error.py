from fastapi import Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from application.exceptions import (
	ApplicationException,
	NotFoundError,
	UnauthorizedError,
	ValidationError,
)
from logger import logger


class ErrorMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next) -> Response:
		try:
			return await call_next(request)
		except ApplicationException as exc:
			status_code = status.HTTP_400_BAD_REQUEST
			if isinstance(exc, NotFoundError):
				status_code = status.HTTP_404_NOT_FOUND
			elif isinstance(exc, UnauthorizedError):
				status_code = status.HTTP_401_UNAUTHORIZED
			elif isinstance(exc, ValidationError):
				status_code = status.HTTP_400_BAD_REQUEST

			return JSONResponse(
				status_code=status_code, content={'detail': exc.message}
			)
		except RequestValidationError as exc:
			logger.error(
				'Request validation failed',
				method=request.method,
				path=request.url.path,
				errors=exc.errors(),
			)
			return JSONResponse(
				status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
				content={'detail': exc.errors()},
			)
		except HTTPException as exc:
			return JSONResponse(
				status_code=exc.status_code,
				content={'detail': exc.detail},
			)
		except Exception as exc:
			logger.critical(
				'Unhandled exception',
				method=request.method,
				path=request.url.path,
				error=str(exc),
			)
			return JSONResponse(
				status_code=500, content={'detail': 'Internal server error'}
			)
