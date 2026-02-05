import re
from datetime import datetime
from flask import request

def generate_slug(text):
    """Generate URL-friendly slug from text"""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug

def format_response(data=None, message="Success", status="success", code=200, meta=None):
    """Standard API response format"""
    response = {
        'status': status,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if meta:
        response['meta'] = meta
    
    return response, code

def error_response(message="Error occurred", status="error", code=400, errors=None):
    """Standard error response format"""
    response = {
        'status': status,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if errors:
        response['errors'] = errors
    
    return response, code

def paginate_query(query, page, per_page):
    """Paginate SQLAlchemy query"""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    meta = {
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total_pages': pagination.pages,
        'total_items': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'next_page': pagination.next_num if pagination.has_next else None,
        'prev_page': pagination.prev_num if pagination.has_prev else None
    }
    
    return pagination.items, meta