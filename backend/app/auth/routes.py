"""Auth API routes — register, login, refresh, profile."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends

from .models import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    TokenRefreshRequest, PasswordChange, UserUpdate,
)
from .jwt_handler import (
    hash_password, verify_password, create_token_pair,
    decode_token, create_access_token, create_refresh_token,
)
from .dependencies import require_user
from ..db import get_db, insert_row, update_row
from ..utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserCreate):
    """Register a new user account."""
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (req.email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

    user_id = insert_row("users", {
        "email": req.email,
        "password_hash": hash_password(req.password),
        "display_name": req.display_name,
        "role": "user",
        "created_at": datetime.utcnow().isoformat(),
    })

    logger.info("user_registered", user_id=user_id, email=req.email)
    tokens = create_token_pair(user_id, req.email)
    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLogin):
    """Authenticate user and return JWT tokens."""
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (req.email,)).fetchone()

    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    logger.info("user_logged_in", user_id=user["id"], email=req.email)
    tokens = create_token_pair(user["id"], user["email"])
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: TokenRefreshRequest):
    """Refresh an expired access token using a refresh token."""
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    email = payload.get("email", "")

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (int(user_id),)).fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    tokens = create_token_pair(int(user_id), email)
    return TokenResponse(**tokens)


@router.get("/me", response_model=UserResponse)
async def get_profile(user: dict = Depends(require_user)):
    """Get current user profile."""
    return UserResponse(
        id=user["id"],
        email=user["email"],
        display_name=user["display_name"],
        role=user["role"],
        created_at=user["created_at"],
    )


@router.put("/me", response_model=UserResponse)
async def update_profile(req: UserUpdate, user: dict = Depends(require_user)):
    """Update current user profile."""
    updates = {}
    if req.display_name is not None:
        updates["display_name"] = req.display_name
    if req.email is not None:
        # Check for conflict
        with get_db() as conn:
            existing = conn.execute("SELECT id FROM users WHERE email = ? AND id != ?",
                                    (req.email, user["id"])).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
        updates["email"] = req.email

    if updates:
        update_row("users", user["id"], updates)
        logger.info("profile_updated", user_id=user["id"], fields=list(updates.keys()))

    with get_db() as conn:
        updated = conn.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()

    return UserResponse(
        id=updated["id"],
        email=updated["email"],
        display_name=updated["display_name"],
        role=updated["role"],
        created_at=updated["created_at"],
    )


@router.post("/change-password")
async def change_password(req: PasswordChange, user: dict = Depends(require_user)):
    """Change the current user's password."""
    if not verify_password(req.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    update_row("users", user["id"], {"password_hash": hash_password(req.new_password)})
    logger.info("password_changed", user_id=user["id"])
    return {"status": "password_changed"}
