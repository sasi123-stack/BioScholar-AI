# BioMedScholar AI - Modern Frontend Setup & Implementation Guide

## What Has Been Created ✅

### HTML Structure (`index.html`)
- Complete, semantic HTML5 structure
- All UI elements and modals
- Proper accessibility attributes (aria-labels, roles)
- Meta tags for mobile responsiveness

### CSS Styling (3 files)
- **styles.css** (800+ lines) - Complete styling system with CSS variables, responsive grid layout, typography, components
- **components.css** (600+ lines) - Article cards, modals, toasts, animations
- **dark-mode.css** (300+ lines) - Full dark mode support

### JavaScript Foundation (2 files)
- **utils.js** - 20+ utility functions (debounce, throttle, formatting, validation, etc.)
- **storage.js** - Complete LocalStorage management system (reading list, search history, settings, export/import)

## JavaScript Files to Complete

### 3. search.js (Mock API Implementation)
```javascript
const Search = {
  currentPage: 1,
  totalResults: 0,

  async search(query, filters = {}, page = 1) {
    // Returns mock article data
    // In production, replace with real API call
    return {
      results: mockArticles(),
      total: 1000,
      page: page,
      pageSize: 10,
      hasMore: true
    };
  },

  async getArticleDetails(articleId) {
    // Get full article information
  },

  async generateCitation(articleId, format) {
    // Generate citation in specified format
  }
};
```

### 4. ui.js (User Interface Management)
```javascript
const UI = {
  // Render article results
  renderResults(articles) { },

  // Display loading state
  showLoading() { },
  hideLoading() { },

  // Show toast notifications
  showToast(message, type = 'info') { },

  // Open modals
  openModal(modalId) { },
  closeModal(modalId) { },

  // Update reading list UI
  updateReadingListUI() { },

  // Pagination
  renderPagination(total, currentPage) { }
};
```

### 5. keyboard-shortcuts.js (Keyboard Handlers)
```javascript
const KeyboardShortcuts = {
  init() {
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
      }

      if (e.key === 'b' && !e.ctrlKey && !e.metaKey) {
        document.getElementById('readingListBtn').click();
      }

      if (e.key === 'd' && !e.ctrlKey && !e.metaKey) {
        document.getElementById('darkModeToggle').click();
      }

      if (e.key === 'Escape') {
        closeAllModals();
      }
    });
  }
};
```

### 6. service-worker.js (Service Worker Registration)
```javascript
// Register service worker for offline functionality
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
    .then(reg => console.log('SW registered'))
    .catch(err => console.log('SW registration failed'));
}
```

### 7. app.js (Main Application Logic)
```javascript
const App = {
  init() {
    // 1. Initialize dark mode
    this.initDarkMode();

    // 2. Set up event listeners
    this.setupEventListeners();

    // 3. Initialize keyboard shortcuts
    KeyboardShortcuts.init();

    // 4. Load reading list
    this.loadReadingList();

    // 5. Register service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js');
    }
  },

  initDarkMode() {
    const isDark = Storage.getSetting('darkMode');
    if (isDark) {
      document.body.classList.add('dark-mode');
    }
  },

  setupEventListeners() {
    // Search
    // Buttons
    // Modals
    // etc
  }
};

document.addEventListener('DOMContentLoaded', () => App.init());
```

## Implementation Steps

### Step 1: Add Mock Data
Create a file with sample articles for testing without API:

```javascript
const mockArticles = () => [
  {
    id: 'pubmed-12345',
    title: 'AI-Powered Drug Discovery',
    authors: [
      { name: 'Dr. John Smith', affiliation: 'MIT' },
      { name: 'Dr. Jane Doe', affiliation: 'Stanford' }
    ],
    abstract: 'This study demonstrates...',
    source: 'pubmed',
    publicationDate: '2023-11-15',
    journal: 'Nature Medicine',
    citationCount: 1234,
    url: 'https://pubmed.ncbi.nlm.nih.gov/...',
    relevanceScore: 0.95
  },
  // ... more articles
];
```

### Step 2: Create Service Worker (`sw.js`)

```javascript
const CACHE_NAME = 'biomed-v1';
const urlsToCache = ['/', '/index.html', '/css/', '/js/'];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => {
      return response || fetch(e.request);
    })
  );
});
```

### Step 3: Connect Real API

Once you have a backend API at `/api/v1/search`:

```javascript
async function performSearch(query, filters, page = 1) {
  const response = await fetch('/api/v1/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      filters,
      page,
      pageSize: Storage.getSetting('resultsPerPage')
    })
  });

  if (!response.ok) throw new Error('Search failed');
  return response.json();
}
```

## Quick Test Checklist

- [ ] Dark mode toggle works
- [ ] Reading list saves articles
- [ ] Search results display
- [ ] Keyboard shortcuts work (Ctrl+K, B, D)
- [ ] Modals open/close
- [ ] Responsive on mobile
- [ ] Export/import data works
- [ ] Pagination functions
- [ ] Citations generate correctly
- [ ] Offline functionality works

## Common Patterns Used

### Event Delegation
```javascript
document.addEventListener('click', (e) => {
  if (e.target.matches('.btn-primary')) {
    // Handle click
  }
});
```

### Debounced Search
```javascript
const debouncedSearch = Utils.debounce((query) => {
  Search.search(query);
}, 300);

searchInput.addEventListener('input', (e) => {
  debouncedSearch(e.target.value);
});
```

### Toast Notification
```javascript
UI.showToast('Article saved to reading list!', 'success');
```

### Modal Management
```javascript
function openModal(modalId) {
  document.getElementById(modalId).classList.add('open');
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove('open');
}
```

## Environment Variables

Create a `.env` file for API configuration:

```
API_BASE_URL=https://api.example.com/api/v1
FIREBASE_API_KEY=xxxxx
FIREBASE_AUTH_DOMAIN=xxxxx
```

## Development Tools

### Local Server
```bash
# Using Python 3
python -m http.server 8000

# Using Node.js
npx http-server

# Using VS Code Live Server Extension
# Right-click index.html → Open with Live Server
```

### Testing
- Open DevTools (F12)
- Test in mobile view (Ctrl+Shift+M)
- Disable JavaScript to test fallbacks
- Check Network tab for slow connections

## Production Checklist

- [ ] Minify CSS/JS
- [ ] Optimize images
- [ ] Enable gzip compression
- [ ] Set cache headers
- [ ] Enable HTTPS
- [ ] Test service worker
- [ ] Check lighthouse score
- [ ] Mobile responsiveness
- [ ] Accessibility audit
- [ ] Cross-browser testing

## Migration from Existing Site

1. Update API endpoints to match real backend
2. Import reading lists from old site
3. Test all features with real data
4. A/B test new in parallel with old
5. Gradually migrate users
6. Monitor performance metrics

## Support & Troubleshooting

### Performance issues?
- Check Network tab in DevTools
- Enable code splitting
- Optimize images
- Use requestIdleCallback for non-critical tasks

### Dark mode not switching?
- Check if dark-mode class is toggled
- Verify CSS variables are defined
- Check system preference detector

### Service worker not caching?
- Verify HTTPS is enabled
- Check service worker status in DevTools
- Clear cache if stuck on old version

## Next Steps

1. Complete the 5 remaining JavaScript files
2. Create `manifest.json` for PWA
3. Create `sw.js` for service worker
4. Add real API endpoints
5. Deploy to hosting platform
6. Monitor and iterate based on user feedback
