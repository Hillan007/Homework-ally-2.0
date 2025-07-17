"""
Simple file-based storage as a fallback when MongoDB is not available
"""
import json
import os
from datetime import datetime
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SimpleFileDB:
    def __init__(self, db_file="users.json"):
        self.db_file = db_file
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.users, f, indent=2, default=str)
    
    def create_user(self, email, password, profile_pic=None):
        """Create a new user"""
        if email in self.users:
            return None
        
        user_id = str(uuid.uuid4())
        self.users[email] = {
            "id": user_id,
            "email": email,
            "password": pwd_context.hash(password),
            "profile_pic": profile_pic,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self._save_users()
        return user_id
    
    def get_user_by_email(self, email):
        """Get user by email"""
        return self.users.get(email)
    
    def verify_password(self, plain_password, hashed_password):
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def update_user_profile_pic(self, email, profile_pic_path):
        """Update user's profile picture"""
        if email in self.users:
            self.users[email]["profile_pic"] = profile_pic_path
            self.users[email]["updated_at"] = datetime.utcnow().isoformat()
            self._save_users()
            return True
        return False

# Global instance
file_db = SimpleFileDB()
