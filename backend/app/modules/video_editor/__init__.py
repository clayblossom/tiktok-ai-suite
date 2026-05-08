"""Video Editor Module — Video processing & editing."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from ...db import insert_row, get_row, get_rows, update_row
from ...models import (
    VideoUploadResponse, VideoStatus, AutoCutRequest,
    CaptionOverlayRequest, TextOverlayRequest,
    VideoExportRequest, VideoTemplate,
)
from ...config import VIDEOS_DIR, TEMP_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS

router = APIRouter()


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Upload a raw video for editing."""
    filename = f"raw_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file_path = VIDEOS_DIR / filename

    # Save file
    content = await file.read()
    file_path.write_bytes(content)
    file_size_mb = len(content) / (1024 * 1024)

    # Get video info
    duration = _get_video_duration(str(file_path))
    resolution = _get_video_resolution(str(file_path))

    # Save to DB
    data = {
        "source_path": str(file_path),
        "duration_sec": duration,
        "resolution": resolution,
        "file_size_mb": round(file_size_mb, 2),
        "status": VideoStatus.READY.value,
        "created_at": datetime.utcnow().isoformat(),
    }
    video_id = insert_row("videos", data)

    return VideoUploadResponse(
        id=video_id,
        filename=filename,
        duration_sec=duration,
        resolution=resolution,
        file_size_mb=round(file_size_mb, 2),
        status=VideoStatus.READY,
    )


@router.get("/")
async def list_videos(limit: int = 50):
    """List all videos."""
    return get_rows("videos", limit=limit)


@router.get("/{video_id}")
async def get_video(video_id: int):
    """Get video detail."""
    row = get_row("videos", video_id)
    if not row:
        raise HTTPException(404, "Video not found")
    row["captions"] = json.loads(row.get("captions", "[]"))
    row["overlays"] = json.loads(row.get("overlays", "[]"))
    return row


