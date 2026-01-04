"""Categories routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, validate, ValidationError
from slugify import slugify
from app import db
from app.models.category import Category
from app.middleware.rbac import require_role, authenticated_user

bp = Blueprint('categories', __name__)


# Validation schemas
class CategorySchema(Schema):
    """Schema for category create/update."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str()


@bp.route('', methods=['GET'])
def list_categories():
    """Get all categories (public)."""
    categories = Category.query.order_by(Category.name).all()

    return jsonify({
        'categories': [category.to_dict() for category in categories]
    }), 200


@bp.route('/<int:id>', methods=['GET'])
def get_category(id):
    """Get a single category (public)."""
    category = Category.query.get_or_404(id)

    return jsonify({
        'category': category.to_dict()
    }), 200


@bp.route('', methods=['POST'])
@jwt_required()
@authenticated_user
def create_category(current_user):
    """Create a category (any authenticated user)."""
    try:
        schema = CategorySchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Generate slug
    base_slug = slugify(data['name'])
    slug = base_slug
    counter = 1
    while Category.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    category = Category(
        name=data['name'],
        slug=slug,
        description=data.get('description')
    )

    try:
        db.session.add(category)
        db.session.commit()

        return jsonify({
            "message": "Category created successfully",
            "category": category.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create category"}), 500


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@require_role('admin', 'editor')
def update_category(id, current_user):
    """Update a category (admin/editor only)."""
    category = Category.query.get_or_404(id)

    try:
        schema = CategorySchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Update slug if name changed
    if data['name'] != category.name:
        base_slug = slugify(data['name'])
        slug = base_slug
        counter = 1
        while Category.query.filter(Category.slug == slug, Category.id != id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        category.slug = slug

    category.name = data['name']
    if 'description' in data:
        category.description = data['description']

    try:
        db.session.commit()
        return jsonify({
            "message": "Category updated successfully",
            "category": category.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update category"}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_category(id, current_user):
    """Delete a category (admin only)."""
    category = Category.query.get_or_404(id)

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete category"}), 500
