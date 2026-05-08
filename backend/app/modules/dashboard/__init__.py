"""Dashboard Module — Overview, calendar, AI chat."""
from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter

from ...db import insert_row, get_rows, count_rows, get_api_usage_today
from ...models import ChatRequest, ChatResponse
from ...connectors.openai_client import chat_completion
from ...config import OPENAI_API_KEY

router = APIRouter()


@router.get("/overview")
async def get_overview():
    """Get dashboard overview."""
    api_usage = get_api_usage_today()

    return {
        "total_projects": count_rows("projects"),
        "total_scripts": count_rows("scripts"),
        "total_videos": count_rows("videos"),
        "total_voiceovers": count_rows("voiceovers"),
        "total_sounds": count_rows("sounds"),
        "total_products": count_rows("products"),
        "api_cost_today": api_usage.get("total_cost", 0),
        "api_usage_by_service": api_usage.get("by_service", {}),
    }


@router.get("/calendar")
async def get_calendar(month: str = ""):
    """Get content calendar."""
    if not month:
        month = datetime.utcnow().strftime("%Y-%m")

    entries = get_rows("content_calendar", limit=100)
    filtered = [e for e in entries if e.get("scheduled_date", "").startswith(month)]

    return {"month": month, "entries": filtered, "total": len(filtered)}


@router.post("/calendar")
async def add_calendar_entry(entry: dict):
    """Add calendar entry."""
    data = {
        "project_id": entry.get("project_id"),
        "title": entry.get("title", "Untitled"),
        "scheduled_date": entry.get("scheduled_date", datetime.utcnow().isoformat()),
        "content_type": entry.get("content_type", "custom"),
        "status": entry.get("status", "draft"),
        "notes": entry.get("notes", ""),
        "created_at": datetime.utcnow().isoformat(),
    }
    entry_id = insert_row("content_calendar", data)
    return {"id": entry_id, "status": "created"}


@router.get("/activity")
async def get_activity(limit: int = 20):
    """Get recent activity."""
    activities = []

    # Recent scripts
    scripts = get_rows("scripts", limit=5)
    for s in scripts:
        activities.append({
            "type": "script",
            "action": "created",
            "title": s.get("topic", "Untitled"),
            "timestamp": s.get("created_at"),
        })

    # Recent videos
    videos = get_rows("videos", limit=5)
    for v in videos:
        activities.append({
            "type": "video",
            "action": v.get("status", "uploaded"),
            "title": f"Video #{v['id']}",
            "timestamp": v.get("created_at"),
        })

    # Recent sounds
    sounds = get_rows("sounds", limit=5)
    for s in sounds:
        activities.append({
            "type": "sound",
            "action": s.get("source", "added"),
            "title": s.get("title", "Untitled"),
            "timestamp": s.get("created_at"),
        })

    # Sort by timestamp
    activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return activities[:limit]


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(req: ChatRequest):
    """AI assistant chat."""
    system_prompt = """You are TikTok AI Suite assistant. You help with:
- Content ideas and script writing
- Trending topics and hashtags
- Video editing tips
- TikTok Shop strategies
- Sound/music selection

Be concise, helpful, and TikTok-savvy. Use emojis."""

    if OPENAI_API_KEY:
        try:
            reply = await chat_completion(req.message, system_prompt)
            return ChatResponse(reply=reply, suggestions=[
                "Generate a script",
                "What's trending?",
                "Create a content plan",
            ])
        except Exception:
            pass

    # Fallback
    return ChatResponse(
        reply=f"I can help with that! Here's what I can do:\n\n"
              f"📝 Generate scripts for: \"{req.message}\"\n"
              f"🎵 Find trending sounds\n"
              f"🎬 Edit videos\n"
              f"🛒 Manage TikTok Shop\n\n"
              f"Try asking: \"Generate a script about {req.message[:30]}\"",
        suggestions=["Generate script", "Trending sounds", "Video templates"],
    )
