"""Content Factory — Content scheduling and calendar."""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException

from ...db import insert_row, get_row, get_rows, update_row, delete_row
from ...utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Best posting times by day of week (hour in UTC)
BEST_POSTING_TIMES = {
    0: ["06:00", "10:00", "19:00"],  # Monday
    1: ["06:00", "09:00", "19:00"],  # Tuesday
    2: ["06:00", "10:00", "20:00"],  # Wednesday
    3: ["06:00", "09:00", "18:00"],  # Thursday
    4: ["06:00", "10:00", "19:00"],  # Friday
    5: ["08:00", "11:00", "19:00"],  # Saturday
    6: ["08:00", "12:00", "18:00"],  # Sunday
}


@router.get("/schedule")
async def get_schedule(month: str = ""):
    """Get content schedule for a month."""
    if not month:
        month = datetime.utcnow().strftime("%Y-%m")

    entries = get_rows("content_calendar", limit=200)
    filtered = [e for e in entries if e.get("scheduled_date", "").startswith(month)]

    return {
        "month": month,
        "entries": filtered,
        "total": len(filtered),
        "best_times": BEST_POSTING_TIMES,
    }


@router.post("/schedule")
async def schedule_content(entry: dict):
    """Schedule content for publishing."""
    data = {
        "project_id": entry.get("project_id"),
        "title": entry.get("title", "Untitled"),
        "scheduled_date": entry.get("scheduled_date", datetime.utcnow().isoformat()),
        "content_type": entry.get("content_type", "custom"),
        "status": entry.get("status", "scheduled"),
        "notes": entry.get("notes", ""),
        "created_at": datetime.utcnow().isoformat(),
    }
    entry_id = insert_row("content_calendar", data)
    logger.info("content_scheduled", entry_id=entry_id, date=data["scheduled_date"])
    return {"id": entry_id, "status": "scheduled"}


@router.put("/schedule/{entry_id}")
async def update_schedule(entry_id: int, data: dict):
    """Update a scheduled content entry."""
    if not get_row("content_calendar", entry_id):
        raise HTTPException(404, "Schedule entry not found")
    update_row("content_calendar", entry_id, data)
    return {"status": "updated", "id": entry_id}


@router.delete("/schedule/{entry_id}")
async def delete_schedule(entry_id: int):
    """Delete a scheduled content entry."""
    delete_row("content_calendar", entry_id)
    return {"status": "deleted", "id": entry_id}


@router.get("/schedule/suggestions")
async def get_posting_suggestions(niche: str = "", days_ahead: int = 7):
    """Get AI-powered posting time suggestions."""
    suggestions = []
    now = datetime.utcnow()

    for i in range(days_ahead):
        date = now + timedelta(days=i)
        dow = date.weekday()
        times = BEST_POSTING_TIMES.get(dow, ["09:00", "18:00"])

        for time_str in times:
            suggestions.append({
                "date": date.strftime("%Y-%m-%d"),
                "time": time_str,
                "day_of_week": date.strftime("%A"),
                "confidence": "high" if time_str in ["09:00", "19:00"] else "medium",
            })

    return {
        "niche": niche,
        "suggestions": suggestions[:10],
        "tip": "Post consistently at the same times for best results",
    }
