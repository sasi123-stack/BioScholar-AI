---
title: BioScholar AI Unified
emoji: 🔬
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

<div align="center">

# 🔬 BioMedScholar AI

### *Evidence-Based Biomedical Research Intelligence Platform*

[![Live](https://img.shields.io/badge/🌐_Web_App-Live-brightgreen?style=for-the-badge)](https://biomed-scholar.web.app)
[![Bot](https://img.shields.io/badge/🤖_Telegram_Bot-Active-blue?style=for-the-badge)](https://t.me/Meverick_AI_bot)
[![API](https://img.shields.io/badge/⚡_Backend_API-Running-orange?style=for-the-badge)](https://huggingface.co/spaces/sasidhara123/biomed-scholar-api)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/sasi123-stack/BioScholar-AI)

</div>

---

## 🚀 Live Deployment Links

| Platform | URL | Status |
|---|---|---|
| 🌐 **Web App (Firebase)** | https://biomed-scholar.web.app | ✅ Live |
| ⚡ **Backend API (HF Space)** | https://sasidhara123-biomed-scholar-api.hf.space | ✅ Running |
| 🤖 **Maverick Telegram Bot** | https://t.me/Meverick_AI_bot | ✅ Active |
| 💠 **Bot Landing Page (HF)** | https://sasidhara123-maverick-ai-bot.hf.space | ✅ Live |
| 🐙 **GitHub Repository** | https://github.com/sasi123-stack/BioScholar-AI | ✅ Public |
| 🔥 **Firebase Console** | https://console.firebase.google.com/project/biomed-scholar | 🔒 Private |

---

## ✨ Features

### 🧠 Maverick AI Bot (In-Browser Assistant)
Powered by Groq's low-latency GPT OSS 120B platform, Maverick acts as a dedicated research counterpart:
- **Smart Plugins & Tools**: Switch on specific research lenses, including **Clinical Trial Finder**, **Molecule Solver** (semantic weighting for chemical structures), **Summarize Mode**, **Gene/Drug Lookup** (auto-detects and links biological targets), and **Citation Generator** (APA 7th edition).
- **Deep Research Synthesis**: Default mode fetches up to 8 top hits, dynamically generates an overview framing the publication timeline, extracts multi-paragraph findings with proper citations, and provides clinical implications.
- **Context-Aware Follow-Ups**: Dynamically maps 12 unique biomedical domains (Oncology, Cardiology, CRISPR, etc.) to generate intelligent, specialized click-to-ask follow-up questions.
- **Voice Dictation & Transcription**: Native Web Speech API integration allows for seamless dictation without auto-submitting unreviewed text.
- **Collaboration & Privacy Modes**: Toggle **Group Session** mode for multi-persona analysis or **Incognito Mode** to prevent the session from saving to cloud history.
- **Scheduled Actions (NEW v0.9.0)**: Proactive automation tools for setting research reminders, automated reports, and personalized triggers (e.g., anniversary wishes or periodic synthesis).

### 🔬 Research Desk (Analytical Engine)
A high-density workspace for literature review and data extraction:
- **Hybrid Search Engine**: Seamlessly blend traditional BM25 keyword matching with dense Vector Embeddings.
- **Advanced Filtering Deck**: Instantly slice 35M+ articles by Date Range, Source Database (PubMed vs ClinicalTrials.gov), and specific evidence tiers (Meta-Analysis, RCTs, Case Studies).
- **Deep-Dive Modals**: Expanding an article generates a full-screen view exposing structured abstracts, sanitized metadata, and external DOI resolution routing.
- **Bulk Export & Citation Management**: Select clusters of articles and bulk-export metadata directly to `.ris`, `.tsv`, or `.json` for reference managers. Build and save custom Reading Lists to local storage or cloud.
- **Dark Mode & Responsive UI**: Fully responsive frontend built on CSS Grid/Flexbox with semantic variable theming.
### 🤖 Maverick Telegram Bot (`@Meverick_AI_bot`)
| Command | Description |
|---|---|
| `/start` | Welcome message & quick start |
| `/help` | Show all commands |
| `/search <topic>` | AI biomedical literature search |
| `/clear` | Clear conversation memory |
| `/history` | View recent conversation |
| `/about` | About Maverick AI |
| `/test` | Open BioMedScholar AI with buttons |

### ⚡ Backend API
- **FastAPI** with BioBERT semantic search
- **Elasticsearch (Bonsai)** full-text index
- **Groq GPT OSS 120B** AI inference
- **PubMed + ClinicalTrials.gov** data sources

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         BioMedScholar AI Stack          │
├─────────────────┬───────────────────────┤
│   Frontend      │   Firebase Hosting    │
│   (HTML/CSS/JS) │   biomed-scholar.     │
│                 │   web.app             │
├─────────────────┼───────────────────────┤
│   Backend API   │   HF Space (Docker)   │
│   (FastAPI +    │   biomed-scholar-api  │
│    BioBERT)     │                       │
├─────────────────┼───────────────────────┤
│   Telegram Bot  │   HF Space (Docker)   │
│   (python-      │   maverick-ai-bot     │
│    telegram +   │                       │
│    Groq GPT)    │                       │
└─────────────────┴───────────────────────┘
```

---

## 🔐 Required Secrets

### Backend API Space (`biomed-scholar-api`)
| Secret | Description |
|---|---|
| `GROQ_API_KEY` | Groq API for GPT OSS 120B |
| `ELASTICSEARCH_HOST` | Bonsai Elasticsearch URL |
| `ELASTICSEARCH_USERNAME` | Bonsai username |
| `ELASTICSEARCH_PASSWORD` | Bonsai password |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `REDIS_HOST` | Upstash Redis host |
| `REDIS_PORT` | Upstash Redis port |
| `REDIS_PASSWORD` | Upstash Redis password |

### Telegram Bot Space (`maverick-ai-bot`)
| Secret | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | From @BotFather |
| `GROQ_API_KEY` | Groq API for GPT OSS 120B |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JS |
| **Hosting** | Firebase Hosting |
| **Backend** | FastAPI (Python) |
| **AI/Search** | BioBERT, Groq GPT OSS 120B |
| **Database** | Elasticsearch (Bonsai), SQLite |
| **Auth** | Firebase Authentication |
| **Bot** | python-telegram-bot, Flask |
| **Deployment** | Hugging Face Spaces (Docker) |
| **Version Control** | GitHub |

---

## 📊 Data Sources

- **PubMed** — 35M+ biomedical research articles
- **ClinicalTrials.gov** — Global clinical trial registry
- **Google Search (Serper API)** — Real-time web search

---

## ✅ System Status Verification (March 11, 2026)

### 🎂 Birthday Reminder System ✅ **WORKING**

**Code Location:** `frontend/app.js`

✅ **Core Functions:**
- `scheduleBirthdayReminder()` - Scheduled for tomorrow (March 9, 2026) at 9 AM IST
- `scheduleNotification()` - Stores to localStorage
- `checkScheduledNotifications()` - Checks every 60 seconds
- `window.testBirthdayReminder()` - Test function available

✅ **Features:**
- Timezone-aware IST calculation using `Intl.DateTimeFormat`
- Auto-prevents duplicate scheduling
- Persists across page refreshes using localStorage
- Sound notification + browser notification support

---

### 📝 Enhanced Response Formatting ✅ **WORKING**

**Code Location:** `frontend/app.js` - Lines 3199-3290

✅ **Automatic Link Detection (NEW):**
- 🔗 **URLs** — `https://` links auto-detect and become clickable with icon
- 📚 **PubMed PMIDs** — `pmid:12345678` → Links to pubmed.ncbi.nlm.nih.gov
- 📄 **DOI Citations** — `10.xxxx/yyyy` → Links to doi.org
- 📋 **Markdown Links** — `[text](url)` → Properly formatted

✅ **Security:**
- All links use `target="_blank" rel="noopener noreferrer"`
- HTML properly escaped and sanitized

✅ **Integration:**
- Used in all chat messages via `addChatMessage()`
- Applied to Maverick Insight responses
- Preserves existing markdown, LaTeX, and citation formatting

---

### 🔥 Firebase Frontend ✅ **DEPLOYED**

**Live URL:** https://biomed-scholar.web.app

✅ **Configuration:**
- Project ID: `biomed-scholar`
- Auth Domain: `biomed-scholar.firebaseapp.com`
- Firestore integration for chat history
- Real-time database: `users/{uid}/chat_history`

✅ **Features:**
- Email/Password authentication
- Auto-save user messages to Firestore
- Chat history recall on page reload
- Secure CORS enabled

✅ **Deployment Status:**
- ✅ Git commits: e182275, d705462, d06ad15 (pushed to GitHub + HF Spaces)
- ✅ Firebase hosting: Just deployed (March 11, 2026)
- ✅ CDN: Global distribution via Firebase Edge

---

### ⚡ API Backend ✅ **LIVE**

**Base URL:** https://sasidhara123-biomed-scholar-api.hf.space/api/v1

✅ **Available Endpoints:**
- `/health` - Service status
- `/search` - Full-text biomedical search
- `/maverick/chat` - Groq LLM integration
- `/maverick/history` - Chat history retrieval
- `/favicon.ico` - Static file serving
- `/docs` - Auto-generated Swagger UI

✅ **Backend Configuration:**
- FastAPI with Uvicorn
- Groq LLM: `openai/gpt-oss-120b`
- OpenSearch: Bonsai cluster (assertive-mahogany-1m2hcasg.us-east-1)
- SQLite: `/tmp/conversation_history.db`

---

### 💬 Chat System ✅ **WORKING**

✅ **Core Features:**
- Plugin system (trials, molecule, gene, citation, summarize)
- Incognito mode (no cloud save)
- Web search integration
- Source citations with confidence scores
- Message actions (copy, edit, speak, feedback)
- Thinking/reasoning display

✅ **Response Synthesis:**
- Connects to `/search` endpoint
- Fetches up to 8 results for synthesis
- Generates overview with publication timeline
- Extracts clinical implications

---

### 📋 Deployment History

| Commit | Date | Feature | Status |
|--------|------|---------|--------|
| e182275 | Mar 8 | Birthday Reminder (March 9 @ 9 AM IST) | ✅ Deployed |
| d705462 | Mar 8 | testBirthdayReminder() function | ✅ Deployed |
| d06ad15 | Mar 8 | Birthday reminder scheduling system | ✅ Deployed |
| 37eba6e | Earlier | Favicon + static file serving | ✅ Live |

---

### 🧪 Testing Birthday Reminder

**Steps to test:**
1. Visit: https://biomed-scholar.web.app
2. Hard refresh: **Ctrl + Shift + R** (or **Cmd + Shift + R** on Mac)
3. Open console: **F12** → **Console** tab
4. Run: `testBirthdayReminder()`
5. Expected result: Notification scheduled for March 9, 2026 at 9 AM IST
6. Verification: `localStorage.getItem("scheduledNotifications")`

**Tomorrow (March 9 @ 9 AM IST):** Notification auto-triggers with sound and browser notification

---

<div align="center">

**Built with ❤️ for the Biomedical Research Community**

*Last updated: March 11, 2026 (v1.4.0 - GPT OSS 120B Integration)*

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>
