import os
import random
import requests
from bs4 import BeautifulSoup
from .model_responce import model_responce

def fetch_article(url, query):
    # Set headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    
    try:
        # Make the HTTP request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove unnecessary elements
        for element in soup(['header', 'footer', 'nav', 'aside', 'a', 'script']):
            element.decompose()

        # Extract article details
        body = soup.find('body')
        title = body.find('h1').get_text(strip=True) if body.find('h1') else 'No title found'
        paragraphs = body.find_all('p')
        full_text = '\n'.join([p.get_text(strip=True) for p in paragraphs])

        # Get the summary using the model response
        summary = model_responce(full_text)

        # Create the directory for storing HTML files if it doesn't exist
        dir_path = f'html_data/{query}'
        os.makedirs(dir_path, exist_ok=True)
        
        # Generate a random file name
        name_f = f"{random.randint(1000, 9999)}"
        file_path = os.path.join(dir_path, f"{name_f}.html")
        
        # Save the HTML content to a file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(body.prettify())

        # Prepare the article data for return
        article_data = {
            "query": query,
            "title": title,
            "content": full_text,
            "summary": summary,
            "html": [body.prettify()],  # List of HTML content
            "filename": f"{name_f}.html"  # File name of saved HTML
        }
        
        return article_data

    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.RequestException as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return None
