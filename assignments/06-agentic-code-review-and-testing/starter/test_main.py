from datetime import date, timedelta

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


# --- Validation Tests ---


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
        "20260922",  # Python 3.11+ fromisoformat edge case caught by CodeRabbit
        "2026-W39-2",  # ISO week date caught by CodeRabbit
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


# --- Streak Tests ---


def test_streak_zero_checkins():
    hid = client.post("/habits", json={"name": "Meditate"}).json()["id"]
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 0}


def test_streak_consecutive_days():
    hid = client.post("/habits", json={"name": "Journaling"}).json()["id"]
    today = date.today()
    d1 = (today - timedelta(days=2)).isoformat()
    d2 = (today - timedelta(days=1)).isoformat()
    d3 = today.isoformat()

    client.post(f"/habits/{hid}/checkin", json={"day": d1})
    client.post(f"/habits/{hid}/checkin", json={"day": d2})
    client.post(f"/habits/{hid}/checkin", json={"day": d3})

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 3}


def test_streak_broken():
    hid = client.post("/habits", json={"name": "Workout"}).json()["id"]
    today = date.today()
    d1 = (today - timedelta(days=2)).isoformat()
    d3 = today.isoformat()

    # Checked in today and 2 days ago, but missed yesterday
    client.post(f"/habits/{hid}/checkin", json={"day": d1})
    client.post(f"/habits/{hid}/checkin", json={"day": d3})

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 1}


def test_streak_duplicate_checkin_same_day():
    hid = client.post("/habits", json={"name": "Hydration"}).json()["id"]
    today = date.today().isoformat()
    client.post(f"/habits/{hid}/checkin", json={"day": today})
    client.post(f"/habits/{hid}/checkin", json={"day": today})

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 1}


def test_streak_with_custom_today_query_param():
    hid = client.post("/habits", json={"name": "Running"}).json()["id"]
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-20"})
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-21"})
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-22"})

    r = client.get(f"/habits/{hid}/streak?today=2026-09-22")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 3}

    r_invalid = client.get(f"/habits/{hid}/streak?today=invalid-date")
    assert r_invalid.status_code == 400


def test_streak_explicit_empty_today_returns_400():
    # Edge case caught by CodeRabbit review on PR #1
    hid = client.post("/habits", json={"name": "Guitar"}).json()["id"]
    r = client.get(f"/habits/{hid}/streak?today=")
    assert r.status_code == 400


def test_streak_active_through_yesterday_with_custom_today():
    # Test gap identified by CodeRabbit review on PR #1
    hid = client.post("/habits", json={"name": "Floss"}).json()["id"]
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-20"})
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-21"})
    # No check-in on 2026-09-22 (today)
    r = client.get(f"/habits/{hid}/streak?today=2026-09-22")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 2}


def test_streak_unknown_habit_404():
    r = client.get("/habits/99999/streak")
    assert r.status_code == 404
