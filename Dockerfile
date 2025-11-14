# The builder image, used to build the virtual environment
FROM python:3.11-buster AS builder

RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# service runtime
FROM python:3.11-slim-bookworm AS service

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY app ./app
COPY .env ./.env
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations
COPY uvicorn_disable_logging.json ./uvicorn_disable_logging.json

ENV LOG_JSON_FORMAT="1" \
    LOG_LEVEL="INFO"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--log-config", "uvicorn_disable_logging.json", "--workers", "2"]