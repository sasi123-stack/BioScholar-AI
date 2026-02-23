// ============================================================================
// BIOMED SCHOLAR AI - STORAGE MANAGEMENT
// ============================================================================

const Storage = {
  // Storage keys
  KEYS: {
    READING_LIST: 'biomed_reading_list',
    SEARCHES: 'biomed_searches',
    SETTINGS: 'biomed_settings',
    DARK_MODE: 'biomed_dark_mode',
    LAST_SEARCH: 'biomed_last_search',
    FILTERS: 'biomed_filters',
  },

  /**
   * Initialize storage
   */
  init() {
    // Create default settings if they don't exist
    if (!this.getSetting(null)) {
      this.setSettings({
        darkMode: this.prefersDarkMode(),
        resultsPerPage: 10,
        autoSave: true,
        enableAnimations: true,
        enableNotifications: true,
      });
    }
  },

  /**
   * Check if user prefers dark mode
   */
  prefersDarkMode() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  },

  /**
   * Get all settings
   */
  getSettings() {
    const settings = localStorage.getItem(this.KEYS.SETTINGS);
    return settings ? JSON.parse(settings) : null;
  },

  /**
   * Get specific setting
   */
  getSetting(key) {
    const settings = this.getSettings();
    return settings ? settings[key] : null;
  },

  /**
   * Set all settings
   */
  setSettings(settings) {
    localStorage.setItem(this.KEYS.SETTINGS, JSON.stringify(settings));
  },

  /**
   * Update specific setting
   */
  updateSetting(key, value) {
    const settings = this.getSettings();
    if (settings) {
      settings[key] = value;
      this.setSettings(settings);
    }
  },

  /**
   * Get reading list
   */
  getReadingList() {
    const list = localStorage.getItem(this.KEYS.READING_LIST);
    return list ? JSON.parse(list) : [];
  },

  /**
   * Add item to reading list
   */
  addToReadingList(article) {
    const list = this.getReadingList();
    if (!list.find((item) => item.id === article.id)) {
      list.unshift({
        ...article,
        addedAt: new Date().toISOString(),
      });
      localStorage.setItem(this.KEYS.READING_LIST, JSON.stringify(list));
      return true;
    }
    return false;
  },

  /**
   * Remove item from reading list
   */
  removeFromReadingList(articleId) {
    const list = this.getReadingList();
    const filtered = list.filter((item) => item.id !== articleId);
    localStorage.setItem(this.KEYS.READING_LIST, JSON.stringify(filtered));
    return list.length !== filtered.length;
  },

  /**
   * Check if article is in reading list
   */
  isInReadingList(articleId) {
    return this.getReadingList().some((item) => item.id === articleId);
  },

  /**
   * Clear reading list
   */
  clearReadingList() {
    localStorage.removeItem(this.KEYS.READING_LIST);
  },

  /**
   * Get search history
   */
  getSearchHistory() {
    const searches = localStorage.getItem(this.KEYS.SEARCHES);
    return searches ? JSON.parse(searches) : [];
  },

  /**
   * Add search to history
   */
  addToSearchHistory(query, filters = {}) {
    const history = this.getSearchHistory();
    const search = {
      id: Utils.generateId(),
      query,
      filters,
      timestamp: new Date().toISOString(),
    };

    // Remove duplicate
    history = history.filter((s) => s.query !== query);

    // Add to beginning
    history.unshift(search);

    // Limit to 50 items
    if (history.length > 50) {
      history.pop();
    }

    localStorage.setItem(this.KEYS.SEARCHES, JSON.stringify(history));
  },

  /**
   * Clear search history
   */
  clearSearchHistory() {
    localStorage.removeItem(this.KEYS.SEARCHES);
  },

  /**
   * Get last search
   */
  getLastSearch() {
    const lastSearch = localStorage.getItem(this.KEYS.LAST_SEARCH);
    return lastSearch ? JSON.parse(lastSearch) : null;
  },

  /**
   * Set last search
   */
  setLastSearch(query, filters = {}) {
    const search = {
      query,
      filters,
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem(this.KEYS.LAST_SEARCH, JSON.stringify(search));
  },

  /**
   * Get saved filters
   */
  getFilters() {
    const filters = localStorage.getItem(this.KEYS.FILTERS);
    return filters
      ? JSON.parse(filters)
      : {
          source: ['pubmed', 'clinical-trials', 'arxiv'],
          articleType: ['research', 'review', 'systematic', 'meta-analysis'],
          yearFrom: 2020,
          yearTo: 2024,
        };
  },

  /**
   * Save filters
   */
  setFilters(filters) {
    localStorage.setItem(this.KEYS.FILTERS, JSON.stringify(filters));
  },

  /**
   * Export data as JSON
   */
  exportData() {
    const data = {
      readingList: this.getReadingList(),
      searchHistory: this.getSearchHistory(),
      settings: this.getSettings(),
      exportedAt: new Date().toISOString(),
    };
    return JSON.stringify(data, null, 2);
  },

  /**
   * Import data from JSON
   */
  importData(jsonString) {
    try {
      const data = JSON.parse(jsonString);
      if (data.readingList) {
        localStorage.setItem(this.KEYS.READING_LIST, JSON.stringify(data.readingList));
      }
      if (data.searchHistory) {
        localStorage.setItem(this.KEYS.SEARCHES, JSON.stringify(data.searchHistory));
      }
      if (data.settings) {
        localStorage.setItem(this.KEYS.SETTINGS, JSON.stringify(data.settings));
      }
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Clear all storage
   */
  clearAll() {
    Object.values(this.KEYS).forEach((key) => {
      localStorage.removeItem(key);
    });
  },

  /**
   * Get storage usage
   */
  getStorageUsage() {
    let total = 0;
    for (const key in localStorage) {
      if (key.startsWith('biomed_')) {
        total += localStorage[key].length + key.length;
      }
    }
    return (total / 1024).toFixed(2) + ' KB';
  },
};

// Initialize storage on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Storage.init());
} else {
  Storage.init();
}
