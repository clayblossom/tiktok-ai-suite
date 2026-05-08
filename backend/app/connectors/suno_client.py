"""Suno Music Generation Client."""
from __future__ import annotations

import httpx

from ..config import SUNO_API_KEY


async def generate_music(req, output_path: str) -> dict:
    """Generate music using Suno API."""
    # Suno API (simplified - actual API may differ)
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.suno.ai/v1/generate",
            headers={
                "Authorization": f"Bearer {SUNO_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "prompt": req.prompt,
                "genre": req.genre,
                "mood": req.mood,
                "duration": req.duration,
                "instrumental": req.instrumental,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    # Download generated audio
    audio_url = data.get("audio_url", "")
    if audio_url:
        async with httpx.AsyncClient(timeout=30) as client:
            audio_resp = await client.get(audio_url)
            with open(output_path, "wb") as f:
                f.write(audio_resp.content)

    return {
        "prompt": req.prompt,
        "genre": req.genre,
        "mood": req.mood,
        "duration_sec": req.duration,
        "file_path": output_path,
        "bpm": req.bpm,
    }
