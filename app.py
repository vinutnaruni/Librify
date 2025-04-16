from flask import Flask, render_template, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import os

from config import Config
from routes.auth import auth_bp
from routes.books import books_bp
from routes.admin import admin_bp
from routes.feedback import feedback_bp  # Add this line
from routes.chatbot import chatbot_bp    # Add this line

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize MongoDB
mongo = PyMongo(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(books_bp, url_prefix='/books')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(feedback_bp, url_prefix='/feedback')  # Add this line
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')    # Add this line

# Inject mongo instance into blueprints
auth_bp.mongo = mongo
books_bp.mongo = mongo
admin_bp.mongo = mongo
feedback_bp.mongo = mongo  # Add this line
chatbot_bp.mongo = mongo   # Add this line

# Template filters
@app.template_filter('format_date')
def format_date_filter(date):
    return date.strftime("%B %d, %Y") if date else ""

@app.template_filter('calculate_fine')
def calculate_fine_filter(due_date, return_date=None):
    from utils.helpers import calculate_fine
    return calculate_fine(due_date, return_date)

@app.route('/')
def index():
    try:
        recent_books = list(mongo.db.books.find().sort('created_at', -1).limit(6))
        genres = mongo.db.books.distinct('genre')
    except Exception as e:
        print("MongoDB connection error:", e)
        recent_books = []
        genres = []

    return render_template('index.html', recent_books=recent_books, genres=genres)

@app.route('/setup')
def setup():
    # from werkzeug.security import generate_password_hash
    from models.user import User
    import time

    # Insert Admin User
    admin = mongo.db.users.find_one({'is_admin': True})
    if not admin:
        admin_user = User(
            username='admin',
            email='admin@library.com',
            password='admin123',
            is_admin=True
        )
        mongo.db.users.insert_one(admin_user.to_dict())
        flash('Admin created! Email: admin@library.com, Password: admin123', 'success')
    else:
        flash('Admin already exists.', 'info')

    # Insert Books
    now_ms = int(time.time() * 1000)
    sample_books = [
        {
            "title": "The Alchemist",
            "author": "Paulo Coelho",
            "genre": "Fiction",
            "isbn": "LIB001",
            "description": "A philosophical story about following one's dreams and listening to the heart.",
            "quantity": 7,
            "available_quantity": 7,
            "created_at": datetime.now()
        },
        {
            "title": "1984",
            "author": "George Orwell",
            "genre": "Dystopian Fiction",
            "isbn": "LIB002",
            "description": "A chilling depiction of a totalitarian regime that explores surveillance and individual freedom.",
            "quantity": 5,
            "available_quantity": 5,
            "created_at": datetime.now()
        },
        {
            "title": "Becoming",
            "author": "Michelle Obama",
            "genre": "Biography",
            "isbn": "LIB003",
            "description": "An inspiring memoir by the former First Lady of the United States.",
            "quantity": 6,
            "available_quantity": 6,
            "created_at": datetime.now()
        },
        {
            "title": "The Subtle Art of Not Giving a F*ck",
            "author": "Mark Manson",
            "genre": "Self-Help",
            "isbn": "LIB004",
            "description": "A counterintuitive guide to living a good life by embracing limitations.",
            "quantity": 9,
            "available_quantity": 9,
            "created_at": datetime.now()
        },
        {
            "title": "The Midnight Library",
            "author": "Matt Haig",
            "genre": "Fantasy Fiction",
            "isbn": "LIB005",
            "description": "A woman finds herself in a mysterious library between life and death, exploring alternate lives.",
            "quantity": 4,
            "available_quantity": 4,
            "created_at": datetime.now()
        },
        {
            "title": "Introduction to Algorithms",
            "author": "Thomas H. Cormen",
            "genre": "Computer Science / Engineering",
            "isbn": "LIB006",
            "description": "A comprehensive book on algorithms widely used in engineering and CS courses.",
            "quantity": 3,
            "available_quantity": 3,
            "created_at": datetime.now()
        },
        {
            "title": "Engineering Mechanics: Dynamics",
            "author": "J.L. Meriam, L.G. Kraige",
            "genre": "Mechanical Engineering",
            "isbn": "LIB007",
            "description": "A foundational textbook for engineering students on dynamics and motion.",
            "quantity": 5,
            "available_quantity": 5,
            "created_at": datetime.now()
        },
        {
            "title": "Digital Design",
            "author": "M. Morris Mano",
            "genre": "Electronics & Communication",
            "isbn": "LIB008",
            "description": "Covers the fundamentals of digital logic design with practical applications.",
            "quantity": 4,
            "available_quantity": 4,
            "created_at": datetime.now()
        },
        {
            "title": "Signals and Systems",
            "author": "Alan V. Oppenheim",
            "genre": "Electrical Engineering",
            "isbn": "LIB009",
            "description": "Classic textbook on signal processing, ideal for EE and related streams.",
            "quantity": 3,
            "available_quantity": 3,
            "created_at": datetime.now()
        },
        {
            "title": "Fluid Mechanics",
            "author": "Frank M. White",
            "genre": "Mechanical / Civil Engineering",
            "isbn": "LIB010",
            "description": "Core subject book that explains the principles and applications of fluid dynamics.",
            "quantity": 2,
            "available_quantity": 2,
            "created_at": datetime.now()
        }
    ]

    # Check if books already exist to avoid duplicates
    if mongo.db.books.count_documents({}) == 0:
        mongo.db.books.insert_many(sample_books)
        flash('Sample books added to database.', 'success')
    else:
        flash('Books already exist in the database.', 'info')

    return redirect(url_for('index'))

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        from models.user import User
        user_data = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
        user = User.from_dict(user_data) if user_data else None
    return {'current_user': user}

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])