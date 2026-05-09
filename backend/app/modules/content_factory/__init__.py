"""Content Factory module — scripts, captions, templates, scheduling."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

# ── Import sub-routers ─────────────────────────────────────────────────────
from .script_generator import router as script_router
from .caption_generator import router as caption_router
from .templates import router as template_router
from .scheduler import router as scheduler_router

# Include all sub-routers under /api/content
router.include_router(script_router, tags=["Scripts"])
router.include_router(caption_router, tags=["Captions"])
router.include_router(template_router, tags=["Templates"])
router.include_router(scheduler_router, tags=["Scheduler"])
