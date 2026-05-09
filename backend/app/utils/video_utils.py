"""Video processing utility functions using FFmpeg."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional

from ..config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, TEMP_DIR
from .logging import get_logger

logger = get_logger(__name__)


def get_video_info(path: str | Path) -> dict:
    """Get comprehensive video metadata."""
    path = str(path)
    info = {
        "duration": 0.0,
        "width": 0,
        "height": 0,
        "fps": 0.0,
        "codec": "",
        "file_size_mb": 0.0,
        "bitrate": 0,
    }

    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                path,
            ],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(result.stdout)

        # Format info
        fmt = data.get("format", {})
        info["duration"] = float(fmt.get("duration", 0))
        info["bitrate"] = int(fmt.get("bit_rate", 0))
        info["file_size_mb"] = round(int(fmt.get("size", 0)) / (1024 * 1024), 2)

        # Stream info
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                info["width"] = stream.get("width", 0)
                info["height"] = stream.get("height", 0)
                info["codec"] = stream.get("codec_name", "")
                # Parse frame rate
                r_frame_rate = stream.get("r_frame_rate", "0/1")
                if "/" in r_frame_rate:
                    num, den = r_frame_rate.split("/")
                    info["fps"] = round(int(num) / int(den), 2) if int(den) else 0
                break

    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning("video_info_failed", path=path, error=str(e))

    return info


def get_video_duration(path: str | Path) -> float:
    """Get video duration in seconds."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        return float(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError):
        return 0.0


def get_video_resolution(path: str | Path) -> str:
    """Get video resolution as 'WIDTHxHEIGHT' string."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        parts = result.stdout.strip().split(",")
        if len(parts) >= 2:
            return f"{parts[0]}x{parts[1]}"
    except (subprocess.TimeoutExpired, ValueError):
        pass
    return "unknown"


def extract_audio(input_path: str | Path, output_path: str | Path, format: str = "mp3") -> str:
    """Extract audio track from video file."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(input_path),
                "-vn", "-acodec", "libmp3lame" if format == "mp3" else "aac",
                "-q:a", "2", str(output_path),
            ],
            capture_output=True, check=True, timeout=120,
        )
        logger.info("audio_extracted", input=str(input_path), output=str(output_path))
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("audio_extract_failed", error=str(e))
        raise


def generate_thumbnail(input_path: str | Path, output_path: str | Path, timestamp: float = 1.0) -> str:
    """Extract a thumbnail frame from video at given timestamp."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(input_path),
                "-ss", str(timestamp), "-vframes", "1",
                "-vf", f"scale=480:-1",
                str(output_path),
            ],
            capture_output=True, check=True, timeout=30,
        )
        logger.info("thumbnail_generated", output=str(output_path))
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("thumbnail_failed", error=str(e))
        raise


def resize_video(input_path: str | Path, output_path: str | Path,
                 width: int = VIDEO_WIDTH, height: int = VIDEO_HEIGHT) -> str:
    """Resize video to target dimensions with padding."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(input_path),
                "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                       f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black",
                "-c:v", "libx264", "-crf", "23", "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k",
                str(output_path),
            ],
            capture_output=True, check=True, timeout=300,
        )
        logger.info("video_resized", output=str(output_path), resolution=f"{width}x{height}")
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("resize_failed", error=str(e))
        raise


def change_speed(input_path: str | Path, output_path: str | Path, speed: float = 1.0) -> str:
    """Change video playback speed."""
    if speed <= 0 or speed > 4:
        raise ValueError("Speed must be between 0 and 4")

    video_filter = f"setpts={1/speed}*PTS"
    audio_filter = f"atempo={min(2.0, max(0.5, speed))}"

    # For extreme speeds, chain atempo filters
    if speed > 2.0:
        chain_count = int(speed / 2.0)
        remaining = speed / (2.0 ** chain_count)
        audio_filter = ",".join(["atempo=2.0"] * chain_count + [f"atempo={remaining}"])

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(input_path),
                "-vf", video_filter,
                "-af", audio_filter,
                "-c:v", "libx264", "-crf", "23",
                str(output_path),
            ],
            capture_output=True, check=True, timeout=300,
        )
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("speed_change_failed", error=str(e))
        raise


def trim_video(input_path: str | Path, output_path: str | Path,
               start: float = 0, end: float = 0) -> str:
    """Trim video between start and end timestamps."""
    cmd = ["ffmpeg", "-y", "-i", str(input_path), "-ss", str(start)]
    if end > 0:
        cmd += ["-to", str(end)]
    cmd += ["-c", "copy", str(output_path)]

    try:
        subprocess.run(cmd, capture_output=True, check=True, timeout=120)
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("trim_failed", error=str(e))
        raise


def concat_videos(input_paths: list[str | Path], output_path: str | Path) -> str:
    """Concatenate multiple video files."""
    concat_file = str(TEMP_DIR / "concat_list.txt")
    with open(concat_file, "w") as f:
        for p in input_paths:
            f.write(f"file '{p}'\n")

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_file, "-c", "copy", str(output_path),
            ],
            capture_output=True, check=True, timeout=300,
        )
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("concat_failed", error=str(e))
        raise


def detect_silence(input_path: str | Path, threshold_db: float = -30,
                   min_duration: float = 0.5) -> list[dict]:
    """Detect silent segments in audio/video."""
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-i", str(input_path),
                "-af", f"silencedetect=noise={threshold_db}dB:d={min_duration}",
                "-f", "null", "-",
            ],
            capture_output=True, text=True, timeout=120,
        )
        # Parse silence detection output
        import re
        silences = []
        starts = re.findall(r"silence_start: ([\d.]+)", result.stderr)
        ends = re.findall(r"silence_end: ([\d.]+)", result.stderr)
        for s, e in zip(starts, ends):
            silences.append({"start": float(s), "end": float(e), "duration": float(e) - float(s)})
        return silences
    except (subprocess.TimeoutExpired, ValueError) as e:
        logger.warning("silence_detect_failed", error=str(e))
        return []
