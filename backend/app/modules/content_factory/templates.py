"""Content Factory — Content templates."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter()

# Content template definitions
CONTENT_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "storytime",
        "name": "Storytime",
        "description": "Personal story with hook — perfect for engagement",
        "icon": "📖",
        "structure": ["hook", "setup", "conflict", "resolution", "cta"],
        "tips": [
            "Start with a shocking or relatable hook",
            "Keep the story concise — under 60 seconds",
            "End with a cliffhanger for comments",
        ],
        "best_for": ["lifestyle", "entertainment", "personal"],
        "avg_engagement": 8.5,
    },
    {
        "id": "tutorial",
        "name": "Tutorial/How-to",
        "description": "Step-by-step guide viewers can follow",
        "icon": "📚",
        "structure": ["hook", "materials", "step_1", "step_2", "step_3", "result", "cta"],
        "tips": [
            "Show the end result first to hook viewers",
            "Number each step clearly",
            "Keep steps simple and visual",
        ],
        "best_for": ["education", "crafts", "cooking", "tech"],
        "avg_engagement": 7.2,
    },
    {
        "id": "did_you_know",
        "name": "Did You Know",
        "description": "Facts & trivia that surprise viewers",
        "icon": "🧠",
        "structure": ["hook", "fact_1", "fact_2", "fact_3", "mind_blown_cta"],
        "tips": [
            "Start with the most surprising fact",
            "Use text overlays for emphasis",
            "End with 'Follow for more facts'",
        ],
        "best_for": ["education", "science", "history", "nature"],
        "avg_engagement": 9.1,
    },
    {
        "id": "pov",
        "name": "POV",
        "description": "Point of view scenario for immersion",
        "icon": "👁️",
        "structure": ["scenario", "action", "reaction"],
        "tips": [
            "Make the POV relatable to your audience",
            "Use trending sounds for POV videos",
            "Keep it under 15 seconds for max replays",
        ],
        "best_for": ["comedy", "relatable", "drama"],
        "avg_engagement": 8.8,
    },
    {
        "id": "ranking",
        "name": "Ranking/Tier List",
        "description": "Rank items or ideas from worst to best",
        "icon": "🏆",
        "structure": ["intro", "worst", "bad", "mid", "good", "best", "cta"],
        "tips": [
            "Put controversial picks to spark comments",
            "Use visual tier list overlays",
            "Ask viewers for their rankings",
        ],
        "best_for": ["food", "entertainment", "sports", "tech"],
        "avg_engagement": 7.8,
    },
    {
        "id": "before_after",
        "name": "Before/After",
        "description": "Transformation content",
        "icon": "🔄",
        "structure": ["before_hook", "transformation", "after_reveal", "cta"],
        "tips": [
            "Build suspense before the reveal",
            "Use transitions for the transformation",
            "Show the process briefly",
        ],
        "best_for": ["fitness", "home", "makeup", "cleaning"],
        "avg_engagement": 9.3,
    },
    {
        "id": "things_that",
        "name": "Things That...",
        "description": "Relatable list format",
        "icon": "📋",
        "structure": ["hook", "item_1", "item_2", "item_3", "relate_cta"],
        "tips": [
            "Make each item increasingly relatable",
            "Use trending sounds",
            "Tag someone in the CTA",
        ],
        "best_for": ["comedy", "relatable", "niche"],
        "avg_engagement": 7.5,
    },
    {
        "id": "duet",
        "name": "Duet/Stitch",
        "description": "Response format for engagement",
        "icon": "🎭",
        "structure": ["original_hook", "your_response", "addition", "cta"],
        "tips": [
            "React to trending content",
            "Add unique value with your response",
            "Use the stitch format for hot takes",
        ],
        "best_for": ["reactions", "debates", "tutorials"],
        "avg_engagement": 8.0,
    },
]


@router.get("/content-templates")
async def list_content_templates():
    """List available content templates with details."""
    return CONTENT_TEMPLATES


@router.get("/content-templates/{template_id}")
async def get_content_template(template_id: str):
    """Get a specific content template by ID."""
    for t in CONTENT_TEMPLATES:
        if t["id"] == template_id:
            return t
    return {"error": "Template not found"}


@router.get("/content-templates/recommend")
async def recommend_template(niche: str = "", goal: str = "engagement"):
    """Get template recommendations based on niche and goal."""
    scored = []
    for t in CONTENT_TEMPLATES:
        score = t.get("avg_engagement", 5)
        if niche and niche.lower() in [b.lower() for b in t.get("best_for", [])]:
            score += 2
        scored.append({**t, "recommendation_score": round(score, 1)})

    scored.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return scored[:5]
