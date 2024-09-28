from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
import asyncio
from .scraper import save_results_to_mongo
from .user_login import auth_bp, login_manager
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Database connection
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['ashok']
    data_db = client['StoreData']
    users_collection = db['users']
    
    
    app.config['SECRET_KEY'] = 'xyz'
except Exception as e:
    print(f"Error in database connection: {e}")

# Flask-Login initialization
login_manager.init_app(app)
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    username = session.get('username') or current_user.username

    try:
        user = users_collection.find_one({'username': username})

        if user:
            user_category = user.get('category', 'No category defined')
            print("User category details:", user_category)

            if user_category != 'No category defined':
                user_category = user_category.lower()

                # Access the MongoDB collection based on user category
                try:
                    data_collection = data_db[user_category]  # Dynamically accesses the collection
                    articles = list(data_collection.find())  # Convert cursor to list

                    if len(articles) == 0:  # Check if collection is empty
                        print(f"No articles found for category '{user_category}'. Saving new results...")
                        asyncio.run(save_results_to_mongo([user_category]))
                        articles = list(data_collection.find())  # Refresh articles after saving new data
                        # print(f"New data saved for category {user_category}.")
                except Exception as e:
                    print(f"Error accessing the collection for category {user_category}: {e}")
                    return render_template('index.html', username=username, articles=[])

                # Print out articles to debug structure
                # print("Retrieved articles:", articles)  # Debugging line

                # Prepare data for rendering
                data = {
                    'username': username,
                    'user_category': user_category,
                    'articles': articles  # Pass articles for rendering
                }
                
                return render_template('index.html', data=data)

        else:
            print('User not found.')

    except Exception as e:
        print(f'An error occurred: {e}')
        return render_template('index.html', username=username, articles=[])

    return render_template('index.html', data={'username': username, 'articles': []})

@app.route('/search', methods=['POST'])
@login_required
def search():
    query = request.form.get('query')
    query = query.lower()
    if query:
        try:
            query = [query]
            print(query)
            articles = asyncio.run(save_results_to_mongo(query))
            print("Run successfully")
            return render_template('index.html')
        except Exception as e:
            flash('An error occurred while searching for articles. Please try again.')
            print(f'Error: {e}')
            return redirect(url_for('index'))
    else:
        flash('Please enter a search query.')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
