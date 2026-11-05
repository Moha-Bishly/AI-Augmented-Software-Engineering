"""Habit Tracker — starter app for Week 6.

A tiny FastAPI service for habits and daily check-ins. You'll add features on
branches, open PRs, and compare your manual review with an AI reviewer.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload
Test:
    pytest
"""

import re
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

DB_PATH = Path(__file__).parent / "habits.db"

app = FastAPI(title="Habit Tracker")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_db()) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS habits (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS checkins (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                day      TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )""")
        conn.commit()


init_db()


class HabitIn(BaseModel):
    """Input payload for habit creation."""

    name: str = Field(..., min_length=1, description="Habit name cannot be empty")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Reject empty or whitespace-only habit names."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("habit name cannot be empty or whitespace only")
        return trimmed


class CheckinIn(BaseModel):
    """Input payload for habit check-in."""

    day: str  # ISO date, e.g. "2026-09-22"

    @field_validator("day")
    @classmethod
    def validate_day(cls, v: str) -> str:
        """Validate exact YYYY-MM-DD ISO calendar date."""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("invalid day format; expected YYYY-MM-DD")
        try:
            parsed = date.fromisoformat(v)
        except (ValueError, TypeError):
            raise ValueError("invalid calendar date")
        return parsed.isoformat()


@app.post("/habits")
def create_habit(habit: HabitIn):
    with closing(get_db()) as conn:
        cur = conn.execute("INSERT INTO habits (name) VALUES (?)", (habit.name,))
        conn.commit()
        return {"id": cur.lastrowid, "name": habit.name}


@app.get("/habits")
def list_habits():
    with closing(get_db()) as conn:
        rows = conn.execute("SELECT id, name FROM habits ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@app.post("/habits/{habit_id}/checkin")
def add_checkin(habit_id: int, checkin: CheckinIn):
    with closing(get_db()) as conn:
        habit = conn.execute(
            "SELECT id FROM habits WHERE id = ?", (habit_id,)
        ).fetchone()
        if habit is None:
            raise HTTPException(status_code=404, detail="unknown habit")
        conn.execute(
            "INSERT INTO checkins (habit_id, day) VALUES (?, ?)",
            (habit_id, checkin.day),
        )
        conn.commit()
    return {"habit_id": habit_id, "day": checkin.day}


@app.get("/habits/{habit_id}/checkins")
def list_checkins(habit_id: int):
    with closing(get_db()) as conn:
        rows = conn.execute(
            "SELECT day FROM checkins WHERE habit_id = ? ORDER BY day", (habit_id,)
        ).fetchall()
    return [r["day"] for r in rows]


@app.get("/habits/{habit_id}/streak")
def get_streak(habit_id: int, today: str | None = None):
    """Calculate the consecutive day check-in streak up to and including today."""
    with closing(get_db()) as conn:
        habit = conn.execute(
            "SELECT id FROM habits WHERE id = ?", (habit_id,)
        ).fetchone()
        if habit is None:
            raise HTTPException(status_code=404, detail="unknown habit")
        rows = conn.execute(
            "SELECT DISTINCT day FROM checkins WHERE habit_id = ?", (habit_id,)
        ).fetchall()

    checkin_dates = {r["day"] for r in rows}

    if today is not None:
        try:
            current_date = date.fromisoformat(today)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="invalid today date format, expected YYYY-MM-DD",
            )
    else:
        current_date = date.today()

    streak = 0
    target_date = current_date
    if target_date.isoformat() in checkin_dates:
        while target_date.isoformat() in checkin_dates:
            streak += 1
            target_date -= timedelta(days=1)
    elif (target_date - timedelta(days=1)).isoformat() in checkin_dates:
        target_date -= timedelta(days=1)
        while target_date.isoformat() in checkin_dates:
            streak += 1
            target_date -= timedelta(days=1)
    else:
        streak = 0

    return {"habit_id": habit_id, "streak": streak}
