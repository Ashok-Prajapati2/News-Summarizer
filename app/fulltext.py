from bs4 import BeautifulSoup
import requests
import os
import random
from .model_responce import model_responce
from .model_responce import model_responce
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
        title = body.find('h1').get_text(strip=True) if body.find('h1') else 'No title found'
        paragraphs = body.find_all('p')
        full_text = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        summary = model_responce(full_text)

        if not os.path.exists(f'html_data/{query}'):
            os.makedirs(f'html_data/{query}')
        name_f = f"{random.randint(1000, 9999)}"

        body = body.find_all('p')
        body = model_responce(f"give me full html in json formet. <{body}>")
        with open(f'html_data/{query}/{name_f}.json', 'w') as f:
            f.write(body)
        # with open(f'html_data/{query}/{name_f}.html', 'w', encoding='utf-8') as file:
        #     file.write(body.prettify())


        
        return {"title": title, "content": full_text, "summary":summary }
    
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.RequestException as e:
        print(f"Request error occurred: {e}")
    return None
