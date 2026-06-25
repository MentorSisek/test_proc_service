from enum import StrEnum


class PaymentStatus(StrEnum):
	PENDING = 'pending'  # Создан, ожидает обработки
	SUCCEEDED = 'succeeded'  # Успешно обработан
	FAILED = 'failed'  # Обработка завершилась ошибкой
