from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from bson.objectid import ObjectId
from datetime import datetime

from models.feedback import Feedback

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

@feedback_bp.route('/add/<book_id>', methods=['GET', 'POST'])
def add_feedback(book_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to leave feedback.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get MongoDB connection from app
    mongo = feedback_bp.mongo
    
    # Get book by ID
    book_data = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    
    if not book_data:
        flash('Book not found!', 'danger')
        return redirect(url_for('books.index'))
    
    # Check if user has already left feedback for this book
    existing_feedback = mongo.db.feedback.find_one({
        'user_id': ObjectId(session['user_id']),
        'book_id': ObjectId(book_id)
    })
    
    if request.method == 'POST':
        rating = int(request.form.get('rating', 5))
        comment = request.form.get('comment', '')
        
        if existing_feedback:
            # Update existing feedback
            mongo.db.feedback.update_one(
                {'_id': existing_feedback['_id']},
                {
                    '$set': {
                        'rating': rating,
                        'comment': comment,
                        'created_at': datetime.utcnow()
                    }
                }
            )
            flash('Your feedback has been updated!', 'success')
        else:
            # Create new feedback
            feedback = Feedback(
                user_id=ObjectId(session['user_id']),
                book_id=ObjectId(book_id),
                rating=rating,
                comment=comment
            )
            
            # Insert feedback into database
            mongo.db.feedback.insert_one(feedback.to_dict())
            flash('Your feedback has been submitted!', 'success')
        
        return redirect(url_for('books.view', book_id=book_id))
    
    return render_template('feedback/add.html', book=book_data, existing_feedback=existing_feedback)

@feedback_bp.route('/book/<book_id>')
def book_feedback(book_id):
    # Get MongoDB connection from app
    mongo = feedback_bp.mongo
    
    # Get book by ID
    book_data = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    
    if not book_data:
        flash('Book not found!', 'danger')
        return redirect(url_for('books.index'))
    
    # Get all feedback for this book
    feedback_list = list(mongo.db.feedback.find({'book_id': ObjectId(book_id)}).sort('created_at', -1))
    
    # Get user data for each feedback
    for feedback in feedback_list:
        user_data = mongo.db.users.find_one({'_id': feedback['user_id']})
        feedback['user'] = user_data
    
    # Calculate average rating
    avg_rating = 0
    if feedback_list:
        avg_rating = sum(f['rating'] for f in feedback_list) / len(feedback_list)
    
    return render_template('feedback/book.html', book=book_data, feedback_list=feedback_list, avg_rating=avg_rating)

@feedback_bp.route('/delete/<feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to delete feedback.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get MongoDB connection from app
    mongo = feedback_bp.mongo
    
    # Get feedback by ID
    feedback_data = mongo.db.feedback.find_one({'_id': ObjectId(feedback_id)})
    
    if not feedback_data:
        flash('Feedback not found!', 'danger')
        return redirect(url_for('books.index'))
    
    # Check if feedback belongs to user or user is admin
    if str(feedback_data['user_id']) != session['user_id'] and not session.get('is_admin'):
        flash('You are not authorized to delete this feedback.', 'danger')
        return redirect(url_for('books.view', book_id=str(feedback_data['book_id'])))
    
    # Delete feedback
    mongo.db.feedback.delete_one({'_id': ObjectId(feedback_id)})
    
    flash('Feedback deleted successfully!', 'success')
    return redirect(url_for('books.view', book_id=str(feedback_data['book_id'])))
