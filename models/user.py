from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta
import os
import secrets

from models import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    session_token = db.Column(db.String(100), nullable=True)
    session_expiry = db.Column(db.DateTime, nullable=True)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def verify_password(self, password):
        if self.is_account_locked():
            return False
            
        is_valid = check_password_hash(self.password_hash, password)
        
        if not is_valid:
            self.login_attempts += 1
            if self.login_attempts >= 5:  # Lock after 5 failed attempts
                self.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
        else:
            self.login_attempts = 0
            self.last_login = datetime.utcnow()
            # Generate a new session token when user logs in
            self.generate_session_token()
            db.session.commit()
            
        return is_valid
    
    def is_account_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        if self.locked_until:  # If lock time has passed, reset attempts
            self.login_attempts = 0
            self.locked_until = None
            db.session.commit()
        return False
    
    def is_admin(self):
        return self.role == 'admin'
    
    def generate_session_token(self):
        """Generate a new session token with 24-hour expiry"""
        self.session_token = secrets.token_hex(32)
        self.session_expiry = datetime.utcnow() + timedelta(hours=24)
        return self.session_token
    
    def is_session_valid(self):
        """Check if the current session is valid"""
        if not self.session_token or not self.session_expiry:
            return False
        return self.session_expiry > datetime.utcnow()
    
    def invalidate_session(self):
        """Invalidate the current session"""
        self.session_token = None
        self.session_expiry = None
        db.session.commit()
    
    @classmethod
    def create_default_user(cls):
        """Create default admin user if no users exist"""
        if not cls.query.first():
            # Set fixed credentials for testing environments
            admin_password = 'admin123'
            
            default_user = cls(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            default_user.password = admin_password
            db.session.add(default_user)
            db.session.commit()
            
            # Return password so it can be displayed or logged once
            return admin_password
        return None 