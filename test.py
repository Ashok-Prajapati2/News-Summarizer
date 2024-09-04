from bs4 import BeautifulSoup
import requests

url ='https://indianexpress.com/article/technology/tech-news-technology/tech-news-today-23-december-2023-instagram-openai-9080092/'

def fetch_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        for element in soup(['header', 'footer', 'nav', 'aside','a']):
            element.decompose()
        # Extract all paragraphs from the page
        soup = soup.find('body')
        title = soup.find('h1')
        paragraphs = soup.find_all('p')
        title = '\n'.join([p.get_text() for p in title])
        full_text = '\n'.join([p.get_text() for p in paragraphs])
        
        return {"paragraphs":paragraphs,'title':title}
    
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.RequestException as e:
        print(f"Request error occurred: {e}")
    return None

if __name__ == "__main__":
    article_text = fetch_article(url)
    
    if article_text:

        print("Full article text:\n")
        print(article_text['title'] , '\n\n',article_text['paragraphs'])
    else:
        print("Failed to fetch the article.")
