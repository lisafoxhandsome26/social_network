from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import env
from dotinputs.routers import router
from database.core import close_session
from database.dao import create_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_users()
    yield
    await close_session()


def get_application(lifespan) -> FastAPI:
    app = FastAPI(title=env.PROJECT_NAME, lifespan=lifespan)
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=env.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["*"],
    )
    return app


app = get_application(lifespan)
