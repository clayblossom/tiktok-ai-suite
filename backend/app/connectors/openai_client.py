"""OpenAI API Client."""
from __future__ import annotations

from typing import Any

import httpx

from ..config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL


async def generate_script(req) -> Any:
    """Generate TikTok script using OpenAI."""
    from ..models import ScriptResponse, ScriptVariation, ContentType

    system = f"""You are a TikTok content creator expert. Generate {req.variations} script variations for a {req.duration}-second TikTok video.

Format: {req.content_type.value}
Tone: {req.tone.value}
Niche: {req.niche or 'general'}
Language: {req.language}

For each variation, provide:
1. HOOK (first 3 seconds - must grab attention!)
2. BODY (main content)
3. CTA (call to action)

Also suggest 5 hashtags and best posting time.

Return as JSON:
{{
  "variations": [
    {{"hook": "...", "body": "...", "cta": "...", "full_text": "...", "estimated_duration": {req.duration}, "engagement_score": 85}}
  ],
  "hashtags": ["#tag1", "#tag2"],
  "best_posting_time": "6:00 PM"
}}"""

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Generate TikTok script about: {req.topic}"},
                ],
                "temperature": 0.8,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        data = resp.json()

    import json
    content = json.loads(data["choices"][0]["message"]["content"])
    variations = [ScriptVariation(**v) for v in content.get("variations", [])]

    return ScriptResponse(
        topic=req.topic,
        niche=req.niche,
        tone=req.tone,
        duration=req.duration,
        content_type=req.content_type,
        variations=variations,
        hashtags=content.get("hashtags", []),
        best_posting_time=content.get("best_posting_time", ""),
    )


async def generate_captions(req) -> Any:
    """Generate captions and hashtags."""
    from ..models import CaptionResponse

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "Generate TikTok caption and hashtags. Return JSON: {\"caption\": \"...\", \"hashtags\": [...], \"emoji_suggestions\": [...]}"},
                    {"role": "user", "content": f"Script: {req.script_text}\nNiche: {req.niche}\nEmoji style: {req.emoji_style}"},
                ],
                "temperature": 0.7,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        data = resp.json()

    import json
    content = json.loads(data["choices"][0]["message"]["content"])
    caption = content.get("caption", "")

    return CaptionResponse(
        caption=caption,
        hashtags=content.get("hashtags", []),
        emoji_suggestions=content.get("emoji_suggestions", []),
        character_count=len(caption),
    )


async def generate_listing(req) -> Any:
    """Generate product listing."""
    from ..models import ListingResponse

    features_text = "\n".join(f"- {f}" for f in req.features) if req.features else "N/A"

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "Generate TikTok Shop listing. Return JSON: {\"title\": \"...\", \"description\": \"...\", \"suggested_price\": 0, \"category\": \"...\", \"tags\": [...], \"seo_keywords\": [...]}"},
                    {"role": "user", "content": f"Product: {req.product_name}\nFeatures: {features_text}\nAudience: {req.target_audience}\nPrice range: {req.price_range}"},
                ],
                "temperature": 0.7,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        data = resp.json()

    import json
    content = json.loads(data["choices"][0]["message"]["content"])

    return ListingResponse(
        title=content.get("title", req.product_name),
        description=content.get("description", ""),
        suggested_price=content.get("suggested_price", 0),
        category=content.get("category", "General"),
        tags=content.get("tags", []),
        seo_keywords=content.get("seo_keywords", []),
    )


async def chat_completion(message: str, system: str = "") -> str:
    """General chat completion."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": message})

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={"model": OPENAI_MODEL, "messages": messages, "temperature": 0.7},
        )
        resp.raise_for_status()
        data = resp.json()

    return data["choices"][0]["message"]["content"]
