# BioMed Scholar User Guide

Welcome to **BioMed Scholar**, your AI-powered companion for biomedical literature search and analysis. This guide will help you navigate the platform and make the most of its advanced features.

---

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Searching the Literature](#searching-the-literature)
4. [Asking Questions (Q&A)](#asking-questions-qa)
5. [Exploring Trends](#exploring-trends)
6. [Managing Your Library](#managing-your-library)
7. [Citations & Exports](#citations--exports)
8. [Personalization](#personalization)
9. [Keyboard Shortcuts](#keyboard-shortcuts)

---

## 🚀 Getting Started

Access BioMed Scholar through your web browser. The interface is designed to be intuitive, with a central search bar and navigation tabs for different modes.

### Dashboard Overview
- **Header**: Contains the search bar, account controls, and quick access to your reading list.
- **Navigation Bar**: Switch between **Articles** (search), **Ask Questions** (Q&A), and **Trends**.
- **Sidebar**: Filters and index statistics.
- **Main Content**: Search results and detailed views.

---

## 🔐 Authentication

Create an account to sync your research across devices and personalize your experience.

### Sign Up / Login
1. Click the **"Login"** button in the top-right corner.
2. **To Sign Up**:
   - Click "Sign up" at the bottom of the modal.
   - Enter your **Full Name**, **Email**, and **Password**.
   - Click **"Sign Up"**.
3. **To Login**:
   - Enter your registered **Email** and **Password**.
   - Click **"Sign In"**.

### Google Sign-In
- Click **"Continue with Google"** in the login modal to sign in instantly with your Google account.

> **Note**: Your reading list is saved to your account when logged in. Without an account, it is saved only to your local browser storage.

---

## 🔍 Searching the Literature

BioMed Scholar uses hybrid search, combining keyword matching (BM25) with AI semantic search (BioBERT).

### Basic Search
- Type your query into the main search bar (e.g., *"mRNA vaccine efficacy"*).
- Press **Enter** or click the search icon.

### Search Modes
Use the **Search Mode Slider** in the sidebar to adjust how the engine works:
- **Keyword (0%)**: Strict exact word matching. Good for specific medical codes or proper nouns.
- **Balanced (50%)**: The default setting. Combines keywords with meaning.
- **Semantic (100%)**: Focuses on the *meaning* of your query. Good for natural language descriptions (e.g., *"drugs that lower blood pressure without side effects"*).

### Advanced Search
Click the sliders icon next to the search bar or press `Ctrl + Shift + F` to open Advanced Search:
- **All of these words**: Must appear.
- **Exact phrase**: Searches for the specific sequence.
- **Any of these words**: Good for synonyms (e.g., *cancer OR tumor*).
- **None of these words**: Excludes results containing these terms.
- **Author / Journal**: Restrict by metadata.

### Filters
Refine your results using the sidebar:
- **Source Type**: PubMed or Clinical Trials.
- **Date Range**: Preset ranges or custom years.
- **Article Type**: Research, Review, Meta-Analysis, etc.
- **Language**: Filter by publication language.

---

## ❓ Asking Questions (Q&A)

Get direct answers extracted from the literature instead of a list of links.

1. Switch to the **Ask Questions** tab.
2. Type a natural language question (e.g., *"What are the side effects of ACE inhibitors?"*).
3. Select the **Source** (All, PubMed, Clinical Trials).
4. Click **"Get Answer"**.

The AI will scan relevant documents and present:
- A direct answer summary.
- A confidence score.
- Supporting passages with citations.

---

## 📈 Exploring Trends

Stay updated with what's hot in biomedical research.

1. Switch to the **Trends** tab.
2. View **Trending Topics** (ranked by recent activity).
3. Click any topic card to instantly search for it.
4. View **Publication Trends** charts to see the volume of research over time.

---

## 🔖 Managing Your Library

### Reading List
- **Save**: Click the **Bookmark** icon on any search result to add it to your Reading List.
- **View**: Click the **Bookmark** icon in the top header to open the Reading List panel.
- **Remove**: Click "Remove" on an item in the panel.

---

## 📝 Citations & Exports

### Generate Citations
1. Click the **"Cite"** button on any search result.
2. Choose your format: **APA**, **MLA**, **Chicago**, or **BibTeX**.
3. Click **"Copy to Clipboard"**.

### Export Data
- **Export Results**: In the search results header, click **"Export"** to download the current page of results as a CSV file.
- **Export Reading List**: In the Reading List panel, choose **CSV** or **BibTeX** to download your saved library.

---

## 🎨 Personalization

- **Dark Mode**: Toggle between Light and Dark themes by clicking the Sun/Moon icon in the header (or press `D`).
- **View Options**: Switch between **List View** (detailed) and **Compact View** (dense) using the toggle in the navigation bar.

---

## ⌨️ Keyboard Shortcuts

Speed up your workflow with these hotkeys:

| Key | Action |
|-----|--------|
| `Ctrl + K` | Focus Search Bar |
| `Ctrl + Shift + F` | Open Advanced Search |
| `Escape` | Close Modal / Clear Focus |
| `?` | Show Shortcuts |
| `1` | Go to Articles Tab |
| `2` | Go to Q&A Tab |
| `3` | Go to Trends Tab |
| `B` | Toggle Reading List |
| `D` | Toggle Dark Mode |
| `← / →` | Previous / Next Page |

---

*Powered by BioBERT, Elasticsearch, and FastAPI.*
