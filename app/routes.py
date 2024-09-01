from flask import Flask, render_template, request
from .scraper import scrape_news
from .summarizer import summarize_articles

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if query:
        articles = scrape_news(query)
        summarized_articles = summarize_articles(articles)
        return render_template('index.html', query=query, articles=summarized_articles)
    return render_template('index.html', error="Please enter a search query.")

if __name__ == "__main__":
    app.run(debug=True)
