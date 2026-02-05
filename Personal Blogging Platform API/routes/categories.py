from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_current_user
from models import db, Category, Post
from middleware import validate_json_content_type, pagination_params, admin_required
from utils.helpers import format_response, error_response, paginate_query, generate_slug

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return format_response(data=[category.to_dict() for category in categories])

@categories_bp.route('/<slug>', methods=['GET'])
def get_category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    return format_response(data=category.to_dict())

@categories_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
@validate_json_content_type
def create_category():
    data = request.get_json()
    
    required_fields = ['name']
    for field in required_fields:
        if field not in data:
            return error_response(f'{field} is required', code=400)
    
    slug = data.get('slug', generate_slug(data['name']))
    
    if Category.query.filter_by(slug=slug).first():
        return error_response('Category slug already exists', code=409)
    
    category = Category(
        name=data['name'],
        slug=slug,
        description=data.get('description', '')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return format_response(
        data=category.to_dict(),
        message='Category created successfully',
        code=201
    )

@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
@validate_json_content_type
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    
    if 'name' in data:
        category.name = data['name']
        if 'slug' not in data:
            category.slug = generate_slug(data['name'])
    
    if 'slug' in data:
        existing = Category.query.filter_by(slug=data['slug']).first()
        if existing and existing.id != category.id:
            return error_response('Category slug already exists', code=409)
        category.slug = data['slug']
    
    if 'description' in data:
        category.description = data['description']
    
    db.session.commit()
    
    return format_response(
        data=category.to_dict(),
        message='Category updated successfully'
    )

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Check if category has posts
    if category.posts:
        return error_response('Cannot delete category with posts', code=400)
    
    db.session.delete(category)
    db.session.commit()
    
    return format_response(message='Category deleted successfully')

@categories_bp.route('/<slug>/posts', methods=['GET'])
@pagination_params
def get_category_posts(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.page
    per_page = request.per_page
    
    query = Post.query.filter_by(
        category_id=category.id,
        is_published=True
    ).order_by(Post.created_at.desc())
    
    posts, meta = paginate_query(query, page, per_page)
    
    return format_response(
        data=[post.to_summary_dict() for post in posts],
        meta=meta
    )