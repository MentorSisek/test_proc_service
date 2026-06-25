from fastapi import FastAPI

from config import settings
from presentation.api.middlewares import ErrorMiddleware, LoggingMiddleware
from presentation.api.routers import payment_router

_debug = settings.logger.level.upper() == 'DEBUG'

app = FastAPI(
	title='Payment Processing API',
	description='Асинхронный сервис процессинга платежей',
	version='0.1.0',
	docs_url='/docs',
	redoc_url='/redoc',
	openapi_url='/openapi.json',
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorMiddleware)

app.include_router(payment_router)


@app.get('/health')
async def health():
	return {'status': 'ok'}
