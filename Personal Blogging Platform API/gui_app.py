# gui_app.py
from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
import os
from app import create_app as create_api_app  # Import your API factory

def create_gui_app():
    # Create main GUI app
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # --------------------------
    # Register API blueprints
    # --------------------------
    api_app = create_api_app()
    for blueprint in api_app.blueprints.values():
        app.register_blueprint(blueprint, url_prefix='/api')

    # --------------------------
    # GUI Routes
    # --------------------------
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    #@app.route('/register')
    #def register_page():
        #return render_template('register.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/posts')
    def posts_page():
        return render_template('posts.html')

    @app.route('/posts/create')
    def create_post_page():
        return render_template('create_post.html')

    #@app.route('/posts/<slug>')
    #def view_post_page(slug):
       # return render_template('view_post.html', slug=slug)

    #@app.route('/profile')
    #def profile_page():
       # return render_template('profile.html')

    # --------------------------
    # Static files (optional)
    # --------------------------
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)

    # --------------------------
    # Health check
    # --------------------------
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'blog-gui'})

    return app


# --------------------------
# Run the app
# --------------------------
if __name__ == '__main__':
    app = create_gui_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
