# TikTok AI Creator Suite — Detailed Project Plan

Status: Planning phase
Target: VPS-1 (14GB disk, 5.4GB free, 1.9GB RAM, 2 CPU)
Approach: API-based (external AI services + local processing)
Estimated size: ~3.5 GB

---

## One-line pitch
All-in-one AI platform for TikTok creators: generate scripts, voiceovers, videos, trending sounds, and manage TikTok Shop — all from a single dashboard.

## Tagline
Your AI-powered TikTok command center.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│                    USER INTERFACES                               │
│                                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │   Web App    │  │   CLI Tool   │  │  Telegram    │         │
│   │  (React)     │  │  (Python)    │  │    Bot       │         │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│          │                 │                 │                   │
│          └─────────────────┼─────────────────┘                   │
│                            │                                     │
│                    ┌───────▼───────┐                             │
│                    │   FastAPI     │                             │
│                    │   Gateway     │                             │
│                    │  (port 8800)  │                             │
│                    └───────┬───────┘                             │
│                            │                                     │
│        ┌───────────────────┼───────────────────┐                │
│        │                   │                   │                │
│   ┌────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐          │
│   │ Content  │      │  Video    │      │  Sound    │          │
│   │ Factory  │      │  Editor   │      │ Analyzer  │          │
│   │ Module   │      │  Module   │      │  Module   │          │
│   └────┬─────┘      └─────┬─────┘      └─────┬─────┘          │
│        │                  │                   │                 │
│        └──────────────────┼───────────────────┘                │
│                           │                                     │
│                    ┌──────▼──────┐                              │
│                    │  TikTok     │                              │
│                    │  Shop       │                              │
│                    │  Module     │                              │
│                    └──────┬──────┘                              │
│                           │                                     │
│        ┌──────────────────┼──────────────────┐                 │
│        │                  │                  │                 │
│   ┌────▼─────┐     ┌─────▼─────┐     ┌─────▼──────┐          │
│   │  SQLite  │     │  Celery   │     │  File      │          │
│   │    DB    │     │  Workers  │     │  Storage   │          │
│   └──────────┘     └───────────┘     └────────────┘          │
│                                                                │
│        ┌──────────────────────────────────────┐               │
│        │         EXTERNAL AI APIs             │               │
│        │                                      │               │
│        │  OpenAI ─ Anthropic ─ ElevenLabs     │               │
│        │  Replicate ─ Suno ─ Pexels           │               │
│        └──────────────────────────────────────┘               │
│                                                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Module 1: Content Factory (📝)

### Purpose
Generate complete TikTok content from a topic/niche: script, voiceover, visuals, captions, hashtags.

### Features

#### 1.1 AI Script Generator
- Input: topic, niche, tone (funny/educational/dramatic), duration (15s/30s/60s/3min)
- Output: structured script with:
  - Hook (first 3 seconds — critical for retention)
  - Body (main content, pacing markers)
  - CTA (call to action — follow, comment, share)
  - Estimated watch time
- Multiple variations (generate 3-5 scripts, pick best)
- Trending format templates:
  - Storytime format
  - Tutorial/How-to format
  - "Did you know" format
  - POV format
  - Ranking/Tier list format
  - Before/After format
  - "Things that..." format
  - Duet/Stitch format

#### 1.2 Voice Generation (TTS)
- Multiple voice styles:
  - Trending TikTok voices (narrator, whisper, excited, calm)
  - Multi-language support (EN, ID, JA, KO, ZH, ES)
  - Custom voice cloning (optional, via ElevenLabs)
- Voice settings: speed, pitch, emotion
- Preview before download
- Export: MP3, WAV, OGG

#### 1.3 Visual Asset Manager
- Auto B-roll sourcing:
  - Pexels API (free stock video)
  - Pixabay API (free stock images/video)
  - AI-generated images (via Replicate/FLUX)
- Image overlay templates:
  - Text overlays (trending fonts)
  - Sticker packs
  - Progress bars
  - Subscribe/Follow buttons
