#!/usr/bin/env python3
"""
Script to add a new user from the command line.
"""
import sys
import os
import argparse
from getpass import getpass

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.user import User

def create_user(username, email, password, role='user'):
    """
    Create a new user in the database.
    
    Args:
        username (str): Username for the new user
        email (str): Email address for the new user
        password (str): Password for the new user
        role (str): Role for the new user ('user' or 'admin')
        
    Returns:
        User: The created user object, or None if creation failed
    """
    app = create_app()
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"Error: User '{username}' already exists.")
            return None
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            print(f"Error: Email '{email}' is already registered.")
            return None
        
        # Create the new user
        new_user = User(
            username=username,
            email=email,
            role=role
        )
        new_user.password = password
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"User '{username}' created successfully.")
            return new_user
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {str(e)}")
            return None

def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(description='Add a new user to the application.')
    parser.add_argument('--username', '-u', required=True, help='Username for the new user')
    parser.add_argument('--email', '-e', required=True, help='Email address for the new user')
    parser.add_argument('--password', '-p', help='Password for the new user (if not provided, will be prompted)')
    parser.add_argument('--role', '-r', choices=['user', 'admin'], default='user', 
                        help='Role for the new user (default: user)')
    
    args = parser.parse_args()
    
    # If password not provided as argument, prompt for it
    password = args.password
    if not password:
        password = getpass('Enter password for the new user: ')
        password_confirm = getpass('Confirm password: ')
        
        if password != password_confirm:
            print("Error: Passwords do not match.")
            sys.exit(1)
    
    # Create the user
    user = create_user(args.username, args.email, password, args.role)
    
    if user is None:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == '__main__':
    main()