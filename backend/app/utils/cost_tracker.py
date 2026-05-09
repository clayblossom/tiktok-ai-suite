"""Cost tracking and budget management for API usage."""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from ..config import DAILY_BUDGET_USD
from ..db import track_api_usage, get_api_usage_today, get_db
from .logging import get_logger

logger = get_logger(__name__)

# Pricing per 1K tokens (or per call for non-token services)
PRICING = {
    "openai": {
        "gpt-4o": {"input": 0.0025, "output": 0.01},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "whisper": {"per_minute": 0.006},
    },
    "elevenlabs": {
        "per_character": 0.00003,  # ~$0.30 per 10K chars
    },
    "replicate": {
        "flux": {"per_image": 0.003},
        "video_gen": {"per_second": 0.01},
    },
    "suno": {
        "per_song": 0.05,
    },
}


def calculate_openai_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for OpenAI API call."""
    pricing = PRICING["openai"].get(model, PRICING["openai"]["gpt-4o-mini"])
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    return round(input_cost + output_cost, 6)


def calculate_elevenlabs_cost(character_count: int) -> float:
    """Calculate cost for ElevenLabs TTS."""
    return round(character_count * PRICING["elevenlabs"]["per_character"], 6)


def calculate_replicate_cost(model: str, units: int = 1) -> float:
    """Calculate cost for Replicate API call."""
    if model == "flux":
        return round(units * PRICING["replicate"]["flux"]["per_image"], 6)
    elif model == "video_gen":
        return round(units * PRICING["replicate"]["video_gen"]["per_second"], 6)
    return round(units * 0.003, 6)


def track(service: str, endpoint: str, tokens: int = 0, cost: float = 0,
          metadata: Optional[dict] = None) -> None:
    """Track an API call with cost."""
    track_api_usage(service, endpoint, tokens, cost, metadata or {})
    logger.info("api_usage_tracked", service=service, endpoint=endpoint,
                tokens=tokens, cost_usd=cost)


def check_budget() -> dict:
    """Check if daily budget has been exceeded."""
    usage = get_api_usage_today()
    current_cost = usage.get("total_cost", 0)
    remaining = max(0, DAILY_BUDGET_USD - current_cost)
    exceeded = current_cost >= DAILY_BUDGET_USD

    if exceeded:
        logger.warning("daily_budget_exceeded", spent=current_cost, budget=DAILY_BUDGET_USD)

    return {
        "budget_usd": DAILY_BUDGET_USD,
        "spent_usd": round(current_cost, 4),
        "remaining_usd": round(remaining, 4),
        "exceeded": exceeded,
        "by_service": usage.get("by_service", {}),
    }


def is_within_budget(estimated_cost: float) -> bool:
    """Check if a proposed API call fits within remaining budget."""
    usage = get_api_usage_today()
    remaining = DAILY_BUDGET_USD - usage.get("total_cost", 0)
    return remaining >= estimated_cost


def get_usage_report(days: int = 7) -> list[dict]:
    """Get usage report for the last N days."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT DATE(timestamp) as day, service,
                      SUM(cost_usd) as total_cost, SUM(tokens_used) as total_tokens,
                      COUNT(*) as call_count
               FROM api_usage
               WHERE timestamp >= DATE('now', ?)
               GROUP BY DATE(timestamp), service
               ORDER BY day DESC""",
            (f"-{days} days",),
        ).fetchall()

    report: dict[str, dict] = {}
    for r in rows:
        day = r["day"]
        if day not in report:
            report[day] = {"date": day, "total_cost": 0, "total_calls": 0, "services": {}}
        report[day]["total_cost"] += r["total_cost"]
        report[day]["total_calls"] += r["call_count"]
        report[day]["services"][r["service"]] = {
            "cost": round(r["total_cost"], 4),
            "tokens": r["total_tokens"],
            "calls": r["call_count"],
        }

    return list(report.values())
