"""Audio processing background tasks."""
from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from .celery_app import celery_app
from ..config import AUDIO_DIR
from ..db import get_row, update_row


@celery_app.task(bind=True, name="app.workers.audio_tasks.process_tts")
def process_tts(self, voiceover_id: int) -> dict:
    """Background task to generate TTS audio.

    Args:
        voiceover_id: Database ID of the voiceover record

    Returns:
        Status dict with file path
    """
    try:
        voiceover = get_row("voiceovers", voiceover_id)
        if not voiceover:
            return {"status": "error", "message": "Voiceover not found"}

        # In production, this would call ElevenLabs/other TTS API
        # For now, create a placeholder
        output_path = voiceover.get("file_path", "")

        return {
            "status": "done",
            "voiceover_id": voiceover_id,
            "file_path": output_path,
            "duration_sec": voiceover.get("duration_sec", 0),
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="app.workers.audio_tasks.process_music_generation")
def process_music_generation(self, sound_id: int, gen_config: dict) -> dict:
    """Background task to generate music.

    Args:
        sound_id: Database ID of the sound record
        gen_config: Dict with prompt, genre, mood, duration

    Returns:
        Status dict with file path
    """
    try:
        sound = get_row("sounds", sound_id)
        if not sound:
            return {"status": "error", "message": "Sound not found"}

        output_path = sound.get("file_path", "")

        return {
            "status": "done",
            "sound_id": sound_id,
            "file_path": output_path,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="app.workers.audio_tasks.process_audio_mix")
def process_audio_mix(self, tracks: list, output_filename: str) -> dict:
    """Background task to mix multiple audio tracks.

    Args:
        tracks: List of dicts with path, volume, start_at
        output_filename: Name for the output file

    Returns:
        Status dict with output path
    """
    try:
        output_path = str(AUDIO_DIR / output_filename)

        if len(tracks) == 1:
            subprocess.run(
                ["ffmpeg", "-y", "-i", tracks[0]["path"],
                 "-af", f"volume={tracks[0].get('volume', 1.0)}",
                 output_path],
                capture_output=True, check=True, timeout=120,
            )
            return {"status": "done", "output_path": output_path}

        # Build complex filter
        inputs = []
        filter_parts = []
        for i, t in enumerate(tracks):
            inputs += ["-i", t["path"]]
            vol = t.get("volume", 1.0)
            delay_ms = int(t.get("start_at", 0) * 1000)
            filter_parts.append(f"[{i}:a]volume={vol},adelay={delay_ms}|{delay_ms}[a{i}]")

        mix_inputs = "".join(f"[a{i}]" for i in range(len(tracks)))
        filter_parts.append(f"{mix_inputs}amix=inputs={len(tracks)}:duration=longest[out]")
        filter_str = ";".join(filter_parts)

        cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_str, "-map", "[out]", output_path]
        subprocess.run(cmd, capture_output=True, check=True, timeout=300)

        return {"status": "done", "output_path": output_path}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task(name="app.workers.audio_tasks.normalize_audio_file")
def normalize_audio_file(input_path: str, output_path: str, target_lufs: float = -16.0) -> dict:
    """Normalize audio loudness as background task."""
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path,
             "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
             output_path],
            capture_output=True, check=True, timeout=120,
        )
        return {"status": "done", "output_path": output_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}
