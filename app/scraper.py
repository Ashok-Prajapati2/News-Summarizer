
import os
import json
import asyncio
import time
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
import httpx
from .fulltext import fetch_article
from bs4 import BeautifulSoup 

# Load environment variables
load_dotenv()
api_key = os.getenv('api_key')
search_engine_id = os.getenv('search_engine_id')

# MongoDB Client
client = MongoClient('mongodb://localhost:27017/')

async def fetch_results(query):
    """Fetch results from Google Custom Search API."""
    date_15_days_ago = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&dateRestrict=d15&key={api_key}&cx={search_engine_id}'
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
    return None

async def process_query(query):
    """Process a query to fetch articles and summarize them."""
    results = await fetch_results(query)
    if results:
        items = results.get('items', [])
        result_rows = []
        
        for item in items:
            title = item.get('title', 'No title found')
            link = item.get('link', 'No link found')
            snippet = item.get('snippet', 'No snippet available')
            date = 'Date not available'
            
            if snippet:
                parts = snippet.split(' ... ')
                if len(parts) > 1:
                    date = parts[0]  
            
            # Fetch full article details
            full_article = fetch_article(link, query)
            if full_article:  # Check if fetching was successful
                new_title = full_article.get('title', 'No title found')
                new_article = full_article.get('content', 'No content found')
                summary = full_article.get('summary', 'No summary available')
                html = full_article.get('html', [])
                filename = full_article.get('filename', 'No filename available')

                result_rows.append({
                    'query': query,
                    'date': date,
                    'title': title,
                    'new_title': new_title,
                    'link': link,
                    'snippet': snippet,
                    'summary': summary,
                    'full_article': full_article,
                    'filename': filename,
                    'html': html
                })
        return result_rows
    return []

async def save_results_to_mongo(queries):
    """Save results to MongoDB, updating existing records to avoid duplicates."""
    print("Saving results to MongoDB...")
    
    for query in queries:
        db = client['StoreData']
        collection = db[query]

        results = await process_query(query)
        timestamp = time.time()

        if results:
            operations = []
            for result in results:
                result['_id'] = str(uuid.uuid4())
                result['timestamp'] = timestamp  
                operations.append(UpdateOne(
                    {'_id': result['_id']},  
                    {'$set': result},  
                    upsert=True  
                ))

            try:
                if operations:
                    collection.bulk_write(operations)
                    print(f"Results for query '{query}' saved to MongoDB in the collection '{query}'.")
            except Exception as e:
                print(f"Error inserting results for query '{query}': {e}")

    return "All queries processed."

# Uncomment the following lines to run the script directly
# if __name__ == "__main__":
#     queries = ['share market']  
#     asyncio.run(save_results_to_mongo(queries))