- Background removal (rembg)
- Smart cropping for 9:16 ratio

#### 1.4 Caption & Hashtag Generator
- Auto-generate captions based on script
- Hashtag research:
  - Trending hashtags by niche
  - Hashtag difficulty scoring
  - Optimal hashtag count (3-5 recommended)
- Emoji suggestions
- Character count optimization

#### 1.5 Content Scheduler
- Calendar view for scheduled posts
- Best posting time suggestions (AI-powered)
- Queue management
- Draft system
- Content recycling (repost evergreen content)

### API Integrations
- OpenAI GPT-4 (script generation)
- ElevenLabs (voice generation)
- Pexels (stock footage)
- Replicate (AI image generation)

---

## Module 2: Video Editor (🎬)

### Purpose
AI-powered video editing specifically optimized for TikTok format.

### Features

#### 2.1 Auto-Cutter
- Upload raw video → AI analyzes and cuts for optimal pacing
- Pacing rules:
  - Cut every 2-5 seconds (TikTok best practice)
  - Remove dead air/silence
  - Cut on speech pauses
  - Jump cut generator
- Silence detection and removal
- Scene change detection

#### 2.2 Auto-Captions
- Speech-to-text (Whisper API or local)
- Caption styles:
  - Word-by-word highlight (trending TikTok style)
  - Karaoke-style (word color change)
  - Subtitle style (2-3 words per line)
  - Emoji-enhanced captions
- Positioning: bottom, center, top
- Font library (trending TikTok fonts):
  - Classic (sans-serif)
  - Handwritten
  - Bold Impact
  - Neon glow
  - Retro
- Color schemes: white/black outline, yellow, custom
- Size and animation options

#### 2.3 Transition Effects
- Cut transitions (hard cut, jump cut)
- Zoom transitions (zoom in/out on speaker)
- Swipe transitions (left, right, up, down)
- Fade transitions
- Glitch effect
- Shake effect (emphasis)
- Speed ramp (slow-mo → fast)

#### 2.4 Template Library
Pre-built templates for common TikTok formats:
- **Storytime**: Text overlay + background video + voiceover
- **Tutorial**: Step-by-step with numbered overlays
- **Review**: Product showcase + text rating
- **Before/After**: Split screen transformation
- **Ranking**: Tier list with drag positions
- **POV**: First-person perspective with text
- **Green Screen**: Background replacement
- **Duet Layout**: Side-by-side format
- **React**: Picture-in-picture reaction

#### 2.5 Overlay System
- Text overlays with animation
- Image/sticker overlays
- Logo/watermark placement
- Progress bar overlay
- Subscribe button animation
- Countdown timer overlay
- Lower third (name/title bar)

#### 2.6 Audio Processing
- Background music mixing (volume ducking during speech)
- Sound effect insertion
- Audio normalization
- Noise reduction
- Voice enhancement

#### 2.7 Export
- Format: MP4 (H.264)
- Resolution: 1080x1920 (9:16 TikTok native)
- Frame rate: 30fps
- Quality presets: Draft (fast), Standard, High (slow)
- File size optimization

### Technical
- FFmpeg for all video processing
- OpenCV for scene detection
- Pillow for image overlays
- moviepy for complex edits

---

## Module 3: Sound Analyzer (🎵)

### Purpose
Track trending sounds, predict viral audio, generate custom music.

### Features

#### 3.1 Trending Sounds Tracker
- Data sources:
  - TikTok Creative Center (trending sounds)
  - Chartmetric API
  - Manual scraping (ethical, rate-limited)
- Track metrics:
  - Usage count (how many videos use this sound)
  - Growth rate (is it rising or falling?)
  - Category/genre
  - Duration
  - Associated hashtags
- Trending timeline (when did it start trending?)
- Category filtering (hip-hop, pop, electronic, spoken, etc.)

