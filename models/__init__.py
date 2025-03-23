from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# Import models after db to avoid circular imports
from models.user import User
from models.tracking import UploadedFile, TrackingData 