from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models import Base
from config.settings import env


engine = create_async_engine(
    url=env.Database_url,
    echo=True
)
session = async_sessionmaker(engine)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
