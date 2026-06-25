"""Базовые исключения application layer."""


class ApplicationException(Exception):
	"""Базовое исключение для application layer."""

	def __init__(self, message: str):
		self.message = message
		super().__init__(message)


class NotFoundError(ApplicationException):
	"""Ресурс не найден."""

	pass


class ValidationError(ApplicationException):
	"""Ошибка валидации."""

	pass


class UnauthorizedError(ApplicationException):
	"""Ошибка авторизации."""

	pass
