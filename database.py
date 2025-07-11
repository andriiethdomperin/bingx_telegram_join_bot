import json
import os
from typing import Dict, Any, Optional

class UserDatabase:
    def __init__(self, db_file: str = "users.json"):
        self.db_file = db_file
        self.users = self._load_users()
    
    def _load_users(self) -> Dict[str, Any]:
        """Load users from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user data by user ID"""
        return self.users.get(str(user_id), {
            'state': 'GREETING',
            'has_kyc': None,
            'has_deposit': None,
            'username': None,
            'name': None
        })
    
    def update_user(self, user_id: int, **kwargs):
        """Update user data"""
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            self.users[user_id_str] = {}
        
        self.users[user_id_str].update(kwargs)
        self._save_users()
    
    def set_user_state(self, user_id: int, state: str):
        """Set user's current state"""
        self.update_user(user_id, state=state)
    
    def set_user_info(self, user_id: int, username: str = None, name: str = None):
        """Set user's basic information"""
        self.update_user(user_id, username=username, name=name)
    
    def set_kyc_status(self, user_id: int, has_kyc: bool):
        """Set user's KYC status"""
        self.update_user(user_id, has_kyc=has_kyc)
    
    def set_deposit_status(self, user_id: int, has_deposit: bool):
        """Set user's deposit status"""
        self.update_user(user_id, has_deposit=has_deposit)
    
    def get_pending_users(self) -> Dict[str, Any]:
        """Get all users waiting for admin verification"""
        return {
            user_id: user_data 
            for user_id, user_data in self.users.items() 
            if user_data.get('state') == 'WAITING_FOR_ADMIN'
        } 