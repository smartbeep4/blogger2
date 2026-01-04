"""Flask application factory."""
import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def create_app(config_name=None):
    """Create and configure the Flask application.

    Args:
        config_name: Configuration to use (development, testing, production)

    Returns:
        Configured Flask application
    """
    app = Flask(__name__, static_folder='../../frontend/dist', static_url_path='')

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    from app.config import config
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "supports_credentials": True
        }
    })

    # Register blueprints
    from app.routes import auth, posts, users, media, categories, tags, analytics

    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(posts.bp, url_prefix='/api/posts')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(media.bp, url_prefix='/api/media')
    app.register_blueprint(categories.bp, url_prefix='/api/categories')
    app.register_blueprint(tags.bp, url_prefix='/api/tags')
    app.register_blueprint(analytics.bp, url_prefix='/api/analytics')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200

    # Serve React frontend for all non-API routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            # Return index.html for client-side routing
            return send_from_directory(app.static_folder, 'index.html')

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        if app.config['DEBUG']:
            return jsonify({"error": "Not found", "message": str(error)}), 404
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if app.config['DEBUG']:
            return jsonify({"error": "Internal server error", "message": str(error)}), 500
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    return app