#### 3.2 Sound Viral Predictor
- AI scoring model (0-100) for sound viral potential
- Factors:
  - Current growth trajectory
  - Genre momentum
  - Creator adoption rate
  - Cross-platform presence
  - Seasonal relevance
- Prediction: "This sound will peak in ~3 days"

#### 3.3 AI Music Generator
- Input: mood, genre, duration, BPM
- Output: custom royalty-free music
- Genres: lo-fi, hip-hop, electronic, cinematic, pop, ambient
- Duration presets: 15s, 30s, 60s
- Loop-friendly generation
- Stems separation (optional)
- API: Suno API or Replicate (MusicGen)

#### 3.4 Sound Library
- Personal sound library (save favorites)
- Collections by mood/genre
- Quick preview and download
- Import from trending list
- Custom sound upload

#### 3.5 Sound-to-Content Matching
- Input a sound → suggest content types that work well
- Input content → suggest trending sounds that match
- Mood/energy matching algorithm
- Genre-content correlation database

### API Integrations
- Suno API (music generation)
- Replicate/MusicGen (fallback music gen)
- TikTok Creative Center (trending data)
- Spotify API (music metadata, optional)

---

## Module 4: TikTok Shop Manager (🛒)

### Purpose
AI-powered e-commerce management for TikTok Shop sellers.

### Features

