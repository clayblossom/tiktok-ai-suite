"""Content Factory Module — Aggregates all content sub-routers."""
from __future__ import annotations

from fastapi import APIRouter

from .script_generator import router as script_router
from .templates import router as template_router
from .caption_generator import router as caption_router
from .scheduler import router as scheduler_router

router = APIRouter()

# Include all sub-routers
router.include_router(script_router)
router.include_router(template_router)
router.include_router(caption_router)
router.include_router(scheduler_router)
