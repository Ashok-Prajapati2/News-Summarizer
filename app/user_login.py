from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import session

login_manager = LoginManager()
bcrypt = Bcrypt()
client = MongoClient('mongodb://localhost:27017/')
db = client['ashok']
users_collection = db['users']

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user['_id']), user['username'])
    return None

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        category = request.form.get('category')  
        manual_category = request.form.get('manualCategory')

        if category == 'other' and manual_category:
            category = manual_category

        if users_collection.find_one({'username': username}):
            flash('Username already exists!')
            return redirect(url_for('auth.signup'))

     
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user_id = users_collection.insert_one({
            'username': username,
            'password': hashed_password,
            'category': category  
        }).inserted_id

        # Create user object and log them in
        user = User(str(user_id), username)
        login_user(user)

        flash('Signup successful!')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username})

        if user and bcrypt.check_password_hash(user['password'], password):
            login_user(User(str(user['_id']), user['username']))
            session['username'] = user['username']
            flash('Login successful!')
            
            return redirect(url_for('index'))  
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
