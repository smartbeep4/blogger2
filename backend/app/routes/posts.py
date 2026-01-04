"""Posts routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from slugify import slugify
from datetime import datetime
from app import db, limiter
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.analytics import AutosaveDraft, PageView
from app.middleware.rbac import authenticated_user, can_edit_post, can_delete_post, can_publish_post

bp = Blueprint('posts', __name__)


# Validation schemas
class PostCreateSchema(Schema):
    """Schema for creating a post."""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    excerpt = fields.Str(validate=validate.Length(max=500))
    featured_image_url = fields.Url()
    category_ids = fields.List(fields.Int())
    tag_ids = fields.List(fields.Int())
    status = fields.Str(validate=validate.OneOf(['draft', 'published']))


class PostUpdateSchema(Schema):
    """Schema for updating a post."""
    title = fields.Str(validate=validate.Length(min=1, max=255))
    content = fields.Str(validate=validate.Length(min=1))
    excerpt = fields.Str(validate=validate.Length(max=500))
    featured_image_url = fields.Url()
    category_ids = fields.List(fields.Int())
    tag_ids = fields.List(fields.Int())
    status = fields.Str(validate=validate.OneOf(['draft', 'published']))


class AutosaveSchema(Schema):
    """Schema for autosaving post content."""
    title = fields.Str(validate=validate.Length(max=255))
    content = fields.Str(required=True)


@bp.route('', methods=['GET'])
def list_posts():
    """Get list of posts (public for published, authenticated for drafts).

    Query params:
        - status: draft or published (default: published for public, all for authenticated)
        - category: category slug
        - tag: tag slug
        - author: author username
        - search: search query
        - page: page number (default: 1)
        - per_page: posts per page (default: 10)
    """
    # Check if user is authenticated
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        user_id = None

    # Build query
    query = Post.query

    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    elif not user_id:
        # Public users only see published posts
        query = query.filter_by(status='published')

    # Filter by category
    category_slug = request.args.get('category')
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = query.filter(Post.categories.contains(category))

    # Filter by tag
    tag_slug = request.args.get('tag')
    if tag_slug:
        tag = Tag.query.filter_by(slug=tag_slug).first()
        if tag:
            query = query.filter(Post.tags.contains(tag))

    # Filter by author
    author_username = request.args.get('author')
    if author_username:
        from app.models.user import User
        author = User.query.filter_by(username=author_username).first()
        if author:
            query = query.filter_by(author_id=author.id)

    # Search
    search_query = request.args.get('search')
    if search_query:
        query = query.filter(
            db.or_(
                Post.title.ilike(f'%{search_query}%'),
                Post.content.ilike(f'%{search_query}%')
            )
        )

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 100)  # Max 100 per page

    # Order by published date (or created date for drafts)
    query = query.order_by(Post.published_at.desc().nullslast(), Post.created_at.desc())

    # Execute pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'posts': [post.to_dict(include_content=False) for post in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    }), 200


@bp.route('/<slug>', methods=['GET'])
def get_post(slug):
    """Get a single post by slug (public for published, authenticated for drafts)."""
    post = Post.query.filter_by(slug=slug).first_or_404()

    # Check if user can view this post
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        user_id = None

    # Public can only see published posts
    if post.status == 'draft' and not user_id:
        return jsonify({"error": "Post not found"}), 404

    # Track page view (only for published posts)
    if post.status == 'published':
        view = PageView(
            post_id=post.id,
            user_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(view)
        post.increment_view_count()
        db.session.commit()

    return jsonify({
        'post': post.to_dict(include_content=True)
    }), 200


@bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
@authenticated_user
def create_post(current_user):
    """Create a new post (authenticated users only)."""
    try:
        schema = PostCreateSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Generate unique slug
    base_slug = slugify(data['title'])
    slug = base_slug
    counter = 1
    while Post.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create post
    post = Post(
        title=data['title'],
        slug=slug,
        content=data['content'],
        excerpt=data.get('excerpt'),
        featured_image_url=data.get('featured_image_url'),
        author_id=current_user.id,
        status=data.get('status', 'draft')
    )

    # Set published_at if status is published
    if post.status == 'published':
        post.published_at = datetime.utcnow()

    # Add categories
    if 'category_ids' in data:
        categories = Category.query.filter(Category.id.in_(data['category_ids'])).all()
        post.categories.extend(categories)

    # Add tags
    if 'tag_ids' in data:
        tags = Tag.query.filter(Tag.id.in_(data['tag_ids'])).all()
        post.tags.extend(tags)

    try:
        db.session.add(post)
        db.session.commit()

        return jsonify({
            "message": "Post created successfully",
            "post": post.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create post"}), 500


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@can_edit_post
def update_post(id, current_user, post):
    """Update a post (owner, editor, or admin)."""
    try:
        schema = PostUpdateSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Update fields
    if 'title' in data:
        # Regenerate slug if title changed
        if data['title'] != post.title:
            base_slug = slugify(data['title'])
            slug = base_slug
            counter = 1
            while Post.query.filter(Post.slug == slug, Post.id != post.id).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            post.slug = slug
        post.title = data['title']

    if 'content' in data:
        post.content = data['content']

    if 'excerpt' in data:
        post.excerpt = data['excerpt']

    if 'featured_image_url' in data:
        post.featured_image_url = data['featured_image_url']

    if 'status' in data:
        old_status = post.status
        post.status = data['status']
        # Set published_at when publishing
        if old_status == 'draft' and data['status'] == 'published':
            post.published_at = datetime.utcnow()

    # Update categories
    if 'category_ids' in data:
        post.categories.clear()
        categories = Category.query.filter(Category.id.in_(data['category_ids'])).all()
        post.categories.extend(categories)

    # Update tags
    if 'tag_ids' in data:
        post.tags.clear()
        tags = Tag.query.filter(Tag.id.in_(data['tag_ids'])).all()
        post.tags.extend(tags)

    try:
        db.session.commit()
        return jsonify({
            "message": "Post updated successfully",
            "post": post.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update post"}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@can_delete_post
def delete_post(id, current_user, post):
    """Delete a post (owner or admin)."""
    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Post deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete post"}), 500


@bp.route('/<int:id>/publish', methods=['POST'])
@jwt_required()
@can_publish_post
def publish_post(id, current_user, post):
    """Publish a draft post (owner, editor, or admin)."""
    if post.status == 'published':
        return jsonify({"message": "Post is already published"}), 200

    post.publish()

    try:
        db.session.commit()
        return jsonify({
            "message": "Post published successfully",
            "post": post.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to publish post"}), 500


@bp.route('/<int:id>/autosave', methods=['POST'])
@jwt_required()
@authenticated_user
def autosave_post(id, current_user):
    """Autosave post content (for editor)."""
    post = Post.query.get_or_404(id)

    # Check if user can edit this post
    if not (current_user.role in ['admin', 'editor'] or post.author_id == current_user.id):
        return jsonify({"error": "You don't have permission to edit this post"}), 403

    try:
        schema = AutosaveSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Find or create autosave draft
    autosave = AutosaveDraft.query.filter_by(
        post_id=id,
        user_id=current_user.id
    ).first()

    if autosave:
        autosave.content = data['content']
        if 'title' in data:
            autosave.title = data['title']
        autosave.saved_at = datetime.utcnow()
    else:
        autosave = AutosaveDraft(
            post_id=id,
            user_id=current_user.id,
            content=data['content'],
            title=data.get('title')
        )
        db.session.add(autosave)

    try:
        db.session.commit()
        return jsonify({
            "message": "Autosaved successfully",
            "autosave": autosave.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to autosave"}), 500


@bp.route('/<int:id>/autosave', methods=['GET'])
@jwt_required()
@authenticated_user
def get_autosave(id, current_user):
    """Get autosaved content for a post."""
    post = Post.query.get_or_404(id)

    # Check if user can edit this post
    if not (current_user.role in ['admin', 'editor'] or post.author_id == current_user.id):
        return jsonify({"error": "You don't have permission to edit this post"}), 403

    autosave = AutosaveDraft.query.filter_by(
        post_id=id,
        user_id=current_user.id
    ).first()

    if not autosave:
        return jsonify({"message": "No autosave found"}), 404

    return jsonify({
        "autosave": autosave.to_dict()
    }), 200
