"""Voice Module — TTS generation & management."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ...db import insert_row, get_row, get_rows
from ...models import VoiceRequest, VoiceInfo, VoiceoverResponse
from ...connectors.elevenlabs_client import generate_tts, list_voices
from ...config import ELEVENLABS_API_KEY, AUDIO_DIR

router = APIRouter()


@router.post("/generate", response_model=VoiceoverResponse)
async def generate_voiceover(req: VoiceRequest):
    """Generate TTS voiceover."""
    filename = f"voice_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
    file_path = AUDIO_DIR / filename

    if ELEVENLABS_API_KEY:
        try:
            result = await generate_tts(req, str(file_path))
            track_api_usage("elevenlabs", "tts/generate")
        except Exception as e:
            result = _fallback_tts(req, str(file_path))
    else:
        result = _fallback_tts(req, str(file_path))

    # Save to DB
    data = {
        "voice_id": req.voice_id,
        "voice_name": req.voice_id,
        "language": req.language,
        "speed": req.speed,
        "file_path": str(file_path),
        "duration_sec": len(req.text) * 0.05,  # rough estimate
        "created_at": datetime.utcnow().isoformat(),
    }
    voiceover_id = insert_row("voiceovers", data)
    result.id = voiceover_id
    return result


@router.get("/voices")
async def get_voices():
    """List available voices."""
    if ELEVENLABS_API_KEY:
        try:
            return await list_voices()
        except Exception:
            pass

    return [
        {"id": "alloy", "name": "Alloy", "language": "en", "gender": "neutral", "provider": "openai"},
        {"id": "echo", "name": "Echo", "language": "en", "gender": "male", "provider": "openai"},
        {"id": "fable", "name": "Fable", "language": "en", "gender": "male", "provider": "openai"},
        {"id": "onyx", "name": "Onyx", "language": "en", "gender": "male", "provider": "openai"},
        {"id": "nova", "name": "Nova", "language": "en", "gender": "female", "provider": "openai"},
        {"id": "shimmer", "name": "Shimmer", "language": "en", "gender": "female", "provider": "openai"},
    ]


@router.get("/{voiceover_id}")
async def get_voiceover(voiceover_id: int):
    """Get voiceover detail."""
    row = get_row("voiceovers", voiceover_id)
    if not row:
        raise HTTPException(404, "Voiceover not found")
    return row


@router.get("/")
async def list_voiceovers(limit: int = 50):
    """List all voiceovers."""
    return get_rows("voiceovers", limit=limit)


def _fallback_tts(req: VoiceRequest, file_path: str) -> VoiceoverResponse:
    """Fallback when no TTS API is configured."""
    # Create a placeholder file
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    Path(file_path).write_text(f"[TTS placeholder] {req.text}")

    return VoiceoverResponse(
        voice_id=req.voice_id,
        voice_name=req.voice_id,
        language=req.language,
        speed=req.speed,
        file_path=file_path,
        duration_sec=len(req.text) * 0.05,
    )


def track_api_usage(service: str, endpoint: str, tokens: int = 0, cost: float = 0):
    from ...db import track_api_usage as _track
    _track(service, endpoint, tokens, cost)
