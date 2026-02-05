from flask import request, jsonify
from functools import wraps
from models import db, User
import re

def validate_json_content_type(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                return jsonify({
                    'status': 'error',
                    'message': 'Content-Type must be application/json',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 415
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_jwt_extended import get_jwt
        
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return jsonify({
                'status': 'error',
                'message': 'Admin privileges required',
                'code': 'ADMIN_REQUIRED'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def validate_user_input(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if 'email' in data:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, data['email']):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid email format',
                    'code': 'INVALID_EMAIL'
                }), 400
        
        if 'username' in data:
            if len(data['username']) < 3 or len(data['username']) > 50:
                return jsonify({
                    'status': 'error',
                    'message': 'Username must be between 3 and 50 characters',
                    'code': 'INVALID_USERNAME'
                }), 400
        
        if 'password' in data:
            if len(data['password']) < 6:
                return jsonify({
                    'status': 'error',
                    'message': 'Password must be at least 6 characters',
                    'code': 'INVALID_PASSWORD'
                }), 400
        
        return f(*args, **kwargs)
    return decorated_function

def pagination_params(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 10
                
            request.page = page
            request.per_page = per_page
            
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid pagination parameters',
                'code': 'INVALID_PAGINATION'
            }), 400
            
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=100, window=900):  # 100 requests per 15 minutes
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    requests = defaultdict(list)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            now = datetime.now()
            
            # Clean old requests
            requests[ip] = [req_time for req_time in requests[ip] 
                           if now - req_time < timedelta(seconds=window)]
            
            # Check if limit exceeded
            if len(requests[ip]) >= max_requests:
                return jsonify({
                    'status': 'error',
                    'message': 'Rate limit exceeded',
                    'code': 'RATE_LIMIT_EXCEEDED'
                }), 429
            
            # Add current request
            requests[ip].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator