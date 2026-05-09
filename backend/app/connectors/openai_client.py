"""OpenAI API Client — Enhanced with retry, streaming, cost tracking."""
from __future__ import annotations

import json
from typing import Any, AsyncIterator, Optional

import httpx

from ..config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL
from ..utils.logging import get_logger
from ..utils import cost_tracker

logger = get_logger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 1.0  # seconds


class OpenAIError(Exception):
    """Custom OpenAI API error."""
    def __init__(self, message: str, status_code: int = 0, response_body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


def _get_headers() -> dict:
    return {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }


async def _request_with_retry(
    method: str,
    url: str,
    json_body: Optional[dict] = None,
    timeout: float = 30,
    stream: bool = False,
) -> httpx.Response:
    """Make an HTTP request with exponential backoff retry."""
    import asyncio
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if stream:
                    # For streaming, return immediately
                    resp = await client.send(
                        client.build_request(method, url, headers=_get_headers(), json=json_body),
                        stream=True,
                    )
                    if resp.status_code == 200:
                        return resp
                else:
                    resp = await client.request(method, url, headers=_get_headers(), json=json_body)

                if resp.status_code == 429:
                    # Rate limited — wait and retry
                    retry_after = float(resp.headers.get("retry-after", RETRY_BACKOFF_BASE * (2 ** attempt)))
                    logger.warning("openai_rate_limited", attempt=attempt + 1, retry_after=retry_after)
                    await asyncio.sleep(retry_after)
                    continue

                if resp.status_code >= 500:
                    # Server error — retry
                    await asyncio.sleep(RETRY_BACKOFF_BASE * (2 ** attempt))
                    continue

                if resp.status_code >= 400:
                    raise OpenAIError(
                        f"OpenAI API error: {resp.status_code}",
                        status_code=resp.status_code,
                        response_body=resp.text,
                    )

                return resp

        except httpx.TimeoutException as e:
            last_error = e
            logger.warning("openai_timeout", attempt=attempt + 1)
            await asyncio.sleep(RETRY_BACKOFF_BASE * (2 ** attempt))
        except OpenAIError:
            raise
        except Exception as e:
            last_error = e
            await asyncio.sleep(RETRY_BACKOFF_BASE * (2 ** attempt))

    raise OpenAIError(f"OpenAI request failed after {MAX_RETRIES} retries: {last_error}")


async def _chat(messages: list[dict], model: str = OPENAI_MODEL,
                temperature: float = 0.7, response_format: Optional[dict] = None,
                max_tokens: Optional[int] = None) -> dict:
    """Core chat completion with cost tracking."""
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format:
        body["response_format"] = response_format
    if max_tokens:
        body["max_tokens"] = max_tokens

    resp = await _request_with_retry(
        "POST",
        f"{OPENAI_BASE_URL}/chat/completions",
        json_body=body,
        timeout=60,
    )
    data = resp.json()

    # Track usage
    usage = data.get("usage", {})
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)
    cost = cost_tracker.calculate_openai_cost(model, input_tokens, output_tokens)
    cost_tracker.track("openai", "chat/completions", input_tokens + output_tokens, cost,
                       {"model": model})

    return data


async def stream_chat(messages: list[dict], model: str = OPENAI_MODEL,
                      temperature: float = 0.7) -> AsyncIterator[str]:
    """Stream chat completion tokens."""
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream(
            "POST",
            f"{OPENAI_BASE_URL}/chat/completions",
            headers=_get_headers(),
            json=body,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    line = line[6:]
                    if line.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(line)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError):
                        continue


async def generate_script(req: Any) -> Any:
    """Generate TikTok script using OpenAI."""
    from ..models import ScriptResponse, ScriptVariation

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

    data = await _chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Generate TikTok script about: {req.topic}"},
        ],
        temperature=0.8,
        response_format={"type": "json_object"},
    )

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


async def generate_captions(req: Any) -> Any:
    """Generate captions and hashtags."""
    from ..models import CaptionResponse

    data = await _chat(
        messages=[
            {"role": "system", "content": 'Generate TikTok caption and hashtags. Return JSON: {"caption": "...", "hashtags": [...], "emoji_suggestions": [...]}'},
            {"role": "user", "content": f"Script: {req.script_text}\nNiche: {req.niche}\nEmoji style: {req.emoji_style}"},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    content = json.loads(data["choices"][0]["message"]["content"])
    caption = content.get("caption", "")

    return CaptionResponse(
        caption=caption,
        hashtags=content.get("hashtags", []),
        emoji_suggestions=content.get("emoji_suggestions", []),
        character_count=len(caption),
    )


async def generate_listing(req: Any) -> Any:
    """Generate product listing."""
    from ..models import ListingResponse

    features_text = "\n".join(f"- {f}" for f in req.features) if req.features else "N/A"

    data = await _chat(
        messages=[
            {"role": "system", "content": 'Generate TikTok Shop listing. Return JSON: {"title": "...", "description": "...", "suggested_price": 0, "category": "...", "tags": [...], "seo_keywords": [...]}'},
            {"role": "user", "content": f"Product: {req.product_name}\nFeatures: {features_text}\nAudience: {req.target_audience}\nPrice range: {req.price_range}"},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

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

    data = await _chat(messages=messages, temperature=0.7)
    return data["choices"][0]["message"]["content"]


async def generate_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """Generate text embedding."""
    resp = await _request_with_retry(
        "POST",
        f"{OPENAI_BASE_URL}/embeddings",
        json_body={"model": model, "input": text},
        timeout=15,
    )
    data = resp.json()
    cost_tracker.track("openai", "embeddings", data.get("usage", {}).get("total_tokens", 0), 0.0001)
    return data["data"][0]["embedding"]
