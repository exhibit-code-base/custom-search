import api from './api.js';

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const resultsDiv = document.getElementById('results');

    async function performSearch(query) {
        if (!query.trim()) {
            resultsDiv.innerHTML = '';
            return;
        }

        try {
            resultsDiv.innerHTML = '<div class="loading">Searching...</div>';
            const results = await api.search(query);
            await displayResults(results);
        } catch (error) {
            console.error('Search error:', error);
            resultsDiv.innerHTML = `<div class="error">${error.message}</div>`;
        }
    }

    async function displayResults(results) {
        resultsDiv.innerHTML = '';
        
        if (results.length === 0) {
            resultsDiv.innerHTML = '<div class="result-item">No results found</div>';
            return;
        }

        for (const result of results) {
            const resultElement = document.createElement('div');
            resultElement.className = 'result-item';
            
            // Add main result content
            resultElement.innerHTML = `
                <div class="result-title">
                    <a href="${result.url}" target="_blank">${result.title}</a>
                </div>
                <div class="result-url">${result.url}</div>
                <div class="result-snippet">${result.snippet}</div>
                <div class="headings-section">
                    <div class="headings-title">
                        <svg viewBox="0 0 24 24" width="24" height="24">
                            <path fill="currentColor" d="M2 3h8v2H4v14h6v2H2V3zm16 0h-8v2h6v14h-6v2h8V3zm-4 6h-4v2h4V9zm0 4h-4v2h4v-2zm0-8h-4v2h4V5z"/>
                        </svg>
                        Page Structure
                    </div>
                    <div class="structure-list">
                        <div class="loading">Loading structure...</div>
                    </div>
                </div>
            `;
            
            resultsDiv.appendChild(resultElement);
            
            // Fetch and display headings for this result
            try {
                const structureList = resultElement.querySelector('.structure-list');
                const headings = await api.scrapeContent(result.url);
                
                if (headings && headings.structure && headings.structure.length > 0) {
                    structureList.innerHTML = headings.structure
                        .map(heading => `
                            <div class="structure-item" style="margin-left: ${(heading.level - 1) * 20}px">
                                <span class="heading-level">H${heading.level}</span>
                                <span class="heading-text">${heading.text}</span>
                            </div>
                        `).join('');
                } else {
                    structureList.innerHTML = '<div class="structure-item">No headings found</div>';
                }
            } catch (error) {
                const structureList = resultElement.querySelector('.structure-list');
                structureList.innerHTML = '<div class="error">Could not load page structure</div>';
            }
        }
    }

    // Handle search button click
    searchButton.addEventListener('click', () => {
        performSearch(searchInput.value);
    });

    // Handle Enter key in search input
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch(searchInput.value);
        }
    });
});

class SearchAPI {
    constructor(baseURL = window.location.origin) {
        this.baseURL = baseURL;
    }
    // ... rest of the code
}
