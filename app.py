"""
Tracking Tool Web Application
A Flask application for tracking and processing Excel file data.
"""
import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session, send_from_directory, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_apscheduler import APScheduler
import pandas as pd
import logging
from werkzeug.security import generate_password_hash

from models import db, migrate
from models.user import User
from models.tracking import UploadedFile, TrackingData
from forms import LoginForm, RegistrationForm, ChangePasswordForm, UploadFileForm
from config import config
from utils import allowed_file, save_uploaded_file, validate_excel_file, process_excel_file

# Create scheduler instance only when needed
def get_scheduler():
    return APScheduler()

def create_app(config_name='default'):
    """
    Create and configure the Flask application.
    
    Args:
        config_name (str): Configuration to use (default, development, production)
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Enable CORS for all routes
    CORS(app)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf = CSRFProtect(app)
    
    # Initialize scheduler only in production or development
    if config_name != 'testing':
        scheduler = get_scheduler()
        scheduler.init_app(app)
        
        # Define cleanup task here
        @scheduler.task('interval', id='cleanup_old_files', hours=24, misfire_grace_time=900)
        def cleanup_old_files():
            """Task to clean up old uploaded files periodically."""
            with app.app_context():
                app.logger.info("Running scheduled cleanup task")
                upload_dir = app.config['UPLOAD_FOLDER']
                if os.path.exists(upload_dir):
                    now = datetime.now()
                    for filename in os.listdir(upload_dir):
                        filepath = os.path.join(upload_dir, filename)
                        file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                        # Delete files older than 7 days
                        if (now - file_modified).days > 7:
                            try:
                                os.remove(filepath)
                                app.logger.info(f"Deleted old file: {filename}")
                            except Exception as e:
                                app.logger.error(f"Error deleting file {filename}: {e}")
        
        try:
            scheduler.start()
        except Exception as e:
            app.logger.warning(f"Scheduler issue: {e}")
    
    # Set up logging
    configure_logging(app)
    
    # Initialize rate limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Context processor to add current datetime to all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app, limiter)
    
    # Create initial admin user if not exists
    with app.app_context():
        db.create_all()
        create_admin_user(app)
    
    return app

def configure_logging(app):
    """
    Configure application logging based on environment.
    
    Args:
        app (Flask): Flask application instance
    """
    if not app.debug:
        # Configure production logging
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application started')

def create_admin_user(app):
    """
    Create admin user if not exists.
    
    Args:
        app (Flask): Flask application instance
    """
    if User.query.filter_by(username='admin').first() is None:
        password = 'admin123'
        admin = User(
            username='admin',
            email='admin@example.com',
            password=password,
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        app.logger.warning(f"Created admin user with password: {password}")
        app.logger.warning("PLEASE CHANGE THIS PASSWORD IMMEDIATELY AFTER FIRST LOGIN!")

def register_error_handlers(app):
    """
    Register error handlers for the application.
    
    Args:
        app (Flask): Flask application instance
    """
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Server error: {str(error)}")
        return render_template('errors/500.html'), 500

def register_routes(app, limiter):
    """
    Register all routes for the application.
    
    Args:
        app (Flask): Flask application instance
        limiter (Limiter): Rate limiter instance
    """
    # Authentication routes
    @app.route('/login', methods=['GET', 'POST'])
    @limiter.limit("5 per minute")
    def login():
        """Handle user login."""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.verify_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                app.logger.info(f"User {user.username} logged in")
                flash(f'Welcome back, {user.username}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                app.logger.warning(f"Failed login attempt for username: {form.username.data}")
                flash('Invalid username or password', 'danger')
        
        return render_template('login.html', title='Login', form=form)
    
    @app.route('/logout')
    def logout():
        """Handle user logout."""
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Handle user registration."""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            app.logger.info(f"New user registered: {user.username}")
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', title='Register', form=form)
    
    @app.route('/')
    @login_required
    def index():
        """Render application home page."""
        return render_template('index.html', title='Home')
    
    # Tracking tool routes
    @app.route('/tracking-tool', methods=['GET', 'POST'])
    @login_required
    def tracking_tool():
        """
        Handle tracking tool file uploads and display.
        GET: Display upload form
        POST: Process uploaded Excel file
        """
        form = UploadFileForm()
        
        if request.method == 'POST':
            return handle_file_upload(app)
        
        # For GET requests, just render the upload form
        return render_template('tracking_tool.html', form=form)
    
    @app.route('/tracking-data')
    @login_required
    def tracking_data():
        """Display tracking data from uploaded file."""
        # Get uploaded file ID from session
        file_id = session.get('uploaded_file_id')
        
        if not file_id:
            flash('No file selected', 'warning')
            return redirect(url_for('tracking_tool'))
        
        # Get the uploaded file record
        uploaded_file = UploadedFile.query.get(file_id)
        
        if not uploaded_file:
            flash('File not found', 'error')
            return redirect(url_for('tracking_tool'))
        
        # Get tracking data for this file
        tracking_items = TrackingData.query.filter_by(file_id=file_id).all()
        
        return render_template(
            'tracking_data.html', 
            tracking_items=tracking_items,
            uploaded_file=uploaded_file
        )
    
    @app.route('/uploads/<filename>')
    @login_required
    def uploaded_file(filename):
        """Serve uploaded file."""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/api/tracking-data', methods=['GET'])
    @login_required
    def api_tracking_data():
        """API endpoint to get tracking data."""
        file_id = request.args.get('file_id') or session.get('uploaded_file_id')
        
        if not file_id:
            return jsonify({'error': 'No file selected'}), 400
        
        # Get tracking data for this file
        tracking_items = TrackingData.query.filter_by(file_id=file_id).all()
        
        # Convert to JSON-serializable format
        data = [{
            'id': item.id,
            'placement_name': item.placement_name,
            'ad_name': item.ad_name,
            'creative_name': item.creative_name,
            'click_tag': item.click_tag_converted
        } for item in tracking_items]
        
        return jsonify({'data': data})

