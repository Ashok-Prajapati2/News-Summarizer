from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
import asyncio
from .scraper import save_results_to_mongo
from .user_login import auth_bp, login_manager
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from .article_bot import ArticleChatbot  
from dotenv import load_dotenv
from .logging_config import logger  

app = Flask(__name__)


try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['ashok']
    data_db = client['StoreData']
    users_collection = db['users']
    app.config['SECRET_KEY'] = 'xyz'
    logger.info("Database connection established successfully.")
except Exception as e:
    logger.error(f"Error in database connection: {e}")


login_manager.init_app(app)
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    username = session.get('username') or current_user.username

    try:
        user = users_collection.find_one({'username': username})

        if user:
            user_category = user.get('category', 'No category defined')
            logger.info(f"User category details: {user_category}")

            if user_category != 'No category defined':
                user_category = user_category.lower()

                try:
                    data_collection = data_db[user_category] 
                    articles = list(data_collection.find())  

                    if len(articles) == 0:  
                        logger.warning(f"No articles found for category '{user_category}'. Saving new results...")
                        asyncio.run(save_results_to_mongo([user_category]))
                        articles = list(data_collection.find())  # Refresh articles after saving new data
                except Exception as e:
                    logger.error(f"Error accessing the collection for category {user_category}: {e}")
                    return render_template('index.html', username=username, articles=[])

                data = {
                    'username': username,
                    'user_category': user_category,
                    'articles': articles  
                }
                
                return render_template('index.html', data=data)

        else:
            logger.warning('User not found.')

    except Exception as e:
        logger.error(f'An error occurred: {e}')
        return render_template('index.html', username=username, articles=[])

    return render_template('index.html', data={'username': username, 'articles': []})

@app.route('/search', methods=['POST'])
@login_required
def search(): 
    global query 
    query = request.form.get('query')
    logger.info(f"Search query received: '{query}'")
    
    if query:
        try:
            query = query.lower()
            # Fetch articles from the general category or user category
            data_collection = data_db[query]  # Adjust this line based on your logic
            articles = list(data_collection.find()) 

            if len(articles) == 0:  
                logger.warning(f"No articles found for category '{query}'. Saving new results...")
                asyncio.run(save_results_to_mongo([query]))
                articles = list(data_collection.find())  

            logger.info(f"Articles found: {len(articles)}")
           
            data = {
                'articles': articles,
                'query': query
            }
            return render_template('list_search.html', data=data)
            
        except Exception as e:
            logger.error(f"Error during search operation: {e}")
            flash('An error occurred during the search. Please try again.')
            return redirect(url_for('index'))

    else:
        flash('Please enter a search query.')
        return redirect(url_for('index'))


@app.route('/full_article/<article_id>', methods=['GET', 'POST'])
@login_required
def full_article(article_id):
    logger.info(f"Fetching full article for article_id: {article_id}")

    # Retrieve the current user from the database
    user = users_collection.find_one({'username': current_user.username})
    
    if not user:
        logger.warning(f"User {current_user.username} not found in the database.")
        return "User not found", 404

    user_category = user.get('category', 'No category defined').lower()
    logger.info(f"User {current_user.username}'s category: {user_category}")
    
    if request.args.get('query') : 
        logger.info(f"Using search query: {query}")
        data_collection = data_db[query]
    else:
        data_collection = data_db[user_category]
    article = data_collection.find_one({'_id': article_id})  

    if not article:
        logger.warning(f"Article with id {article_id} not found in {user_category} category.")
        return "Article not found", 404

    logger.info(f"Fetched article: {article_id}")

    # Initialize the chatbot for this article
    chatbot = ArticleChatbot(article['full_article']['content'])
    logger.info(f"Initialized chatbot for article: {article_id}")

    # Handle POST request (user asking a question)
    if request.method == 'POST':
        logger.info("Handling POST request for question.")
        try:
            question = request.json.get('question')
            if not question:
                logger.warning("No question provided in the request.")
                return jsonify({'error': 'No question provided'}), 400

            logger.info(f"Received question: {question}")

            # Ask the chatbot the question and return the response
            response = chatbot.ask_question(question)
            logger.info(f"Question asked: {question}, Response: {response}")
            return jsonify({'answer': response}), 200
            
        except Exception as e:
            logger.error(f"Error in chatbot interaction: {str(e)}")
            return jsonify({'error': str(e)}), 500  # Return the actual error message for debugging


    # If GET request, render the article
    logger.info(f"Rendering full_article.html for article {article_id}")
    return render_template('full_article.html', article=article)


if __name__ == '__main__':
    app.run(debug=True)
