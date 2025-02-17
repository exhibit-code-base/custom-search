#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Search query
QUERY="python programming"
echo -e "${BLUE}Testing Search API with query: ${QUERY}${NC}"

# Perform search
SEARCH_RESULTS=$(curl -s -X GET "http://localhost:5000/search?q=${QUERY}" \
-H "Accept: application/json" \
-H "Content-Type: application/json")

echo -e "${GREEN}Search Results:${NC}"
echo $SEARCH_RESULTS | python -m json.tool

# Get first URL from results and scrape it
FIRST_URL=$(echo $SEARCH_RESULTS | python -c "import sys, json; print(json.load(sys.stdin)[0]['url'])")

echo -e "\n${BLUE}Testing Scrape API with URL: ${FIRST_URL}${NC}"

# Perform scraping
SCRAPE_RESULTS=$(curl -s -X GET "http://localhost:5000/api/scrape?url=${FIRST_URL}" \
-H "Accept: application/json")

echo -e "${GREEN}Scrape Results:${NC}"
echo $SCRAPE_RESULTS | python -m json.tool 