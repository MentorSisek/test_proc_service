from faststream.rabbit import RabbitBroker

from config import settings
from presentation.consumer.middlewares import ErrorMiddleware

broker = RabbitBroker(
	settings.rabbitmq.dsn,
	logger=None,
	middlewares=[ErrorMiddleware],
)
