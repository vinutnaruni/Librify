from datetime import datetime
from bson import ObjectId

class Book:
    """Book model for MongoDB"""
    
    collection_name = 'books'
    
    def __init__(self, title, author, genre, isbn, description, quantity=1, _id=None):
        self.title = title
        self.author = author
        self.genre = genre
        self.isbn = isbn
        self.description = description
        self.quantity = quantity
        self.available_quantity = quantity
        self.created_at = datetime.utcnow()
        self._id = _id or ObjectId()
    
    @classmethod
    def from_dict(cls, data):
        """Create a Book instance from a dictionary"""
        if not data:
            return None
        
        return cls(
            title=data.get('title'),
            author=data.get('author'),
            genre=data.get('genre'),
            isbn=data.get('isbn'),
            description=data.get('description'),
            quantity=data.get('quantity', 1),
            _id=data.get('_id')
        )
    
    def to_dict(self):
        """Convert Book instance to a dictionary"""
        return {
            '_id': self._id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'isbn': self.isbn,
            'description': self.description,
            'quantity': self.quantity,
            'available_quantity': self.available_quantity,
            'created_at': self.created_at
        }
    
    @property
    def is_available(self):
        """Check if the book is available for borrowing"""
        return self.available_quantity > 0
