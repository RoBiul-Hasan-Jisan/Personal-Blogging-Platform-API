from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_current_user
from models import db, Post, Category, Tag, Like
from middleware import validate_json_content_type, pagination_params, admin_required
from utils.helpers import format_response, error_response, paginate_query, generate_slug
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/', methods=['GET'])
@pagination_params
def get_posts():
    page = request.page
    per_page = request.per_page
    
    # Build query
    query = Post.query.filter_by(is_published=True)
    
    # Filtering
    category_slug = request.args.get('category')
    tag_slug = request.args.get('tag')
    author_id = request.args.get('author_id')
    search = request.args.get('search')
    featured = request.args.get('featured')
    
    if category_slug:
        query = query.join(Category).filter(Category.slug == category_slug)
    
    if tag_slug:
        query = query.join(Post.tags).filter(Tag.slug == tag_slug)
    
    if author_id:
        query = query.filter(Post.user_id == author_id)
    
    if search:
        query = query.filter(
            Post.title.ilike(f'%{search}%') | 
            Post.content.ilike(f'%{search}%') |
            Post.excerpt.ilike(f'%{search}%')
        )
    
    if featured and featured.lower() == 'true':
        query = query.filter(Post.is_featured == True)
    
    # Sorting
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    if sort_by == 'views':
        sort_column = Post.views
    elif sort_by == 'title':
        sort_column = Post.title
    else:
        sort_column = Post.created_at
    
    if sort_order.lower() == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Paginate
    posts, meta = paginate_query(query, page, per_page)
    
    return format_response(
        data=[post.to_summary_dict() for post in posts],
        meta=meta
    )

@posts_bp.route('/<slug>', methods=['GET'])
def get_post(slug):
    post = Post.query.filter_by(slug=slug).first()
    
    if not post:
        return error_response('Post not found', code=404)
    
    # Increment views
    post.views += 1
    db.session.commit()
    
    return format_response(data=post.to_dict())

@posts_bp.route('/', methods=['POST'])
@jwt_required()
@validate_json_content_type
def create_post():
    current_user = get_current_user()
    data = request.get_json()
    
    required_fields = ['title', 'content']
    for field in required_fields:
        if field not in data:
            return error_response(f'{field} is required', code=400)
    
    # Generate slug
    slug = data.get('slug', generate_slug(data['title']))
    
    # Check if slug exists
    if Post.query.filter_by(slug=slug).first():
        return error_response('Slug already exists', code=409)
    
    # Create post
    post = Post(
        title=data['title'],
        content=data['content'],
        excerpt=data.get('excerpt', data['content'][:297] + '...'),
        slug=slug,
        featured_image=data.get('featured_image'),
        is_published=data.get('is_published', False),
        is_featured=data.get('is_featured', False),
        user_id=current_user.id,
        category_id=data.get('category_id')
    )
    
    if post.is_published and not post.published_at:
        post.published_at = datetime.utcnow()
    
    # Handle tags
    if 'tags' in data:
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag_slug = generate_slug(tag_name)
                tag = Tag(name=tag_name, slug=tag_slug)
                db.session.add(tag)
            post.tags.append(tag)
    
    db.session.add(post)
    db.session.commit()
    
    return format_response(
        data=post.to_dict(),
        message='Post created successfully',
        code=201
    )

@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
@validate_json_content_type
def update_post(post_id):
    current_user = get_current_user()
    post = Post.query.get_or_404(post_id)
    
    # Check authorization
    if post.user_id != current_user.id and not current_user.is_admin:
        return error_response('Unauthorized', code=403)
    
    data = request.get_json()
    
    if 'title' in data:
        post.title = data['title']
        if 'slug' not in data:
            post.slug = generate_slug(data['title'])
    
    if 'slug' in data:
        existing_post = Post.query.filter_by(slug=data['slug']).first()
        if existing_post and existing_post.id != post.id:
            return error_response('Slug already exists', code=409)
        post.slug = data['slug']
    
    if 'content' in data:
        post.content = data['content']
        if 'excerpt' not in data:
            post.excerpt = data['content'][:297] + '...'
    
    if 'excerpt' in data:
        post.excerpt = data['excerpt']
    
    if 'featured_image' in data:
        post.featured_image = data['featured_image']
    
    if 'is_published' in data:
        post.is_published = data['is_published']
        if data['is_published'] and not post.published_at:
            post.published_at = datetime.utcnow()
    
    if 'is_featured' in data:
        post.is_featured = data['is_featured']
    
    if 'category_id' in data:
        post.category_id = data['category_id']
    
    # Update tags
    if 'tags' in data:
        post.tags.clear()
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag_slug = generate_slug(tag_name)
                tag = Tag(name=tag_name, slug=tag_slug)
                db.session.add(tag)
            post.tags.append(tag)
    
    post.updated_at = datetime.utcnow()
    db.session.commit()
    
    return format_response(
        data=post.to_dict(),
        message='Post updated successfully'
    )

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    current_user = get_current_user()
    post = Post.query.get_or_404(post_id)
    
    # Check authorization
    if post.user_id != current_user.id and not current_user.is_admin:
        return error_response('Unauthorized', code=403)
    
    db.session.delete(post)
    db.session.commit()
    
    return format_response(message='Post deleted successfully')

@posts_bp.route('/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    current_user = get_current_user()
    post = Post.query.get_or_404(post_id)
    
    # Check if already liked
    existing_like = Like.query.filter_by(
        user_id=current_user.id, 
        post_id=post_id
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        action = 'unliked'
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    
    return format_response(
        data={
            'action': action,
            'likes_count': len(post.likes),
            'post_id': post_id
        },
        message=f'Post {action} successfully'
    )

@posts_bp.route('/drafts', methods=['GET'])
@jwt_required()
@pagination_params
def get_drafts():
    current_user = get_current_user()
    page = request.page
    per_page = request.per_page
    
    query = Post.query.filter_by(
        user_id=current_user.id,
        is_published=False
    ).order_by(Post.created_at.desc())
    
    posts, meta = paginate_query(query, page, per_page)
    
    return format_response(
        data=[post.to_summary_dict() for post in posts],
        meta=meta
    )