"""Analytics model for tracking page views."""
from datetime import datetime
from app import db


class PageView(db.Model):
    """Page view tracking model."""

    __tablename__ = 'page_views'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Post relationship
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)

    # User relationship (nullable for anonymous views)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), index=True)

    # Request information
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.Text)

    # Timestamp
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    post = db.relationship('Post', backref=db.backref('views', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('page_views', lazy='dynamic'))

    def to_dict(self):
        """Convert page view to dictionary.

        Returns:
            dict: Page view data
        """
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None
        }

    def __repr__(self):
        return f'<PageView post_id={self.post_id} at {self.viewed_at}>'


class AutosaveDraft(db.Model):
    """Autosave draft model for editor autosave functionality."""

    __tablename__ = 'autosave_drafts'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Post relationship
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)

    # User relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Draft content
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255))

    # Timestamp
    saved_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    post = db.relationship('Post', backref=db.backref('autosave_drafts', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('autosaves', lazy='dynamic'))

    # Constraints: One autosave per post per user
    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='unique_post_user_autosave'),
    )

    def to_dict(self):
        """Convert autosave draft to dictionary.

        Returns:
            dict: Autosave draft data
        """
        return {
            'id': self.id,
            'post_id': self.post_id,
            'title': self.title,
            'content': self.content,
            'saved_at': self.saved_at.isoformat() if self.saved_at else None
        }

    def __repr__(self):
        return f'<AutosaveDraft post_id={self.post_id} user_id={self.user_id}>'
