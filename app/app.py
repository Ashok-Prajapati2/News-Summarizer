from flask import Flask, render_template, request
from .scraper import main
import asyncio

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    print(query)
    if query:
        articles = asyncio.run(main(query))
    return render_template('index.html', error="Please enter a search query.")

if __name__ == "__main__":
    app.run(debug=True)
