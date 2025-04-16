from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from bson.objectid import ObjectId
from datetime import datetime

from models.book import Book
from models.transaction import Transaction

books_bp = Blueprint('books', __name__)

@books_bp.route('/')
def index():
    # Get MongoDB connection from app
    mongo = books_bp.mongo
    
    # Get query parameters for filtering
    search_query = request.args.get('search', '')
    genre_filter = request.args.get('genre', '')
    
    # Build query
    query = {}
    if search_query:
        query['$or'] = [
            {'title': {'$regex': search_query, '$options': 'i'}},
            {'author': {'$regex': search_query, '$options': 'i'}},
            {'isbn': {'$regex': search_query, '$options': 'i'}}
        ]
    
    if genre_filter:
        query['genre'] = genre_filter
    
    # Get all books matching the query
    books = list(mongo.db.books.find(query))
    
    # Get all genres for filter dropdown
    genres = mongo.db.books.distinct('genre')
    
    return render_template('books/index.html', books=books, genres=genres, 
                          search_query=search_query, genre_filter=genre_filter)

@books_bp.route('/<book_id>')
def view(book_id):
    # Get MongoDB connection from app
    mongo = books_bp.mongo
    
    # Get book by ID
    book_data = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    
    if not book_data:
        flash('Book not found!', 'danger')
        return redirect(url_for('books.index'))
    
    book = Book.from_dict(book_data)
    
    # Get feedback data for this book
    feedback_list = list(mongo.db.feedback.find({'book_id': ObjectId(book_id)}))
    feedback_data = None
    
    if feedback_list:
        avg_rating = sum(f['rating'] for f in feedback_list) / len(feedback_list)
        feedback_data = {
            'avg_rating': avg_rating,
            'count': len(feedback_list)
        }
    
    return render_template('books/view.html', book=book, feedback_data=feedback_data)

@books_bp.route('/borrow/<book_id>', methods=['POST'])
def borrow(book_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to borrow books.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get MongoDB connection from app
    mongo = books_bp.mongo
    
    # Get book by ID
    book_data = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    
    if not book_data:
        flash('Book not found!', 'danger')
        return redirect(url_for('books.index'))
    
    # Check if book is available
    if book_data['available_quantity'] <= 0:
        flash('This book is currently not available for borrowing.', 'danger')
        return redirect(url_for('books.view', book_id=book_id))
    
    # Check if user has already borrowed this book
    existing_transaction = mongo.db.transactions.find_one({
        'user_id': ObjectId(session['user_id']),
        'book_id': ObjectId(book_id),
        'status': 'borrowed'
    })
    
    if existing_transaction:
        flash('You have already borrowed this book.', 'warning')
        return redirect(url_for('books.view', book_id=book_id))
    
    # Create new transaction
    transaction = Transaction(
        user_id=ObjectId(session['user_id']),
        book_id=ObjectId(book_id)
    )
    
    # Insert transaction into database
    mongo.db.transactions.insert_one(transaction.to_dict())
    
    # Update book available quantity
    mongo.db.books.update_one(
        {'_id': ObjectId(book_id)},
        {'$inc': {'available_quantity': -1}}
    )
    
    flash('Book borrowed successfully!', 'success')
    return redirect(url_for('auth.profile'))

@books_bp.route('/return/<transaction_id>', methods=['POST'])
def return_book(transaction_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to return books.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get MongoDB connection from app
    mongo = books_bp.mongo
    
    # Get transaction by ID
    transaction_data = mongo.db.transactions.find_one({'_id': ObjectId(transaction_id)})
    
    if not transaction_data:
        flash('Transaction not found!', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Check if transaction belongs to user
    if str(transaction_data['user_id']) != session['user_id'] and not session.get('is_admin'):
        flash('You are not authorized to return this book.', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Update transaction
    mongo.db.transactions.update_one(
        {'_id': ObjectId(transaction_id)},
        {
            '$set': {
                'return_date': datetime.utcnow(),
                'status': 'returned'
            }
        }
    )
    
    # Update book available quantity
    mongo.db.books.update_one(
        {'_id': transaction_data['book_id']},
        {'$inc': {'available_quantity': 1}}
    )
    
    flash('Book returned successfully!', 'success')
    
    if session.get('is_admin'):
        return redirect(url_for('admin.transactions'))
    else:
        return redirect(url_for('auth.profile'))
