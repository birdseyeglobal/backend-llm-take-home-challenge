from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from app.base.api.routes import router as api_router
from app.base.config import settings


def run_migrations() -> None:
    alembic_config = Config("alembic.ini")
    alembic_config.attributes["configure_logger"] = False
    command.upgrade(alembic_config, "head")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    load_dotenv()
    if settings.MODE == "production":
        run_migrations()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow only POST method
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
)

if settings.ENV == "dev":

    @app.get("/public/openapi.json", include_in_schema=False)
    def custom_openapi() -> JSONResponse:
        return JSONResponse(app.openapi())


app.include_router(api_router, prefix="/public")
add_pagination(app)
