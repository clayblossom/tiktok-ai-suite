"""TikTok AI Creator Suite — SQLite database layer."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from .config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't exist."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                content_type TEXT DEFAULT 'custom',
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                topic TEXT NOT NULL,
                niche TEXT DEFAULT '',
                tone TEXT DEFAULT 'casual',
                duration INTEGER DEFAULT 30,
                content_type TEXT DEFAULT 'custom',
                variations TEXT DEFAULT '[]',
                hashtags TEXT DEFAULT '[]',
                best_posting_time TEXT DEFAULT '',
                language TEXT DEFAULT 'en',
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );

            CREATE TABLE IF NOT EXISTS voiceovers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_id INTEGER,
                voice_id TEXT NOT NULL,
                voice_name TEXT DEFAULT '',
                language TEXT DEFAULT 'en',
                speed REAL DEFAULT 1.0,
                file_path TEXT NOT NULL,
                duration_sec REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (script_id) REFERENCES scripts(id)
            );

            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                source_path TEXT,
                output_path TEXT,
                thumbnail_path TEXT,
                duration_sec REAL DEFAULT 0,
                resolution TEXT DEFAULT '1080x1920',
                file_size_mb REAL DEFAULT 0,
                template_used TEXT DEFAULT '',
                captions TEXT DEFAULT '[]',
                overlays TEXT DEFAULT '[]',
                status TEXT DEFAULT 'uploading',
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );

            CREATE TABLE IF NOT EXISTS sounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT DEFAULT '',
                source TEXT DEFAULT 'custom',
                genre TEXT DEFAULT '',
                mood TEXT DEFAULT '',
                bpm INTEGER DEFAULT 0,
                duration_sec REAL DEFAULT 0,
                file_path TEXT,
                viral_score REAL DEFAULT 0,
                trending_data TEXT DEFAULT '{}',
                preview_url TEXT DEFAULT '',
                external_id TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                price REAL DEFAULT 0,
                category TEXT DEFAULT '',
                images TEXT DEFAULT '[]',
                tags TEXT DEFAULT '[]',
                stock INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                listing_data TEXT DEFAULT '{}',
                sales_data TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity INTEGER DEFAULT 1,
                total_price REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                customer_data TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS sound_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sound_id INTEGER,
                collection TEXT DEFAULT 'favorites',
                notes TEXT DEFAULT '',
                added_at TEXT NOT NULL,
                FOREIGN KEY (sound_id) REFERENCES sounds(id)
            );

            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                endpoint TEXT DEFAULT '',
                tokens_used INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0,
                metadata TEXT DEFAULT '{}',
                timestamp TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS trending_sounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT UNIQUE,
                title TEXT NOT NULL,
                artist TEXT DEFAULT '',
                usage_count INTEGER DEFAULT 0,
                growth_rate REAL DEFAULT 0,
                category TEXT DEFAULT '',
                duration_sec REAL DEFAULT 0,
                viral_score REAL DEFAULT 0,
                preview_url TEXT DEFAULT '',
                first_seen TEXT NOT NULL,
                last_updated TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS content_calendar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                title TEXT NOT NULL,
                scheduled_date TEXT NOT NULL,
                content_type TEXT DEFAULT 'custom',
                status TEXT DEFAULT 'draft',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );

            CREATE INDEX IF NOT EXISTS idx_scripts_project ON scripts(project_id);
            CREATE INDEX IF NOT EXISTS idx_videos_project ON videos(project_id);
            CREATE INDEX IF NOT EXISTS idx_voiceovers_script ON voiceovers(script_id);
            CREATE INDEX IF NOT EXISTS idx_api_usage_ts ON api_usage(timestamp);
            CREATE INDEX IF NOT EXISTS idx_api_usage_service ON api_usage(service);
            CREATE INDEX IF NOT EXISTS idx_trending_sounds_score ON trending_sounds(viral_score);
            CREATE INDEX IF NOT EXISTS idx_calendar_date ON content_calendar(scheduled_date);
        """)


# ── Generic CRUD helpers ────────────────────────────────────────────────────

def insert_row(table: str, data: dict[str, Any]) -> int:
    with get_db() as conn:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        cur = conn.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
            list(data.values()),
        )
        return cur.lastrowid


def get_row(table: str, row_id: int) -> dict[str, Any] | None:
    with get_db() as conn:
        row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,)).fetchone()
    return dict(row) if row else None


def get_rows(table: str, limit: int = 50, offset: int = 0, order: str = "id DESC") -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            f"SELECT * FROM {table} ORDER BY {order} LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [dict(r) for r in rows]


def update_row(table: str, row_id: int, data: dict[str, Any]) -> bool:
    with get_db() as conn:
        sets = ", ".join(f"{k} = ?" for k in data)
        conn.execute(
            f"UPDATE {table} SET {sets} WHERE id = ?",
            list(data.values()) + [row_id],
        )
    return True


def delete_row(table: str, row_id: int) -> bool:
    with get_db() as conn:
        conn.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
    return True


def count_rows(table: str) -> int:
    with get_db() as conn:
        row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
    return row["cnt"] if row else 0


# ── API Usage ───────────────────────────────────────────────────────────────

def track_api_usage(service: str, endpoint: str, tokens: int = 0, cost: float = 0, metadata: dict = None):
    insert_row("api_usage", {
        "service": service,
        "endpoint": endpoint,
        "tokens_used": tokens,
        "cost_usd": cost,
        "metadata": json.dumps(metadata or {}),
        "timestamp": datetime.utcnow().isoformat(),
    })


def get_api_usage_today() -> dict[str, float]:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    with get_db() as conn:
        rows = conn.execute(
            """SELECT service, SUM(cost_usd) as total_cost, SUM(tokens_used) as total_tokens
               FROM api_usage WHERE timestamp LIKE ? GROUP BY service""",
            (f"{today}%",),
        ).fetchall()
    result = {"total_cost": 0, "total_tokens": 0, "by_service": {}}
    for r in rows:
        result["total_cost"] += r["total_cost"]
        result["total_tokens"] += r["total_tokens"]
        result["by_service"][r["service"]] = {
            "cost": r["total_cost"],
            "tokens": r["total_tokens"],
        }
    return result
