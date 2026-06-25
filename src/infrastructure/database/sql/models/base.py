from enum import Enum as PyEnum

from sqlalchemy import Enum
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
	pass


def pg_enum(enum_cls: type[PyEnum], name: str) -> Enum:
	"""PG enum, хранящий строковые значения (`.value`), а не имена членов.

	По умолчанию SQLAlchemy пишет имена членов; для StrEnum с значениями в нижнем
	регистре это расходится с типом в БД, поэтому используем values_callable.
	"""
	return Enum(
		enum_cls,
		name=name,
		values_callable=lambda enum: [member.value for member in enum],
	)