def handle_file_upload(app):
    """
    Process file upload from tracking tool form.
    
    Args:
        app (Flask): Flask application instance
        
    Returns:
        Response: Redirect response
    """
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    
    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    
    # Check if the file has an allowed extension
    allowed_extensions = app.config['ALLOWED_EXTENSIONS']
    if not allowed_file(file.filename, allowed_extensions):
        flash('Invalid file type. Please upload an Excel file (.xlsx, .xls)', 'error')
        return redirect(request.url)
    
    # Save the uploaded file
    result = save_uploaded_file(file, app.config['UPLOAD_FOLDER'], allowed_extensions)
    
    if result[0] is None:
        flash(result[1], 'error')
        return redirect(request.url)
    
    filepath, new_filename = result
    
    try:
        # Validate that the Excel file has the required columns
        validation_result = validate_excel_file(filepath)
        
        if not validation_result[0]:
            # If validation fails, delete the file and show error
            os.remove(filepath)
            flash(f'Invalid Excel file: {validation_result[1]}', 'error')
            return redirect(request.url)
        
        # Validation succeeded, get the dataframe
        df = validation_result[1]
        
        # Create record in the database for the uploaded file
        uploaded_file = UploadedFile(
            filename=new_filename,
            original_filename=file.filename,
            file_path=filepath,
            file_type='excel',
            uploaded_by=current_user.id
        )
        db.session.add(uploaded_file)
        db.session.commit()
        
        # Process the Excel file and extract tracking data
        tracking_data = process_excel_file(df, uploaded_file.id)
        
        # Save tracking data to database
        for data in tracking_data:
            tracking_item = TrackingData(**data)
            db.session.add(tracking_item)
        
        db.session.commit()
        app.logger.info(f"Successfully processed file {new_filename} with {len(tracking_data)} tracking items")
        
        # Store the uploaded file ID in the session
        session['uploaded_file_id'] = uploaded_file.id
        
        # Redirect to tracking data display
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('tracking_data'))
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        
        app.logger.error(f"Error processing file {new_filename}: {str(e)}")
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(request.url)

# Create the application instance 
# (Called by run.py or WSGI server)
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
