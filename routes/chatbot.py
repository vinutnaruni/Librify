from flask import Blueprint, request, jsonify, session
from bson.objectid import ObjectId
import re

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/ask', methods=['POST'])
def ask():
    # Get MongoDB connection from app
    mongo = chatbot_bp.mongo
    
    # Get the question from the request
    data = request.get_json()
    question = data.get('question', '').lower().strip()
    
    # Define predefined questions and responses
    responses = get_response(question, mongo)
    
    return jsonify(responses)

def get_response(question, mongo):
    """Get response for a predefined question"""
    
    # Check for greetings
    if re.search(r'\b(hi|hello|hey|greetings)\b', question):
        return {
            'answer': 'Hello! How can I help you with the library today?',
            'type': 'text'
        }
    
    # Check for book availability
    book_match = re.search(r'(do you have|is there|availability of|looking for) ["\']?([^"\'?]+)["\']?', question)
    if book_match or "available" in question:
        book_title = book_match.group(2) if book_match else re.sub(r'(is|available|book|the|\?)', '', question).strip()
        
        # Search for the book in the database
        book = mongo.db.books.find_one({
            'title': {'$regex': book_title, '$options': 'i'}
        })
        
        if book:
            if book['available_quantity'] > 0:
                return {
                    'answer': f"Yes, '{book['title']}' by {book['author']} is available! We have {book['available_quantity']} copies available for borrowing.",
                    'type': 'book',
                    'book_id': str(book['_id'])
                }
            else:
                return {
                    'answer': f"We have '{book['title']}' by {book['author']} in our collection, but all copies are currently borrowed. Would you like to check it out anyway?",
                    'type': 'book',
                    'book_id': str(book['_id'])
                }
        else:
            return {
                'answer': f"I couldn't find a book with the title '{book_title}' in our collection. Would you like to search for another book?",
                'type': 'text'
            }
    
    # Check for borrowed books
    if re.search(r'\b(my books|borrowed|my account|my profile)\b', question):
        if 'user_id' in session:
            # Get user's borrowed books
            transactions = list(mongo.db.transactions.find({
                'user_id': ObjectId(session['user_id']),
                'status': 'borrowed'
            }))
            
            if transactions:
                book_count = len(transactions)
                return {
                    'answer': f"You currently have {book_count} book(s) borrowed. You can view them in your profile.",
                    'type': 'profile'
                }
            else:
                return {
                    'answer': "You don't have any books borrowed at the moment. Would you like to browse our collection?",
                    'type': 'browse'
                }
        else:
            return {
                'answer': "You need to be logged in to check your borrowed books. Would you like to log in?",
                'type': 'login'
            }
    
    # Check for due dates
    if re.search(r'\b(due date|when|return|late)\b', question):
        if 'user_id' in session:
            # Get user's borrowed books
            transactions = list(mongo.db.transactions.find({
                'user_id': ObjectId(session['user_id']),
                'status': 'borrowed'
            }))
            
            if transactions:
                # Find the earliest due date
                earliest_due = min(transactions, key=lambda x: x['due_date'])
                book = mongo.db.books.find_one({'_id': earliest_due['book_id']})
                
                return {
                    'answer': f"Your earliest due date is for '{book['title']}', which is due on {earliest_due['due_date'].strftime('%B %d, %Y')}.",
                    'type': 'profile'
                }
            else:
                return {
                    'answer': "You don't have any books borrowed at the moment, so no due dates to worry about!",
                    'type': 'browse'
                }
        else:
            return {
                'answer': "You need to be logged in to check your due dates. Would you like to log in?",
                'type': 'login'
            }
    
    # Check for library hours
    if re.search(r'\b(hours|open|close|timing|schedule)\b', question):
        return {
            'answer': "Our library is open Monday to Friday from 9:00 AM to 8:00 PM, and on weekends from 10:00 AM to 6:00 PM.",
            'type': 'text'
        }
    
    # Check for help with the system
    if re.search(r'\b(how to|help|guide|tutorial|use)\b', question):
        return {
            'answer': "To use our library system, you can browse books, create an account to borrow books, and manage your borrowed items through your profile. What specific feature do you need help with?",
            'type': 'text'
        }
    
    # Check for popular books
    if re.search(r'\b(popular|recommended|best|top|most read)\b', question):
        # Get popular books from the database
        pipeline = [
            {'$group': {
                '_id': '$book_id',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 3}
        ]
        popular_books_data = list(mongo.db.transactions.aggregate(pipeline))
        
        if popular_books_data:
            book_titles = []
            for item in popular_books_data:
                book = mongo.db.books.find_one({'_id': item['_id']})
                if book:
                    book_titles.append(f"'{book['title']}' by {book['author']}")
            
            if book_titles:
                return {
                    'answer': f"Our most popular books right now are: {', '.join(book_titles)}. Would you like to check any of them out?",
                    'type': 'browse'
                }
        
        return {
            'answer': "We have many popular books in our collection. You can browse them by visiting our Books page.",
            'type': 'browse'
        }
    
    # Default response
    return {
        'answer': "I'm not sure I understand your question. You can ask me about book availability, your borrowed books, library hours, or how to use the system.",
        'type': 'text'
    }
