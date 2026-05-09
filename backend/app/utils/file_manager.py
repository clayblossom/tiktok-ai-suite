"""File management utilities for uploads, temp files, and cleanup."""
from __future__ import annotations

import hashlib
import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ..config import TEMP_DIR, VIDEOS_DIR, AUDIO_DIR, IMAGES_DIR, MAX_TEMP_AGE_HOURS, MAX_FILE_SIZE_MB
from .logging import get_logger

logger = get_logger(__name__)


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(filename: str) -> str:
    """Sanitize a filename by removing dangerous characters."""
    import re
    name = re.sub(r'[^\w\s\-.]', '', filename)
    name = re.sub(r'\s+', '_', name)
    return name[:200]  # cap length


def generate_unique_filename(prefix: str, extension: str, directory: Optional[Path] = None) -> Path:
    """Generate a unique filename with timestamp and hash."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    random_hash = hashlib.md5(os.urandom(16)).hexdigest()[:8]
    filename = f"{prefix}_{timestamp}_{random_hash}.{extension.lstrip('.')}"
    directory = directory or TEMP_DIR
    ensure_dir(directory)
    return directory / filename


def validate_file_size(file_size_bytes: int) -> bool:
    """Check if file size is within limits."""
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        logger.warning("file_too_large", size_mb=file_size_bytes / (1024 * 1024), max_mb=MAX_FILE_SIZE_MB)
        return False
    return True


def get_file_size_mb(path: str | Path) -> float:
    """Get file size in megabytes."""
    try:
        size_bytes = Path(path).stat().st_size
        return round(size_bytes / (1024 * 1024), 2)
    except OSError:
        return 0.0


def get_directory_size_mb(directory: str | Path) -> float:
    """Calculate total size of all files in a directory."""
    total = 0
    try:
        for path in Path(directory).rglob("*"):
            if path.is_file():
                total += path.stat().st_size
    except OSError:
        pass
    return round(total / (1024 * 1024), 2)


def cleanup_temp_files(max_age_hours: int = MAX_TEMP_AGE_HOURS) -> dict:
    """Remove temp files older than max_age_hours."""
    cutoff = time.time() - (max_age_hours * 3600)
    removed = 0
    freed_bytes = 0

    for path in TEMP_DIR.rglob("*"):
        if path.is_file() and path.stat().st_mtime < cutoff:
            size = path.stat().st_size
            try:
                path.unlink()
                removed += 1
                freed_bytes += size
            except OSError as e:
                logger.warning("cleanup_failed", path=str(path), error=str(e))

    freed_mb = round(freed_bytes / (1024 * 1024), 2)
    logger.info("temp_cleanup", files_removed=removed, freed_mb=freed_mb)
    return {"files_removed": removed, "freed_mb": freed_mb}


def move_file(src: str | Path, dest_dir: str | Path, new_name: Optional[str] = None) -> Path:
    """Move a file to a destination directory."""
    src = Path(src)
    dest_dir = Path(dest_dir)
    ensure_dir(dest_dir)

    dest = dest_dir / (new_name or src.name)
    shutil.move(str(src), str(dest))
    logger.debug("file_moved", src=str(src), dest=str(dest))
    return dest


def copy_file(src: str | Path, dest: str | Path) -> Path:
    """Copy a file to a destination."""
    src = Path(src)
    dest = Path(dest)
    ensure_dir(dest.parent)
    shutil.copy2(str(src), str(dest))
    return dest


def file_exists(path: str | Path) -> bool:
    """Check if a file exists."""
    return Path(path).is_file()


def delete_file(path: str | Path) -> bool:
    """Safely delete a file."""
    try:
        Path(path).unlink(missing_ok=True)
        return True
    except OSError as e:
        logger.warning("delete_failed", path=str(path), error=str(e))
        return False


def get_storage_stats() -> dict:
    """Get storage usage statistics for all data directories."""
    return {
        "videos_mb": get_directory_size_mb(VIDEOS_DIR),
        "audio_mb": get_directory_size_mb(AUDIO_DIR),
        "images_mb": get_directory_size_mb(IMAGES_DIR),
        "temp_mb": get_directory_size_mb(TEMP_DIR),
        "total_mb": (
            get_directory_size_mb(VIDEOS_DIR)
            + get_directory_size_mb(AUDIO_DIR)
            + get_directory_size_mb(IMAGES_DIR)
            + get_directory_size_mb(TEMP_DIR)
        ),
    }
