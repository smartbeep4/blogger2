"""User model."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """User model with authentication and role-based access."""

    __tablename__ = 'users'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Authentication fields
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Role-based access control
    role = db.Column(db.String(20), nullable=False, default='author', index=True)

    # Profile fields
    display_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    media = db.relationship('Media', backref='uploader', lazy='dynamic')

    # Constraints
    __table_args__ = (
        db.CheckConstraint(role.in_(['admin', 'editor', 'author']), name='check_user_role'),
    )

    def set_password(self, password):
        """Hash and set the user's password.

        Args:
            password: Plain text password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Check if the provided password matches the hash.

        Args:
            password: Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def has_role(self, *roles):
        """Check if user has one of the specified roles.

        Args:
            *roles: One or more role names

        Returns:
            bool: True if user has any of the specified roles
        """
        return self.role in roles

    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin'

    def is_editor(self):
        """Check if user is an editor or admin."""
        return self.role in ['admin', 'editor']

    def is_author(self):
        """Check if user is an author (or higher)."""
        return self.role in ['admin', 'editor', 'author']

    def to_dict(self, include_email=False):
        """Convert user to dictionary.

        Args:
            include_email: Whether to include email (only for self/admin)

        Returns:
            dict: User data
        """
        data = {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name or self.username,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

        if include_email:
            data['email'] = self.email
            data['last_login'] = self.last_login.isoformat() if self.last_login else None

        return data

    def __repr__(self):
        return f'<User {self.username}>'
