"""Pexels Stock Media Client."""
from __future__ import annotations

import httpx

from ..config import PEXELS_API_KEY


async def search_videos(query: str, per_page: int = 10) -> list[dict]:
    """Search Pexels for stock videos."""
    if not PEXELS_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": query, "per_page": per_page, "orientation": "portrait"},
        )
        resp.raise_for_status()
        data = resp.json()

    return [
        {
            "id": v["id"],
            "url": v["url"],
            "duration": v["duration"],
            "thumbnail": v.get("image", ""),
            "preview": next(
                (f["link"] for f in v.get("video_files", []) if f.get("quality") == "sd"),
                v.get("video_files", [{}])[0].get("link", ""),
            ),
        }
        for v in data.get("videos", [])
    ]


async def search_images(query: str, per_page: int = 10) -> list[dict]:
    """Search Pexels for stock images."""
    if not PEXELS_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": query, "per_page": per_page, "orientation": "portrait"},
        )
        resp.raise_for_status()
        data = resp.json()

    return [
        {
            "id": p["id"],
            "url": p["url"],
            "thumbnail": p["src"]["medium"],
            "original": p["src"]["original"],
            "photographer": p["photographer"],
        }
        for p in data.get("photos", [])
    ]
