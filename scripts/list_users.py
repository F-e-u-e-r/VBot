#!/usr/bin/env python3
"""
Script to list all users from the command line.
"""
import sys
import os
import argparse
from tabulate import tabulate
from datetime import datetime

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models.user import User

def list_users(role=None, format_type='table'):
    """
    List all users in the database.
    
    Args:
        role (str, optional): Filter users by role ('user' or 'admin')
        format_type (str): Output format ('table', 'csv', or 'json')
        
    Returns:
        list: List of users as dictionaries
    """
    app = create_app()
    with app.app_context():
        # Build query
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        # Get all users
        users = query.all()
        
        if not users:
            print("No users found.")
            return []
        
        # Format user data
        user_data = []
        for user in users:
            created_at = user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'N/A'
            last_login = user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'
            
            user_data.append({
                'ID': user.id,
                'Username': user.username,
                'Email': user.email,
                'Role': user.role,
                'Created': created_at,
                'Last Login': last_login
            })
        
        # Display users based on format
        if format_type == 'table':
            # Table format
            headers = user_data[0].keys()
            rows = [u.values() for u in user_data]
            print(tabulate(rows, headers=headers, tablefmt='pretty'))
        elif format_type == 'csv':
            # CSV format
            headers = user_data[0].keys()
            print(','.join(headers))
            for user in user_data:
                print(','.join(str(value) for value in user.values()))
        elif format_type == 'json':
            # JSON format
            import json
            print(json.dumps(user_data, indent=2))
        
        return user_data

def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(description='List all users in the application.')
    parser.add_argument('--role', '-r', choices=['user', 'admin'], 
                        help='Filter by role (all users if not specified)')
    parser.add_argument('--format', '-f', choices=['table', 'csv', 'json'], default='table',
                        help='Output format (default: table)')
    
    args = parser.parse_args()
    
    # List the users
    list_users(args.role, args.format)
    
    sys.exit(0)

if __name__ == '__main__':
    main()