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

def remove_user(username):
    """Remove a user from the database by username"""
    app = create_app()
    
    with app.app_context():
        # Find the user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"User '{username}' not found!")
            return False
        
        try:
            db.session.delete(user)
            db.session.commit()
            print(f"User '{username}' removed successfully!")
            return True
        except Exception as e:
            print(f"Error removing user: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove a user from VBot database")
    parser.add_argument("username", help="Username of the user to remove")
    
    args = parser.parse_args()
    
    remove_user(args.username) 