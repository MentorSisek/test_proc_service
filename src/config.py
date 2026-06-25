from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
	user: str = Field(alias='postgres_user')
	password: str = Field(alias='postgres_password')
	host: str = Field(alias='postgres_host')
	port: int = Field(alias='postgres_port')
	db: str = Field(alias='postgres_db')

	@property
	def dsn(self) -> str:
		return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'


class RabbitMQSettings(BaseSettings):
	user: str = Field(alias='rabbitmq_default_user')
	password: str = Field(alias='rabbitmq_default_pass')
	host: str = Field(alias='rabbitmq_host')
	port: int = Field(alias='rabbitmq_port')
	vhost: str = Field(default='/', alias='rabbitmq_vhost')

	@property
	def dsn(self) -> str:
		return f'amqp://{self.user}:{self.password}@{self.host}:{self.port}{self.vhost}'


class APISettings(BaseSettings):
	key: str = Field(alias='api_key')


class ProcessingSettings(BaseSettings):
	"""Параметры эмуляции обработки и доставки webhook."""

	min_delay_seconds: float = Field(default=2.0, alias='processing_min_delay_seconds')
	max_delay_seconds: float = Field(default=5.0, alias='processing_max_delay_seconds')
	success_rate: float = Field(default=0.9, alias='processing_success_rate')

	max_retries: int = Field(default=3, alias='processing_max_retries')
	retry_base_delay_seconds: float = Field(
		default=2.0, alias='processing_retry_base_delay_seconds'
	)
	webhook_timeout_seconds: float = Field(
		default=10.0, alias='processing_webhook_timeout_seconds'
	)


class OutboxSettings(BaseSettings):
	"""Параметры relay-процесса, публикующего события из outbox."""

	poll_interval_seconds: float = Field(
		default=1.0, alias='outbox_poll_interval_seconds'
	)
	batch_size: int = Field(default=50, alias='outbox_batch_size')


class LoggerSettings(BaseSettings):
	level: str = Field(default='INFO', alias='logger_level_mode')


class Settings(BaseSettings):
	postgres: PostgresSettings = PostgresSettings()  # pyright: ignore
	rabbitmq: RabbitMQSettings = RabbitMQSettings()  # pyright: ignore
	api: APISettings = APISettings()  # pyright: ignore
	processing: ProcessingSettings = ProcessingSettings()
	outbox: OutboxSettings = OutboxSettings()
	logger: LoggerSettings = LoggerSettings()


settings = Settings()  # pyright: ignore
