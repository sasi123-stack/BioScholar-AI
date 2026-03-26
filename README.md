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

## ✨ Features (v1.6.0-BETA)

### 🧩 Hybrid Search Resilience (NEW)
Implemented a high-availability search architecture to ensure zero downtime:
- **Primary Engine**: High-speed semantic search via **Bonsai Elasticsearch**.
- **Failover Engine**: Real-time integration with **NCBI Entrez API**.
- **Auto-Switching**: The system automatically detects upstream provider outages (403/504 errors) and reroutes queries to ensure consistent result delivery.

### 🧠 Maverick AI Insight (RAG Synthesis)
The centerpiece of the Research Desk, providing real-time evidence synthesis:
- **Maverick Insight Box**: Automatically generates a structured "Research Briefing" above search results.
- **RAG Methodology**: Retrieves the top 10 most relevant publications and synthesizes a 3-paragraph executive summary with clinical implications.
- **Dynamic Source Mapping**: Identifies and links citations across PubMed and ClinicalTrials.gov sources.

### 🔬 Research Desk (Analytical Engine)
A high-density workspace for literature review:
- **Advanced Filtering**: Slice 35M+ articles by Date, Source, and Evidence Tier (RCTs, Meta-Analysis).
- **Deep-Dive Modals**: Expanding an article exposes structured abstracts and sanitized metadata.
- **D3.js Knowledge Graph**: Visualizes research connections between papers and topics.
- **Multi-Modal Uploads**: Incorporate local PDF/Image context into AI reasoning loops.

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
| **Search** | Bonsai Elasticsearch + NCBI Entrez API |
| **AI Inference** | Groq GPT OSS 120B / Llama-3 |
| **Hosting** | Firebase & Hugging Face Spaces |
| **Visualization** | D3.js v7 |
| **PDF Processing** | PyMuPDF (fitz) |

---

## ✅ System Milestones (March 26, 2026)

### 🏥 Search Failover System ✅ **DEPLOYED**
- **Location**: `app_minimal.py` + `app.js`
- **Feature**: Integrated native PubMed Entrez API as a live fallback for Elasticsearch.
- **Benefit**: Ensures search works even when the primary database cluster is in "maintenance" or "locked" states.

### 💠 Maverick Insight Restoration ✅ **LIVE**
- **Status**: The RAG Synthesis panel has been restored to the main Research Desk.
- **Logic**: Optimized token usage for faster synthesis across high-volume search queries.

---

## 📅 Future Roadmap (May 2026 Trailer)

The platform is currently optimized for stability and high-availability search in its **v1.6.0-BETA** state. The following high-performance features are slated for the **v1.6.5-PREMIUM** release in May 2026:

- **📄 AI Research Synthesis (v1.6.5)**: One-click export of structured search results and Maverick insights into professional PDF briefings.
- **🖼️ Vision Lab Integration**: A dedicated workspace for drag-and-drop analysis of medical imaging, charts, and diagrams using Maverick Vision.
- **🔊 Maverick Voice Briefing**: High-fidelity text-to-speech integration for hands-free research summaries.
- **📊 Clinical Analytics Gauges**: Real-time safety scoring and methodology variance analysis for trial results.

---

<div align="center">

**Built with ❤️ for the Biomedical Research Community**

*Last updated: March 26, 2026 (v1.6.0-BETA - Resilience & Roadmap Update)*

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>
