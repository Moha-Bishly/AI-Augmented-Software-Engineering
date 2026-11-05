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
    hid = client.post("/habits", json={"name": "Water"}).json()["id"]
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


def test_streak_unknown_habit_404():
    r = client.get("/habits/99999/streak")
    assert r.status_code == 404
