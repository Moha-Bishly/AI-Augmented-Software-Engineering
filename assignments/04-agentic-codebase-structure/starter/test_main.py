from contextlib import closing
import pytest
from fastapi.testclient import TestClient

from main import app, get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    with closing(get_db()) as conn:
        conn.execute("DELETE FROM links")
        conn.commit()
    yield


def test_shorten_and_redirect():
    r = client.post("/shorten", json={"url": "https://example.com"})
    assert r.status_code == 200
    code = r.json()["code"]
    assert code
    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.status_code == 307
    assert r2.headers["location"] == "https://example.com"


def test_rejects_bad_url():
    r = client.post("/shorten", json={"url": "ftp://nope"})
    assert r.status_code == 400


def test_unknown_code_404():
    r = client.get("/does-not-exist", follow_redirects=False)
    assert r.status_code == 404


def test_custom_alias_success():
    r = client.post("/shorten", json={"url": "https://docs.pytest.org", "alias": "pytest-docs"})
    assert r.status_code == 200
    assert r.json()["code"] == "pytest-docs"
    assert r.json()["short_url"] == "/pytest-docs"
    r2 = client.get("/pytest-docs", follow_redirects=False)
    assert r2.status_code == 307
    assert r2.headers["location"] == "https://docs.pytest.org"


def test_custom_alias_conflict_409():
    r1 = client.post("/shorten", json={"url": "https://first.com", "alias": "duplicate-code"})
    assert r1.status_code == 200
    r2 = client.post("/shorten", json={"url": "https://second.com", "alias": "duplicate-code"})
    assert r2.status_code == 409
