from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Post, Category, Comment, Like
from utils.helpers import format_response, generate_slug
from datetime import datetime
import requests

views_bp = Blueprint('views', __name__)

def get_auth_headers():
    """Get authentication headers from session"""
    token = session.get('access_token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}

def api_request(method, endpoint, data=None, requires_auth=True):
    """Make API request to backend"""
    url = f'http://localhost:5000/api{endpoint}'
    headers = {'Content-Type': 'application/json'}
    
    if requires_auth:
        headers.update(get_auth_headers())
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=data)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return None
        
        return response.json() if response.content else {}
    except requests.exceptions.RequestException:
        return None

@views_bp.route('/')
def index():
    """Home page"""
    # Get featured posts
    featured_response = api_request('GET', '/posts/', {'featured': 'true', 'per_page': 3}, False)
    featured_posts = featured_response.get('data', []) if featured_response else []
    
    # Get recent posts
    recent_response = api_request('GET', '/posts/', {'per_page': 6}, False)
    recent_posts = recent_response.get('data', []) if recent_response else []
    
    # Get categories
    categories_response = api_request('GET', '/categories/', requires_auth=False)
    categories = categories_response.get('data', []) if categories_response else []
    
    return render_template('index.html', 
                         featured_posts=featured_posts,
                         recent_posts=recent_posts,
                         categories=categories,
                         user=session.get('user'))

@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        data = {
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        
        response = api_request('POST', '/users/login', data, False)
        
        if response and response.get('status') == 'success':
            # Store token and user info in session
            session['access_token'] = response['data']['tokens']['access_token']
            session['user'] = response['data']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('views.dashboard'))
        else:
            error_msg = response.get('message', 'Login failed') if response else 'Connection error'
            flash(error_msg, 'danger')
    
    return render_template('login.html')

@views_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""
    if request.method == 'POST':
        data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'bio': request.form.get('bio', '')
        }
        
        response = api_request('POST', '/users/register', data, False)
        
        if response and response.get('status') == 'success':
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('views.login'))
        else:
            error_msg = response.get('message', 'Registration failed') if response else 'Connection error'
            flash(error_msg, 'danger')
    
    return render_template('register.html')

@views_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('views.index'))

@views_bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('views.login'))
    
    # Get user's posts
    user_id = session['user']['id']
    posts_response = api_request('GET', f'/posts/?author_id={user_id}')
    posts = posts_response.get('data', []) if posts_response else []
    
    # Get user's drafts
    drafts_response = api_request('GET', '/posts/drafts')
    drafts = drafts_response.get('data', []) if drafts_response else []
    
    return render_template('dashboard.html', 
                         user=session['user'],
                         posts=posts,
                         drafts=drafts)

@views_bp.route('/posts')
def posts_list():
    """List all posts"""
    page = request.args.get('page', 1)
    category = request.args.get('category')
    tag = request.args.get('tag')
    search = request.args.get('search')
    
    params = {
        'page': page,
        'per_page': 9
    }
    
    if category:
        params['category'] = category
    if tag:
        params['tag'] = tag
    if search:
        params['search'] = search
    
    response = api_request('GET', '/posts/', params, False)
    
    posts = response.get('data', []) if response else []
    meta = response.get('meta', {}) if response else {}
    
    # Get categories for sidebar
    categories_response = api_request('GET', '/categories/', requires_auth=False)
    categories = categories_response.get('data', []) if categories_response else []
    
    return render_template('posts/list.html',
                         posts=posts,
                         categories=categories,
                         meta=meta,
                         current_category=category,
                         search_query=search,
                         user=session.get('user'))

@views_bp.route('/posts/<slug>')
def post_view(slug):
    """View single post"""
    response = api_request('GET', f'/posts/{slug}', requires_auth=False)
    
    if not response or response.get('status') != 'success':
        flash('Post not found', 'danger')
        return redirect(url_for('views.posts_list'))
    
    post = response['data']
    
    # Get comments for this post
    comments_response = api_request('GET', f'/comments/post/{post["id"]}', requires_auth=False)
    comments = comments_response.get('data', []) if comments_response else []
    
    # Get related posts (same category)
    related_response = api_request('GET', 
                                 f'/posts/?category={post["category"]["slug"]}&per_page=3', 
                                 requires_auth=False)
    related_posts = related_response.get('data', []) if related_response else []
    
    return render_template('posts/view.html',
                         post=post,
                         comments=comments,
                         related_posts=related_posts,
                         user=session.get('user'))

