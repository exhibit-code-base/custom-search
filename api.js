class SearchAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    // Search function
    async search(query) {
        try {
            const response = await fetch(`${this.baseURL}/search?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const results = await response.json();
            if (results.error) {
                throw new Error(results.error);
            }

            return results;
        } catch (error) {
            console.error('Search API error:', error);
            throw error;
        }
    }

    // Scrape function
    async scrapeContent(url) {
        try {
            const response = await fetch(`${this.baseURL}/api/scrape?url=${encodeURIComponent(url)}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch page structure');
            }

            const data = await response.json();
            return data.content;
        } catch (error) {
            console.error('Scraping API error:', error);
            throw error;
        }
    }
}

// Export a default instance
const api = new SearchAPI();
export default api; 