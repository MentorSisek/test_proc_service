from enum import StrEnum


class OutboxStatus(StrEnum):
	PENDING = 'pending'  # Ожидает публикации в брокер
	PUBLISHED = 'published'  # Опубликовано
