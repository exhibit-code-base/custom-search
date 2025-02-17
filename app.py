from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import requests
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})

# Google Custom Search API configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
port = int(os.getenv('PORT', 5000))

# Debug print to verify environment variables are loaded
print("Environment Variables:")
print(f"API Key: {GOOGLE_API_KEY[:10]}... (truncated)")
print(f"Search Engine ID: {SEARCH_ENGINE_ID}")
print(f"Port: {port}")

GOOGLE_SEARCH_API_URL = "https://www.googleapis.com/customsearch/v1"

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/search', methods=['GET'])
def search():
    """
    Search endpoint that accepts GET requests.
    """
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        return jsonify({
            'error': 'Search service configuration is missing. Please check GOOGLE_API_KEY and SEARCH_ENGINE_ID environment variables.'
        }), 500

    query = request.args.get('q', '')

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    try:
        params = {
            'key': GOOGLE_API_KEY,
            'cx': SEARCH_ENGINE_ID,
            'q': query,
            'num': 10
        }
        
        response = requests.get(GOOGLE_SEARCH_API_URL, params=params)
        response.raise_for_status()
        search_results = response.json()
        
        if 'error' in search_results:
            error_message = search_results.get('error', {}).get('message', 'Unknown error occurred')
            print(f"Google API Error: {error_message}")
            return jsonify({
                'error': f'Search API error: {error_message}',
                'details': search_results.get('error', {})
            }), 500
            
        results = []
        if 'items' in search_results:
            for item in search_results['items']:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
        
        return jsonify(results)

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {str(e)}")
        return jsonify({
            'error': 'Failed to connect to Google Search API',
            'details': str(e)
        }), 500
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scrape', methods=['GET'])
def api_scrape():
    """
    Scrape endpoint that accepts GET requests.
    """
    url = request.args.get('url', '')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Initialize content structure
        content = {
            'title': soup.title.string if soup.title else 'No title found',
            'structure': []
        }

        # Find all heading tags and process them
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading_text = tag.get_text(strip=True)
            if heading_text:  # Only add non-empty headings
                content['structure'].append({
                    'level': int(tag.name[1]),  # Get the heading level number
                    'text': heading_text
                })

        return jsonify({
            'status': 'success',
            'content': content
        })

    except requests.exceptions.RequestException as e:
        print(f"Scraping error for URL {url}: {str(e)}")
        return jsonify({'error': f'Failed to fetch the page: {str(e)}'}), 500
    except Exception as e:
        print(f"Unexpected error while scraping {url}: {str(e)}")
        return jsonify({'error': f'Error processing the page: {str(e)}'}), 500

@app.route('/api/search-and-scrape', methods=['GET'])
def search_and_scrape():
    """
    Combined endpoint that performs both search and scraping in one request.
    Returns only heading structure.
    """
    query = request.args.get('q', '')

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    try:
        # First perform the search
        search_params = {
            'key': GOOGLE_API_KEY,
            'cx': SEARCH_ENGINE_ID,
            'q': query,
            'num': 10
        }
        
        search_response = requests.get(GOOGLE_SEARCH_API_URL, params=search_params)
        search_response.raise_for_status()
        search_results = search_response.json()

        # Process search results and scrape each URL
        combined_results = []
        
        if 'items' in search_results:
            for item in search_results['items']:
                result = {
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'page_data': None
                }

                # Scrape the page content
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    page_response = requests.get(result['url'], headers=headers, timeout=10)
                    page_response.raise_for_status()
                    
                    soup = BeautifulSoup(page_response.text, 'lxml')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    # Initialize headings structure
                    headings = {
                        'h1': [],
                        'h2': [],
                        'h3': [],
                        'h4': [],
                        'h5': [],
                        'h6': []
                    }
                    
                    # Process headings with hierarchy
                    heading_structure = []
                    current_parent = {1: None}  # Track parent for each level
                    
                    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                        heading_text = tag.get_text(strip=True)
                        if heading_text:
                            level = int(tag.name[1])
                            headings[f'h{level}'].append(heading_text)
                            
                            # Find parent level
                            parent_level = None
                            for l in range(level-1, 0, -1):
                                if l in current_parent:
                                    parent_level = l
                                    break
                            
                            heading_entry = {
                                'level': level,
                                'text': heading_text,
                                'parent_level': parent_level
                            }
                            
                            heading_structure.append(heading_entry)
                            current_parent[level] = heading_text

                    result['page_data'] = {
                        'title': soup.title.string if soup.title else 'No title found',
                        'headings': headings,
                        'structure': heading_structure
                    }

                except Exception as e:
                    print(f"Error scraping {result['url']}: {str(e)}")
                    result['page_data'] = {'error': str(e)}

                combined_results.append(result)

        return jsonify({
            'status': 'success',
            'query': query,
            'results': combined_results
        })

    except Exception as e:
        print(f"Error in search-and-scrape: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
