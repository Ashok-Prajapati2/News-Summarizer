from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_login import login_required, current_user
import asyncio
from .scraper import main
from .user_login import auth_bp, login_manager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'xyz' 

login_manager.init_app(app)
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    username = session.get('username')
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))  
    return render_template('index.html',username=username,user=current_user)

@app.route('/search', methods=['POST'])
@login_required
def search():
    query = request.form.get('query')
    if query:
        try:
            print(query)
            articles = asyncio.run(main(query))
            return render_template('index.html', articles=articles)
        except Exception as e:
            flash('An error occurred while searching for articles. Please try again.')
            print(f'Error: {e}') 
            return redirect(url_for('index'))
    else:
        flash('Please enter a search query.')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
