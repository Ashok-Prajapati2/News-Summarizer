from bs4 import BeautifulSoup
import requests
import os
import random
def fetch_article(url,query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  

        soup = BeautifulSoup(response.text, 'html.parser')
        for element in soup(['header', 'footer', 'nav', 'aside', 'a','script']):
            element.decompose()
        body = soup.find('body')
        if not os.path.exists(f'html_data/{query}'):
            os.makedirs(f'html_data/{query}')
        name_f = f"{random.randint(1000, 9999)}"
        with open(f'html_data/{query}/{name_f}.html', 'w', encoding='utf-8') as file:
            file.write(body.prettify())

        title = body.find('h1').get_text(strip=True) if body.find('h1') else 'No title found'

        paragraphs = body.find_all('p')
        full_text = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        
        return {"title": title, "content": full_text}
    
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.RequestException as e:
        print(f"Request error occurred: {e}")
    return None
