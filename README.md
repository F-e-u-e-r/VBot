# VBot - Tracking Tool Web Application

A Flask-based web application for tracking and processing Excel file data.

## Features

- User authentication with admin and regular user roles
- Web-based user management for administrators
- Excel file upload and validation
- Data processing and visualization
- RESTful API endpoints for accessing tracking data
- Command-line utilities for user management

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL (recommended) or SQLite for development
- Virtual environment (recommended)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/F-e-u-e-r/VBot.git
   cd VBot
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file in the project root):
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://username:password@localhost/vbot
   ```

5. Initialize the database:
   ```
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

## User Management

### Web Interface (Admin Only)

1. Login with an admin account
2. Click on the "User Management" link in the dropdown menu
3. Use the interface to add or remove users

### Command Line Scripts

The application includes command-line scripts for user management:

#### Add a User
```
python scripts/add_user.py --username johndoe --email john@example.com --role user
```

#### Remove a User
```
python scripts/remove_user.py --username johndoe
```

#### List Users
```
python scripts/list_users.py
```

## Docker Deployment

A `Dockerfile` and `docker-compose.yml` are provided for containerized deployment.

1. Build and start the containers:
   ```
   docker-compose up -d
   ```

2. The application will be available at `http://localhost:5001`

## Production Deployment

For production deployment, it's recommended to:

1. Use a proper WSGI server (Gunicorn is included in requirements)
2. Set up Nginx as a reverse proxy
3. Use a production-grade database
4. Set up SSL/TLS

Example Gunicorn command:
```
gunicorn -w 4 -b 0.0.0.0:5001 run:app
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Flask and its extensions
- Bootstrap for the UI
- All other open-source libraries used in this project