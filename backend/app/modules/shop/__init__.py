"""TikTok Shop Module — Product management, listings, analytics."""
from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, HTTPException

from ...db import insert_row, get_row, get_rows, update_row, delete_row
from ...models import Product, ListingRequest, ListingResponse, ShopAnalytics
from ...connectors.openai_client import generate_listing
from ...config import OPENAI_API_KEY

router = APIRouter()


@router.get("/products")
async def list_products(limit: int = 50, status: str = ""):
    """List all products."""
    products = get_rows("products", limit=limit)
    if status:
        products = [p for p in products if p.get("status") == status]
    for p in products:
        p["images"] = json.loads(p.get("images", "[]"))
        p["tags"] = json.loads(p.get("tags", "[]"))
        p["listing_data"] = json.loads(p.get("listing_data", "{}"))
    return products


@router.post("/products")
async def create_product(product: Product):
    """Add a new product."""
    data = {
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category": product.category,
        "images": json.dumps(product.images),
        "tags": json.dumps(product.tags),
        "stock": product.stock,
        "status": product.status,
        "created_at": datetime.utcnow().isoformat(),
    }
    product_id = insert_row("products", data)
    return {"id": product_id, "status": "created"}


@router.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get product detail."""
    row = get_row("products", product_id)
    if not row:
        raise HTTPException(404, "Product not found")
    row["images"] = json.loads(row.get("images", "[]"))
    row["tags"] = json.loads(row.get("tags", "[]"))
    row["listing_data"] = json.loads(row.get("listing_data", "{}"))
    return row


@router.put("/products/{product_id}")
async def update_product(product_id: int, data: dict):
    """Update a product."""
    if not get_row("products", product_id):
        raise HTTPException(404, "Product not found")
    update_row("products", product_id, data)
    return {"status": "updated", "id": product_id}


@router.delete("/products/{product_id}")
async def delete_product(product_id: int):
    """Delete a product."""
    delete_row("products", product_id)
    return {"status": "deleted", "id": product_id}


@router.post("/products/research")
async def research_products(category: str = "", budget: float = 0):
    """Research trending products."""
    # Sample trending product data
    trending = [
        {"name": "LED Strip Lights", "category": "Home", "avg_price": 15.99, "trend_score": 92, "competition": "medium"},
        {"name": "Phone Ring Holder", "category": "Accessories", "avg_price": 5.99, "trend_score": 88, "competition": "high"},
        {"name": "Posture Corrector", "category": "Health", "avg_price": 19.99, "trend_score": 85, "competition": "low"},
        {"name": "Mini Projector", "category": "Electronics", "avg_price": 49.99, "trend_score": 82, "competition": "medium"},
        {"name": "Resistance Bands Set", "category": "Fitness", "avg_price": 12.99, "trend_score": 80, "competition": "high"},
        {"name": "Car Phone Mount", "category": "Auto", "avg_price": 9.99, "trend_score": 78, "competition": "medium"},
        {"name": "Reusable Water Bottle", "category": "Lifestyle", "avg_price": 14.99, "trend_score": 75, "competition": "high"},
        {"name": "Noise Cancelling Earbuds", "category": "Electronics", "avg_price": 29.99, "trend_score": 73, "competition": "medium"},
    ]

    if category:
        trending = [t for t in trending if category.lower() in t["category"].lower()]
    if budget:
        trending = [t for t in trending if t["avg_price"] <= budget]

    return {"products": trending, "total": len(trending)}


@router.post("/listings/generate", response_model=ListingResponse)
async def generate_product_listing(req: ListingRequest):
    """Generate AI-optimized product listing."""
    if OPENAI_API_KEY:
        try:
            result = await generate_listing(req)
            from ...db import track_api_usage
            track_api_usage("openai", "listings/generate")
            return result
        except Exception:
            pass

    # Fallback
    return ListingResponse(
        title=f"🔥 {req.product_name} - Must Have!",
        description=f"Amazing {req.product_name} perfect for {'everyone' if not req.target_audience else req.target_audience}.\n\n" +
                    "\n".join(f"✅ {f}" for f in req.features) if req.features else f"High quality {req.product_name}.",
        suggested_price=req.price_range[1] if req.price_range[1] else 19.99,
        category="General",
        tags=["tiktokmademebuyit", "trending", "musthave"],
        seo_keywords=[req.product_name.lower(), "tiktok", "trending"],
    )


@router.get("/analytics")
async def get_shop_analytics(period: str = "7d"):
    """Get sales analytics."""
    products = get_rows("products", limit=100)
    total_products = len(products)
    active = len([p for p in products if p.get("status") == "active"])

    return {
        "period": period,
        "total_products": total_products,
        "active_products": active,
        "total_revenue": 0,  # Would be calculated from orders
        "total_orders": count_rows("orders"),
        "avg_order_value": 0,
        "top_products": [],
        "note": "Connect TikTok Shop API for real data",
    }


@router.get("/inventory")
async def get_inventory():
    """Get inventory status."""
    products = get_rows("products", limit=100)
    low_stock = [p for p in products if p.get("stock", 0) < 10]
    out_of_stock = [p for p in products if p.get("stock", 0) == 0]

    return {
        "total_products": len(products),
        "low_stock_count": len(low_stock),
        "out_of_stock_count": len(out_of_stock),
        "low_stock": [{"id": p["id"], "name": p["name"], "stock": p["stock"]} for p in low_stock],
    }


def count_rows(table: str) -> int:
    from ...db import count_rows as _count
    return _count(table)
