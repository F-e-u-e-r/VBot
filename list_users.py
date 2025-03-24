#!/usr/bin/env python
import os
from flask import Flask
from models import db
from models.user import User
from tabulate import tabulate

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/vbot')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def list_users():
    """List all users in the database with their details"""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in the database.")
            return
        
        user_data = []
        for user in users:
            user_data.append([
                user.id,
                user.username,
                user.email,
                user.role,
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
                user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'Unknown'
            ])
        
        headers = ["ID", "Username", "Email", "Role", "Last Login", "Created At"]
        print(tabulate(user_data, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    # Try to import tabulate, if not available warn the user
    try:
        from tabulate import tabulate
    except ImportError:
        print("Warning: tabulate package not installed. Installing it first...")
        print("Run this inside the container to install: pip install tabulate")
        print("Then run this script again.")
        exit(1)
    
    list_users() 