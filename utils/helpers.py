from datetime import datetime
from bson.objectid import ObjectId

def format_date(date):
    """Format a datetime object to a readable string"""
    if not date:
        return ""
    return date.strftime("%B %d, %Y")

def calculate_fine(due_date, return_date=None):
    """Calculate fine for overdue books"""
    if not return_date:
        return_date = datetime.utcnow()
    
    # If book is not overdue, no fine
    if return_date <= due_date:
        return 0
    
    # Calculate days overdue
    delta = return_date - due_date
    days_overdue = delta.days
    
    # Fine calculation: $0.50 per day overdue
    fine = days_overdue * 0.5
    
    return fine

def is_book_available(mongo, book_id):
    """Check if a book is available for borrowing"""
    book = mongo.db.books.find_one({'_id': ObjectId(book_id)})
    if not book:
        return False
    return book['available_quantity'] > 0
