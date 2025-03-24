from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def create_default_user(cls):
        """Create default admin user if no users exist"""
        if not cls.query.first():
            default_user = cls(username='admin')
            default_user.password = 'admin123'
            db.session.add(default_user)
            db.session.commit()
            return default_user
        return None

class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('uploads', lazy='dynamic'))
    
    def __repr__(self):
        return f'<UploadedFile {self.original_filename}>'

class TrackingData(db.Model):
    __tablename__ = 'tracking_data'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_files.id'))
    placement_name = db.Column(db.String(255), nullable=True)
    ad_name = db.Column(db.String(255), nullable=True)
    creative_name = db.Column(db.String(255), nullable=True)
    imp_tag = db.Column(db.Text, nullable=True)
    click_tag = db.Column(db.Text, nullable=True)
    third_party_tracking = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    file = db.relationship('UploadedFile', backref=db.backref('tracking_data', lazy='dynamic'))
    
    def __repr__(self):
        return f'<TrackingData {self.id}>'
