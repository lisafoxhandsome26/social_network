from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config.settings import env


engine = create_async_engine(url=env.database_url, echo=False)
session = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


async def close_session():
    async with session() as sos:
        await sos.close()
