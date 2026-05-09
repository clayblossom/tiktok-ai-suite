from app.modules.growth_engine import (
    build_brand_profile,
    generate_trend_radar,
    score_content,
    generate_ab_test_plan,
    generate_one_click_blueprint,
    generate_product_content,
)


def test_trend_radar_ranks_actionable_trends_for_niche():
    radar = generate_trend_radar("beauty", "skincare sunscreen")
    assert radar["niche"] == "beauty"
    assert len(radar["trends"]) >= 5
    top = radar["trends"][0]
    assert top["opportunity_score"] >= radar["trends"][-1]["opportunity_score"]
    assert top["hooks"]
    assert top["content_angles"]
    assert "recommended_posting_window" in radar


def test_content_score_detects_weak_hook_and_strong_cta():
    weak = score_content({"hook": "Hello everyone", "body": "This is a product.", "cta": ""})
    strong = score_content({"hook": "Stop wasting money on skincare mistakes", "body": "Here are 3 fixes with before after proof and a quick demo.", "cta": "Comment GUIDE and follow for part 2"})
    assert strong["overall_score"] > weak["overall_score"]
    assert any("hook" in item.lower() for item in weak["recommendations"])
    assert strong["components"]["cta_strength"] > weak["components"]["cta_strength"]


def test_ab_plan_outputs_multiple_variants():
    plan = generate_ab_test_plan("AI tools", "education", 4)
    assert len(plan["variants"]) == 4
    assert {v["variant"] for v in plan["variants"]} == {"A", "B", "C", "D"}
    assert all(v["hook"] and v["caption"] and v["test_goal"] for v in plan["variants"])


def test_one_click_blueprint_contains_full_video_pipeline():
    bp = generate_one_click_blueprint("fitness", "home workout", "motivational", 30)
    assert bp["script"]["hook"]
    assert bp["voiceover"]["style"]
    assert len(bp["visual_plan"]) >= 3
    assert bp["export"]["resolution"] == "1080x1920"
    assert bp["viral_score"]["overall_score"] >= 0


def test_product_content_maps_product_to_conversion_angles():
    result = generate_product_content({"name": "Mini Projector", "category": "Electronics", "price": 49.99, "description": "portable home cinema"})
    assert result["product"]["name"] == "Mini Projector"
    assert len(result["video_ideas"]) >= 5
    assert result["objection_handlers"]
    assert result["conversion_score"] >= 0


def test_brand_profile_normalizes_creator_strategy():
    profile = build_brand_profile({"name": "Daily AI", "niche": "tech", "tone": "casual", "language": "id"})
    assert profile["name"] == "Daily AI"
    assert profile["language"] == "id"
    assert profile["content_pillars"]
