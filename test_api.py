import requests
import json

def test_search_and_scrape():
    base_url = "http://localhost:5000"
    
    # Test search
    query = "python programming"
    search_response = requests.get(
        f"{base_url}/search",
        params={"q": query},
        headers={"Accept": "application/json"}
    )
    
    print("\n=== Search Results ===")
    search_results = search_response.json()
    print(json.dumps(search_results, indent=2))
    
    # Test scrape with first URL from search results
    if search_results and len(search_results) > 0:
        first_url = search_results[0]["url"]
        scrape_response = requests.get(
            f"{base_url}/api/scrape",
            params={"url": first_url},
            headers={"Accept": "application/json"}
        )
        
        print("\n=== Scrape Results ===")
        scrape_results = scrape_response.json()
        print(json.dumps(scrape_results, indent=2))

def test_combined_search_and_scrape():
    base_url = "http://localhost:5000"
    query = "python programming"
    
    response = requests.get(
        f"{base_url}/api/search-and-scrape",
        params={"q": query},
        headers={"Accept": "application/json"}
    )
    
    print("\n=== Combined Search and Scrape Results ===")
    results = response.json()
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    test_search_and_scrape()
    test_combined_search_and_scrape() 