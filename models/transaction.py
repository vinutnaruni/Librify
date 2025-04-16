from datetime import datetime, timedelta
from bson import ObjectId

class Transaction:
    """Transaction model for MongoDB to track book borrowing and returns"""
    
    collection_name = 'transactions'
    
    def __init__(self, user_id, book_id, borrow_date=None, due_date=None, return_date=None, _id=None):
        self.user_id = user_id
        self.book_id = book_id
        self.borrow_date = borrow_date or datetime.utcnow()
        self.due_date = due_date or (self.borrow_date + timedelta(days=14))  # Default due date is 2 weeks
        self.return_date = return_date
        self.status = "borrowed" if not return_date else "returned"
        self._id = _id or ObjectId()
    
    @classmethod
    def from_dict(cls, data):
        """Create a Transaction instance from a dictionary"""
        if not data:
            return None
        
        return cls(
            user_id=data.get('user_id'),
            book_id=data.get('book_id'),
            borrow_date=data.get('borrow_date'),
            due_date=data.get('due_date'),
            return_date=data.get('return_date'),
            _id=data.get('_id')
        )
    
    def to_dict(self):
        """Convert Transaction instance to a dictionary"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date,
            'due_date': self.due_date,
            'return_date': self.return_date,
            'status': self.status
        }
    
    @property
    def is_overdue(self):
        """Check if the transaction is overdue"""
        if self.status == "returned":
            return False
        return datetime.utcnow() > self.due_date
