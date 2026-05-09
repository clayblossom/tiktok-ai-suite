"""Video processing background tasks."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from .celery_app import celery_app
from ..config import VIDEOS_DIR, TEMP_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS
from ..db import get_db, update_row, get_row


@celery_app.task(bind=True, name="app.workers.video_tasks.process_video_export")
def process_video_export(self, video_id: int, export_config: dict) -> dict:
    """Background task to export a video in TikTok format.

    Args:
        video_id: Database ID of the video
        export_config: Dict with quality, watermark settings, etc.

    Returns:
        Dict with status and output path
    """
    try:
        # Update status to processing
        update_row("videos", video_id, {"status": "exporting"})

        video = get_row("videos", video_id)
        if not video:
            return {"status": "error", "message": "Video not found"}

        source = video.get("output_path") or video["source_path"]
        output = str(VIDEOS_DIR / f"final_{video_id}_{datetime.utcnow().strftime('%H%M%S')}.mp4")

        quality = export_config.get("quality", "standard")
        quality_settings = {
            "draft": {"crf": "28", "preset": "ultrafast"},
            "standard": {"crf": "23", "preset": "medium"},
            "high": {"crf": "18", "preset": "slow"},
        }
        q = quality_settings.get(quality, quality_settings["standard"])

        width = export_config.get("width", VIDEO_WIDTH)
        height = export_config.get("height", VIDEO_HEIGHT)
        fps = export_config.get("fps", VIDEO_FPS)

        cmd = [
            "ffmpeg", "-y", "-i", source,
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                   f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black",
            "-c:v", "libx264", "-crf", q["crf"], "-preset", q["preset"],
            "-c:a", "aac", "-b:a", "128k",
            "-r", str(fps),
            output,
        ]

        # Add watermark if requested
        if export_config.get("add_watermark") and export_config.get("watermark_text"):
            watermark_text = export_config["watermark_text"]
            cmd.insert(-1, "-vf")
            cmd.insert(-1, f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white@0.5:"
                          f"x=w-tw-10:y=h-th-10")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            update_row("videos", video_id, {"status": "error"})
            return {"status": "error", "message": result.stderr[:500]}

        update_row("videos", video_id, {
            "output_path": output,
            "status": "done",
        })

        return {
            "status": "done",
            "video_id": video_id,
            "output_path": output,
            "format": f"{width}x{height} @ {fps}fps",
        }

    except subprocess.TimeoutExpired:
        update_row("videos", video_id, {"status": "error"})
        return {"status": "error", "message": "Export timed out"}
    except Exception as e:
        update_row("videos", video_id, {"status": "error"})
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="app.workers.video_tasks.process_auto_cut")
def process_auto_cut(self, video_id: int, cut_config: dict) -> dict:
    """Background task to auto-cut a video.

    Args:
        video_id: Database ID of the video
        cut_config: Dict with cut_interval, silence settings

    Returns:
        Dict with status, cuts made, output path
    """
    try:
        update_row("videos", video_id, {"status": "processing"})

        video = get_row("videos", video_id)
        if not video:
            return {"status": "error", "message": "Video not found"}

        source = video["source_path"]
        output = str(VIDEOS_DIR / f"cut_{video_id}_{datetime.utcnow().strftime('%H%M%S')}.mp4")

        interval = cut_config.get("cut_interval", 3.0)
        remove_silence = cut_config.get("remove_silence", True)
        threshold = cut_config.get("silence_threshold", -30)

        # Get video duration
        duration_result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", source],
            capture_output=True, text=True, timeout=10,
        )
        duration = float(duration_result.stdout.strip() or 0)

        if duration == 0:
            return {"status": "error", "message": "Could not determine video duration"}

        # Generate cuts based on intervals
        cuts = []
        t = 0
        while t < duration:
            cuts.append({"start": t, "end": min(t + interval, duration)})
            t += interval

        # Apply cuts via concat
        segments = []
        for i, cut in enumerate(cuts):
            seg_path = str(TEMP_DIR / f"seg_{video_id}_{i}.mp4")
            subprocess.run(
                ["ffmpeg", "-y", "-i", source, "-ss", str(cut["start"]),
                 "-to", str(cut["end"]), "-c", "copy", seg_path],
                capture_output=True, timeout=60,
            )
            segments.append(seg_path)

        concat_file = str(TEMP_DIR / f"concat_{video_id}.txt")
        with open(concat_file, "w") as f:
            for seg in segments:
                f.write(f"file '{seg}'\n")

        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", concat_file, "-c", "copy", output],
            capture_output=True, timeout=120,
        )

        # Cleanup segments
        for seg in segments:
            try:
                os.remove(seg)
            except OSError:
                pass
        try:
            os.remove(concat_file)
        except OSError:
            pass

        update_row("videos", video_id, {
            "output_path": output,
            "status": "ready",
        })

        return {
            "status": "done",
            "video_id": video_id,
            "cuts_made": len(cuts),
            "output_path": output,
        }

    except Exception as e:
        update_row("videos", video_id, {"status": "error"})
        return {"status": "error", "message": str(e)}


@celery_app.task(name="app.workers.video_tasks.process_captions")
def process_captions(video_id: int, caption_config: dict) -> dict:
    """Add captions to video as a background task.

    Args:
        video_id: Database ID
        caption_config: Caption style, font, color settings

    Returns:
        Status dict
    """
    try:
        video = get_row("videos", video_id)
        if not video:
            return {"status": "error", "message": "Video not found"}

        source = video.get("output_path") or video["source_path"]
        output = str(VIDEOS_DIR / f"captioned_{video_id}_{datetime.utcnow().strftime('%H%M%S')}.mp4")

        # Caption styling from config
        style = caption_config.get("style", "word_highlight")
        font_size = caption_config.get("size", 48)
        color = caption_config.get("color", "white")
        position = caption_config.get("position", "bottom")

        position_filter = {
            "bottom": "(w-text_w)/2:h-text_h-60",
            "center": "(w-text_w)/2:(h-text_h)/2",
            "top": "(w-text_w)/2:60",
        }.get(position, "(w-text_w)/2:h-text_h-60")

        # Use drawtext for placeholder captions
        # In production, this would use Whisper segments
        vf = (f"drawtext=text='Caption':fontsize={font_size}:fontcolor={color}:"
              f"x={position_filter}:borderw=2:bordercolor=black")

        subprocess.run(
            ["ffmpeg", "-y", "-i", source, "-vf", vf,
             "-c:v", "libx264", "-crf", "23", "-preset", "fast",
             "-c:a", "copy", output],
            capture_output=True, check=True, timeout=300,
        )

        # Save caption config to DB
        captions_data = json.loads(video.get("captions", "[]"))
        captions_data.append(caption_config)
        update_row("videos", video_id, {
            "output_path": output,
            "captions": json.dumps(captions_data),
        })

        return {"status": "done", "video_id": video_id, "output_path": output}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task(name="app.workers.video_tasks.cleanup_temp_files")
def cleanup_temp_files() -> dict:
    """Periodic task to clean up old temporary files."""
    import time
    cutoff = time.time() - (24 * 3600)  # 24 hours
    removed = 0
    freed = 0

    for path in TEMP_DIR.rglob("*"):
        if path.is_file() and path.stat().st_mtime < cutoff:
            size = path.stat().st_size
            try:
                path.unlink()
                removed += 1
                freed += size
            except OSError:
                pass

    return {"files_removed": removed, "freed_mb": round(freed / (1024 * 1024), 2)}