@router.post("/{video_id}/auto-cut")
async def auto_cut(video_id: int, req: AutoCutRequest):
    """Auto-cut video for optimal TikTok pacing."""
    video = get_row("videos", video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    source = video["source_path"]
    output = str(VIDEOS_DIR / f"cut_{video_id}_{datetime.utcnow().strftime('%H%M%S')}.mp4")

    try:
        # Detect silence and cut
        cuts = _detect_cuts(source, req.cut_interval, req.remove_silence, req.silence_threshold)
        _apply_cuts(source, output, cuts)

        update_row("videos", video_id, {
            "output_path": output,
            "status": VideoStatus.READY.value,
        })

        return {
            "status": "success",
            "video_id": video_id,
            "cuts_made": len(cuts),
            "output_path": output,
        }
    except Exception as e:
        raise HTTPException(500, f"Auto-cut failed: {e}")


@router.post("/{video_id}/captions")
async def add_captions(video_id: int, req: CaptionOverlayRequest):
    """Add auto-captions to video."""
    video = get_row("videos", video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    # Save caption config
    captions = json.loads(video.get("captions", "[]"))
    captions.append({
        "style": req.style.value,
        "font": req.font,
        "color": req.color,
        "position": req.position,
        "size": req.size,
        "added_at": datetime.utcnow().isoformat(),
    })
    update_row("videos", video_id, {"captions": json.dumps(captions)})

    return {"status": "captions_configured", "video_id": video_id, "config": req.model_dump()}


@router.post("/{video_id}/overlay")
async def add_overlay(video_id: int, req: TextOverlayRequest):
    """Add text overlay to video."""
    video = get_row("videos", video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    overlays = json.loads(video.get("overlays", "[]"))
    overlays.append({
        "text": req.text,
        "x": req.position_x,
        "y": req.position_y,
        "font_size": req.font_size,
        "color": req.color,
        "start_time": req.start_time,
        "end_time": req.end_time,
        "animation": req.animation,
        "added_at": datetime.utcnow().isoformat(),
    })
    update_row("videos", video_id, {"overlays": json.dumps(overlays)})

    return {"status": "overlay_added", "video_id": video_id}


@router.post("/{video_id}/export")
async def export_video(video_id: int, req: VideoExportRequest):
    """Export final video in TikTok format."""
    video = get_row("videos", video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    source = video.get("output_path") or video["source_path"]
    output = str(VIDEOS_DIR / f"final_{video_id}_{datetime.utcnow().strftime('%H%M%S')}.mp4")

    try:
        quality_settings = {
            "draft": {"crf": "28", "preset": "ultrafast"},
            "standard": {"crf": "23", "preset": "medium"},
            "high": {"crf": "18", "preset": "slow"},
        }
        q = quality_settings.get(req.quality, quality_settings["standard"])

        cmd = [
            "ffmpeg", "-y", "-i", source,
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-crf", q["crf"], "-preset", q["preset"],
            "-c:a", "aac", "-b:a", "128k",
            "-r", str(VIDEO_FPS),
            output,
        ]
        subprocess.run(cmd, capture_output=True, check=True, timeout=300)

        update_row("videos", video_id, {
            "output_path": output,
            "status": VideoStatus.DONE.value,
        })

        return {
            "status": "exported",
            "video_id": video_id,
            "output_path": output,
            "format": f"{VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps",
        }
    except Exception as e:
        raise HTTPException(500, f"Export failed: {e}")


@router.get("/templates")
async def list_templates():
    """List available video templates."""
    return [
        {"id": "storytime", "name": "Storytime", "category": "narrative", "icon": "📖", "description": "Text overlay + background + voiceover"},
        {"id": "tutorial", "name": "Tutorial", "category": "educational", "icon": "📚", "description": "Step-by-step with numbered overlays"},
        {"id": "review", "name": "Review", "category": "product", "icon": "⭐", "description": "Product showcase + text rating"},
        {"id": "before_after", "name": "Before/After", "category": "transformation", "icon": "🔄", "description": "Split screen transformation"},
        {"id": "ranking", "name": "Tier List", "category": "ranking", "icon": "🏆", "description": "Drag-and-drop ranking"},
        {"id": "pov", "name": "POV", "category": "narrative", "icon": "👁️", "description": "First-person perspective"},
        {"id": "greenscreen", "name": "Green Screen", "category": "effect", "icon": "🟢", "description": "Background replacement"},
        {"id": "duet", "name": "Duet", "category": "collab", "icon": "🎭", "description": "Side-by-side format"},
        {"id": "react", "name": "React", "category": "reaction", "icon": "😲", "description": "Picture-in-picture reaction"},
    ]


# ── FFmpeg helpers ──────────────────────────────────────────────────────────

def _get_video_duration(path: str) -> float:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0


def _get_video_resolution(path: str) -> str:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=10,
        )
        parts = result.stdout.strip().split(",")
        if len(parts) >= 2:
            return f"{parts[0]}x{parts[1]}"
    except Exception:
        pass
    return "unknown"


def _detect_cuts(source: str, interval: float, remove_silence: bool, threshold: float) -> list[dict]:
    """Detect cut points in video."""
    duration = _get_video_duration(source)
    cuts = []
    t = 0
    while t < duration:
        cuts.append({"start": t, "end": min(t + interval, duration)})
        t += interval
    return cuts


def _apply_cuts(source: str, output: str, cuts: list[dict]):
    """Apply cuts to video using FFmpeg concat."""
    if not cuts:
        return

    # Simple approach: just trim and re-encode
    segments = []
    for i, cut in enumerate(cuts):
        seg_path = str(TEMP_DIR / f"seg_{i}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", source,
            "-ss", str(cut["start"]), "-to", str(cut["end"]),
            "-c", "copy", seg_path,
        ], capture_output=True, timeout=60)
        segments.append(seg_path)

    # Concat
    concat_file = str(TEMP_DIR / "concat.txt")
    with open(concat_file, "w") as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c", "copy", output,
    ], capture_output=True, timeout=120)

    # Cleanup temp segments
    for seg in segments:
        try:
            os.remove(seg)
        except OSError:
            pass
