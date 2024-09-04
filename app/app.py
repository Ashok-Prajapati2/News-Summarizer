from flask import Flask, render_template, request
from .scraper import main
# from .summarizer import summarize_articles
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
        # for i in articles:
            # summarized_articles = summarize_articles(i['snippet'])
            # print(summarize_articles)
               
            # with open("result.txt",'a') as file:
                # file.write(summarized_articles)
        # return render_template('index.html', query=query, articles=summarized_articles)
    return render_template('index.html', error="Please enter a search query.")

if __name__ == "__main__":
    app.run(debug=True)
