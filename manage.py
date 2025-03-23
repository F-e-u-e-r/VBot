#!/usr/bin/env python
import os
import click
from flask.cli import FlaskGroup
from app import create_app
from models import db, migrate

app = create_app(os.getenv('FLASK_ENV', 'default'))

cli = FlaskGroup(create_app=lambda: app)

@cli.command('db-init')
def db_init():
    """Initialize the database."""
    db.create_all()
    from models.user import User
    admin_password = User.create_default_user()
    if admin_password:
        click.echo(f"Initialized the database.")
        click.echo(f"Created admin user with password: {admin_password}")
        click.echo(f"PLEASE CHANGE THIS PASSWORD IMMEDIATELY AFTER FIRST LOGIN!")
    else:
        click.echo("Database already contains users, no default user created.")

@cli.command('db-drop')
@click.confirmation_option(prompt='Are you sure you want to drop all tables?')
def db_drop():
    """Drop all tables."""
    db.drop_all()
    click.echo("Dropped all tables.")

@cli.command('create-test-data')
def create_test_data():
    """Create test data for development."""
    from models.user import User
    from models.tracking import UploadedFile, TrackingData
    import secrets
    from datetime import datetime, timedelta
    
    # Create test users
    users = [
        {'username': 'testuser1', 'email': 'test1@example.com', 'password': 'password123'},
        {'username': 'testuser2', 'email': 'test2@example.com', 'password': 'password123'}
    ]
    
    for user_data in users:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(username=user_data['username'], email=user_data['email'])
            user.password = user_data['password']
            db.session.add(user)
            click.echo(f"Created test user: {user_data['username']}")
    
    db.session.commit()
    
    # Create test file uploads and tracking data for the first test user
    user = User.query.filter_by(username='testuser1').first()
    if user:
        for i in range(1, 4):  # Create 3 test files
            file = UploadedFile(
                filename=f"testfile_{i}.xlsx",
                original_filename=f"test_campaign_{i}.xlsx", 
                file_path=f"/path/to/fake/file_{i}.xlsx",
                file_size=1024 * i,
                file_type='xlsx',
                uploaded_by=user.id,
                uploaded_at=datetime.utcnow() - timedelta(days=i)
            )
            db.session.add(file)
            db.session.commit()
            
            # Add tracking data for each file
            for j in range(1, 4):  # 3 tracking entries per file
                unique_id = secrets.token_hex(4)
                tracking = TrackingData(
                    file_id=file.id,
                    placement_name=f"Placement {i}-{j}",
                    ad_name=f"Ad {i}-{j}",
                    creative_name=f"Creative {i}-{j}",
                    campaign_id=f"CAMP{i}{j}",
                    imp_tag=f"<img src='https://example.com/pixel?id={unique_id}'>",
                    click_tag=f"<a href='https://example.com/click?id={unique_id}'>Click</a>",
                    third_party_tracking=f"<!-- 3rd party tracking for {unique_id} -->"
                )
                db.session.add(tracking)
            
            db.session.commit()
            click.echo(f"Created test file {i} with 3 tracking entries")
    
    click.echo("Test data creation complete")

if __name__ == '__main__':
    cli() 