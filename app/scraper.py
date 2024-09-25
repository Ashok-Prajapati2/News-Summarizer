import httpx
import asyncio
import json
from bs4 import BeautifulSoup 
from .fulltext import fetch_article
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from pymongo import MongoClient , UpdateOne
import asyncio
import uuid
import time
import httpx

load_dotenv()
api_key = os.getenv('api_key')
search_engine_id = os.getenv('search_engine_id')
client = MongoClient('mongodb://localhost:27017/')

async def fetch_results(query):
    date_15_days_ago = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
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
            full_article = fetch_article(link,query)
            new_title = full_article['title']
            new_article = full_article['content']
            summary = full_article['summary']
            html = full_article['html']
            filename = full_article['filename']

            result_rows.append({
                'query': query,
                'date': date,
                'title': title,
                'new_title':new_title,
                'link': link,
                'snippet': snippet,
                'summary':summary,
                'full_article': full_article,
                'filename':filename,
                'html':html
            })
        return result_rows
    return []



async def save_results_to_mongo(queries):
    """Save results to MongoDB, updating existing records to avoid duplicates."""
    print("save in to mongo")
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
        
            # with open(f'search_results_{query}.json', 'w', encoding='utf-8') as file:
            #     json.dump(results, file, ensure_ascii=False, indent=4)
            #     print(f"Results for query '{query}' saved to search_results_{query}.json.")

    return "All queries processed."

# if __name__ == "__main__":
#     queries = ['share market']  
#     asyncio.run(save_results_to_mongo(queries))