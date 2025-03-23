# Tracking Tool

A web application for tracking and processing Excel files with data validation, built with Flask and modern best practices.

## Features

- User authentication system with account locking and role-based access
- Excel file upload (.xlsx/.xls) with intelligent header detection
- Data validation and transformation
- Responsive design for mobile and desktop
- Dockerized deployment with Nginx and PostgreSQL
- Comprehensive logging and error handling
- Service-oriented architecture
- Environment-specific configuration

## Project Structure

```
tracking-tool/
├── app.py                 # Main application file
├── config.py              # Configuration settings
├── forms.py               # WTForms definitions
├── logging_config.py      # Centralized logging configuration
├── manage.py              # CLI commands for database operations
├── run.py                 # Application entry point with enhanced error handling
├── utils.py               # Utility functions
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker container definition
├── models/                # Database models
│   ├── __init__.py        # Database initialization
│   ├── user.py            # User model
│   └── tracking.py        # Tracking data models
├── services/              # Service layer
│   ├── __init__.py         
│   └── tracking_service.py # Business logic for tracking operations
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript
│   └── images/            # Images and icons
├── templates/             # HTML templates
├── nginx/                 # Nginx configuration
│   └── conf.d/            # Server configuration
├── tests/                 # Test suite
├── logs/                  # Application logs (created at runtime)
└── uploads/               # Upload directory (created at runtime)
```

## Setup and Installation

### Local Development

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   ```

4. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. Run the application:
   ```
   python run.py
   ```

### Docker Deployment

1. Create `.env` file with required environment variables:
   ```
   POSTGRES_PASSWORD=your-secure-password
   SECRET_KEY=your-secret-key
   MAIL_SERVER=smtp.example.com
   MAIL_PORT=587
   MAIL_USERNAME=user@example.com
   MAIL_PASSWORD=mail-password
   MAIL_DEFAULT_SENDER=noreply@example.com
   ADMIN_EMAIL=admin@example.com
   ```

2. Build and start services:
   ```
   docker-compose up -d
   ```

3. Initialize the database:
   ```
   docker-compose exec web flask db upgrade
   ```

4. Access the application at http://localhost (or your domain)

## Recent Improvements

- **Service Layer**: Added a service layer to separate business logic from presentation
- **Enhanced Error Handling**: Improved error handling with centralized logging
- **Docker Support**: Added Docker and docker-compose for easy deployment
- **Code Organization**: Refactored code for better organization and maintainability
- **Environment Configuration**: Enhanced configuration for development, testing, and production
- **Security Headers**: Added security headers and content security policy
- **Testing Support**: Improved testing infrastructure

## API Endpoints

- `/tracking-tool` - File upload interface
- `/tracking-data` - Display tracking data
- `/api/tracking-data` - JSON API for tracking data

## Security Features

- CSRF protection
- Content Security Policy
- XSS protection headers
- Rate limiting for login attempts
- Account locking after multiple failed login attempts
- Secure password storage with PBKDF2-SHA256
- HTTPS enforcement in production

## Contribution

1. Clone the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Flask and its extensions
- Bootstrap for responsive UI
- Pandas for data processing
- Docker for containerization
