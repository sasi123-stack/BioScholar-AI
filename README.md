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

### 🌐 Web Application
- **35M+ PubMed articles** with semantic search
- **Clinical Trials database** integration
- **Maverick AI Chat** — in-browser AI assistant
- **Research Trends** — publication analytics
- **Advanced Filters** — year, source, evidence level
- **Reading List** — save & export articles (CSV / BibTeX)
- **Dark Mode** + responsive design

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

*Last updated: February 2026*

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>
