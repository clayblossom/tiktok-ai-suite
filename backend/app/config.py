"""TikTok AI Creator Suite — Configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "tiktok_suite.db"
VIDEOS_DIR = DATA_DIR / "videos"
AUDIO_DIR = DATA_DIR / "audio"
IMAGES_DIR = DATA_DIR / "images"
TEMP_DIR = DATA_DIR / "temp"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
for d in [DATA_DIR, VIDEOS_DIR, AUDIO_DIR, IMAGES_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# API Server
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8800"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# JWT Authentication
SECRET_KEY = os.getenv("SECRET_KEY", "tiktok-ai-suite-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# OpenAI (script generation, chat)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# ElevenLabs (TTS)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")

# Replicate (image/music generation)
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

# Suno (music generation)
SUNO_API_KEY = os.getenv("SUNO_API_KEY", "")

# Pexels (stock footage)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Whisper (speech-to-text)
WHISPER_API_KEY = os.getenv("WHISPER_API_KEY", "")  # Falls back to OPENAI_API_KEY

# TikTok Shop (optional)
TIKTOK_SHOP_API_KEY = os.getenv("TIKTOK_SHOP_API_KEY", "")
TIKTOK_SHOP_SECRET = os.getenv("TIKTOK_SHOP_SECRET", "")

# Processing
MAX_VIDEO_DURATION = int(os.getenv("MAX_VIDEO_DURATION", "600"))  # seconds
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "30"))
VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1080"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1920"))

# Cost tracking
DAILY_BUDGET_USD = float(os.getenv("DAILY_BUDGET_USD", "10.0"))

# Cleanup
MAX_TEMP_AGE_HOURS = int(os.getenv("MAX_TEMP_AGE_HOURS", "24"))
MAX_CACHE_ITEMS = int(os.getenv("MAX_CACHE_ITEMS", "500"))
