# 🎵 TikTok AI Creator Suite

> **Your AI-powered TikTok command center.** Generate scripts, voiceovers, videos, trending sounds, and manage TikTok Shop — all from a single dashboard.

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-yellow)
![React](https://img.shields.io/badge/react-18+-cyan)

---
<img width="1672" height="941" alt="coding 3" src="https://github.com/user-attachments/assets/610047ac-d4e0-413a-9d84-f4d633c8087d" />

## ✨ Features

| Module | Description | Status |
|--------|-------------|--------|
| 📝 **Content Factory** | AI script generation (8 templates), multi-variation, hashtags, captions, scheduler | ✅ |
| 🎙️ **Voice Studio** | TTS voiceover (ElevenLabs), multi-language, speed control | ✅ |
| 🎬 **Video Editor** | Auto-cut, auto-captions, overlays, templates, 9:16 export | ✅ |
| 🎵 **Sound Lab** | Trending tracker, viral predictor, AI music generation (Suno) | ✅ |
| 🛒 **TikTok Shop** | Product research, AI listings, inventory, analytics | ✅ |
| 📊 **Dashboard** | Overview stats, content calendar, activity feed, quick actions | ✅ |
| 🔐 **Authentication** | JWT auth with register, login, refresh tokens, profile management | ✅ |
| 🌙 **Dark Mode** | Full dark mode support with persistent preference | ✅ |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Dashboard │ │ Content  │ │  Voice   │ │  Video   │  ...      │
│  │  Page    │ │ Factory  │ │  Studio  │ │  Editor  │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       └─────────────┴────────────┴─────────────┘                │
│                         │ REST API                              │
└─────────────────────────┼───────────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│  ┌──────────────────────┴──────────────────────┐                │
│  │              Middleware Stack                 │                │
│  │  RequestID → Logger → RateLimiter → Error    │                │
│  └──────────────────────┬──────────────────────┘                │
│       ┌─────────────────┼─────────────────┐                     │
│  ┌────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐             │
│  │  Auth    │     │  Modules  │     │Dashboard  │             │
│  │ (JWT)    │     │ (6 total) │     │           │             │
│  └────┬─────┘     └─────┬─────┘     └───────────┘             │
│       │                 │                                       │
│  ┌────▼─────────────────▼──────────────────────┐               │
│  │            API Connectors                    │               │
│  │  OpenAI · ElevenLabs · Suno · Pexels        │               │
│  │  Replicate · TikTok Shop · Whisper          │               │
│  └──────────────────┬──────────────────────────┘               │
│                     │                                           │
│  ┌──────────┐  ┌────▼─────┐  ┌────────────┐                   │
│  │  SQLite  │  │  Celery  │  │    File    │                   │
│  │    DB    │  │  Workers │  │  Storage   │                   │
│  └──────────┘  └──────────┘  └────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Clone the repository

```bash
git clone https://github.com/clayblossom/tiktok-ai-suite.git
cd tiktok-ai-suite
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your API keys (see API Keys section)

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8800 --reload
```

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Open the app

🌐 **Frontend:** http://localhost:5173
📡 **API Docs:** http://localhost:8800/docs
❤️ **Health Check:** http://localhost:8800/api/health

---

## 🔑 API Keys

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| **OpenAI** | Script generation, chat, captions | $5 credit | [platform.openai.com](https://platform.openai.com) |
| **ElevenLabs** | Voice generation (TTS) | 10K chars/mo | [elevenlabs.io](https://elevenlabs.io) |
| **Suno** | AI music generation | Limited | [suno.ai](https://suno.ai) |
| **Pexels** | Stock footage & images | Unlimited (free) | [pexels.com/api](https://www.pexels.com/api/) |
| **Replicate** | AI image generation | $5 credit | [replicate.com](https://replicate.com) |
| **TikTok Shop** | Shop API (optional) | N/A | [TikTok Shop Open Platform](https://seller.tiktokglobalshop.com) |

### .env.example

```env
# API Server
API_HOST=0.0.0.0
API_PORT=8800
DEBUG=true

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1

# ElevenLabs
ELEVENLABS_API_KEY=...

# Replicate
REPLICATE_API_TOKEN=...

# Suno
SUNO_API_KEY=...

# Pexels (free)
PEXELS_API_KEY=...

# TikTok Shop (optional)
TIKTOK_SHOP_API_KEY=...
TIKTOK_SHOP_SECRET=...

# Processing
MAX_VIDEO_DURATION=600
MAX_FILE_SIZE_MB=500
VIDEO_FPS=30
VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920

# Cost control
DAILY_BUDGET_USD=10.0
```

> 💡 **No API keys?** The app works in fallback mode with basic templates and mock data. You can explore the UI without any keys configured.

---

## 📁 Project Structure

```
tiktok-ai-suite/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── db.py                # SQLite database operations
│   │   ├── models.py            # Pydantic models
│   │   ├── auth/                # Authentication system
│   │   │   ├── routes.py        # Login, register, refresh, profile
│   │   │   ├── jwt_handler.py   # JWT token creation & verification
│   │   │   ├── models.py        # Auth Pydantic models
│   │   │   └── dependencies.py  # Auth dependency injection
│   │   ├── connectors/          # External API clients
│   │   │   ├── openai_client.py
│   │   │   ├── elevenlabs_client.py
│   │   │   ├── suno_client.py
│   │   │   ├── pexels_client.py
│   │   │   ├── replicate_client.py
│   │   │   ├── tiktok_shop_client.py
│   │   │   └── whisper_client.py
│   │   ├── modules/             # Feature modules
│   │   │   ├── content_factory/ # Scripts, captions, templates, scheduler
│   │   │   ├── voice/           # TTS voice generation
│   │   │   ├── video_editor/    # Video processing & export
│   │   │   ├── sound/           # Trending sounds & AI music
│   │   │   ├── shop/            # TikTok Shop management
│   │   │   └── dashboard/       # Overview & analytics
│   │   ├── middleware/           # Request processing
│   │   │   ├── request_id.py    # Unique request ID tracking
│   │   │   ├── request_logger.py # Structured logging
│   │   │   ├── rate_limiter.py  # Sliding window rate limiting
│   │   │   └── error_handler.py # Global error handling
│   │   ├── utils/               # Shared utilities
│   │   │   ├── audio_utils.py
│   │   │   ├── video_utils.py
│   │   │   ├── image_utils.py
│   │   │   ├── file_manager.py
│   │   │   ├── cost_tracker.py
│   │   │   └── logging.py
│   │   └── workers/             # Background tasks
│   │       ├── celery_app.py
│   │       ├── audio_tasks.py
│   │       └── video_tasks.py
│   ├── data/                    # SQLite database
│   ├── requirements.txt
│   └── .venv/
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main app with auth & dark mode
│   │   ├── api.ts               # API client with JWT auto-refresh
│   │   ├── index.css            # Tailwind + custom components
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx    # Auth page with gradient theme
│   │   │   ├── Dashboard.tsx    # Stats, charts, activity feed
│   │   │   ├── ContentFactory.tsx # Script generation UI
│   │   │   ├── VoiceStudio.tsx  # TTS interface
│   │   │   ├── VideoEditor.tsx  # Video editing UI
│   │   │   ├── SoundAnalyzer.tsx # Sound lab interface
│   │   │   └── ShopManager.tsx  # TikTok Shop management
│   │   ├── components/
│   │   │   ├── Header.tsx       # Top bar with dark toggle
│   │   │   ├── Sidebar.tsx      # Navigation sidebar
│   │   │   └── common/          # Reusable UI components
│   │   └── hooks/               # Custom React hooks
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── package.json
├── scripts/
│   ├── run_dev.sh               # Development startup script
│   └── cleanup.sh               # Cleanup script
├── .env.example
├── .gitignore
├── PROJECT_PLAN.md              # Detailed project plan
└── README.md
```

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/register         — Create new account
POST   /api/auth/login            — Sign in, get JWT tokens
POST   /api/auth/refresh          — Refresh access token
GET    /api/auth/me               — Get current user profile
PUT    /api/auth/me               — Update profile
POST   /api/auth/change-password  — Change password
```

### Content Factory
```
POST   /api/content/scripts/generate   — Generate AI script
GET    /api/content/scripts            — List all scripts
GET    /api/content/scripts/{id}       — Get script detail
PUT    /api/content/scripts/{id}       — Update script
DELETE /api/content/scripts/{id}       — Delete script
POST   /api/content/captions/generate  — Generate captions & hashtags
POST   /api/content/captions/hashtags/suggest — Suggest hashtags
POST   /api/content/captions/seo       — SEO-optimized caption
GET    /api/content/content-templates  — List content templates
GET    /api/content/content-templates/{id} — Get template detail
GET    /api/content/schedule           — Get content calendar
POST   /api/content/schedule           — Schedule content
GET    /api/content/schedule/suggestions — Posting time suggestions
```

### Voice Studio
```
POST   /api/voice/generate        — Generate TTS voiceover
GET    /api/voice/voices          — List available voices
GET    /api/voice/{id}            — Get voiceover detail
```

### Video Editor
```
GET    /api/videos                — List videos
GET    /api/videos/{id}           — Get video detail
POST   /api/videos/{id}/auto-cut  — AI auto-cut
POST   /api/videos/{id}/captions  — Add auto-captions
POST   /api/videos/{id}/export    — Export final video
```

### Sound Lab
```
GET    /api/sounds/trending       — Get trending sounds
POST   /api/sounds/generate       — Generate AI music
GET    /api/sounds/library        — Personal sound library
```

### TikTok Shop
```
GET    /api/shop/products         — List products
POST   /api/shop/products         — Add product
POST   /api/shop/listings/generate — Generate AI listing
GET    /api/shop/analytics        — Sales analytics
```

### Dashboard
```
GET    /api/health                — System health check
GET    /api/dashboard/overview    — Dashboard summary
```

---

## 🛡️ Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register** → Get access + refresh tokens
2. **Login** → Get access + refresh tokens
3. **API calls** → Include `Authorization: Bearer <access_token>` header
4. **Token expired** → Use refresh token to get new access token

### Example flow

```bash
# Register
curl -X POST http://localhost:8800/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure123", "display_name": "Creator"}'

# Response: {"access_token": "...", "refresh_token": "...", "token_type": "bearer"}

# Use the token
curl http://localhost:8800/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## 🧩 Content Templates

8 built-in content templates for different TikTok formats:

| Template | Icon | Best For | Avg Engagement |
|----------|------|----------|----------------|
| Storytime | 📖 | Lifestyle, entertainment | 8.5% |
| Tutorial/How-to | 📚 | Education, crafts, cooking | 7.2% |
| Did You Know | 🧠 | Science, history, facts | 9.1% |
| POV | 👁️ | Comedy, drama, relatable | 8.8% |
| Ranking/Tier List | 🏆 | Food, sports, tech | 7.8% |
| Before/After | 🔄 | Fitness, home, makeup | 9.3% |
| Things That... | 📋 | Comedy, relatable, niche | 7.5% |
| Duet/Stitch | 🎭 | Reactions, debates | 8.0% |

---

## 🎨 UI Features

- **🌙 Dark Mode** — Toggle in header, persists across sessions
- **📊 Dashboard** — Stat cards, activity feed, quick actions, performance charts
- **✍️ Content Factory** — Tabbed interface, content type cards, tone selector, duration slider
- **🔐 Login Page** — Gradient dark theme, animated background, social login options
- **📱 Responsive** — Collapsible sidebar, mobile-friendly layout
- **⚡ Animations** — Fade-in, slide-up, hover effects, loading skeletons

---

## 🧰 Tech Stack

### Backend
- **Framework:** FastAPI 0.104+
- **Database:** SQLite (via Python stdlib)
- **Auth:** PyJWT + bcrypt
- **Logging:** structlog
- **HTTP Client:** httpx
- **Background Tasks:** Celery (optional)
- **Video Processing:** FFmpeg, OpenCV, moviepy
- **Image Processing:** Pillow

### Frontend
- **Framework:** React 18+ with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS with custom design system
- **State:** React hooks (useState, useEffect)
- **API Client:** Fetch API with JWT auto-refresh

### AI Services
- **Text Generation:** OpenAI GPT-4o
- **Voice Generation:** ElevenLabs
- **Music Generation:** Suno
- **Image Generation:** Replicate (FLUX)
- **Stock Media:** Pexels API
- **Speech-to-Text:** OpenAI Whisper

---

## 📊 Database Schema

11 tables covering all modules:

| Table | Purpose |
|-------|---------|
| `users` | User accounts & auth |
| `projects` | Content projects |
| `scripts` | Generated scripts |
| `voiceovers` | TTS audio files |
| `videos` | Video projects |
| `sounds` | Music & sound clips |
| `products` | TikTok Shop products |
| `orders` | Shop orders |
| `content_calendar` | Scheduled content |
| `analytics` | Usage metrics |
| `api_usage` | API cost tracking |

---

## 🔧 Development

### Run in development mode

```bash
# Terminal 1: Backend with hot reload
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8800

# Terminal 2: Frontend with hot reload
cd frontend && npm run dev
```

### Run both with script

```bash
./scripts/run_dev.sh
```

### Database

The SQLite database is auto-created on first run at `backend/data/tiktok_suite.db`. Tables are created automatically via `init_db()`.

---

## 🚢 Production Deployment

### Docker (coming soon)

```bash
docker-compose up -d
```

### Manual deployment

```bash
# Build frontend
cd frontend && npm run build

# Serve with production server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8800 --workers 4
```

### Environment variables for production

```env
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8800
DAILY_BUDGET_USD=50.0
```

---

## 📈 Roadmap

- [ ] Docker & docker-compose setup
- [ ] WebSocket real-time progress (video rendering, voice generation)
- [ ] Test suite (pytest + vitest)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] User roles & permissions (admin, editor, viewer)
- [ ] Multi-language UI (EN, ID, JA, KO)
- [ ] TikTok OAuth integration
- [ ] Mobile app (React Native)
- [ ] Collaborative editing
- [ ] AI chat assistant
- [ ] Analytics dashboard with charts (Recharts)
- [ ] Export to TikTok directly

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — Backend framework
- [React](https://react.dev/) — Frontend framework
- [Tailwind CSS](https://tailwindcss.com/) — Styling
- [OpenAI](https://openai.com/) — AI text generation
- [ElevenLabs](https://elevenlabs.io/) — Voice synthesis
- [Suno](https://suno.ai/) — AI music generation
- [Pexels](https://www.pexels.com/) — Stock media

---

<div align="center">
  <b>Built with ❤️ for TikTok creators</b>
  <br>
  <sub>TikTok AI Creator Suite v0.2.0</sub>
</div>
