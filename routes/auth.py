from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId

from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Get MongoDB connection
        mongo = auth_bp.mongo
        
        # Find user by email
        user_data = mongo.db.users.find_one({'email': email})
        
        if user_data and user_data['password'] == password:  # Direct password comparison (plaintext)
            user = User.from_dict(user_data)
            session['user_id'] = str(user._id)
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('index'))  # Fixed 'main.index' to 'index'

        flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        mongo = auth_bp.mongo
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('auth/register.html')
        
        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered!', 'danger')
            return render_template('auth/register.html')
        
        # Store plaintext password directly
        user = User(username=username, email=email, password=password)  # No hashing
        mongo.db.users.insert_one(user.to_dict())
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('auth.login'))
    
    mongo = auth_bp.mongo
    user_data = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    user = User.from_dict(user_data)
    
    transactions = list(mongo.db.transactions.find({
        'user_id': ObjectId(session['user_id']),
        'status': 'borrowed'
    }))
    
    borrowed_books = []
    for transaction in transactions:
        book_data = mongo.db.books.find_one({'_id': transaction['book_id']})
        if book_data:
            borrowed_books.append({
                'book': book_data,
                'transaction': transaction
            })
    
    return render_template('auth/profile.html', user=user, borrowed_books=borrowed_books)
