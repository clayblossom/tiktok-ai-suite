"""ElevenLabs TTS Client — Enhanced with voice cloning and streaming."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, AsyncIterator, Optional

import httpx

from ..config import ELEVENLABS_API_KEY, ELEVENLABS_MODEL
from ..utils.logging import get_logger
from ..utils import cost_tracker

logger = get_logger(__name__)

BASE_URL = "https://api.elevenlabs.io/v1"
MAX_RETRIES = 3


def _headers() -> dict:
    return {"xi-api-key": ELEVENLABS_API_KEY}


async def _request_with_retry(method: str, url: str, **kwargs) -> httpx.Response:
    """Make request with retry logic."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=kwargs.pop("timeout", 30)) as client:
                resp = await client.request(method, url, **kwargs)

                if resp.status_code == 429:
                    retry_after = float(resp.headers.get("retry-after", 2 ** attempt))
                    await asyncio.sleep(retry_after)
                    continue

                if resp.status_code >= 500:
                    await asyncio.sleep(2 ** attempt)
                    continue

                resp.raise_for_status()
                return resp

        except httpx.TimeoutException as e:
            last_error = e
            await asyncio.sleep(2 ** attempt)

    raise Exception(f"ElevenLabs request failed after {MAX_RETRIES} retries: {last_error}")


async def generate_tts(req: Any, output_path: str) -> dict:
    """Generate TTS using ElevenLabs."""
    resp = await _request_with_retry(
        "POST",
        f"{BASE_URL}/text-to-speech/{req.voice_id}",
        headers={**_headers(), "Content-Type": "application/json"},
        json={
            "text": req.text,
            "model_id": ELEVENLABS_MODEL,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "speed": req.speed,
            },
        },
        timeout=60,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)

    # Track cost
    cost = cost_tracker.calculate_elevenlabs_cost(len(req.text))
    cost_tracker.track("elevenlabs", "tts/generate", len(req.text), cost,
                       {"voice_id": req.voice_id, "characters": len(req.text)})

    return {
        "voice_id": req.voice_id,
        "voice_name": req.voice_id,
        "language": req.language,
        "speed": req.speed,
        "file_path": output_path,
        "duration_sec": len(req.text) * 0.05,
    }


async def stream_tts(text: str, voice_id: str, output_path: str) -> str:
    """Stream TTS generation to file for lower latency."""
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream(
            "POST",
            f"{BASE_URL}/text-to-speech/{voice_id}/stream",
            headers={**_headers(), "Content-Type": "application/json"},
            json={
                "text": text,
                "model_id": ELEVENLABS_MODEL,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            },
        ) as resp:
            resp.raise_for_status()
            with open(output_path, "wb") as f:
                async for chunk in resp.aiter_bytes(chunk_size=4096):
                    f.write(chunk)

    cost = cost_tracker.calculate_elevenlabs_cost(len(text))
    cost_tracker.track("elevenlabs", "tts/stream", len(text), cost)
    return output_path


async def list_voices() -> list[dict]:
    """List available ElevenLabs voices."""
    resp = await _request_with_retry(
        "GET",
        f"{BASE_URL}/voices",
        headers=_headers(),
        timeout=15,
    )
    data = resp.json()

    return [
        {
            "id": v["voice_id"],
            "name": v["name"],
            "language": v.get("labels", {}).get("language", "en"),
            "gender": v.get("labels", {}).get("gender", "unknown"),
            "accent": v.get("labels", {}).get("accent", ""),
            "provider": "elevenlabs",
            "preview_url": v.get("preview_url", ""),
        }
        for v in data.get("voices", [])
    ]


async def get_voice_details(voice_id: str) -> dict:
    """Get detailed information about a specific voice."""
    resp = await _request_with_retry(
        "GET",
        f"{BASE_URL}/voices/{voice_id}",
        headers=_headers(),
        timeout=15,
    )
    return resp.json()


async def clone_voice(name: str, description: str, sample_files: list[str]) -> dict:
    """Clone a voice from audio samples.

    Args:
        name: Name for the cloned voice
        description: Voice description
        sample_files: List of file paths to audio samples

    Returns:
        Dict with voice_id and details
    """
    files = []
    for path in sample_files:
        files.append(("files", (Path(path).name, open(path, "rb"), "audio/mpeg")))

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{BASE_URL}/voices/add",
                headers=_headers(),
                data={"name": name, "description": description},
                files=files,
            )
            resp.raise_for_status()
            data = resp.json()

        cost_tracker.track("elevenlabs", "voice/clone", 0, 0.50,  # cloning has a flat cost
                           {"voice_id": data.get("voice_id"), "name": name})
        logger.info("voice_cloned", voice_id=data.get("voice_id"), name=name)
        return data

    finally:
        for _, (_, f, _) in files:
            f.close()


async def delete_voice(voice_id: str) -> bool:
    """Delete a cloned voice."""
    resp = await _request_with_retry(
        "DELETE",
        f"{BASE_URL}/voices/{voice_id}",
        headers=_headers(),
        timeout=15,
    )
    return resp.status_code == 200


async def get_subscription_info() -> dict:
    """Get ElevenLabs subscription info (character limits, usage)."""
    resp = await _request_with_retry(
        "GET",
        f"{BASE_URL}/user/subscription",
        headers=_headers(),
        timeout=15,
    )
    return resp.json()
