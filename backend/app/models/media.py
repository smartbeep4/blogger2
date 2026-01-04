"""Media model."""
from datetime import datetime
from app import db


class Media(db.Model):
    """Media file metadata model."""

    __tablename__ = 'media'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # File metadata
    filename = db.Column(db.String(255), nullable=False)
    imagekit_file_id = db.Column(db.String(255), unique=True, nullable=False)
    imagekit_url = db.Column(db.String(500), nullable=False)

    # File properties
    file_type = db.Column(db.String(50))  # image/jpeg, video/mp4, etc.
    file_size = db.Column(db.Integer)  # in bytes
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

    # Uploader relationship
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), index=True)

    # Accessibility
    alt_text = db.Column(db.String(255))

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Media {self.filename}>'
