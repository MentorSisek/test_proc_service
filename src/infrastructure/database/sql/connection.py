from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings

engine = create_async_engine(
	settings.postgres.dsn,
	pool_size=20,
	max_overflow=10,
	pool_timeout=5,
)

SessionFactory = async_sessionmaker(
	engine,
	class_=AsyncSession,
	expire_on_commit=False,
)
