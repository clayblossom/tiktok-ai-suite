"""TikTok AI Creator Suite — Pydantic models."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    PUBLISHED = "published"


class ContentType(str, Enum):
    STORYTIME = "storytime"
    TUTORIAL = "tutorial"
    DID_YOU_KNOW = "did_you_know"
    POV = "pov"
    RANKING = "ranking"
    BEFORE_AFTER = "before_after"
    THINGS_THAT = "things_that"
    DUET = "duet"
    CUSTOM = "custom"


class ToneStyle(str, Enum):
    FUNNY = "funny"
    EDUCATIONAL = "educational"
    DRAMATIC = "dramatic"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    MOTIVATIONAL = "motivational"


class VideoStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    EXPORTING = "exporting"
    DONE = "done"
    ERROR = "error"


class CaptionStyle(str, Enum):
    WORD_HIGHLIGHT = "word_highlight"
    KARAOKE = "karaoke"
    SUBTITLE = "subtitle"
    EMOJI = "emoji"


# ── Content Factory Models ──────────────────────────────────────────────────

class ScriptRequest(BaseModel):
    topic: str
    niche: str = ""
    tone: ToneStyle = ToneStyle.CASUAL
    duration: int = 30  # seconds
    content_type: ContentType = ContentType.CUSTOM
    variations: int = 3  # number of variations to generate
    language: str = "en"


class ScriptVariation(BaseModel):
    hook: str
    body: str
    cta: str
    full_text: str
    estimated_duration: int
    engagement_score: float = 0  # 0-100


class ScriptResponse(BaseModel):
    id: int | None = None
    topic: str
    niche: str
    tone: ToneStyle
    duration: int
    content_type: ContentType
    variations: list[ScriptVariation]
    hashtags: list[str] = []
    best_posting_time: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CaptionRequest(BaseModel):
    script_text: str
    niche: str = ""
    language: str = "en"
    emoji_style: str = "moderate"  # none, moderate, heavy


class CaptionResponse(BaseModel):
    caption: str
    hashtags: list[str]
    emoji_suggestions: list[str]
    character_count: int


# ── Voice Models ────────────────────────────────────────────────────────────

class VoiceRequest(BaseModel):
    text: str
    voice_id: str = "alloy"
    language: str = "en"
    speed: float = 1.0
    pitch: float = 0
    emotion: str = "neutral"


class VoiceInfo(BaseModel):
    id: str
    name: str
    language: str
    gender: str
    preview_url: str = ""
    provider: str = "elevenlabs"


class VoiceoverResponse(BaseModel):
    id: int | None = None
    script_id: int | None = None
    voice_id: str
    voice_name: str
    language: str
    speed: float
    file_path: str
    duration_sec: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── Video Editor Models ─────────────────────────────────────────────────────

class VideoUploadResponse(BaseModel):
    id: int
    filename: str
    duration_sec: float
    resolution: str
    file_size_mb: float
    status: VideoStatus


class AutoCutRequest(BaseModel):
    video_id: int
    cut_interval: float = 3.0  # seconds between cuts
    remove_silence: bool = True
    silence_threshold: float = -30  # dB
    min_silence_duration: float = 0.5


class CaptionOverlayRequest(BaseModel):
    video_id: int
    style: CaptionStyle = CaptionStyle.WORD_HIGHLIGHT
    font: str = "classic"
    color: str = "#FFFFFF"
    outline_color: str = "#000000"
    position: str = "bottom"  # bottom, center, top
    size: int = 48


class TextOverlayRequest(BaseModel):
    video_id: int
    text: str
    position_x: int = 50  # percentage
    position_y: int = 50
    font_size: int = 48
    color: str = "#FFFFFF"
    start_time: float = 0
    end_time: float = 0  # 0 = until end
    animation: str = "none"  # none, fade, slide, bounce


class VideoExportRequest(BaseModel):
    video_id: int
    quality: str = "standard"  # draft, standard, high
    add_watermark: bool = False
    watermark_text: str = ""
    background_music_id: int | None = None
    music_volume: float = 0.3  # 0-1


class VideoTemplate(BaseModel):
    id: str
    name: str
    description: str
    category: str
    preview_url: str = ""
    overlay_config: dict[str, Any] = {}


# ── Sound Models ────────────────────────────────────────────────────────────

class TrendingSound(BaseModel):
    id: int | None = None
    external_id: str
    title: str
    artist: str
    usage_count: int = 0
    growth_rate: float = 0
    category: str = ""
    duration_sec: float = 0
    viral_score: float = 0  # 0-100
    preview_url: str = ""
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class MusicGenRequest(BaseModel):
    prompt: str
    genre: str = "pop"
    mood: str = "upbeat"
    duration: int = 30  # seconds
    bpm: int = 120
    instrumental: bool = True


class MusicGenResponse(BaseModel):
    id: int | None = None
    prompt: str
    genre: str
    mood: str
    duration_sec: float
    file_path: str
    bpm: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SoundMatchRequest(BaseModel):
    content_type: ContentType
    mood: str
    duration: int
    niche: str = ""


# ── TikTok Shop Models ──────────────────────────────────────────────────────

class Product(BaseModel):
    id: int | None = None
    name: str
    description: str = ""
    price: float = 0
    category: str = ""
    images: list[str] = []
    tags: list[str] = []
    stock: int = 0
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ListingRequest(BaseModel):
    product_name: str
    features: list[str] = []
    target_audience: str = ""
    price_range: tuple[float, float] = (0, 0)
    language: str = "en"


class ListingResponse(BaseModel):
    title: str
    description: str
    suggested_price: float
    category: str
    tags: list[str]
    seo_keywords: list[str]


class SalesData(BaseModel):
    date: str
    revenue: float
    orders: int
    units_sold: int
    avg_order_value: float


class ShopAnalytics(BaseModel):
    period: str
    total_revenue: float
    total_orders: int
    avg_order_value: float
    top_products: list[dict[str, Any]]
    daily_data: list[SalesData]


# ── Dashboard Models ────────────────────────────────────────────────────────

class DashboardOverview(BaseModel):
    total_projects: int
    total_scripts: int
    total_videos: int
    total_sounds: int
    total_products: int
    api_cost_today: float
    storage_used_mb: float
    recent_activity: list[dict[str, Any]]


class CalendarEntry(BaseModel):
    id: int
    project_id: int
    title: str
    date: datetime
    content_type: ContentType
    status: ProjectStatus


class ChatMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str
    context: str = ""


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[str] = []


# ── API Usage Tracking ──────────────────────────────────────────────────────

class ApiUsageRecord(BaseModel):
    id: int | None = None
    service: str  # openai, elevenlabs, replicate, suno, pexels
    endpoint: str
    tokens_used: int = 0
    cost_usd: float = 0
    metadata: dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Health ──────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    uptime_seconds: float = 0
    modules: dict[str, bool] = {}
    storage_mb: dict[str, float] = {}
