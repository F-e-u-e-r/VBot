"""
Database models for tracking system.
This module contains models related to file uploads and tracking data.
"""
from datetime import datetime, timedelta
from models import db

class UploadedFile(db.Model):
    """
    Model for uploaded files.
    
    Attributes:
        id (int): Primary key
        filename (str): Secure filename stored on disk
        original_filename (str): Original filename provided by user
        file_path (str): Full path to the file on server
        file_size (int): File size in bytes
        file_type (str): File type (extension or MIME)
        uploaded_by (int): Foreign key to user who uploaded the file
        uploaded_at (datetime): Timestamp when file was uploaded
        user (relationship): Relationship to User model
    """
    __tablename__ = 'uploaded_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # File size in bytes
    file_type = db.Column(db.String(50))  # MIME type or extension
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('uploads', lazy='dynamic'))
    
    def __repr__(self):
        """String representation of the object."""
        return f'<UploadedFile {self.original_filename}>'
    
    def is_expired(self, retention_hours=24):
        """
        Check if file has exceeded retention policy.
        
        Args:
            retention_hours (int): Number of hours before expiration
            
        Returns:
            bool: True if file is expired, False otherwise
        """
        if not self.uploaded_at:
            return True
        
        expiration_time = self.uploaded_at + timedelta(hours=retention_hours)
        return datetime.utcnow() > expiration_time
    
    @classmethod
    def get_expired_files(cls, retention_hours=24):
        """
        Get all files that have exceeded retention period.
        
        Args:
            retention_hours (int): Number of hours before expiration
            
        Returns:
            list: List of UploadedFile objects that have expired
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=retention_hours)
        return cls.query.filter(cls.uploaded_at < cutoff_time).all()
    
    def get_human_readable_size(self):
        """
        Convert file size to human-readable format.
        
        Returns:
            str: Human-readable file size (e.g., '2.5 MB')
        """
        if not self.file_size:
            return "Unknown"
            
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024 or unit == 'TB':
                break
            size /= 1024
        return f"{size:.1f} {unit}"
    
    def get_file_extension(self):
        """
        Get file extension from filename.
        
        Returns:
            str: File extension without the dot
        """
        if '.' in self.filename:
            return self.filename.rsplit('.', 1)[1].lower()
        return ''
    
    def to_dict(self):
        """
        Convert model to dictionary for API responses.
        
        Returns:
            dict: Dictionary representation of the model
        """
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.get_human_readable_size(),
            'file_type': self.file_type,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'is_expired': self.is_expired()
        }

class TrackingData(db.Model):
    """
    Model for tracking data extracted from uploaded files.
    
    Attributes:
        id (int): Primary key
        file_id (int): Foreign key to UploadedFile
        placement_name (str): Name of the placement
        ad_name (str): Name of the advertisement
        creative_name (str): Name of the creative
        imp_tag (text): Original impression tag
        click_tag (text): Original click tag
        third_party_tracking (text): Original third-party tracking
        imp_tag_converted (text): Processed impression tag
        click_tag_converted (text): Processed click tag
        third_party_converted (text): Processed third-party tracking
        campaign_id (str): Optional campaign identifier
        start_date (date): Campaign start date
        end_date (date): Campaign end date
        created_at (datetime): Timestamp when record was created
        file (relationship): Relationship to UploadedFile model
    """
    __tablename__ = 'tracking_data'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_files.id', ondelete='CASCADE'), nullable=False)
    placement_name = db.Column(db.String(255))
    ad_name = db.Column(db.String(255))
    creative_name = db.Column(db.String(255))
    imp_tag = db.Column(db.Text)
    click_tag = db.Column(db.Text)
    third_party_tracking = db.Column(db.Text)
    imp_tag_converted = db.Column(db.Text)
    click_tag_converted = db.Column(db.Text)
    third_party_converted = db.Column(db.Text)
    campaign_id = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    file = db.relationship('UploadedFile', backref=db.backref('tracking_data', cascade='all, delete-orphan'))
    
    def __repr__(self):
        """String representation of the object."""
        return f'<TrackingData {self.id} for file {self.file_id}>'
    
    def to_dict(self):
        """
        Convert model to dictionary for API responses.
        
        Returns:
            dict: Dictionary representation of the model
        """
        return {
            'id': self.id,
            'placement_name': self.placement_name,
            'ad_name': self.ad_name,
            'creative_name': self.creative_name,
            'click_tag_converted': self.click_tag_converted,
            'imp_tag_converted': self.imp_tag_converted,
            'third_party_converted': self.third_party_converted,
            'campaign_id': self.campaign_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }
    
    def has_impression_tag(self):
        """
        Check if this tracking item has an impression tag.
        
        Returns:
            bool: True if impression tag exists, False otherwise
        """
        return bool(self.imp_tag_converted and self.imp_tag_converted.strip())
    
    def has_click_tag(self):
        """
        Check if this tracking item has a click tag.
        
        Returns:
            bool: True if click tag exists, False otherwise
        """
        return bool(self.click_tag_converted and self.click_tag_converted.strip())
    
    def has_third_party(self):
        """
        Check if this tracking item has third-party tracking.
        
        Returns:
            bool: True if third-party tracking exists, False otherwise
        """
        return bool(self.third_party_converted and self.third_party_converted.strip()) 