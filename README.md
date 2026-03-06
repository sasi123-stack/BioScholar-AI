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
Powered by Groq's low-latency Llama 4 (17B) platform, Maverick acts as a dedicated research counterpart:
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
- **Groq Llama 4 Maverick** AI inference
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
│    Groq Llama)  │                       │
└─────────────────┴───────────────────────┘
```

---

## 🔐 Required Secrets

### Backend API Space (`biomed-scholar-api`)
| Secret | Description |
|---|---|
| `GROQ_API_KEY` | Groq API for Llama 4 Maverick |
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
| `GROQ_API_KEY` | Groq API for Llama 4 Maverick |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JS |
| **Hosting** | Firebase Hosting |
| **Backend** | FastAPI (Python) |
| **AI/Search** | BioBERT, Groq Llama 4 Maverick |
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

<div align="center">

**Built with ❤️ for the Biomedical Research Community**

*Last updated: March 6, 2026 (v0.9.0-BETA Teaser)*

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>
