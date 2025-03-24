#!/usr/bin/env python
import os
import sys
import argparse
from flask import Flask
from models import db
from models.user import User

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/vbot')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def add_user(username, email, password, role='user'):
    """Add a new user to the database"""
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists!")
            return False
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            role=role
        )
        new_user.password = password  # This will hash the password
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"User '{username}' created successfully with role '{role}'!")
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a new user to VBot database")
    parser.add_argument("username", help="Username for the new user")
    parser.add_argument("email", help="Email address for the new user")
    parser.add_argument("password", help="Password for the new user")
    parser.add_argument("--role", choices=["user", "admin"], default="user", 
                        help="User role (default: user)")
    
    args = parser.parse_args()
    
    add_user(args.username, args.email, args.password, args.role)