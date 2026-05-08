"""Sound Module — Trending sounds, AI music, sound library."""
from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, HTTPException

from ...db import insert_row, get_row, get_rows, delete_row
from ...models import (
    TrendingSound, MusicGenRequest, MusicGenResponse,
    SoundMatchRequest,
)
from ...connectors.suno_client import generate_music
from ...config import AUDIO_DIR, SUNO_API_KEY

router = APIRouter()


@router.get("/trending")
async def get_trending_sounds(category: str = "", limit: int = 20):
    """Get trending sounds."""
    # Fetch from external source or DB
    sounds = get_rows("trending_sounds", limit=limit)
    if category:
        sounds = [s for s in sounds if s.get("category") == category]

    # If empty, return sample data
    if not sounds:
        return _sample_trending_sounds()
    return sounds


@router.get("/trending/{sound_id}")
async def get_trending_sound(sound_id: int):
    """Get trending sound detail."""
    row = get_row("trending_sounds", sound_id)
    if not row:
        raise HTTPException(404, "Sound not found")
    return row


@router.get("/predict/{sound_id}")
async def predict_viral(sound_id: int):
    """Predict viral potential of a sound."""
    row = get_row("trending_sounds", sound_id)
    if not row:
        raise HTTPException(404, "Sound not found")

    score = _calculate_viral_score(row)
    return {
        "sound_id": sound_id,
        "viral_score": score,
        "factors": {
            "growth_rate": row.get("growth_rate", 0),
            "usage_count": row.get("usage_count", 0),
            "category_momentum": "high" if row.get("category") in ["pop", "hip-hop"] else "medium",
        },
        "prediction": "Likely to peak in 2-3 days" if score > 70 else "Steady growth",
    }


@router.post("/generate", response_model=MusicGenResponse)
async def generate_custom_music(req: MusicGenRequest):
    """Generate AI music."""
    filename = f"music_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
    file_path = AUDIO_DIR / filename

    if SUNO_API_KEY:
        try:
            result = await generate_music(req, str(file_path))
            from ...db import track_api_usage
            track_api_usage("suno", "music/generate")
        except Exception as e:
            result = _fallback_music(req, str(file_path))
    else:
        result = _fallback_music(req, str(file_path))

    # Save to DB
    data = {
        "title": f"{req.genre} - {req.mood}",
        "artist": "AI Generated",
        "source": "generated",
        "genre": req.genre,
        "mood": req.mood,
        "bpm": req.bpm,
        "duration_sec": req.duration,
        "file_path": str(file_path),
        "created_at": datetime.utcnow().isoformat(),
    }
    sound_id = insert_row("sounds", data)
    result.id = sound_id
    return result


@router.get("/library")
async def get_sound_library(collection: str = ""):
    """Get personal sound library."""
    from ...db import get_db
    with get_db() as conn:
        if collection:
            rows = conn.execute(
                "SELECT s.*, sl.collection, sl.notes FROM sound_library sl JOIN sounds s ON sl.sound_id = s.id WHERE sl.collection = ?",
                (collection,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT s.*, sl.collection, sl.notes FROM sound_library sl JOIN sounds s ON sl.sound_id = s.id",
            ).fetchall()
    return [dict(r) for r in rows]


@router.post("/library/add")
async def add_to_library(sound_id: int, collection: str = "favorites"):
    """Add sound to personal library."""
    if not get_row("sounds", sound_id):
        raise HTTPException(404, "Sound not found")

    insert_row("sound_library", {
        "sound_id": sound_id,
        "collection": collection,
        "added_at": datetime.utcnow().isoformat(),
    })
    return {"status": "added", "sound_id": sound_id, "collection": collection}


@router.post("/match")
async def match_sound(req: SoundMatchRequest):
    """Match sounds to content type."""
    # Simple matching logic
    mood_map = {
        "upbeat": ["pop", "electronic", "hip-hop"],
        "chill": ["lo-fi", "ambient", "acoustic"],
        "dramatic": ["cinematic", "orchestral", "epic"],
        "funny": ["comedy", "quirky", "retro"],
        "motivational": ["edm", "rock", "anthem"],
    }
    genres = mood_map.get(req.mood, ["pop"])

    sounds = get_rows("sounds", limit=50)
    matched = [s for s in sounds if s.get("genre") in genres]

    if not matched:
        return [
            {"genre": g, "mood": req.mood, "suggestion": f"Generate {g} {req.mood} music", "match_score": 85}
            for g in genres[:3]
        ]
    return matched[:5]


def _calculate_viral_score(sound: dict) -> float:
    """Calculate viral score for a sound."""
    growth = sound.get("growth_rate", 0)
    usage = sound.get("usage_count", 0)

    score = 0
    if growth > 100:
        score += 40
    elif growth > 50:
        score += 30
    elif growth > 10:
        score += 20

    if usage > 10000:
        score += 30
    elif usage > 1000:
        score += 20
    elif usage > 100:
        score += 10

    score += min(30, growth * 0.3)
    return min(100, score)


def _fallback_music(req: MusicGenRequest, file_path: str) -> MusicGenResponse:
    """Fallback when no music API is configured."""
    from pathlib import Path
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    Path(file_path).write_text(f"[Music placeholder] {req.genre} {req.mood} {req.duration}s")

    return MusicGenResponse(
        prompt=req.prompt,
        genre=req.genre,
        mood=req.mood,
        duration_sec=req.duration,
        file_path=file_path,
        bpm=req.bpm,
    )


def _sample_trending_sounds():
    """Sample trending sounds data."""
    return [
        {"id": 1, "title": "Oh No", "artist": "Kreepa", "usage_count": 2500000, "growth_rate": 150, "category": "pop", "viral_score": 95},
        {"id": 2, "title": "original sound", "artist": "djai_aja", "usage_count": 1800000, "growth_rate": 200, "category": "electronic", "viral_score": 92},
        {"id": 3, "title": "Aesthetic", "artist": "Toliver", "usage_count": 950000, "growth_rate": 80, "category": "hip-hop", "viral_score": 78},
        {"id": 4, "title": "Money Trees", "artist": "Kendrick Lamar", "usage_count": 3200000, "growth_rate": 45, "category": "hip-hop", "viral_score": 72},
        {"id": 5, "title": "Cupid - Twin Ver.", "artist": "FIFTY FIFTY", "usage_count": 5000000, "growth_rate": 30, "category": "k-pop", "viral_score": 68},
    ]
