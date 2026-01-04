"""Tags routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, validate, ValidationError
from slugify import slugify
from app import db
from app.models.tag import Tag
from app.middleware.rbac import require_role, authenticated_user

bp = Blueprint('tags', __name__)


# Validation schemas
class TagSchema(Schema):
    """Schema for tag create/update."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))


@bp.route('', methods=['GET'])
def list_tags():
    """Get all tags (public)."""
    tags = Tag.query.order_by(Tag.name).all()

    return jsonify({
        'tags': [tag.to_dict() for tag in tags]
    }), 200


@bp.route('/<int:id>', methods=['GET'])
def get_tag(id):
    """Get a single tag (public)."""
    tag = Tag.query.get_or_404(id)

    return jsonify({
        'tag': tag.to_dict()
    }), 200


@bp.route('', methods=['POST'])
@jwt_required()
@authenticated_user
def create_tag(current_user):
    """Create a tag (any authenticated user)."""
    try:
        schema = TagSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Generate slug
    base_slug = slugify(data['name'])
    slug = base_slug
    counter = 1
    while Tag.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    tag = Tag(
        name=data['name'],
        slug=slug
    )

    try:
        db.session.add(tag)
        db.session.commit()

        return jsonify({
            "message": "Tag created successfully",
            "tag": tag.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create tag"}), 500


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@require_role('admin', 'editor')
def update_tag(id, current_user):
    """Update a tag (admin/editor only)."""
    tag = Tag.query.get_or_404(id)

    try:
        schema = TagSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Update slug if name changed
    if data['name'] != tag.name:
        base_slug = slugify(data['name'])
        slug = base_slug
        counter = 1
        while Tag.query.filter(Tag.slug == slug, Tag.id != id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        tag.slug = slug

    tag.name = data['name']

    try:
        db.session.commit()
        return jsonify({
            "message": "Tag updated successfully",
            "tag": tag.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update tag"}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_tag(id, current_user):
    """Delete a tag (admin only)."""
    tag = Tag.query.get_or_404(id)

    try:
        db.session.delete(tag)
        db.session.commit()
        return jsonify({"message": "Tag deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete tag"}), 500
