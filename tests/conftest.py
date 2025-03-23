import os
import tempfile
import pytest
from app import create_app
from models import db

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')
    
    # Create a temporary file to use as the test database
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    
    # Create the database and the tables
    with app.app_context():
        db.create_all()
        yield app
        
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def __init__(self, client):
            self._client = client
            
        def login(self, username='admin', password='admin123'):
            return self._client.post(
                '/login',
                data={'username': username, 'password': password}
            )
            
        def logout(self):
            return self._client.get('/logout')
    
    return AuthActions(client) 