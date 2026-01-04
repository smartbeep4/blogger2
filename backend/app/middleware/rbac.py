"""Role-Based Access Control (RBAC) middleware."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app.models.post import Post


def require_role(*roles):
    """Decorator to require specific user roles.

    Args:
        *roles: One or more role names (admin, editor, author)

    Usage:
        @require_role('admin')
        @require_role('admin', 'editor')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))

            if not user:
                return jsonify({"error": "User not found"}), 401

            if not user.is_active:
                return jsonify({"error": "Account is inactive"}), 403

            if user.role not in roles:
                return jsonify({
                    "error": "Insufficient permissions",
                    "required_roles": list(roles),
                    "your_role": user.role
                }), 403

            # Pass user to the route function
            return fn(*args, current_user=user, **kwargs)
        return wrapper
    return decorator


def can_edit_post(fn):
    """Decorator to check if user can edit a specific post.

    Allows:
    - Admin: Can edit any post
    - Editor: Can edit any post
    - Author: Can only edit their own posts

    Expects post_id or id in kwargs
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return jsonify({"error": "User not found"}), 401

        if not user.is_active:
            return jsonify({"error": "Account is inactive"}), 403

        # Get post_id from kwargs (could be 'id' or 'post_id')
        post_id = kwargs.get('post_id') or kwargs.get('id')

        if not post_id:
            return jsonify({"error": "Post ID not provided"}), 400

        post = Post.query.get(post_id)

        if not post:
            return jsonify({"error": "Post not found"}), 404

        # Admin and Editor can edit any post
        if user.role in ['admin', 'editor']:
            return fn(*args, current_user=user, post=post, **kwargs)

        # Author can only edit their own posts
        if user.role == 'author' and post.author_id == user.id:
            return fn(*args, current_user=user, post=post, **kwargs)

        return jsonify({
            "error": "You don't have permission to edit this post"
        }), 403

    return wrapper


def can_delete_post(fn):
    """Decorator to check if user can delete a specific post.

    Allows:
    - Admin: Can delete any post
    - Author: Can only delete their own posts

    Expects post_id or id in kwargs
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return jsonify({"error": "User not found"}), 401

        if not user.is_active:
            return jsonify({"error": "Account is inactive"}), 403

        # Get post_id from kwargs
        post_id = kwargs.get('post_id') or kwargs.get('id')

        if not post_id:
            return jsonify({"error": "Post ID not provided"}), 400

        post = Post.query.get(post_id)

        if not post:
            return jsonify({"error": "Post not found"}), 404

        # Admin can delete any post
        if user.role == 'admin':
            return fn(*args, current_user=user, post=post, **kwargs)

        # Author can only delete their own posts
        if post.author_id == user.id:
            return fn(*args, current_user=user, post=post, **kwargs)

        return jsonify({
            "error": "You don't have permission to delete this post"
        }), 403

    return wrapper


def can_publish_post(fn):
    """Decorator to check if user can publish a specific post.

    Allows:
    - Admin: Can publish any post
    - Editor: Can publish any post
    - Author: Can only publish their own posts

    Expects post_id or id in kwargs
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return jsonify({"error": "User not found"}), 401

        if not user.is_active:
            return jsonify({"error": "Account is inactive"}), 403

        # Get post_id from kwargs
        post_id = kwargs.get('post_id') or kwargs.get('id')

        if not post_id:
            return jsonify({"error": "Post ID not provided"}), 400

        post = Post.query.get(post_id)

        if not post:
            return jsonify({"error": "Post not found"}), 404

        # Admin and Editor can publish any post
        if user.role in ['admin', 'editor']:
            return fn(*args, current_user=user, post=post, **kwargs)

        # Author can only publish their own posts
        if user.role == 'author' and post.author_id == user.id:
            return fn(*args, current_user=user, post=post, **kwargs)

        return jsonify({
            "error": "You don't have permission to publish this post"
        }), 403

    return wrapper


def authenticated_user(fn):
    """Decorator to get the current authenticated user.

    Simpler than require_role when you just need the user object.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return jsonify({"error": "User not found"}), 401

        if not user.is_active:
            return jsonify({"error": "Account is inactive"}), 403

        return fn(*args, current_user=user, **kwargs)
    return wrapper
