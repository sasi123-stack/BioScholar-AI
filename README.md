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
| ⚡ **Backend API (HF Space)** | https://sasidhara123-biomed-scholar-api.hf.space | ✅ running |
| 🤖 **Maverick Telegram Bot** | https://t.me/Meverick_AI_bot | ✅ Active |
| 💠 **Bot Landing Page (HF)** | https://sasidhara123-maverick-ai-bot.hf.space | ✅ Live |
| 🐙 **GitHub Repository** | https://github.com/sasi123-stack/BioScholar-AI | ✅ Public |
| 🔥 **Firebase Console** | https://console.firebase.google.com/project/biomed-scholar | 🔒 Private |

---

## ✨ Features (1.6.5 PREMIUM - Harden V1)

### 📈 Macro Research Trends (NEW)
A dedicated analytical hub for real-time biomedical discovery tracking:
- **Fast-Emerging Topics**: Pulse-tracking of high-growth research areas (e.g., GLP-1, mRNA).
- **Sentiment Pulse**: AI-driven community sentiment analysis on research safety and efficacy.
- **Global Field Breakdown**: Visualizing the distribution of publications across Oncology, Immunology, etc.
- **Live Discovery Feed**: Real-time ticker of major breakthrough papers within the last 24 hours.

### 🌐 Integrated Web Search (Google)
Expanded search universe beyond peer-reviewed literature:
- **Serper API Integration**: One-click toggle to fetch real-world news, clinical trial updates, and public health reports from the World Wide Web.
- **Unified Results**: Web results are seamlessly blended with PubMed/ClinicalTrials data with functional source linking.

### 🧩 Hybrid Search Resilience
Implemented a high-availability search architecture to ensure zero downtime:
- **Primary Engine**: High-speed semantic search via **Bonsai Elasticsearch**.
- **Failover Engine**: Real-time integration with **NCBI Entrez API**.
- **Auto-Switching**: The system automatically detects upstream provider outages and reroutes queries to ensure consistent delivery.

### 🧠 Maverick AI Insight (RAG Synthesis)
The centerpiece of the Research Desk, providing real-time evidence synthesis:
- **Maverick Insight Box**: Automatically generates a structured "Research Briefing" above search results.
- **Context-Aware Linkage**: Seamless navigation between Research Desk, Maverick Bot, and Research Trends.
- **Dynamic Source Mapping**: Identifies and links citations across all indexed sources.

### 🤖 Maverick Telegram Bot (`@Meverick_AI_bot`)
| Command | Description |
|---|---|
| `/start` | Welcome message & quick start |
| `/search <topic>` | AI biomedical literature search |
| `/history` | View recent conversation |
| `[PDF/Image]` | Direct synthesis of uploaded documents |

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
│    Entrez/BS)   │                       │
├─────────────────┼───────────────────────┤
│   Telegram Bot  │   HF Space (Docker)   │
│   (python-      │   maverick-ai-bot     │
│    telegram)    │                       │
└─────────────────┴───────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JS |
| **Backend** | FastAPI (Python 3.10) |
| **Search** | Bonsai Elasticsearch, NCBI Entrez, Serper API |
| **AI Inference** | Groq & Chrome Gemini Nano (On-Device) |
| **Hosting** | Firebase & Hugging Face Spaces |
| **Visualization** | D3.js v7 & CSS Custom Properties |

---

## ✅ System Milestones (March 27, 2026)

### 📈 Research Trends Hub ✅ **LIVE**
- **Feature**: Connected Research Desk and Maverick Bot to a centralized Trends Tab.
- **Outcome**: Users can pivot from search results to macro-level field analysis with one click.

### 🏥 Web Search Integration ✅ **DEPLOYED**
- **Feature**: Integrated Serper API for real-time web discovery alongside PubMed.
- **Benefit**: Provides a holistic view including scientific literature and global health news.

### 🛡️ Harden-V1 Security ✅ **COMPLETED**
- **Status**: Sanitized all frontend triggers and optimized modal visibility logic.
- **Logic**: Enforced `!important` CSS overrides and explicit JavaScript class toggling.

---

## 🎬 Product Launch Calendar

- **⚡ Teaser Promo**: April 6th, 2026 (6 PM) | 6:00 PM IST
- **🎥 Official Teaser**: April 6th, 2026 | 6:00 PM IST

---

<div align="center">

**Built with ❤️ for the Biomedical Research Community**

*Last updated: March 27, 2026 (1.6.5 PREMIUM - Research Trends & Web Integration)*

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>
