import asyncio

from faststream import FastStream

from config import settings
from infrastructure.messaging import dlq_queue, retry_queue
from presentation.consumer import routers  # noqa: F401  регистрирует подписчиков
from presentation.consumer.broker import broker
from presentation.consumer.relay import OutboxRelay

app = FastStream(broker, logger=None)

_background_tasks: set[asyncio.Task] = set()


@app.after_startup
async def on_startup() -> None:
	# Очереди retry/DLQ не имеют подписчиков, поэтому объявляем их вручную.
	await broker.declare_queue(retry_queue)
	await broker.declare_queue(dlq_queue)

	relay = OutboxRelay(
		broker=broker,
		poll_interval=settings.outbox.poll_interval_seconds,
		batch_size=settings.outbox.batch_size,
	)
	task = asyncio.create_task(relay.run())
	_background_tasks.add(task)
	task.add_done_callback(_background_tasks.discard)
