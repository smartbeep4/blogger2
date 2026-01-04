"""Tag model."""
from datetime import datetime
from app import db


# Association table for post-tag many-to-many relationship
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class Tag(db.Model):
    """Tag model for labeling posts."""

    __tablename__ = 'tags'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Tag information
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    posts = db.relationship('Post', secondary=post_tags, backref=db.backref('tags', lazy='dynamic'))

    def to_dict(self):
        """Convert tag to dictionary.

        Returns:
            dict: Tag data
        """
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'post_count': len(self.posts),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Tag {self.name}>'
