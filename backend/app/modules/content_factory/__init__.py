"""Content Factory Module — Script generation & management."""
from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, HTTPException

from ...db import insert_row, get_row, get_rows, update_row, delete_row, track_api_usage
from ...models import (
    ScriptRequest, ScriptResponse, ScriptVariation,
    CaptionRequest, CaptionResponse,
    ContentType, ToneStyle,
)
from ...connectors.openai_client import generate_script, generate_captions
from ...config import OPENAI_API_KEY

router = APIRouter()


@router.post("/scripts/generate", response_model=ScriptResponse)
async def generate_script_endpoint(req: ScriptRequest):
    """Generate AI-powered TikTok script."""
    if OPENAI_API_KEY:
        try:
            result = await generate_script(req)
            track_api_usage("openai", "scripts/generate", metadata={"topic": req.topic})
        except Exception as e:
            result = _fallback_script(req)
    else:
        result = _fallback_script(req)

    # Save to DB
    data = {
        "topic": req.topic,
        "niche": req.niche,
        "tone": req.tone.value,
        "duration": req.duration,
        "content_type": req.content_type.value,
        "variations": json.dumps([v.model_dump() for v in result.variations]),
        "hashtags": json.dumps(result.hashtags),
        "best_posting_time": result.best_posting_time,
        "language": req.language,
        "created_at": datetime.utcnow().isoformat(),
    }
    script_id = insert_row("scripts", data)
    result.id = script_id
    return result


@router.get("/scripts")
async def list_scripts(limit: int = 50, offset: int = 0):
    """List all scripts."""
    rows = get_rows("scripts", limit=limit, offset=offset)
    for r in rows:
        r["variations"] = json.loads(r.get("variations", "[]"))
        r["hashtags"] = json.loads(r.get("hashtags", "[]"))
    return rows


@router.get("/scripts/{script_id}")
async def get_script(script_id: int):
    """Get script detail."""
    row = get_row("scripts", script_id)
    if not row:
        raise HTTPException(404, "Script not found")
    row["variations"] = json.loads(row.get("variations", "[]"))
    row["hashtags"] = json.loads(row.get("hashtags", "[]"))
    return row


@router.put("/scripts/{script_id}")
async def update_script(script_id: int, data: dict):
    """Update a script."""
    if not get_row("scripts", script_id):
        raise HTTPException(404, "Script not found")
    update_row("scripts", script_id, data)
    return {"status": "updated", "id": script_id}


@router.delete("/scripts/{script_id}")
async def delete_script(script_id: int):
    """Delete a script."""
    delete_row("scripts", script_id)
    return {"status": "deleted", "id": script_id}


@router.post("/captions/generate", response_model=CaptionResponse)
async def generate_captions_endpoint(req: CaptionRequest):
    """Generate captions and hashtags for a script."""
    if OPENAI_API_KEY:
        try:
            result = await generate_captions(req)
            track_api_usage("openai", "captions/generate")
            return result
        except Exception:
            pass

    # Fallback
    return CaptionResponse(
        caption=req.script_text[:150] + "...",
        hashtags=["#fyp", "#viral", "#tiktok", f"#{req.niche}" if req.niche else "#trending"],
        emoji_suggestions=["🔥", "💯", "✨", "👀"],
        character_count=len(req.script_text[:150]),
    )


@router.get("/templates")
async def list_content_templates():
    """List available content templates."""
    return [
        {"id": "storytime", "name": "Storytime", "description": "Personal story with hook", "icon": "📖"},
        {"id": "tutorial", "name": "Tutorial/How-to", "description": "Step-by-step guide", "icon": "📚"},
        {"id": "did_you_know", "name": "Did You Know", "description": "Facts & trivia", "icon": "🧠"},
        {"id": "pov", "name": "POV", "description": "Point of view scenario", "icon": "👁️"},
        {"id": "ranking", "name": "Ranking/Tier List", "description": "Rank items or ideas", "icon": "🏆"},
        {"id": "before_after", "name": "Before/After", "description": "Transformation story", "icon": "🔄"},
        {"id": "things_that", "name": "Things That...", "description": "List format", "icon": "📋"},
        {"id": "duet", "name": "Duet/Stitch", "description": "Response format", "icon": "🎭"},
    ]


def _fallback_script(req: ScriptRequest) -> ScriptResponse:
    """Generate a basic script without AI."""
    hooks = {
        ContentType.STORYTIME: f"Let me tell you about {req.topic}...",
        ContentType.TUTORIAL: f"Here's how to {req.topic} in 3 steps",
        ContentType.DID_YOU_KNOW: f"Did you know that {req.topic}?",
        ContentType.POV: f"POV: {req.topic}",
        ContentType.RANKING: f"Ranking {req.topic} from worst to best",
        ContentType.BEFORE_AFTER: f"Before vs After {req.topic}",
        ContentType.THINGS_THAT: f"Things that only {req.topic} fans understand",
        ContentType.CUSTOM: f"You need to know this about {req.topic}",
    }

    variations = []
    for i in range(min(req.variations, 3)):
        hook = hooks.get(req.content_type, hooks[ContentType.CUSTOM])
        if i > 0:
            hook = f"[Variation {i+1}] {hook}"
        variations.append(ScriptVariation(
            hook=hook,
            body=f"[Main content about {req.topic} goes here. Add your key points, stories, or information.]",
            cta=f"Follow for more {req.niche or 'content'}! Like if you agree!",
            full_text=f"{hook}\n\n[Body]\n\n[CTA]",
            estimated_duration=req.duration,
            engagement_score=60 + i * 5,
        ))

    return ScriptResponse(
        topic=req.topic,
        niche=req.niche,
        tone=req.tone,
        duration=req.duration,
        content_type=req.content_type,
        variations=variations,
        hashtags=["#fyp", "#viral", "#tiktok", f"#{req.topic.replace(' ', '')}"],
        best_posting_time="6:00 PM - 9:00 PM",
    )
