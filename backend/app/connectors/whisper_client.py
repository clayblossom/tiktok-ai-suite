"""Whisper Speech-to-Text Client."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import httpx

from ..config import WHISPER_API_KEY, OPENAI_API_KEY
from ..utils.logging import get_logger
from ..utils import cost_tracker

logger = get_logger(__name__)

WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"
WHISPER_TRANSLATE_URL = "https://api.openai.com/v1/audio/translations"


def _get_api_key() -> str:
    return WHISPER_API_KEY or OPENAI_API_KEY


async def transcribe(
    audio_path: str | Path,
    language: Optional[str] = None,
    response_format: str = "verbose_json",
    timestamp_granularities: Optional[list[str]] = None,
) -> dict:
    """Transcribe audio file to text.

    Args:
        audio_path: Path to audio file
        language: ISO language code (auto-detect if None)
        response_format: json, text, srt, verbose_json, vtt
        timestamp_granularities: word, segment

    Returns:
        Transcription result with text, segments, language, duration
    """
    api_key = _get_api_key()
    if not api_key:
        raise Exception("No Whisper/OpenAI API key configured")

    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Check file size — Whisper has 25MB limit
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 25:
        # Split into chunks and transcribe
        return await _transcribe_large_file(audio_path, language, response_format)

    async with httpx.AsyncClient(timeout=120) as client:
        with open(audio_path, "rb") as f:
            files = {"file": (audio_path.name, f, "audio/mpeg")}
            data = {"model": "whisper-1", "response_format": response_format}
            if language:
                data["language"] = language
            if timestamp_granularities:
                data["timestamp_granularities[]"] = ",".join(timestamp_granularities)

            resp = await client.post(
                WHISPER_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                files=files,
                data=data,
            )
            resp.raise_for_status()

    result = resp.json() if response_format != "text" else {"text": resp.text}

    # Estimate cost (~$0.006/minute)
    duration_min = result.get("duration", 0) / 60 if isinstance(result, dict) else 0
    cost = round(duration_min * 0.006, 4)
    cost_tracker.track("whisper", "transcribe", 0, cost,
                       {"language": language, "file": audio_path.name, "duration_min": round(duration_min, 1)})

    logger.info("transcription_complete", file=audio_path.name, language=result.get("language", language),
                duration=round(duration_min, 1))
    return result


async def translate(audio_path: str | Path, response_format: str = "verbose_json") -> dict:
    """Translate audio to English text."""
    api_key = _get_api_key()
    if not api_key:
        raise Exception("No Whisper/OpenAI API key configured")

    audio_path = Path(audio_path)

    async with httpx.AsyncClient(timeout=120) as client:
        with open(audio_path, "rb") as f:
            files = {"file": (audio_path.name, f, "audio/mpeg")}
            data = {"model": "whisper-1", "response_format": response_format}

            resp = await client.post(
                WHISPER_TRANSLATE_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                files=files,
                data=data,
            )
            resp.raise_for_status()

    return resp.json() if response_format != "text" else {"text": resp.text}


async def _transcribe_large_file(audio_path: Path, language: Optional[str],
                                  response_format: str) -> dict:
    """Handle files larger than 25MB by splitting into chunks."""
    import tempfile

    # Get duration
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(audio_path)],
            capture_output=True, text=True, timeout=10,
        )
        duration = float(result.stdout.strip())
    except Exception:
        raise Exception("Cannot determine audio duration for large file")

    # Split into 10-minute chunks
    chunk_duration = 600  # 10 minutes
    chunks = []
    start = 0
    while start < duration:
        chunk_path = str(Path(tempfile.mktemp(suffix=".mp3")))
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(audio_path), "-ss", str(start),
             "-t", str(chunk_duration), "-c", "copy", chunk_path],
            capture_output=True, timeout=60,
        )
        chunks.append({"path": chunk_path, "start": start})
        start += chunk_duration

    # Transcribe each chunk
    all_text = []
    all_segments = []
    for chunk in chunks:
        result = await transcribe(chunk["path"], language, "verbose_json")
        all_text.append(result.get("text", ""))
        for seg in result.get("segments", []):
            seg["start"] += chunk["start"]
            seg["end"] += chunk["start"]
            all_segments.append(seg)

        # Cleanup chunk file
        Path(chunk["path"]).unlink(missing_ok=True)

    return {
        "text": " ".join(all_text),
        "segments": all_segments,
        "language": language or "auto",
        "duration": duration,
    }


async def generate_srt(segments: list[dict]) -> str:
    """Generate SRT subtitle format from Whisper segments."""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = _format_srt_time(seg.get("start", 0))
        end = _format_srt_time(seg.get("end", 0))
        text = seg.get("text", "").strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


def _format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT time format HH:MM:SS,mmm."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
