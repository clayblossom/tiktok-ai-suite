"""Audio processing utility functions."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from ..config import AUDIO_DIR, TEMP_DIR
from .logging import get_logger

logger = get_logger(__name__)


def get_audio_duration(path: str | Path) -> float:
    """Get audio file duration in seconds."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        return float(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError):
        return 0.0


def get_audio_info(path: str | Path) -> dict:
    """Get audio file metadata."""
    info = {"duration": 0.0, "sample_rate": 0, "channels": 0, "bitrate": 0, "codec": ""}
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        import json
        data = json.loads(result.stdout)
        fmt = data.get("format", {})
        info["duration"] = float(fmt.get("duration", 0))
        info["bitrate"] = int(fmt.get("bit_rate", 0))
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "audio":
                info["sample_rate"] = int(stream.get("sample_rate", 0))
                info["channels"] = stream.get("channels", 0)
                info["codec"] = stream.get("codec_name", "")
                break
    except Exception as e:
        logger.warning("audio_info_failed", path=str(path), error=str(e))
    return info


def convert_audio(input_path: str | Path, output_path: str | Path,
                  format: str = "mp3", bitrate: str = "128k") -> str:
    """Convert audio between formats."""
    codec_map = {"mp3": "libmp3lame", "aac": "aac", "wav": "pcm_s16le", "ogg": "libvorbis"}
    codec = codec_map.get(format, "libmp3lame")

    try:
        cmd = ["ffmpeg", "-y", "-i", str(input_path), "-acodec", codec, "-b:a", bitrate, str(output_path)]
        subprocess.run(cmd, capture_output=True, check=True, timeout=120)
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("audio_convert_failed", error=str(e))
        raise


def normalize_audio(input_path: str | Path, output_path: str | Path,
                    target_db: float = -16.0) -> str:
    """Normalize audio to target loudness."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(input_path),
                "-af", f"loudnorm=I={target_db}:TP=-1.5:LRA=11",
                str(output_path),
            ],
            capture_output=True, check=True, timeout=120,
        )
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("normalize_failed", error=str(e))
        raise


def mix_audio(tracks: list[dict], output_path: str | Path) -> str:
    """Mix multiple audio tracks with individual volumes.

    tracks: list of {"path": str, "volume": float (0-1), "start_at": float (seconds)}
    """
    if not tracks:
        raise ValueError("No tracks to mix")

    if len(tracks) == 1:
        t = tracks[0]
        subprocess.run(
            ["ffmpeg", "-y", "-i", t["path"],
             "-af", f"volume={t.get('volume', 1.0)}",
             str(output_path)],
            capture_output=True, check=True, timeout=120,
        )
        return str(output_path)

    # Build complex filter for mixing
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
    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_str, "-map", "[out]", str(output_path)]

    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=300)
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("audio_mix_failed", error=str(e))
        raise


def add_audio_to_video(video_path: str | Path, audio_path: str | Path,
                       output_path: str | Path, video_audio_vol: float = 1.0,
                       overlay_vol: float = 1.0) -> str:
    """Merge an audio track onto a video."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(video_path), "-i", str(audio_path),
                "-filter_complex",
                f"[0:a]volume={video_audio_vol}[va];[1:a]volume={overlay_vol}[oa];"
                f"[va][oa]amix=inputs=2:duration=first[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-shortest", str(output_path),
            ],
            capture_output=True, check=True, timeout=300,
        )
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("merge_audio_video_failed", error=str(e))
        raise


def generate_silence(duration: float, output_path: str | Path, sample_rate: int = 44100) -> str:
    """Generate a silent audio file of given duration."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"anullsrc=r={sample_rate}:cl=stereo",
                "-t", str(duration), str(output_path),
            ],
            capture_output=True, check=True, timeout=30,
        )
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("silence_gen_failed", error=str(e))
        raise
