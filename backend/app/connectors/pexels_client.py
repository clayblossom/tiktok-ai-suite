"""Pexels Stock Media Client — Enhanced with pagination and downloads."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import httpx

from ..config import PEXELS_API_KEY
from ..utils.logging import get_logger

logger = get_logger(__name__)

BASE_URL = "https://api.pexels.com"


def _headers() -> dict:
    return {"Authorization": PEXELS_API_KEY}


async def search_videos(
    query: str,
    per_page: int = 15,
    page: int = 1,
    orientation: str = "portrait",
    min_duration: int = 0,
    max_duration: int = 0,
) -> dict:
    """Search Pexels for stock videos with pagination.

    Returns dict with 'videos' list and pagination info.
    """
    if not PEXELS_API_KEY:
        return {"videos": [], "total_results": 0, "page": page, "per_page": per_page}

    params = {
        "query": query,
        "per_page": min(per_page, 80),
        "page": page,
        "orientation": orientation,
    }
    if min_duration:
        params["min_duration"] = min_duration
    if max_duration:
        params["max_duration"] = max_duration

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/videos/search", headers=_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()

    videos = [
        {
            "id": v["id"],
            "url": v["url"],
            "width": v.get("width", 0),
            "height": v.get("height", 0),
            "duration": v["duration"],
            "thumbnail": v.get("image", ""),
            "preview": next(
                (f["link"] for f in v.get("video_files", []) if f.get("quality") == "sd"),
                v.get("video_files", [{}])[0].get("link", ""),
            ),
            "hd_url": next(
                (f["link"] for f in v.get("video_files", []) if f.get("quality") == "hd"),
                "",
            ),
            "video_files": [
                {"quality": f.get("quality"), "link": f["link"], "width": f.get("width"), "height": f.get("height")}
                for f in v.get("video_files", [])[:5]
            ],
        }
        for v in data.get("videos", [])
    ]

    return {
        "videos": videos,
        "total_results": data.get("total_results", 0),
        "page": data.get("page", page),
        "per_page": data.get("per_page", per_page),
    }


async def search_images(
    query: str,
    per_page: int = 15,
    page: int = 1,
    orientation: str = "portrait",
    size: str = "medium",
    color: Optional[str] = None,
) -> dict:
    """Search Pexels for stock images with pagination.

    Returns dict with 'images' list and pagination info.
    """
    if not PEXELS_API_KEY:
        return {"images": [], "total_results": 0, "page": page, "per_page": per_page}

    params = {
        "query": query,
        "per_page": min(per_page, 80),
        "page": page,
        "orientation": orientation,
        "size": size,
    }
    if color:
        params["color"] = color

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/v1/search", headers=_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()

    images = [
        {
            "id": p["id"],
            "url": p["url"],
            "width": p.get("width", 0),
            "height": p.get("height", 0),
            "thumbnail": p["src"].get("medium", ""),
            "original": p["src"].get("original", ""),
            "large": p["src"].get("large", ""),
            "photographer": p.get("photographer", ""),
            "photographer_url": p.get("photographer_url", ""),
            "alt": p.get("alt", ""),
        }
        for p in data.get("photos", [])
    ]

    return {
        "images": images,
        "total_results": data.get("total_results", 0),
        "page": data.get("page", page),
        "per_page": data.get("per_page", per_page),
    }


async def get_popular_videos(per_page: int = 15, page: int = 1) -> dict:
    """Get popular/trending videos from Pexels."""
    if not PEXELS_API_KEY:
        return {"videos": [], "page": page}

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{BASE_URL}/videos/popular",
            headers=_headers(),
            params={"per_page": min(per_page, 80), "page": page},
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "videos": [
            {
                "id": v["id"],
                "url": v["url"],
                "duration": v["duration"],
                "thumbnail": v.get("image", ""),
            }
            for v in data.get("videos", [])
        ],
        "page": page,
    }


async def download_media(url: str, output_path: str) -> str:
    """Download a media file from Pexels."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(resp.content)

    logger.info("media_downloaded", url=url, path=output_path)
    return output_path
