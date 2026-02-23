import re
import os

filepath = "d:\\MTech 2nd Year\\BioMedScholar AI\\frontend\\index.html"
with open(filepath, "r", encoding="utf-8") as f:
    html = f.read()

# Remove Mobile Filter Toggle
html = re.sub(r'<!-- Mobile Filter Toggle -->\s*<button class="mobile-filter-toggle"[^>]*>[\s\S]*?</button>\s*', '', html)

# Remove Filters Sidebar (the whole <aside class="filters-sidebar">)
html = re.sub(r'<!-- Sidebar Filters -->\s*<aside class="filters-sidebar"[^>]*>[\s\S]*?</aside>\s*', '', html)

# Remove view-toggle from nav-info
html = re.sub(r'<div class="nav-info">\s*<div class="view-toggle">[\s\S]*?</div>\s*</div>', '<div class="nav-info">\n            </div>', html)

# Consolidate results-actions-header
actions_replacement = """<div class="results-actions-header">
                            <div class="header-action-menu">
                                <button class="results-action-btn menu-trigger" onclick="toggleResultsMenu()" title="Export Options">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                                        <polyline points="7 10 12 15 17 10" />
                                        <line x1="12" y1="15" x2="12" y2="3" />
                                    </svg>
                                    Export All
                                </button>
                                <div class="menu-dropdown hidden" id="results-menu" style="right: 0; left: auto; top: 30px;">
                                    <button class="menu-item" onclick="saveAllResults()">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
                                        <span>Save All</span>
                                    </button>
                                    <button class="menu-item" onclick="exportResults('csv')">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
                                        <span>CSV</span>
                                    </button>
                                    <button class="menu-item" onclick="exportResults('bibtex')">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>
                                        <span>BibTeX</span>
                                    </button>
                                    <button class="menu-item" onclick="window.print()">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9" /><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" /><rect x="6" y="14" width="12" height="8" /></svg>
                                        <span>Print</span>
                                    </button>
                                </div>
                            </div>
                        </div>"""

html = re.sub(r'<div class="results-actions-header">[\s\S]*?</button>\s*</div>', actions_replacement, html)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(html)
print("done")
