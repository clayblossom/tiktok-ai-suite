"""TikTok AI Creator Suite — Main FastAPI application."""
from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import API_HOST, API_PORT, DEBUG
from .db import init_db, count_rows, get_api_usage_today
from .models import HealthResponse

# ── App lifecycle ───────────────────────────────────────────────────────────

START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[tiktok-suite] Initializing database...")
    init_db()
    print(f"[tiktok-suite] Ready! http://{API_HOST}:{API_PORT}")
    yield
    print("[tiktok-suite] Shutting down.")


app = FastAPI(
    title="TikTok AI Creator Suite",
    version="0.2.0",
    description="All-in-one AI platform for TikTok creators.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Middleware stack (order matters: first added = outermost) ───────────────

from .middleware.request_id import RequestIDMiddleware
from .middleware.request_logger import RequestLoggingMiddleware
from .middleware.rate_limiter import RateLimitMiddleware
from .middleware.error_handler import ErrorHandlerMiddleware

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120, requests_per_hour=2000)
app.add_middleware(RequestIDMiddleware)


# ── Health ──────────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        version="0.2.0",
        uptime_seconds=round(time.time() - START_TIME, 1),
        modules={
            "content_factory": True,
            "voice": True,
            "video_editor": True,
            "sound": True,
            "shop": True,
            "dashboard": True,
        },
        storage_mb={
            "videos": 0,
            "audio": 0,
            "images": 0,
            "temp": 0,
        },
    )


# ── Dashboard ───────────────────────────────────────────────────────────────

@app.get("/api/dashboard/overview")
async def dashboard_overview():
    api_usage = get_api_usage_today()
    return {
        "total_projects": count_rows("projects"),
        "total_scripts": count_rows("scripts"),
        "total_videos": count_rows("videos"),
        "total_sounds": count_rows("sounds"),
        "total_products": count_rows("products"),
        "api_cost_today": api_usage["total_cost"],
        "api_usage": api_usage,
    }


# ── Import & register sub-routers ──────────────────────────────────────────

# Auth
from .auth.routes import router as auth_router
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# Content Factory
from .modules.content_factory import router as content_router
app.include_router(content_router, prefix="/api/content", tags=["Content Factory"])

# Voice
from .modules.voice import router as voice_router
app.include_router(voice_router, prefix="/api/voice", tags=["Voice"])

# Video Editor
from .modules.video_editor import router as video_router
app.include_router(video_router, prefix="/api/videos", tags=["Video Editor"])

# Sound
from .modules.sound import router as sound_router
app.include_router(sound_router, prefix="/api/sounds", tags=["Sound"])

# Shop
from .modules.shop import router as shop_router
app.include_router(shop_router, prefix="/api/shop", tags=["TikTok Shop"])

# Dashboard extras
from .modules.dashboard import router as dashboard_router
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=DEBUG)
