from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId
from datetime import datetime

from models.book import Book
from models.user import User
from models.transaction import Transaction

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin authentication middleware
@admin_bp.before_request
def require_admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('You must be an admin to access this page.', 'danger')
        return redirect(url_for('auth.login'))

@admin_bp.route('/')
def dashboard():
    # Get MongoDB connection from app
    mongo = admin_bp.mongo
    
    # Get counts for dashboard
    book_count = mongo.db.books.count_documents({})
    user_count = mongo.db.users.count_documents({})
    transaction_count = mongo.db.transactions.count_documents({})
    active_borrows = mongo.db.transactions.count_documents({'status': 'borrowed'})
    
    # Get recent transactions
    recent_transactions = list(mongo.db.transactions.find().sort('borrow_date', -1).limit(5))
    
    # Get book and user details for transactions
    for transaction in recent_transactions:
        book_data = mongo.db.books.find_one({'_id': transaction['book_id']})
        user_data = mongo.db.users.find_one({'_id': transaction['user_id']})
        transaction['book'] = book_data
        transaction['user'] = user_data
    
    return render_template('admin/dashboard.html', 
                          book_count=book_count,
                          user_count=user_count,
                          transaction_count=transaction_count,
                          active_borrows=active_borrows,
                          recent_transactions=recent_transactions)

# Books management
@admin_bp.route('/books')
def books():
    # Get MongoDB connection from app
    mongo = admin_bp.mongo
    
    # Get all books
    books = list(mongo.db.books.find())
    
    return render_template('admin/books.html', books=books)

@admin_bp.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        isbn = request.form.get('isbn')
        description = request.form.get('description')
        quantity = int(request.form.get('quantity', 1))
        
        # Create new book
        book = Book(
            title=title,
            author=author,
            genre=genre,
            isbn=isbn,
            description=description,
            quantity=quantity
        )
        
        # Get MongoDB connection from app
        mongo = admin_bp.mongo
        
        # Insert book into database
        mongo.db.books.insert_one(book.to_dict())
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin.books'))
    
    return render_template('admin/add_book.html')

@admin_bp.route('/books/edit/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    # Get MongoDB connection from app
    mongo = admin_bp.mongo
    
    # Get book by ID
    book_data = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    
    if not book_data:
        flash('Book not found!', 'danger')
        return redirect(url_for('admin.books'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        isbn = request.form.get('isbn')
        description = request.form.get('description')
        quantity = int(request.form.get('quantity', 1))
        
        # Calculate new available quantity
        borrowed = book_data['quantity'] - book_data['available_quantity']
        new_available = max(0, quantity - borrowed)
        
        # Update book
        mongo.db.books.update_one(
            {'_id': ObjectId(book_id)},
            {
                '$set': {
                    'title': title,
                    'author': author,
                    'genre': genre,
                    'isbn': isbn,
                    'description': description,
                    'quantity': quantity,
                    'available_quantity': new_available
                }
            }
        )
        
        flash('Book updated successfully!', 'success')
        return redirect(url_for('admin.books'))
    
    return render_template('admin/edit_book.html', book=book_data)

@admin_bp.route('/books/delete/<book_id>', methods=['POST'])
def delete_book(book_id):
    # Get MongoDB connection from app
    mongo = admin_bp.mongo
    
    # Check if book is currently borrowed
    active_borrows = mongo.db.transactions.count_documents({
        'book_id': ObjectId(book_id),
        'status': 'borrowed'
    })
    
    if active_borrows > 0:
        flash('Cannot delete book because it is currently borrowed.', 'danger')
        return redirect(url_for('admin.books'))
    
    # Delete book
    mongo.db.books.delete_one({'_id': ObjectId(book_id)})
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin.books'))

# Users management
@admin_bp.route('/users')
def users():
    # Get MongoDB connection from app
    mongo = admin_bp.mongo
    
    # Get all users
    users = list(mongo.db.users.find())
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        
        # Get MongoDB connection from app
        mongo = admin_bp.mongo
        
        # Check if email already exists
        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered!', 'danger')
            return render_template('admin/add_user.html')
        
        # Create new user
        hashed_password = password 
        user = User(
            username=username,
            email=email,
            password=hashed_password,
            is_admin=is_admin
        )
        
        # Insert user into database
        mongo.db.users.insert_one(user.to_dict())
        
        flash('User added successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html')

@admin_bp.route('/users/edit/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # Get MongoDB connection from app
    mongo = admin_bp.mongo
    
    # Get user by ID
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    
    if not user_data:
        flash('User not found!', 'danger')
        return redirect(url_for('admin.users'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        is_admin = 'is_admin' in request.form
        
        # Update user
        update_data = {
            'username': username,
            'email': email,
            'is_admin': is_admin
        }
        
        # Update password if provided
        password = request.form.get('password')
        if password:
            update_data['password'] = password
        
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user_data)

@admin_bp.route('/users/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    # Get MongoDB connection from app
    mongo = admin_bp.mongo
    
    # Check if user has active borrows
    active_borrows = mongo.db.transactions.count_documents({
        'user_id': ObjectId(user_id),
        'status': 'borrowed'
    })
    
    if active_borrows > 0:
        flash('Cannot delete user because they have borrowed books.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Delete user
    mongo.db.users.delete_one({'_id': ObjectId(user_id)})
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

# Transactions management
@admin_bp.route('/transactions')
def transactions():
    # Get MongoDB connection from app
    mongo = admin_bp.mongo
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    
    # Build query
    query = {}
    if status_filter:
        query['status'] = status_filter
    
    # Get transactions
    transactions = list(mongo.db.transactions.find(query).sort('borrow_date', -1))
    
    # Get book and user details for transactions
    for transaction in transactions:
        book_data = mongo.db.books.find_one({'_id': transaction['book_id']})
        user_data = mongo.db.users.find_one({'_id': transaction['user_id']})
        transaction['book'] = book_data
        transaction['user'] = user_data
    
    return render_template('admin/transactions.html', 
                          transactions=transactions,
                          status_filter=status_filter)

@admin_bp.route('/reports')
def reports():
    # Get MongoDB connection from app
    mongo = admin_bp.mongo
    
    # Get popular books (most borrowed)
    pipeline = [
        {'$group': {
            '_id': '$book_id',
            'count': {'$sum': 1}
        }},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]
    popular_books_data = list(mongo.db.transactions.aggregate(pipeline))
    
    popular_books = []
    for item in popular_books_data:
        book_data = mongo.db.books.find_one({'_id': item['_id']})
        if book_data:
            book_data['borrow_count'] = item['count']
            popular_books.append(book_data)
    
    # Get overdue books
    overdue_transactions = list(mongo.db.transactions.find({
        'status': 'borrowed',
        'due_date': {'$lt': datetime.utcnow()}
    }))
    
    overdue_books = []
    for transaction in overdue_transactions:
        book_data = mongo.db.books.find_one({'_id': transaction['book_id']})
        user_data = mongo.db.users.find_one({'_id': transaction['user_id']})
        if book_data and user_data:
            overdue_books.append({
                'book': book_data,
                'user': user_data,
                'transaction': transaction
            })
    
    # Get genre distribution
    genres = mongo.db.books.distinct('genre')
    genre_stats = []
    
    for genre in genres:
        count = mongo.db.books.count_documents({'genre': genre})
        genre_stats.append({
            'genre': genre,
            'count': count
        })
    
    genre_stats.sort(key=lambda x: x['count'], reverse=True)
    
    return render_template('admin/reports.html',
                          popular_books=popular_books,
                          overdue_books=overdue_books,
                          genre_stats=genre_stats)
