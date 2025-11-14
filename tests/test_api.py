import json
import os

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "route,expected_status_code",
    [
        ("openapi.json", 200),
        ("docs", 200),
    ],
    ids=[
        "openapi",
        "docs",
    ],
)
def test_routes(
    client: TestClient,
    route: str,
    expected_status_code: int,
) -> None:
    """
    Test basic fast api routes
    """
    response = client.get(
        f"/{route}",
    )

    if route == "openapi.json":
        with open("openapi.json", "w") as f:
            json.dump(response.json(), f)
        os.remove("openapi.json")

    assert response.status_code == expected_status_code
