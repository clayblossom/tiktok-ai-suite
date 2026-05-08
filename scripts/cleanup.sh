#!/usr/bin/env bash
# TikTok AI Creator Suite — Disk cleanup
set -e
cd "$(dirname "$0")/.."

echo "=== Disk Cleanup ==="
echo "Before:"
df -h / | tail -1

echo "[1/4] Cleaning temp files..."
rm -rf backend/data/temp/*

echo "[2/4] Cleaning Python caches..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

echo "[3/4] Cleaning build artifacts..."
rm -rf frontend/dist 2>/dev/null || true

echo "[4/4] Vacuuming SQLite..."
if [ -f "backend/data/tiktok_suite.db" ]; then
    sqlite3 backend/data/tiktok_suite.db "VACUUM;"
fi

echo ""
echo "After:"
df -h / | tail -1
