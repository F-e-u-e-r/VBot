import pytest
import os
import io
from models.tracking import UploadedFile, TrackingData

def test_tracking_tool_page_requires_login(client):
    """Test that the tracking tool page requires a user to be logged in."""
    response = client.get('/tracking-tool', follow_redirects=True)
    assert b'Login' in response.data

def test_tracking_tool_page_access(client, auth):
    """Test that a logged-in user can access the tracking tool page."""
    # Create admin user and login
    with client.application.app_context():
        from models.user import User
        from models import db
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', email='admin@example.com', role='admin')
            user.password = 'admin123'
            db.session.add(user)
            db.session.commit()
    
    auth.login()
    response = client.get('/tracking-tool')
    assert response.status_code == 200
    assert b'Upload Excel File' in response.data

def test_file_upload_invalid_extension(client, auth):
    """Test that uploading a file with invalid extension fails."""
    auth.login()
    
    # Create a text file as a test
    data = {'file': (io.BytesIO(b'This is a test file'), 'test.txt')}
    
    response = client.post('/tracking-tool', data=data, follow_redirects=True)
    assert b'Excel files only' in response.data

# Note: To properly test Excel uploads, we would need to create a valid Excel file
# This is a simplified version focused on checking the UI and permissions 