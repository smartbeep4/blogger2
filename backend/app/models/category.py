"""Category model."""
from datetime import datetime
from app import db


# Association table for post-category many-to-many relationship
post_categories = db.Table('post_categories',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)


class Category(db.Model):
    """Category model for organizing posts."""

    __tablename__ = 'categories'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Category information
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    posts = db.relationship('Post', secondary=post_categories, backref=db.backref('categories', lazy='dynamic'))

    def to_dict(self):
        """Convert category to dictionary.

        Returns:
            dict: Category data
        """
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'post_count': len(self.posts),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Category {self.name}>'
