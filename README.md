# TikTok AI Creator Suite

All-in-one AI platform for TikTok creators: generate scripts, voiceovers, videos, trending sounds, and manage TikTok Shop — all from a single dashboard.

## Features

- 📝 **Content Factory** — AI script generation (7 templates), multi-variation, hashtags, captions
- 🎙️ **Voice Studio** — TTS voiceover (ElevenLabs), multi-language, speed control
- 🎬 **Video Editor** — Auto-cut, auto-captions, overlays, templates, 9:16 export
- 🎵 **Sound Lab** — Trending tracker, viral predictor, AI music generation
- 🛒 **TikTok Shop** — Product research, AI listings, inventory, analytics
- 📊 **Dashboard** — Overview stats, content calendar, AI chat assistant

## Quick Start

```bash
git clone <repo-url>
cd tiktok-ai-suite

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env  # Edit with your API keys
uvicorn app.main:app --host 0.0.0.0 --port 8800 --reload

# Frontend (new terminal)
cd frontend
npm install && npm run dev
```

Open http://localhost:5173

## API Keys

| Service | Purpose | Get Key |
|---------|---------|---------|
| OpenAI | Script generation, chat | platform.openai.com |
| ElevenLabs | Voice generation | elevenlabs.io |
| Suno | Music generation | suno.ai |
| Pexels | Stock footage (free) | pexels.com/api |

## Tech Stack

- **Backend**: FastAPI, SQLite, FFmpeg, OpenCV
- **Frontend**: React, TypeScript, Tailwind CSS, Recharts
- **AI**: OpenAI GPT-4, ElevenLabs, Suno, Pexels
