"""Post model."""
from datetime import datetime
from app import db


class Post(db.Model):
    """Blog post model."""

    __tablename__ = 'posts'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Content fields
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    featured_image_url = db.Column(db.String(500))

    # Author relationship
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Status
    status = db.Column(db.String(20), default='draft', nullable=False, index=True)

    # Timestamps
    published_at = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Analytics
    view_count = db.Column(db.Integer, default=0, nullable=False)

    # Constraints
    __table_args__ = (
        db.CheckConstraint(status.in_(['draft', 'published']), name='check_post_status'),
    )

    def publish(self):
        """Publish the post."""
        if self.status != 'published':
            self.status = 'published'
            self.published_at = datetime.utcnow()

    def unpublish(self):
        """Revert post to draft status."""
        if self.status == 'published':
            self.status = 'draft'
            self.published_at = None

    def increment_view_count(self):
        """Increment the view count."""
        self.view_count += 1

    def to_dict(self, include_content=True):
        """Convert post to dictionary.

        Args:
            include_content: Whether to include full content (False for list views)

        Returns:
            dict: Post data
        """
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'featured_image_url': self.featured_image_url,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'display_name': self.author.display_name or self.author.username
            } if self.author else None,
            'status': self.status,
            'view_count': self.view_count,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'categories': [{'id': c.id, 'name': c.name, 'slug': c.slug} for c in self.categories],
            'tags': [{'id': t.id, 'name': t.name, 'slug': t.slug} for t in self.tags]
        }

        if include_content:
            data['content'] = self.content

        return data

    def __repr__(self):
        return f'<Post {self.title}>'
