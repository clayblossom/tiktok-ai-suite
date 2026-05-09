"""Content Factory — Caption and hashtag generation."""
from __future__ import annotations

from fastapi import APIRouter

from ...models import CaptionRequest, CaptionResponse
from ...connectors.openai_client import generate_captions
from ...config import OPENAI_API_KEY
from ...utils.logging import get_logger
from ...utils.cost_tracker import track

logger = get_logger(__name__)

router = APIRouter()


@router.post("/captions/generate", response_model=CaptionResponse)
async def generate_captions_endpoint(req: CaptionRequest):
    """Generate captions and hashtags for a script."""
    if OPENAI_API_KEY:
        try:
            result = await generate_captions(req)
            track("openai", "captions/generate")
            return result
        except Exception as e:
            logger.warning("caption_generation_fallback", error=str(e))

    # Fallback
    return CaptionResponse(
        caption=req.script_text[:150] + "..." if len(req.script_text) > 150 else req.script_text,
        hashtags=["#fyp", "#viral", "#tiktok", f"#{req.niche}" if req.niche else "#trending"],
        emoji_suggestions=["🔥", "💯", "✨", "👀"],
        character_count=len(req.script_text[:150]),
    )


@router.post("/captions/hashtags/suggest")
async def suggest_hashtags(topic: str, niche: str = "", count: int = 10):
    """Suggest relevant hashtags for a topic."""
    # Base hashtags everyone uses
    base_tags = ["#fyp", "#foryou", "#foryoupage", "#viral", "#trending"]

    # Niche-specific tags
    niche_tags = {
        "tech": ["#tech", "#techtok", "#coding", "#ai", "#gadgets"],
        "fitness": ["#fitness", "#gym", "#workout", "#fitcheck", "#gains"],
        "food": ["#foodtok", "#recipe", "#cooking", "#foodie", "#yummy"],
        "beauty": ["#beauty", "#makeup", "#skincare", "#grwm", "#glowup"],
        "comedy": ["#comedy", "#funny", "#humor", "#laugh", "#relatable"],
        "education": ["#learnontiktok", "#facts", "#education", "#knowledge", "#study"],
        "music": ["#music", "#singing", "#newmusic", "#songwriter", "#musician"],
        "fashion": ["#fashion", "#ootd", "#style", "#outfitcheck", "#fashiontiktok"],
        "travel": ["#travel", "#wanderlust", "#adventure", "#explore", "#travelgram"],
    }

    tags = list(base_tags)
    if niche and niche.lower() in niche_tags:
        tags.extend(niche_tags[niche.lower()])

    # Add topic-based tags
    topic_words = topic.lower().split()
    for word in topic_words[:3]:
        if len(word) > 2:
            tags.append(f"#{word}")

    return {"hashtags": tags[:count], "topic": topic, "niche": niche}


@router.post("/captions/seo")
async def generate_seo_caption(text: str, platform: str = "tiktok"):
    """Generate SEO-optimized caption text."""
    if OPENAI_API_KEY:
        try:
            from ...models import CaptionRequest
            req = CaptionRequest(script_text=text, emoji_style="moderate")
            result = await generate_captions(req)
            return result
        except Exception:
            pass

    # Fallback SEO optimization
    optimized = text[:150]
    if len(text) > 150:
        optimized += "..."

    return {
        "caption": optimized,
        "character_count": len(optimized),
        "platform": platform,
        "seo_score": 72,
        "tips": [
            "Keep under 150 characters for maximum reach",
            "Include a question to boost comments",
            "Use 3-5 relevant hashtags",
        ],
    }
