from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
import asyncio
from .scraper import save_results_to_mongo
from .user_login import auth_bp, login_manager
from pymongo import MongoClient

app = Flask(__name__)

# Database connection
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['ashok']  # This is your main database
    users_collection = db['users']  # The collection containing user data

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
        # Find the current user in the users collection
        user = users_collection.find_one({'username': username})

        if user:
            # Get the user's category
            user_category = user.get('category', 'No category defined')
            print("User category details:", user_category)

            if user_category != 'No category defined':
                user_category = user_category.lower()

                # Access the MongoDB collection based on user category
                # For example, if user_category is 'tech', it fetches data from the 'tech' collection
                try:
                    data_collection = db[user_category]  # This dynamically accesses the collection
                    articles = data_collection.find()  # Retrieve data from the collection
                    
                    # If the collection is empty, scrape and save new data
                    if data_collection.count_documents({}) == 0:
                        articles = asyncio.run(save_results_to_mongo(user_category))
                        data_collection = db[user_category]  # Update collection after saving new data
                        print(f"New data saved for category {user_category}.")
                except Exception as e:
                    print(f"Error accessing the collection for category {user_category}: {e}")
                    return render_template('index.html', username=username)

                print(f"Data collection for category {user_category}: {data_collection}")

                # Prepare data to pass to the template
                data = {
                    'username': username,
                    'user_category': user_category,
                    'data_collection': articles  # Pass the articles from the collection
                }

                return render_template('index.html', data=data)

        else:
            print('User not found.')

    except Exception as e:
        print(f'An error occurred: {e}')
        return render_template('index.html', username=username)

    return render_template('index.html')

@app.route('/search', methods=['POST'])
@login_required
def search():
    query = request.form.get('query').lower()
    if query:
        try:
            query_list = [query]
            print(query_list)
            articles = asyncio.run(save_results_to_mongo(query_list))
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