#### 4.1 Product Research
- Trending product finder:
  - Category analysis (what's selling)
  - Price range analysis
  - Competition density
  - Profit margin calculator
- Product scoring (0-100):
  - Trend score
  - Competition score
  - Margin score
  - Shipping complexity score
- Niche opportunity detector

#### 4.2 AI Listing Generator
- Input: product name, images, key features
- Output:
  - Optimized title (SEO-friendly, keyword-rich)
  - Description (bullet points + narrative)
  - Price suggestion (based on competition)
  - Category recommendation
  - Tag suggestions
- A/B title testing suggestions
- Keyword density analysis

#### 4.3 Dynamic Pricing
- Competitor price monitoring
- Demand-based pricing suggestions
- Discount strategy optimizer
- Bundle pricing calculator
- Flash sale timing suggestions

#### 4.4 Sales Analytics Dashboard
- Revenue tracking (daily, weekly, monthly)
- Order volume trends
- Best-selling products
- Customer demographics
- Return rate tracking
- Profit margin analysis
- Conversion funnel visualization

#### 4.5 Inventory Management
- Stock level tracking
- Low stock alerts
- Reorder point calculator
- Supplier management
- SKU generator

#### 4.6 Ad Creative Generator
- TikTok ad video scripts
- Ad copy generation
- Audience targeting suggestions
- Budget allocation optimizer
- A/B test creative variations

### API Integrations
- TikTok Shop API (products, orders, analytics)
- OpenAI (listing generation)
- Pexels (product imagery)

---

## Module 5: Dashboard & Analytics (📊)

### Purpose
Unified dashboard showing all metrics, projects, and AI insights.

### Features

#### 5.1 Project Manager
- List all content projects
- Status tracking: Draft → In Progress → Review → Published
- Kanban board view
- Project templates

#### 5.2 Content Calendar
- Monthly/weekly calendar view
- Drag-and-drop scheduling
- Content type color coding
- Best time indicators

#### 5.3 Analytics Overview
- Total content created
- AI usage metrics (tokens, API calls, cost)
- Processing queue status
- Storage usage
- Recent activity feed

#### 5.4 AI Assistant Chat
- Chat interface for quick tasks:
  - "Generate 5 hook ideas for fitness niche"
  - "What's trending on TikTok today?"
  - "Suggest a content plan for this week"
  - "Analyze this video script"
- Context-aware (knows your recent content)
- Quick action buttons

#### 5.5 Settings & Configuration
- API key management
- Default voice/video preferences
- Notification settings
- Export preferences
- Account management

---

## Database Schema

### Tables

#### users
- id, username, email, api_keys (encrypted), preferences (JSON), created_at

#### projects
- id, user_id, title, status (draft/in_progress/review/published), type, metadata (JSON), created_at, updated_at

#### scripts
- id, project_id, topic, niche, tone, duration, hook, body, cta, full_text, hashtags, variations (JSON), created_at

#### voiceovers
- id, script_id, voice_id, voice_name, language, speed, pitch, file_path, duration_sec, created_at

#### videos
- id, project_id, source_path, output_path, duration_sec, resolution, template_used, captions (JSON), status, created_at

#### sounds
- id, title, artist, source (trending/custom), genre, bpm, duration_sec, file_path, viral_score, trending_data (JSON), created_at

#### products
- id, name, description, price, category, images (JSON), listing_data (JSON), sales_data (JSON), created_at

#### orders
- id, product_id, quantity, total_price, status, customer_data (JSON), created_at

#### analytics
- id, date, metric_type, metric_value, metadata (JSON)

#### trending_sounds
- id, sound_id_ext, title, artist, usage_count, growth_rate, category, first_seen, last_updated

#### api_usage
- id, service, endpoint, tokens_used, cost_usd, timestamp

---

## API Endpoints

### Content Factory
```
POST   /api/scripts/generate          — Generate AI script
GET    /api/scripts                    — List scripts
GET    /api/scripts/{id}              — Get script detail
PUT    /api/scripts/{id}              — Update script
POST   /api/voiceovers/generate       — Generate TTS voiceover
GET    /api/voiceovers/{id}           — Get voiceover detail
GET    /api/voices                     — List available voices
POST   /api/assets/search             — Search stock footage/images
POST   /api/captions/generate         — Generate hashtags & captions
```

### Video Editor
```
POST   /api/videos/upload             — Upload raw video
POST   /api/videos/{id}/auto-cut      — Auto-cut video
POST   /api/videos/{id}/captions      — Add auto-captions
POST   /api/videos/{id}/overlay       — Add overlay/sticker
POST   /api/videos/{id}/music         — Mix background music
POST   /api/videos/{id}/export        — Export final video
GET    /api/videos/{id}/preview       — Get preview thumbnail
GET    /api/templates                  — List video templates
POST   /api/templates/{id}/apply      — Apply template to video
```

### Sound Analyzer
```
GET    /api/sounds/trending           — Get trending sounds
GET    /api/sounds/trending/{id}      — Sound detail + metrics
GET    /api/sounds/predict/{id}       — Predict viral score
POST   /api/sounds/generate           — Generate AI music
GET    /api/sounds/library            — Personal sound library
POST   /api/sounds/library/add        — Add to library
GET    /api/sounds/match              — Match sound to content
```

### TikTok Shop
```
GET    /api/shop/products             — List products
POST   /api/shop/products             — Add product
PUT    /api/shop/products/{id}        — Update product
POST   /api/shop/products/research    — Research trending products
POST   /api/shop/listings/generate    — Generate AI listing
GET    /api/shop/analytics            — Sales analytics
GET    /api/shop/orders               — List orders
GET    /api/shop/inventory            — Inventory status
```

### Dashboard
```
GET    /api/dashboard/overview        — Dashboard summary
GET    /api/dashboard/calendar        — Content calendar
GET    /api/dashboard/activity        — Recent activity
POST   /api/chat                      — AI assistant chat
GET    /api/settings                  — User settings
PUT    /api/settings                  — Update settings
GET    /api/health                    — Health check
```

---

## Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: SQLite (WAL mode)
- **Task Queue**: Celery + Redis (for long video processing)
- **Video**: FFmpeg, OpenCV, moviepy, Pillow
- **Audio**: pydub, librosa, soundfile
- **Image**: Pillow, rembg (background removal)
- **HTTP**: httpx (async), requests

### Frontend
- **Framework**: React 18 + TypeScript
- **Build**: Vite 5
- **Styling**: Tailwind CSS
- **State**: React hooks (useState, useEffect, useContext)
- **Charts**: Recharts
- **Calendar**: react-big-calendar
- **DnD**: @dnd-kit/core
- **Video Player**: react-player
- **Audio Player**: wavesurfer.js

### External APIs
- **LLM**: OpenAI GPT-4 (scripts, listings, chat)
- **TTS**: ElevenLabs API (voice generation)
- **Image Gen**: Replicate API (FLUX/SDXL)
- **Music Gen**: Suno API or Replicate (MusicGen)
- **Stock Media**: Pexels API (free)
- **Speech-to-Text**: OpenAI Whisper API
- **TikTok**: TikTok Shop API (optional)

### Infrastructure
- **Runtime**: Python 3.11+, Node 18+
- **Process Manager**: systemd or supervisord
- **File Storage**: Local filesystem (/data/videos, /data/audio, /data/images)
- **Logging**: Python logging + file rotation

---

## Size Budget

| Component | Min | Standard | Full |
|-----------|-----|----------|------|
| Python venv | 800 MB | 1.2 GB | 1.5 GB |
| Node modules | 150 MB | 200 MB | 250 MB |
| FFmpeg + codecs | 80 MB | 100 MB | 120 MB |
| Video templates | 100 MB | 300 MB | 500 MB |
| Audio assets | 50 MB | 200 MB | 400 MB |
| Image assets | 50 MB | 200 MB | 400 MB |
| Database | 20 MB | 50 MB | 100 MB |
| Cache/temp | 200 MB | 500 MB | 1 GB |
| Source code | 5 MB | 5 MB | 5 MB |
| **TOTAL** | **1.5 GB** | **2.8 GB** | **4.3 GB** |

VPS free: 5.4 GB → Fits all scenarios ✅

---

## Milestones

### Milestone 1 — Skeleton & Core (Day 1)
- Project structure
- FastAPI app with health endpoint
- React dashboard shell
- SQLite schema
- Basic API endpoints (CRUD)

### Milestone 2 — Content Factory (Day 2-3)
- AI script generator (OpenAI)
- Script templates (7 formats)
- Multiple variation generation
- Script editor UI

### Milestone 3 — Voice & Assets (Day 3-4)
- TTS integration (ElevenLabs)
- Voice selection & preview
- Pexels stock footage search
- Asset library management

### Milestone 4 — Video Editor (Day 4-6)
- Video upload & storage
- Auto-cut (FFmpeg + silence detection)
- Auto-captions (Whisper)
- Basic overlays (text, image)
- Export (9:16 MP4)

### Milestone 5 — Sound Analyzer (Day 6-7)
- Trending sounds tracker
- Viral prediction scoring
- AI music generation (Suno/Replicate)
- Sound library

### Milestone 6 — TikTok Shop (Day 7-8)
- Product CRUD
- AI listing generator
- Sales analytics dashboard
- Inventory management

### Milestone 7 — Dashboard & Polish (Day 8-9)
- Unified dashboard
- Content calendar
- AI chat assistant
- Settings page
- Responsive design

### Milestone 8 — Integration & Deploy (Day 9-10)
- Full pipeline test (script → voice → video → export)
- Performance optimization
- Error handling & logging
- Documentation
- GitHub push

---

## File Structure

```
tiktok-ai-suite/
├── backend/
│   ├── app/
│   │   ├── main.py                    — FastAPI app
│   │   ├── config.py                  — Environment config
│   │   ├── models.py                  — Pydantic models
│   │   ├── db.py                      — SQLite layer
│   │   ├── modules/
│   │   │   ├── content_factory/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── script_generator.py    — AI script generation
│   │   │   │   ├── templates.py           — Script templates
│   │   │   │   ├── caption_generator.py   — Hashtags & captions
│   │   │   │   └── scheduler.py           — Content scheduling
│   │   │   ├── voice/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tts_engine.py          — TTS integration
│   │   │   │   └── voice_library.py       — Voice management
│   │   │   ├── video_editor/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auto_cutter.py         — Video cutting
│   │   │   │   ├── captions.py            — Auto-captions
│   │   │   │   ├── overlays.py            — Text/image overlays
│   │   │   │   ├── transitions.py         — Transition effects
│   │   │   │   ├── templates.py           — Video templates
│   │   │   │   ├── audio_mixer.py         — Background music
│   │   │   │   └── exporter.py            — Final export
│   │   │   ├── sound/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── trending.py            — Trending tracker
│   │   │   │   ├── predictor.py           — Viral prediction
│   │   │   │   ├── generator.py           — AI music gen
│   │   │   │   └── library.py             — Sound library
│   │   │   ├── shop/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── products.py            — Product management
│   │   │   │   ├── listings.py            — AI listing gen
│   │   │   │   ├── pricing.py             — Dynamic pricing
│   │   │   │   ├── analytics.py           — Sales analytics
│   │   │   │   └── inventory.py           — Inventory mgmt
│   │   │   └── dashboard/
│   │   │       ├── __init__.py
│   │   │       ├── overview.py            — Dashboard data
│   │   │       ├── calendar.py            — Content calendar
│   │   │       └── chat.py                — AI assistant
│   │   ├── connectors/
│   │   │   ├── openai_client.py           — OpenAI API
│   │   │   ├── elevenlabs_client.py       — ElevenLabs API
│   │   │   ├── replicate_client.py        — Replicate API
│   │   │   ├── suno_client.py             — Suno API
│   │   │   ├── pexels_client.py           — Pexels API
│   │   │   ├── whisper_client.py          — Whisper API
│   │   │   └── tiktok_shop_client.py      — TikTok Shop API
│   │   └── utils/
│   │       ├── file_manager.py            — File operations
│   │       ├── video_utils.py             — FFmpeg wrappers
│   │       ├── audio_utils.py             — Audio processing
│   │       ├── image_utils.py             — Image processing
│   │       └── cost_tracker.py            — API cost tracking
│   ├── data/
│   │   ├── homeops.db                     — SQLite database
│   │   ├── videos/                        — Video storage
│   │   ├── audio/                         — Audio storage
│   │   ├── images/                        — Image storage
│   │   └── temp/                          — Temporary files
│   ├── templates/
│   │   ├── video/                         — Video templates
│   │   ├── overlay/                       — Overlay assets
│   │   └── font/                          — Font files
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ChatPanel.tsx
│   │   │   └── common/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ContentFactory.tsx
│   │   │   ├── ScriptEditor.tsx
│   │   │   ├── VoiceStudio.tsx
│   │   │   ├── VideoEditor.tsx
│   │   │   ├── SoundAnalyzer.tsx
│   │   │   ├── ShopManager.tsx
│   │   │   ├── Calendar.tsx
│   │   │   └── Settings.tsx
│   │   └── hooks/
│   │       └── useApi.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   ├── user-guide.md
│   └── deployment.md
├── scripts/
│   ├── run_dev.sh
│   ├── cleanup.sh
│   └── setup.sh
├── .env.example
├── .gitignore
└── README.md
```

---

## Cost Estimation (API Usage)

| API | Cost Model | Est. Monthly |
|-----|------------|--------------|
| OpenAI GPT-4 | ~$0.03/1K tokens | $5-15 |
| ElevenLabs | ~$0.30/1K chars | $3-10 |
| Replicate | ~$0.002-0.05/image | $2-8 |
| Suno | Per song | $5-15 |
| Pexels | Free | $0 |
| Whisper | $0.006/min | $1-3 |
| **TOTAL** | | **$16-51/month** |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API rate limits | Celery queue + retry logic + caching |
| Large video files | Stream processing + temp cleanup |
| API costs spike | Cost tracker + daily budget cap |
| VPS disk full | Auto-cleanup cron + retention policy |
| Slow video processing | Background tasks + progress tracking |
| API downtime | Fallback APIs + graceful degradation |

---

## Next Steps
1. Create GitHub repo
2. Build Milestone 1 (skeleton)
3. Iterate through milestones
4. Deploy & test
5. Document & polish
