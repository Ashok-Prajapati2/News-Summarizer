import httpx
import asyncio
import json
from bs4 import BeautifulSoup 
from .fulltext import fetch_article
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('api_key')
search_engine_id = os.getenv('search_engine_id')

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

            result_rows.append({
                'query': query,
                'date': date,
                'title': title,
                'new_title':new_title,
                'link': link,
                'snippet': snippet,
                'full_article': full_article
            })
        return result_rows
    return []

async def main(queries):
    all_results = []
    results = await process_query(queries)
    all_results.extend(results)
    
    with open('search_results.json', 'w', encoding='utf-8') as file:
        json.dump(all_results, file, ensure_ascii=False, indent=4)
    print("Search completed. Results saved to search_results.json.")
    return all_results

if __name__ == "__main__":
    queries = ['tech news'] 
    asyncio.run(main(queries))
