"""TikTok Growth OS engine.

Deterministic strategy generators for trend intelligence, viral scoring,
A/B tests, one-click content blueprints, brand memory, and TikTok Shop
conversion planning. These functions are API-key free so the suite has a
useful fallback mode for demos and local development.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
import hashlib

TREND_FORMATS = [
    {"name": "3-second problem hook", "pattern": "Call out a painful mistake, then promise a fast fix.", "sound_mood": "fast upbeat voiceover bed", "base_score": 91, "saturation": 48},
    {"name": "POV transformation", "pattern": "Show before/after identity shift with quick proof cuts.", "sound_mood": "dramatic build", "base_score": 87, "saturation": 55},
    {"name": "Comment-to-video answer", "pattern": "Open with a real audience question and answer it visually.", "sound_mood": "clean tutorial", "base_score": 84, "saturation": 34},
    {"name": "Myth vs truth", "pattern": "Break one common belief, reveal the surprising alternative.", "sound_mood": "curiosity pulse", "base_score": 82, "saturation": 41},
    {"name": "Tiny experiment", "pattern": "Run a small test on camera and reveal the result at the end.", "sound_mood": "suspense loop", "base_score": 79, "saturation": 37},
    {"name": "Checklist swipe", "pattern": "Rapid checklist with visual ticks every 1-2 seconds.", "sound_mood": "snappy pop", "base_score": 76, "saturation": 52},
]

NICHE_SIGNALS = {
    "beauty": ["before/after", "routine", "ingredient", "glow", "mistake"],
    "fitness": ["form check", "challenge", "transformation", "routine", "protein"],
    "tech": ["AI tool", "automation", "setup", "shortcut", "hidden feature"],
    "education": ["explain", "framework", "mistake", "study", "step-by-step"],
    "food": ["recipe", "texture", "budget", "hack", "taste test"],
    "fashion": ["outfit", "dupe", "styling", "capsule", "before/after"],
    "crypto": ["risk", "wallet", "alpha", "explain", "chart"],
    "shop": ["problem-solution", "demo", "unboxing", "proof", "objection"],
}

DEFAULT_BRAND = {
    "name": "Creator Brand",
    "niche": "general",
    "tone": "casual",
    "language": "en",
    "target_audience": "TikTok viewers who want fast, useful content",
    "forbidden_words": [],
    "visual_style": "high-contrast vertical captions, quick proof cuts, clean overlays",
    "voice_style": "energetic but natural",
    "cta_style": "comment keyword + follow for the next part",
}


def _stable_jitter(*parts: Any, scale: int = 9) -> int:
    raw = "|".join(str(p).lower() for p in parts)
    return int(hashlib.sha256(raw.encode()).hexdigest()[:4], 16) % scale


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def build_brand_profile(data: dict[str, Any] | None = None) -> dict[str, Any]:
    data = data or {}
    profile = {**DEFAULT_BRAND, **{k: v for k, v in data.items() if v not in (None, "")}}
    niche = str(profile.get("niche", "general")).lower()
    pillars = data.get("content_pillars") or [
        f"{niche} education",
        "trend riding",
        "proof/demo content",
        "soft-selling stories",
        "audience Q&A",
    ]
    profile["content_pillars"] = pillars
    profile["posting_mix"] = {"education": 40, "trend_riding": 25, "proof_or_demo": 20, "personal_story": 10, "direct_offer": 5}
    profile["updated_at"] = datetime.utcnow().isoformat()
    return profile


def generate_trend_radar(niche: str = "general", topic: str = "") -> dict[str, Any]:
    niche_key = (niche or "general").lower()
    signals = NICHE_SIGNALS.get(niche_key, ["hook", "proof", "story", "tutorial", "mistake"])
    trends = []
    for idx, trend in enumerate(TREND_FORMATS):
        signal = signals[idx % len(signals)]
        jitter = _stable_jitter(niche_key, topic, trend["name"])
        opportunity = _clamp_score(trend["base_score"] + jitter - trend["saturation"] * 0.22)
        trends.append({
            "rank": 0,
            "name": trend["name"],
            "pattern": trend["pattern"],
            "niche_signal": signal,
            "sound_mood": trend["sound_mood"],
            "velocity": _clamp_score(62 + jitter * 3 + idx),
            "saturation_score": trend["saturation"],
            "opportunity_score": opportunity,
            "hooks": [
                f"Stop doing this with {topic or niche_key}...",
                f"Nobody tells beginners this {signal} trick",
                f"I tested the {topic or niche_key} advice so you do not have to",
            ],
            "content_angles": [
                f"Show the common {signal} mistake",
                "Reveal proof within the first 5 seconds",
                "End with a comment keyword for follow-up demand",
            ],
        })
    trends.sort(key=lambda x: x["opportunity_score"], reverse=True)
    for i, item in enumerate(trends, 1):
        item["rank"] = i
    return {
        "niche": niche_key,
        "topic": topic,
        "generated_at": datetime.utcnow().isoformat(),
        "recommended_posting_window": "18:00-21:00 local time",
        "trend_summary": f"Best current angle for {niche_key}: {trends[0]['name']} using {trends[0]['niche_signal']} proof.",
        "trends": trends,
    }


def score_content(payload: dict[str, Any]) -> dict[str, Any]:
    hook = str(payload.get("hook") or payload.get("title") or "")
    body = str(payload.get("body") or payload.get("script") or "")
    cta = str(payload.get("cta") or "")
    caption = str(payload.get("caption") or "")
    lower = " ".join([hook, body, cta, caption]).lower()
    hook_strength = 30
    if any(w in hook.lower() for w in ["stop", "mistake", "secret", "nobody", "pov", "before", "after", "tested", "don't"]):
        hook_strength += 35
    if 6 <= len(hook.split()) <= 14:
        hook_strength += 20
    if "?" in hook or "..." in hook:
        hook_strength += 8
    proof = 35 + sum(word in lower for word in ["proof", "demo", "tested", "before", "after", "result", "step"]) * 10
    clarity = 45 + min(30, len(body.split()) // 4)
    emotion = 35 + sum(word in lower for word in ["waste", "fear", "love", "hate", "shocking", "easy", "fast", "pain"]) * 8
    cta_strength = 20 + sum(word in cta.lower() for word in ["comment", "follow", "save", "share", "link", "part 2", "guide"]) * 15
    pacing = 55 + (15 if payload.get("duration", 30) <= 45 else 0) + (10 if len(body.split()) < 120 else -10)
    components = {
        "hook_strength": _clamp_score(hook_strength),
        "proof_density": _clamp_score(proof),
        "clarity": _clamp_score(clarity),
        "emotional_trigger": _clamp_score(emotion),
        "cta_strength": _clamp_score(cta_strength),
        "visual_pacing": _clamp_score(pacing),
    }
    overall = _clamp_score(sum(components.values()) / len(components))
    recommendations = []
    if components["hook_strength"] < 70:
        recommendations.append("Strengthen hook: call out a mistake, secret, test, or before/after result in the first 3 seconds.")
    if components["proof_density"] < 65:
        recommendations.append("Add visual proof: demo, result, screenshot, or before/after cut.")
    if components["cta_strength"] < 60:
        recommendations.append("Add a specific CTA: comment a keyword, save this, or follow for part 2.")
    if components["visual_pacing"] < 65:
        recommendations.append("Tighten pacing: cut every 2-4 seconds and keep one idea per scene.")
    return {"overall_score": overall, "components": components, "recommendations": recommendations or ["Ready to publish; test 2 hook variants."], "verdict": "high_potential" if overall >= 78 else "needs_revision" if overall < 62 else "solid"}


def generate_ab_test_plan(topic: str, niche: str = "general", variants: int = 5) -> dict[str, Any]:
    styles = [
        ("Curiosity", f"Nobody explains {topic} like this", "curiosity hold rate"),
        ("Problem", f"Stop making this {topic} mistake", "pain-point resonance"),
        ("Proof", f"I tested {topic} for 7 days", "proof-driven retention"),
        ("Contrarian", f"The popular {topic} advice is wrong", "comment velocity"),
        ("Checklist", f"3 {topic} fixes you can use today", "save rate"),
    ]
    out = []
    for idx, (style, hook, goal) in enumerate(styles[: max(1, min(variants, 5))]):
        out.append({
            "variant": chr(65 + idx),
            "angle": style,
            "hook": hook,
            "cover_text": hook[:42],
            "caption": f"Testing this {niche} angle: {topic}. Save this and comment GUIDE for the checklist.",
            "hashtags": ["#fyp", "#tiktoktips", f"#{niche.replace(' ', '')}", f"#{topic.replace(' ', '')[:24]}"],
            "test_goal": goal,
            "success_metric": "3-second hold + saves + comments",
        })
    return {"topic": topic, "niche": niche, "variants": out, "testing_window": "Publish variants across 3 posting windows; keep visual style constant."}


def generate_one_click_blueprint(niche: str, topic: str, tone: str = "casual", duration: int = 30, brand: dict[str, Any] | None = None) -> dict[str, Any]:
    profile = build_brand_profile({"niche": niche, "tone": tone, **(brand or {})})
    radar = generate_trend_radar(niche, topic)
    top = radar["trends"][0]
    hook = top["hooks"][0]
    script = {"hook": hook, "body": f"Show the common problem around {topic}, demonstrate the fix in 3 quick steps, then reveal the result with a clear before/after proof shot.", "cta": "Comment GUIDE and follow for the next breakdown.", "duration": duration, "tone": tone}
    visual_plan = [
        {"time": "0-3s", "shot": "pattern interrupt close-up", "overlay": hook},
        {"time": "3-10s", "shot": "problem demo", "overlay": "The mistake"},
        {"time": "10-22s", "shot": "3 fast proof cuts", "overlay": "Fix 1 / Fix 2 / Fix 3"},
        {"time": f"22-{duration}s", "shot": "result + CTA", "overlay": "Comment GUIDE"},
    ]
    score = score_content({**script, "caption": f"{topic} guide for {niche}", "duration": duration})
    return {"brand_profile": profile, "trend_used": top, "script": script, "voiceover": {"style": profile["voice_style"], "speed": 1.05 if duration <= 30 else 1.0, "language": profile["language"]}, "visual_plan": visual_plan, "sound": {"mood": top["sound_mood"], "mix": "duck music to 25% under voiceover"}, "caption": f"{hook} Save this if you want the full {topic} checklist.", "hashtags": ["#fyp", f"#{niche.replace(' ', '')}", "#viral", "#creator"], "export": {"resolution": "1080x1920", "fps": 30, "format": "mp4", "safe_zones": True}, "viral_score": score}


def generate_product_content(product: dict[str, Any]) -> dict[str, Any]:
    name = product.get("name", "Product")
    category = product.get("category", "Shop")
    price = float(product.get("price") or product.get("avg_price") or 0)
    pain = f"people who want a faster/easier {category.lower()} solution"
    ideas = []
    angles = ["problem-solution demo", "unboxing proof", "before-after result", "3 reasons", "myth vs truth", "budget comparison"]
    for i, angle in enumerate(angles, 1):
        ideas.append({"title": f"{i}. {name}: {angle}", "hook": f"I did not expect this {name} to solve this problem", "script_angle": f"Open with the pain point, show {name} in use, reveal one measurable benefit, then handle price/value.", "cta": "Comment LINK for the product checklist" if price else "Comment REVIEW for the checklist", "conversion_intent": _clamp_score(72 + i * 3 - (8 if price > 60 else 0))})
    objections = [
        {"objection": "Is it worth the price?", "response_angle": "Compare cost per use and show the alternative cost."},
        {"objection": "Will it work for me?", "response_angle": "Show 3 use cases and who should/should not buy it."},
        {"objection": "Is the quality good?", "response_angle": "Film close-up proof, stress test, and real result."},
    ]
    return {"product": {"name": name, "category": category, "price": price, "target_audience": pain}, "positioning": f"{name} as a practical shortcut for {pain}.", "video_ideas": ideas, "objection_handlers": objections, "bundle_or_offer": "Bundle with a complementary low-ticket item and frame it as a starter kit.", "conversion_score": _clamp_score(78 - (5 if price > 75 else 0) + _stable_jitter(name, category))}


def generate_content_calendar(niche: str, days: int = 30) -> dict[str, Any]:
    pillars = ["education", "trend_riding", "proof_or_demo", "soft_sell", "audience_QA"]
    entries = []
    start = datetime.utcnow().date()
    for i in range(max(1, min(days, 60))):
        pillar = pillars[i % len(pillars)]
        entries.append({"date": (start + timedelta(days=i)).isoformat(), "pillar": pillar, "title": f"{niche.title()} {pillar.replace('_', ' ')} video #{i+1}", "format": TREND_FORMATS[i % len(TREND_FORMATS)]["name"], "goal": "retention" if pillar in ("education", "trend_riding") else "conversion" if pillar == "soft_sell" else "community", "posting_window": "18:00-21:00"})
    return {"niche": niche, "days": len(entries), "mix": build_brand_profile({"niche": niche})["posting_mix"], "entries": entries}
