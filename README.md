---
title: BioScholar AI Unified
emoji: 🔬
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

<div align="center">
 
# 🧬 BioMedScholar AI: 1.6.5 PROFESSIONAL
 
### *Intelligent Biomedical Research Engine powered by OpenClaw RAG and Llama 4 Maverick*
 
[![Live App](https://img.shields.io/badge/Launch-Firebase-orange?style=for-the-badge&logo=firebase)](https://biomed-scholar.web.app)
[![Hugging Face](https://img.shields.io/badge/Full--Stack-HF%20Space-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/sasidhara123/biomed-scholar-api)
[![Maverick AI](https://img.shields.io/badge/Powered--By-Llama--3.3--70B-blue?style=for-the-badge&logo=meta)](https://huggingface.co/spaces/sasidhara123/maverick-ai-bot)
[![Version](https://img.shields.io/badge/Version-1.6.5%20PREMIUM-blueviolet?style=for-the-badge)](#)
 
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

### 🧠 Maverick AI Insight (v2 - Llama 3.3)
The centerpiece of the Research Desk, providing real-time evidence synthesis:
- **Llama 3.3 Powered**: High-speed, high-accuracy RAG synthesis via Groq.
- **Maverick Insight Box**: Automatically generates a structured "Research Briefing" above search results.
- **Context-Aware Linkage**: Seamless navigation between Research Desk, Maverick Bot, and Research Trends.
- **Dynamic Source Mapping**: Identifies and links citations across all indexed sources.

### 🎭 Interactive Presentation Deck (NEW)
A professional, cinematic web-based slide deck for the April 10th showcase:
- **Premium Design**: Space Grotesk typography & Glassmorphism UI.
- **Presenter Notes**: Fast-access one-liners for a polished 10-minute delivery.
- **3D Transitions**: Seamless navigation between architectural and feature pillars.

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

## ✅ System Milestones (April 1, 2026)

### 🎥 Professional Showcase Deck ✅ **PRODUCTION READY**
- **Feature**: Standalone interactive presentation app in `/presentation`.
- **Outcome**: Optimized for the April 10th 10-minute presentation at 3:20 PM IST.

### 📊 Modernized Research Trends ✅ **HARDENED**

### 🧠 Gemini Nano Integration ✅ **HARDENED**
- **Feature**: On-device "Local AI Summary" container in article details.
- **Benefit**: Zero-latency research synthesis for Chrome users.

### 🛡️ v1.6.5 PREMIUM Hardening ✅ **COMPLETED**
- **Status**: Removed all traces of "BETA" labels across UI/UX.
- **Logic**: Consolidated Trends CSS (24px radius, 28px padding) for a premium production feel.

---

## 🎬 Production Showcase Automation (v1.6.5)

We have implemented a high-fidelity **Selenium-based Showcase Script** (`selenium_test.py`) for automated product demos and QA verification.

### 🚀 How to Run the Showcase:
1. **Prepare Environment**:
   ```bash
   pip install selenium webdriver-manager
   ```
2. **Execute Script**:
   ```bash
   python selenium_test.py
   ```
3. **Wait for Playback**: The script will automatically navigate the v1.6.5 platform, trigger live analysis, execute searches, and highlight the Local AI summaries. Perfect for creating promotional videos with voiceovers.

---

## 📅 Product Launch Calendar
- **🎥 Initial Product Demo Video**: April 9th, 2026 | 9:00 AM IST
- **🎥 Official Product Showcase**: April 9th, 2026 | 3:40 PM IST
- **📊 Interactive Deck (Live)**: https://biomed-scholar.web.app/presentation/index.html
- **📊 Interactive Deck (Local)**: `/presentation/index.html`
---

<div align="center">

**Built with ❤️ for the Biomedical Research Community**

*Last updated: April 5, 2026 (1.6.5 PROFESSIONAL - Presentation Finalization & UI Polish)*

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>
