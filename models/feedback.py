from datetime import datetime
from bson import ObjectId

class Feedback:
    """Feedback model for MongoDB to store book reviews and ratings"""
    
    collection_name = 'feedback'
    
    def __init__(self, user_id, book_id, rating, comment, _id=None):
        self.user_id = user_id
        self.book_id = book_id
        self.rating = rating  # Rating out of 5
        self.comment = comment
        self.created_at = datetime.utcnow()
        self._id = _id or ObjectId()
    
    @classmethod
    def from_dict(cls, data):
        """Create a Feedback instance from a dictionary"""
        if not data:
            return None
        
        return cls(
            user_id=data.get('user_id'),
            book_id=data.get('book_id'),
            rating=data.get('rating'),
            comment=data.get('comment'),
            _id=data.get('_id')
        )
    
    def to_dict(self):
        """Convert Feedback instance to a dictionary"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at
        }
