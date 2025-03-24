#!/usr/bin/env python3
"""
Script to remove a user from the command line.
"""
import sys
import os
import argparse

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.user import User

def remove_user(username):
    """
    Remove a user from the database.
    
    Args:
        username (str): Username of the user to remove
        
    Returns:
        bool: True if user was removed, False otherwise
    """
    app = create_app()
    with app.app_context():
        # Find the user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"Error: User '{username}' not found.")
            return False
        
        # Don't remove the last admin user
        if user.is_admin():
            admin_count = User.query.filter_by(role='admin').count()
            
            if admin_count <= 1:
                print("Error: Cannot remove the last admin user.")
                return False
        
        try:
            db.session.delete(user)
            db.session.commit()
            print(f"User '{username}' removed successfully.")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error removing user: {str(e)}")
            return False

def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(description='Remove a user from the application.')
    parser.add_argument('--username', '-u', required=True, help='Username of the user to remove')
    parser.add_argument('--force', '-f', action='store_true', help='Force removal without confirmation')
    
    args = parser.parse_args()
    
    # If not force, ask for confirmation
    if not args.force:
        confirm = input(f"Are you sure you want to remove user '{args.username}'? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(0)
    
    # Remove the user
    success = remove_user(args.username)
    
    if not success:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == '__main__':
    main()