@views_bp.route('/posts/create', methods=['GET', 'POST'])
def post_create():
    """Create new post"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('views.login'))
    
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'content': request.form.get('content'),
            'excerpt': request.form.get('excerpt'),
            'category_id': request.form.get('category_id'),
            'tags': request.form.get('tags', '').split(','),
            'is_published': 'is_published' in request.form,
            'is_featured': 'is_featured' in request.form
        }
        
        response = api_request('POST', '/posts/', data)
        
        if response and response.get('status') == 'success':
            flash('Post created successfully!', 'success')
            return redirect(url_for('views.dashboard'))
        else:
            error_msg = response.get('message', 'Creation failed') if response else 'Connection error'
            flash(error_msg, 'danger')
    
    # Get categories for dropdown
    categories_response = api_request('GET', '/categories/', requires_auth=False)
    categories = categories_response.get('data', []) if categories_response else []
    
    return render_template('posts/create.html',
                         categories=categories,
                         user=session.get('user'))

@views_bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def post_edit(post_id):
    """Edit post"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('views.login'))
    
    # Get post data
    response = api_request('GET', f'/posts/{post_id}')
    
    if not response or response.get('status') != 'success':
        flash('Post not found', 'danger')
        return redirect(url_for('views.dashboard'))
    
    post = response['data']
    
    # Check ownership
    if post['author']['id'] != session['user']['id'] and not session['user'].get('is_admin'):
        flash('You can only edit your own posts', 'danger')
        return redirect(url_for('views.dashboard'))
    
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'content': request.form.get('content'),
            'excerpt': request.form.get('excerpt'),
            'category_id': request.form.get('category_id'),
            'tags': request.form.get('tags', '').split(','),
            'is_published': 'is_published' in request.form,
            'is_featured': 'is_featured' in request.form
        }
        
        response = api_request('PUT', f'/posts/{post_id}', data)
        
        if response and response.get('status') == 'success':
            flash('Post updated successfully!', 'success')
            return redirect(url_for('views.dashboard'))
        else:
            error_msg = response.get('message', 'Update failed') if response else 'Connection error'
            flash(error_msg, 'danger')
    
    # Get categories for dropdown
    categories_response = api_request('GET', '/categories/', requires_auth=False)
    categories = categories_response.get('data', []) if categories_response else []
    
    return render_template('posts/edit.html',
                         post=post,
                         categories=categories,
                         user=session.get('user'))

@views_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
def post_delete(post_id):
    """Delete post"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    response = api_request('DELETE', f'/posts/{post_id}')
    
    if response and response.get('status') == 'success':
        flash('Post deleted successfully!', 'success')
        return jsonify({'success': True}), 200
    else:
        error_msg = response.get('message', 'Deletion failed') if response else 'Connection error'
        return jsonify({'success': False, 'message': error_msg}), 400

@views_bp.route('/profile')
def profile():
    """User profile page"""
    if 'user' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('views.login'))
    
    return render_template('profile.html', user=session['user'])

@views_bp.route('/profile/update', methods=['POST'])
def profile_update():
    """Update user profile"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'bio': request.form.get('bio'),
        'profile_image': request.form.get('profile_image')
    }
    
    # Remove empty fields
    data = {k: v for k, v in data.items() if v is not None}
    
    if 'password' in request.form and request.form['password']:
        data['password'] = request.form['password']
    
    response = api_request('PUT', '/users/profile', data)
    
    if response and response.get('status') == 'success':
        # Update session
        session['user'] = response['data']
        flash('Profile updated successfully!', 'success')
        return jsonify({'success': True}), 200
    else:
        error_msg = response.get('message', 'Update failed') if response else 'Connection error'
        return jsonify({'success': False, 'message': error_msg}), 400

@views_bp.route('/comments/add', methods=['POST'])
def comment_add():
    """Add comment to post"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please login to comment'}), 401
    
    data = {
        'post_id': request.form.get('post_id'),
        'content': request.form.get('content'),
        'parent_id': request.form.get('parent_id')
    }
    
    response = api_request('POST', '/comments/', data)
    
    if response and response.get('status') == 'success':
        return jsonify({'success': True, 'comment': response['data']}), 200
    else:
        error_msg = response.get('message', 'Comment failed') if response else 'Connection error'
        return jsonify({'success': False, 'message': error_msg}), 400

@views_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def post_like(post_id):
    """Like/unlike a post"""
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Please login to like'}), 401
    
    response = api_request('POST', f'/posts/{post_id}/like')
    
    if response and response.get('status') == 'success':
        return jsonify({'success': True, 'data': response['data']}), 200
    else:
        error_msg = response.get('message', 'Action failed') if response else 'Connection error'
        return jsonify({'success': False, 'message': error_msg}), 400

@views_bp.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    if 'user' not in session or not session['user'].get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('views.index'))
    
    # Get statistics
    total_posts = Post.query.count()
    total_users = User.query.count()
    total_comments = Comment.query.count()
    total_categories = Category.query.count()
    
    # Get recent activity
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         user=session['user'],
                         stats={
                             'posts': total_posts,
                             'users': total_users,
                             'comments': total_comments,
                             'categories': total_categories
                         },
                         recent_posts=recent_posts,
                         recent_users=recent_users)