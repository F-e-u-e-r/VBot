"""
Tracking data service.
This module handles business logic for tracking data operations.
"""
import os
import logging
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from models import db
from models.tracking import UploadedFile, TrackingData
from utils import allowed_file, save_uploaded_file, validate_excel_file, process_excel_file

# Configure logger
logger = logging.getLogger(__name__)

class TrackingService:
    """
    Service class for tracking data operations.
    Handles file uploads, validation, processing, and database operations.
    """
    
    @staticmethod
    def upload_file(file, user_id):
        """
        Upload and process an Excel file.
        
        Args:
            file: The uploaded file object
            user_id: ID of the user uploading the file
            
        Returns:
            tuple: (success, result) where:
                - If successful: (True, file_id)
                - If failed: (False, error_message)
        """
        if not file or file.filename == '':
            return False, "No file selected"
        
        # Check file extension
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        if not allowed_file(file.filename, allowed_extensions):
            return False, "Invalid file type. Please upload an Excel file (.xlsx, .xls)"
        
        # Save the uploaded file
        result = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'], allowed_extensions)
        
        if result[0] is None:
            return False, result[1]
        
        filepath, new_filename = result
        
        try:
            # Validate Excel file
            validation_result = validate_excel_file(filepath)
            
            if not validation_result[0]:
                # If validation fails, delete the file and return error
                os.remove(filepath)
                return False, f"Invalid Excel file: {validation_result[1]}"
            
            # Create database record for uploaded file
            file_size = os.path.getsize(filepath)
            file_type = file.filename.rsplit('.', 1)[1].lower()
            
            uploaded_file = UploadedFile(
                filename=new_filename,
                original_filename=file.filename,
                file_path=filepath,
                file_size=file_size,
                file_type=file_type,
                uploaded_by=user_id
            )
            db.session.add(uploaded_file)
            db.session.commit()
            
            # Process Excel data
            df = validation_result[1]
            tracking_data = process_excel_file(df, uploaded_file.id)
            
            # Save tracking data to database
            for data in tracking_data:
                tracking_item = TrackingData(**data)
                db.session.add(tracking_item)
            
            db.session.commit()
            
            logger.info(f"Successfully processed file {new_filename} with {len(tracking_data)} tracking items")
            return True, uploaded_file.id
            
        except Exception as e:
            logger.exception(f"Error processing file {new_filename}: {str(e)}")
            
            # Clean up on error
            if os.path.exists(filepath):
                os.remove(filepath)
                
            # Clean up database records if they were created
            try:
                if 'uploaded_file' in locals() and uploaded_file.id:
                    TrackingData.query.filter_by(file_id=uploaded_file.id).delete()
                    db.session.delete(uploaded_file)
                    db.session.commit()
            except Exception as db_error:
                logger.error(f"Error cleaning up database records: {str(db_error)}")
                db.session.rollback()
                
            return False, f"Error processing file: {str(e)}"
    
    @staticmethod
    def get_tracking_data(file_id):
        """
        Get tracking data for a specific file.
        
        Args:
            file_id: ID of the uploaded file
            
        Returns:
            tuple: (success, result) where:
                - If successful: (True, (file_info, tracking_items))
                - If failed: (False, error_message)
        """
        if not file_id:
            return False, "No file selected"
        
        # Get the uploaded file record
        uploaded_file = UploadedFile.query.get(file_id)
        
        if not uploaded_file:
            return False, "File not found"
        
        # Get tracking data for this file
        tracking_items = TrackingData.query.filter_by(file_id=file_id).all()
        
        if not tracking_items:
            return False, "No tracking data found for this file"
        
        return True, (uploaded_file, tracking_items)
    
    @staticmethod
    def get_file_info(file_id):
        """
        Get information about an uploaded file.
        
        Args:
            file_id: ID of the uploaded file
            
        Returns:
            tuple: (success, result) where:
                - If successful: (True, file_info)
                - If failed: (False, error_message)
        """
        if not file_id:
            return False, "No file selected"
        
        uploaded_file = UploadedFile.query.get(file_id)
        
        if not uploaded_file:
            return False, "File not found"
        
        return True, uploaded_file
    
    @staticmethod
    def delete_file(file_id, user_id=None):
        """
        Delete an uploaded file and its tracking data.
        
        Args:
            file_id: ID of the uploaded file
            user_id: ID of the user requesting deletion (for permission check)
            
        Returns:
            tuple: (success, result) where:
                - If successful: (True, message)
                - If failed: (False, error_message)
        """
        if not file_id:
            return False, "No file selected"
        
        # Get the uploaded file record
        uploaded_file = UploadedFile.query.get(file_id)
        
        if not uploaded_file:
            return False, "File not found"
        
        # Check if the user has permission to delete this file
        if user_id and uploaded_file.uploaded_by != user_id:
            # Check if user is an admin
            from models.user import User
            user = User.query.get(user_id)
            
            if not user or not user.is_admin:
                return False, "You don't have permission to delete this file"
        
        try:
            # Delete the physical file if it exists
            if os.path.exists(uploaded_file.file_path):
                os.remove(uploaded_file.file_path)
                logger.info(f"Deleted physical file: {uploaded_file.file_path}")
            
            # Delete tracking data and file record
            TrackingData.query.filter_by(file_id=file_id).delete()
            db.session.delete(uploaded_file)
            db.session.commit()
            
            return True, "File deleted successfully"
            
        except Exception as e:
            logger.exception(f"Error deleting file {file_id}: {str(e)}")
            db.session.rollback()
            return False, f"Error deleting file: {str(e)}"
    
    @staticmethod
    def search_tracking_data(search_term, file_id=None):
        """
        Search tracking data based on a search term.
        
        Args:
            search_term: Search term to filter by
            file_id: Optional file ID to restrict search
            
        Returns:
            list: Matching tracking data items
        """
        if not search_term:
            # If no search term, return an empty list or all items based on file_id
            if file_id:
                return TrackingData.query.filter_by(file_id=file_id).all()
            return []
        
        # Convert search term to lowercase for case-insensitive search
        search_term = f"%{search_term.lower()}%"
        
        # Construct the base query
        query = TrackingData.query
        
        # Add file_id filter if provided
        if file_id:
            query = query.filter_by(file_id=file_id)
        
        # Add search filters for relevant fields
        results = query.filter(
            db.or_(
                db.func.lower(TrackingData.placement_name).like(search_term),
                db.func.lower(TrackingData.ad_name).like(search_term),
                db.func.lower(TrackingData.creative_name).like(search_term),
                db.func.lower(TrackingData.campaign_id).like(search_term)
            )
        ).all()
        
        return results 