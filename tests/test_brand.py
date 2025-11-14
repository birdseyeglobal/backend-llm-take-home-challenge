from fastapi.testclient import TestClient
from sqlmodel import Session

from app.brand.db.models import Brand

def test_api(
    client: TestClient,
    session: Session,
) -> None:
    post_response = client.post(
        "public/api/brands",
        json={
            "url": "https://www.google.com/",
            "docs": ["https://www.google.com/docs/about/"],
        },
    )
    assert post_response.status_code == 200
    post_response_json = post_response.json()
    
    assert post_response_json.get("id") is not None
    assert post_response_json.get("url") == "https://www.google.com/"
    assert post_response_json.get("docs") == ["https://www.google.com/docs/about/"]

    brand = session.get(Brand, post_response_json.get("id"))
    assert brand is not None
    assert brand.url == "https://www.google.com/"
    assert brand.docs == ["https://www.google.com/docs/about/"]

    get_response = client.get(
        f"public/api/brands/{post_response_json.get('id')}",
    )
    assert get_response.status_code == 200
    get_response_json = get_response.json()
    assert get_response_json.get("id") == post_response_json.get("id")
    assert get_response_json.get("url") == "https://www.google.com/"
    assert get_response_json.get("docs") == ["https://www.google.com/docs/about/"]

    session.delete(brand)
    session.commit()