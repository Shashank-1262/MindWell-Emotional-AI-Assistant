import os
import json
import hashlib
from utils.timestamp import get_current_timestamp

class UserManager:
    def __init__(self, base_dir="users"):
        self.base_dir = base_dir
        self.users_file = os.path.join(self.base_dir, "users.json")
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
                
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username, password):
        with open(self.users_file, 'r') as f:
            users = json.load(f)
        
        if username in users:
            return False, "Username already exists."
        
        user_id = username.lower().replace(" ", "_")
        users[username] = {
            "password": self._hash_password(password),
            "user_id": user_id,
            "created_at": get_current_timestamp()
        }
        
        # Create user data directory
        user_dir = os.path.join(self.base_dir, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=4)
            
        return True, user_id

    def login(self, username, password):
        with open(self.users_file, 'r') as f:
            users = json.load(f)
            
        if username not in users:
            return False, "User not found."
        
        if users[username]["password"] == self._hash_password(password):
            return True, users[username]["user_id"]
        
        return False, "Invalid password."

    def get_user_dir(self, user_id):
        return os.path.join(self.base_dir, user_id)
