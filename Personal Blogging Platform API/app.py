from flask import Flask, jsonify
from config import Config
from models import db
from auth import jwt
from routes.users import users_bp
from routes.posts import posts_bp
from routes.comments import comments_bp
from routes.categories import categories_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    app.register_blueprint(comments_bp, url_prefix='/api/comments')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Resource not found',
            'code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'status': 'error',
            'message': 'Method not allowed',
            'code': 'METHOD_NOT_ALLOWED'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'status': 'success',
            'message': 'Personal Blogging Platform API',
            'version': '1.0.0',
            'endpoints': {
                'documentation': '/api/docs',
                'authentication': '/api/users',
                'posts': '/api/posts',
                'comments': '/api/comments',
                'categories': '/api/categories'
            }
        })
    
    # Health check
    @app.route('/api/health')
    def health_check():
        from datetime import datetime
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except:
            db_status = 'disconnected'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': db_status,
            'version': '1.0.0'
        })
    
    # API Documentation
    @app.route('/api/docs')
    def api_docs():
        return jsonify({
            'status': 'success',
            'documentation': {
                'Authentication': {
                    'POST /api/users/register': 'Register new user',
                    'POST /api/users/login': 'Login user',
                    'POST /api/users/refresh': 'Refresh access token',
                    'GET /api/users/profile': 'Get current user profile (JWT required)',
                    'PUT /api/users/profile': 'Update user profile (JWT required)',
                    'GET /api/users/<username>': 'Get public user profile'
                },
                'Posts': {
                    'GET /api/posts/': 'Get all published posts',
                    'GET /api/posts/<slug>': 'Get single post',
                    'POST /api/posts/': 'Create new post (JWT required)',
                    'PUT /api/posts/<id>': 'Update post (JWT required)',
                    'DELETE /api/posts/<id>': 'Delete post (JWT required)',
                    'POST /api/posts/<id>/like': 'Like/unlike post (JWT required)',
                    'GET /api/posts/drafts': 'Get user drafts (JWT required)'
                },
                'Comments': {
                    'GET /api/comments/post/<post_id>': 'Get post comments',
                    'POST /api/comments/': 'Create comment (JWT required)',
                    'PUT /api/comments/<id>': 'Update comment (JWT required)',
                    'DELETE /api/comments/<id>': 'Delete comment (JWT required)'
                },
                'Categories': {
                    'GET /api/categories/': 'Get all categories',
                    'GET /api/categories/<slug>': 'Get single category',
                    'POST /api/categories/': 'Create category (Admin JWT required)',
                    'PUT /api/categories/<id>': 'Update category (Admin JWT required)',
                    'DELETE /api/categories/<id>': 'Delete category (Admin JWT required)',
                    'GET /api/categories/<slug>/posts': 'Get category posts'
                }
            },
            'query_parameters': {
                'pagination': '?page=1&per_page=10',
                'sorting': '?sort_by=created_at&sort_order=desc',
                'filtering': '?category=tech&tag=python&search=flask&featured=true'
            }
        })
    
    return app

def init_database():
    """Initialize database with sample data"""
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        print("Database tables created!")
        
        # Create admin user if not exists
        from models import User
        admin = User.query.filter_by(email='admin@blog.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@blog.com',
                password='adminadmin',
                bio='System Administrator',
                is_admin=True
            )
            db.session.add(admin)
        
        # Create default categories
        from models import Category
        default_categories = [
            {'name': 'Technology', 'slug': 'technology', 'description': 'Tech articles'},
            {'name': 'Lifestyle', 'slug': 'lifestyle', 'description': 'Lifestyle stories'},
            {'name': 'Travel', 'slug': 'travel', 'description': 'Travel guides'},
        ]
        
        for cat_data in default_categories:
            if not Category.query.filter_by(slug=cat_data['slug']).first():
                category = Category(**cat_data)
                db.session.add(category)
        
        db.session.commit()
        print("Database initialized with sample data!")

if __name__ == '__main__':
    # Check if database exists, initialize if not
    db_path = Config().SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
    if not os.path.exists(db_path):
        init_database()
    
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)