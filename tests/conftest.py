# .init import must go first
from .init import POSTGRES_CONTAINER_PORT  # noqa: I001

import os
import socket
from collections.abc import Generator
from contextlib import contextmanager

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlmodel import Session, create_engine
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.postgres import PostgresContainer

from app.base.config import settings
from app.base.api.dependencies import get_session
from app.main import app

POSTGRES_IMAGE = "pgvector/pgvector:pg15"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "birdseye"
POSTGRES_DATABASE = "seo_service"


def _is_port_in_use(port: int) -> bool:
    """Try to bind to localhost:port. If it fails, the port is in use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # SO_REUSEADDR here just to avoid TIME_WAIT conflicts.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", port))
    except OSError:
        return True
    finally:
        sock.close()
    return False


@pytest.fixture(scope="session", autouse=True)
def ensure_ports_free() -> None:
    """
    Before anything else runs, error out if our DB or proxy ports are already
    bound locally.
    """
    if os.environ.get("SKIP_PORT_CHECK") == "1":
        return

    ports_to_check = {POSTGRES_CONTAINER_PORT}
    if settings.POSTGRES_PORT is not None:
        ports_to_check.add(int(settings.POSTGRES_PORT))
    in_use = [p for p in set(ports_to_check) if _is_port_in_use(p)]
    if in_use:
        raise Exception(
            f"ERROR: Test ports already in use: {', '.join(map(str, in_use))}"
        )


@pytest.fixture(scope="session")
def postgres_container(
    ensure_ports_free: None,
) -> Generator[PostgresContainer, None, None]:
    """
    Setup postgres container
    """
    postgres = PostgresContainer(
        image=POSTGRES_IMAGE,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DATABASE,
        port=5432,
    )
    with postgres.with_bind_ports(5432, POSTGRES_CONTAINER_PORT):
        wait_for_logs(
            postgres,
            r"UTC \[1\] LOG:  database system is ready to accept connections",
            10,
        )
        yield postgres


@pytest.fixture(scope="session")
def engine(
    postgres_container: PostgresContainer,
) -> Generator[Engine, None, None]:
    url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_CONTAINER_PORT}/{POSTGRES_DATABASE}"
    engine = create_engine(
        url,
        echo=False,
    )
    # SQLModel.metadata.create_all(engine)
    alembic_config = Config("alembic.ini")
    alembic_config.attributes["configure_logger"] = False
    command.upgrade(alembic_config, "head")
    command.check(alembic_config)
    # TODO: load mock data into db
    yield engine


def yield_database_session(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@contextmanager
def database_session(engine: Engine) -> Generator[Session, None, None]:
    try:
        db = next(yield_database_session(engine))
        yield db
    finally:
        db.close()


@pytest.fixture(name="session")
def session_fixture(engine: Engine) -> Generator[Session, None, None]:
    with database_session(engine) as session:
        try:
            yield session
        finally:
            # Roll back anything left open and close cleanly
            if session.in_transaction():
                session.rollback()
            session.close()


@pytest.fixture(autouse=True)
def set_dummy_llm_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensures pydantic-ai can construct the gateway Agent during VCR replay.
    The key is never sent over the network — VCR intercepts before it leaves the process."""
    monkeypatch.setenv("PYDANTIC_AI_GATEWAY_API_KEY", "test-vcr-key")


@pytest.fixture(scope="module")
def vcr_config() -> dict:
    # On CI (record_mode=none), tests replay from committed cassettes only.
    # Locally (record_mode=once), cassettes are recorded on first run when
    # PYDANTIC_AI_GATEWAY_API_KEY is set, then replayed on subsequent runs.
    import os

    record_mode = "none" if os.getenv("CI") else "once"
    return {
        "record_mode": record_mode,
        "filter_headers": ["authorization", "x-api-key"],
    }


@pytest.fixture(scope="module")
def vcr_cassette_dir(request: pytest.FixtureRequest) -> str:
    return str(request.fspath.dirpath("cassettes"))


@pytest.fixture(name="client")
def client_fixture(
    session: Session,
) -> Generator[TestClient, None, None]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
