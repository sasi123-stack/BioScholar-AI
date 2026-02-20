#!/usr/bin/env node

/**
 * BioVault Search Script for Maverick Agent
 * Connects Telegram to the BioMed Scholar Platform
 */

const API_BASE = 'https://sasidhara123-biomed-scholar-api.hf.space/api/v1';

async function search(query, limit = 5) {
    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                max_results: limit,
                index: 'both'
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        const data = await response.json();
        return data.results.map(r => ({
            title: r.title,
            abstract: r.abstract.substring(0, 300) + '...',
            source: r.source,
            url: `https://biomed-scholar.web.app/search?q=${encodeURIComponent(query)}&doc=${r.id}`
        }));
    } catch (error) {
        return { error: error.message };
    }
}

// Get arguments from command line
const args = process.argv.slice(2);
const command = args[0];
const query = args.slice(1).join(' ');

if (command === 'search') {
    search(query).then(res => console.log(JSON.stringify(res, null, 2)));
} else {
    console.log(JSON.stringify({ error: "Unknown command" }));
}
