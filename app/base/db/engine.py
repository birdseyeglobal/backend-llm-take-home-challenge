from typing import Any

from sqlalchemy import Engine
from sqlmodel import create_engine
from tenacity import retry, stop_after_attempt, wait_exponential

from app.base.config import settings

@retry(wait=wait_exponential(min=1, max=20), stop=stop_after_attempt(6))
def create_engine_with_retry(**kwargs: Any) -> Engine:
    return create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        # AlloyDB is using its own managed pooling so we keep this small
        pool_pre_ping=True,  # evict stale sockets before handing to requests
        pool_use_lifo=True,  # reduce tail latency for bursty traffic
        connect_args={
            "connect_timeout": 10,
            # TCP keepalives help with PSC/NAT idles
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
        **kwargs,
    )

engine = create_engine_with_retry(pool_size=4, max_overflow=4)
