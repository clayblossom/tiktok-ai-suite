"""TikTok Shop API Client."""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Optional

import httpx

from ..config import TIKTOK_SHOP_API_KEY, TIKTOK_SHOP_SECRET
from ..utils.logging import get_logger

logger = get_logger(__name__)

BASE_URL = "https://open-api.tiktokglobalshop.com"


def _generate_sign(params: dict) -> str:
    """Generate HMAC signature for TikTok Shop API."""
    sorted_params = "&".join(f"{k}={params[k]}" for k in sorted(params))
    return hmac.new(
        TIKTOK_SHOP_SECRET.encode(),
        sorted_params.encode(),
        hashlib.sha256,
    ).hexdigest()


def _base_params() -> dict:
    """Common API parameters."""
    return {
        "app_key": TIKTOK_SHOP_API_KEY,
        "timestamp": str(int(time.time())),
    }


async def get_products(page: int = 1, page_size: int = 20) -> dict:
    """Get products from TikTok Shop."""
    if not TIKTOK_SHOP_API_KEY:
        return {"products": [], "total": 0}

    params = {**_base_params(), "page": str(page), "page_size": str(page_size)}
    params["sign"] = _generate_sign(params)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{BASE_URL}/product/search", params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error("tiktok_shop_products_failed", error=str(e))
        return {"products": [], "total": 0, "error": str(e)}


async def get_order_details(order_id: str) -> Optional[dict]:
    """Get order details."""
    if not TIKTOK_SHOP_API_KEY:
        return None

    params = {**_base_params(), "order_id": order_id}
    params["sign"] = _generate_sign(params)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{BASE_URL}/order/detail", params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error("tiktok_shop_order_failed", order_id=order_id, error=str(e))
        return None


async def update_inventory(sku_id: str, quantity: int) -> bool:
    """Update product inventory."""
    if not TIKTOK_SHOP_API_KEY:
        return False

    params = {**_base_params(), "sku_id": sku_id, "quantity": str(quantity)}
    params["sign"] = _generate_sign(params)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{BASE_URL}/product/inventory/update",
                json=params,
            )
            resp.raise_for_status()
            return True
    except Exception as e:
        logger.error("tiktok_shop_inventory_failed", sku_id=sku_id, error=str(e))
        return False


async def get_shop_analytics(date_range: str = "7d") -> dict:
    """Get shop analytics from TikTok Shop API."""
    if not TIKTOK_SHOP_API_KEY:
        return {"configured": False, "message": "TikTok Shop API not configured"}

    params = {**_base_params(), "date_range": date_range}
    params["sign"] = _generate_sign(params)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{BASE_URL}/analytics/overview", params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error("tiktok_shop_analytics_failed", error=str(e))
        return {"configured": True, "error": str(e)}


async def check_connection() -> dict:
    """Check TikTok Shop API connectivity."""
    if not TIKTOK_SHOP_API_KEY:
        return {"connected": False, "reason": "API key not configured"}
    return {"connected": True, "shop_id": TIKTOK_SHOP_API_KEY[:8] + "..."}
