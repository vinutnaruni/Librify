from datetime import datetime
from bson import ObjectId

class User:
    """User model for MongoDB"""
    
    collection_name = 'users'
    
    def __init__(self, username, email, password, is_admin=False, _id=None):
        self.username = username
        self.email = email
        self.password = password  # This should be hashed before storing
        self.is_admin = is_admin
        self.created_at = datetime.utcnow()
        self._id = _id or ObjectId()
    
    @classmethod
    def from_dict(cls, data):
        """Create a User instance from a dictionary"""
        if not data:
            return None
        
        return cls(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            is_admin=data.get('is_admin', False),
            _id=data.get('_id')
        )
    
    def to_dict(self):
        """Convert User instance to a dictionary"""
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }
    
    def get_id(self):
        """Return the user ID as a string"""
        return str(self._id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
