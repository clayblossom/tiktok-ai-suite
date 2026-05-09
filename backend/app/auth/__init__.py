"""Authentication module — JWT auth, user management, middleware."""
from __future__ import annotations

from fastapi import APIRouter

from .routes import router as auth_router

router = auth_router

__all__ = ["router"]
