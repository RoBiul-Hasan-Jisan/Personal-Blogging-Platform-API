from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_current_user
from models import db, Comment, Post
from middleware import validate_json_content_type, pagination_params, admin_required
from utils.helpers import format_response, error_response, paginate_query

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/post/<int:post_id>', methods=['GET'])
@pagination_params
def get_post_comments(post_id):
    page = request.page
    per_page = request.per_page
    
    post = Post.query.get_or_404(post_id)
    
    # Get top-level comments
    query = Comment.query.filter_by(
        post_id=post_id,
        parent_id=None,
        is_approved=True
    ).order_by(Comment.created_at.desc())
    
    comments, meta = paginate_query(query, page, per_page)
    
    return format_response(
        data=[comment.to_dict() for comment in comments],
        meta=meta
    )

@comments_bp.route('/', methods=['POST'])
@jwt_required()
@validate_json_content_type
def create_comment():
    current_user = get_current_user()
    data = request.get_json()
    
    required_fields = ['content', 'post_id']
    for field in required_fields:
        if field not in data:
            return error_response(f'{field} is required', code=400)
    
    post = Post.query.get(data['post_id'])
    if not post:
        return error_response('Post not found', code=404)
    
    # Check if parent comment exists
    if 'parent_id' in data:
        parent = Comment.query.get(data['parent_id'])
        if not parent:
            return error_response('Parent comment not found', code=404)
    
    comment = Comment(
        content=data['content'],
        user_id=current_user.id,
        post_id=data['post_id'],
        parent_id=data.get('parent_id'),
        is_approved=True  # Auto-approve for now
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return format_response(
        data=comment.to_dict(),
        message='Comment created successfully',
        code=201
    )

@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
@validate_json_content_type
def update_comment(comment_id):
    current_user = get_current_user()
    comment = Comment.query.get_or_404(comment_id)
    
    # Check authorization
    if comment.user_id != current_user.id and not current_user.is_admin:
        return error_response('Unauthorized', code=403)
    
    data = request.get_json()
    
    if 'content' in data:
        comment.content = data['content']
    
    db.session.commit()
    
    return format_response(
        data=comment.to_dict(),
        message='Comment updated successfully'
    )

@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    current_user = get_current_user()
    comment = Comment.query.get_or_404(comment_id)
    
    # Check authorization
    if comment.user_id != current_user.id and not current_user.is_admin:
        return error_response('Unauthorized', code=403)
    
    db.session.delete(comment)
    db.session.commit()
    
    return format_response(message='Comment deleted successfully')

@comments_bp.route('/<int:comment_id>/approve', methods=['PUT'])
@jwt_required()
@admin_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.is_approved = True
    db.session.commit()
    
    return format_response(
        data=comment.to_dict(),
        message='Comment approved'
    )

@comments_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@pagination_params
def get_user_comments(user_id):
    current_user = get_current_user()
    
    # Users can only see their own comments unless admin
    if user_id != current_user.id and not current_user.is_admin:
        return error_response('Unauthorized', code=403)
    
    page = request.page
    per_page = request.per_page
    
    query = Comment.query.filter_by(user_id=user_id).order_by(Comment.created_at.desc())
    comments, meta = paginate_query(query, page, per_page)
    
    return format_response(
        data=[comment.to_dict() for comment in comments],
        meta=meta
    )