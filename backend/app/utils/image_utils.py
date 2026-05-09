"""Image processing utility functions."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from ..config import IMAGES_DIR
from .logging import get_logger

logger = get_logger(__name__)


def resize_image(input_path: str | Path, output_path: str | Path,
                 width: int = 1080, height: int = 1920, maintain_aspect: bool = True) -> str:
    """Resize an image to target dimensions."""
    scale = f"scale={width}:{height}"
    if maintain_aspect:
        scale += ":force_original_aspect_ratio=decrease"
        scale += f",pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black"

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(input_path), "-vf", scale, str(output_path)],
            capture_output=True, check=True, timeout=30,
        )
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("image_resize_failed", error=str(e))
        raise


def add_text_overlay(input_path: str | Path, output_path: str | Path,
                     text: str, position: str = "center",
                     font_size: int = 48, font_color: str = "white",
                     bg_color: str = "black@0.5") -> str:
    """Add text overlay to an image."""
    position_map = {
        "center": "(w-text_w)/2:(h-text_h)/2",
        "top": "(w-text_w)/2:50",
        "bottom": "(w-text_w)/2:h-text_h-50",
        "top-left": "50:50",
        "top-right": "w-text_w-50:50",
    }
    xy = position_map.get(position, position_map["center"])

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(input_path),
                "-vf", f"drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:"
                       f"box=1:boxcolor={bg_color}:boxborderw=10:{xy}",
                str(output_path),
            ],
            capture_output=True, check=True, timeout=30,
        )
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("text_overlay_failed", error=str(e))
        raise


def create_image_from_color(output_path: str | Path, color: str = "black",
                            width: int = 1080, height: int = 1920) -> str:
    """Create a solid color image."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"color=c={color}:s={width}x{height}:d=1",
                "-frames:v", "1", str(output_path),
            ],
            capture_output=True, check=True, timeout=15,
        )
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("color_image_failed", error=str(e))
        raise


def create_slideshow(image_paths: list[str | Path], output_path: str | Path,
                     duration_per_image: float = 3.0, transition: str = "fade",
                     fps: int = 30) -> str:
    """Create a video slideshow from images."""
    if not image_paths:
        raise ValueError("No images provided")

    # Create input file list
    concat_file = str(IMAGES_DIR / "slideshow_concat.txt")
    with open(concat_file, "w") as f:
        for img in image_paths:
            f.write(f"file '{img}'\n")
            f.write(f"duration {duration_per_image}\n")
        # Last image needs to be listed again
        f.write(f"file '{image_paths[-1]}'\n")

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
                "-vf", f"scale=1080:1920:force_original_aspect_ratio=decrease,"
                       f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p",
                "-c:v", "libx264", "-crf", "23", "-r", str(fps),
                str(output_path),
            ],
            capture_output=True, check=True, timeout=300,
        )
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error("slideshow_failed", error=str(e))
        raise


def get_image_info(path: str | Path) -> dict:
    """Get image metadata."""
    info = {"width": 0, "height": 0, "format": "", "file_size_mb": 0.0}
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_streams", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        import json
        data = json.loads(result.stdout)
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                info["width"] = stream.get("width", 0)
                info["height"] = stream.get("height", 0)
                info["format"] = stream.get("codec_name", "")
                break
        info["file_size_mb"] = round(Path(path).stat().st_size / (1024 * 1024), 2)
    except Exception as e:
        logger.warning("image_info_failed", path=str(path), error=str(e))
    return info
