import pytest
from flask import session
from models.user import User

def test_login_page(client):
    """Test that the login page loads successfully."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_registration_page(client):
    """Test that the registration page loads successfully."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Create an Account' in response.data

def test_create_user(app):
    """Test creating a new user."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.password = 'password123'
        
        from models import db
        db.session.add(user)
        db.session.commit()
        
        assert User.query.filter_by(username='testuser').first() is not None

def test_invalid_login(client):
    """Test login with invalid credentials."""
    response = client.post(
        '/login',
        data={'username': 'nonexistent', 'password': 'wrong'},
        follow_redirects=True
    )
    assert b'Invalid username or password' in response.data 