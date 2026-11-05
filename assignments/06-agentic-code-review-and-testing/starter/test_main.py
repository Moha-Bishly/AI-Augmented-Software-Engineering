from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_and_list_habit():
    r = client.post("/habits", json={"name": "Read 20 minutes"})
    assert r.status_code == 200
    hid = r.json()["id"]
    r2 = client.get("/habits")
    assert r2.status_code == 200
    assert any(h["id"] == hid for h in r2.json())


def test_checkin_flow():
    hid = client.post("/habits", json={"name": "Stretch"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 200
    r2 = client.get(f"/habits/{hid}/checkins")
    assert r2.json() == ["2026-09-22"]


def test_checkin_unknown_habit_404():
    r = client.post("/habits/99999/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 404


def test_create_habit_rejects_empty_name():
    r = client.post("/habits", json={"name": ""})
    assert r.status_code == 422
    errors = r.json().get("detail", [])
    assert any(
        "at least 1 character" in str(e).lower() or "empty" in str(e).lower()
        for e in errors
    )


def test_create_habit_rejects_whitespace_name():
    r = client.post("/habits", json={"name": "   "})
    assert r.status_code == 422
    errors = r.json().get("detail", [])
    assert any(
        "whitespace" in str(e).lower() or "empty" in str(e).lower() for e in errors
    )


def test_create_habit_rejects_missing_name():
    r = client.post("/habits", json={})
    assert r.status_code == 422


def test_checkin_rejects_malformed_day_formats():
    hid = client.post("/habits", json={"name": "Drink Water"}).json()["id"]

    malformed_days = [
        "not-a-date",
        "2026/09/22",
        "09-22-2026",
        "2026-02-31",  # Invalid calendar date
        "2026-13-01",  # Invalid month
        "",
    ]
    for bad_day in malformed_days:
        r = client.post(f"/habits/{hid}/checkin", json={"day": bad_day})
        assert (
            r.status_code == 422
        ), f"Expected 422 for day={bad_day}, got {r.status_code}"


def test_checkin_rejects_missing_day():
    hid = client.post("/habits", json={"name": "Yoga"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={})
    assert r.status_code == 422
