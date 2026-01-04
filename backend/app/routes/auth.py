"""Authentication routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from marshmallow import Schema, fields, validate, ValidationError
from app import db, limiter
from app.models.user import User

bp = Blueprint('auth', __name__)


# Validation schemas
class RegisterSchema(Schema):
    """Schema for user registration."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    display_name = fields.Str(validate=validate.Length(max=100))


class LoginSchema(Schema):
    """Schema for user login."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class ProfileUpdateSchema(Schema):
    """Schema for profile updates."""
    display_name = fields.Str(validate=validate.Length(max=100))
    bio = fields.Str()
    avatar_url = fields.Url()


class PasswordChangeSchema(Schema):
    """Schema for password change."""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))


@bp.route('/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """Register a new user.

    Returns:
        JSON response with user data and tokens
    """
    try:
        # Validate request data
        schema = RegisterSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already taken"}), 400

    # Create new user
    try:
        user = User(
            username=data['username'],
            email=data['email'],
            display_name=data.get('display_name'),
            role='author'  # Default role
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Create tokens (convert user.id to string for JWT)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict(include_email=True),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create user"}), 500


@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Login a user.

    Returns:
        JSON response with user data and tokens
    """
    try:
        # Validate request data
        schema = LoginSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Find user by email
    user = User.query.filter_by(email=data['email']).first()

    # Check credentials
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    # Check if user is active
    if not user.is_active:
        return jsonify({"error": "Account is inactive"}), 403

    # Update last login
    user.update_last_login()

    # Create tokens (convert user.id to string for JWT)
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "user": user.to_dict(include_email=True),
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token.

    Returns:
        JSON response with new access token
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_active:
        return jsonify({"error": "User not found or inactive"}), 401

    access_token = create_access_token(identity=user_id)

    return jsonify({
        "access_token": access_token
    }), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information.

    Returns:
        JSON response with user data
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user": user.to_dict(include_email=True)
    }), 200


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile.

    Returns:
        JSON response with updated user data
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        # Validate request data
        schema = ProfileUpdateSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Update profile fields
    if 'display_name' in data:
        user.display_name = data['display_name']
    if 'bio' in data:
        user.bio = data['bio']
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']

    try:
        db.session.commit()
        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict(include_email=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile"}), 500


@bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password.

    Returns:
        JSON response confirming password change
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        # Validate request data
        schema = PasswordChangeSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Verify current password
    if not user.check_password(data['current_password']):
        return jsonify({"error": "Current password is incorrect"}), 400

    # Set new password
    try:
        user.set_password(data['new_password'])
        db.session.commit()

        return jsonify({
            "message": "Password changed successfully"
        }), 200
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to change password"}), 500
