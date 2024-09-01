import requests
from bs4 import BeautifulSoup

def scrape_news(query):
    url = f"https://news.google.com/search?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    articles = []
    for item in soup.find_all('article'):
        title = item.find('h3').text if item.find('h3') else "No title"
        link = item.find('a')['href'] if item.find('a') else "#"
        summary = item.find('p').text if item.find('p') else "No summary"
        
        articles.append({
            'title': title,
            'link': f"https://news.google.com{link[1:]}", # Adjust link to be a complete URL
            'summary': summary
        })
    
    return articles
