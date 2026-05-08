"""ElevenLabs TTS Client."""
from __future__ import annotations

import httpx

from ..config import ELEVENLABS_API_KEY, ELEVENLABS_MODEL


async def generate_tts(req, output_path: str) -> dict:
    """Generate TTS using ElevenLabs."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{req.voice_id}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            url,
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": req.text,
                "model_id": ELEVENLABS_MODEL,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "speed": req.speed,
                },
            },
        )
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(resp.content)

    return {
        "voice_id": req.voice_id,
        "voice_name": req.voice_id,
        "language": req.language,
        "speed": req.speed,
        "file_path": output_path,
        "duration_sec": len(req.text) * 0.05,
    }


async def list_voices() -> list[dict]:
    """List available ElevenLabs voices."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
        )
        resp.raise_for_status()
        data = resp.json()

    return [
        {
            "id": v["voice_id"],
            "name": v["name"],
            "language": v.get("labels", {}).get("language", "en"),
            "gender": v.get("labels", {}).get("gender", "unknown"),
            "provider": "elevenlabs",
        }
        for v in data.get("voices", [])
    ]
