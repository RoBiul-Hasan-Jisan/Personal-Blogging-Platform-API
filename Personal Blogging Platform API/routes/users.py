from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_current_user
from models import db, User
from middleware import validate_json_content_type, validate_user_input, rate_limit
from utils.helpers import format_response, error_response
import re

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
@validate_json_content_type
@validate_user_input
@rate_limit(max_requests=5, window=300)  # 5 registrations per 5 minutes
def register():
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return error_response(f'{field} is required', code=400)
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return error_response('Username already exists', code=409)
    
    if User.query.filter_by(email=data['email']).first():
        return error_response('Email already exists', code=409)
    
    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        bio=data.get('bio', ''),
        profile_image=data.get('profile_image')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    
    user_data = user.to_dict()
    user_data['tokens'] = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }
    
    return format_response(
        data=user_data,
        message='User registered successfully',
        code=201
    )

@users_bp.route('/login', methods=['POST'])
@validate_json_content_type
@validate_user_input
@rate_limit(max_requests=10, window=300)  # 10 login attempts per 5 minutes
def login():
    data = request.get_json()
    
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return error_response(f'{field} is required', code=400)
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return error_response('Invalid email or password', code=401)
    
    if not user.is_active:
        return error_response('Account is deactivated', code=403)
    
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    
    user_data = user.to_dict()
    user_data['tokens'] = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }
    
    return format_response(
        data=user_data,
        message='Login successful'
    )

@users_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_current_user()
    new_access_token = create_access_token(identity=current_user)
    
    return format_response(
        data={'access_token': new_access_token},
        message='Token refreshed successfully'
    )

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_current_user()
    return format_response(data=current_user.to_dict())

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
@validate_json_content_type
@validate_user_input
def update_profile():
    current_user = get_current_user()
    data = request.get_json()
    
    if 'username' in data and data['username'] != current_user.username:
        if User.query.filter_by(username=data['username']).first():
            return error_response('Username already exists', code=409)
        current_user.username = data['username']
    
    if 'email' in data and data['email'] != current_user.email:
        if User.query.filter_by(email=data['email']).first():
            return error_response('Email already exists', code=409)
        current_user.email = data['email']
    
    if 'bio' in data:
        current_user.bio = data['bio']
    
    if 'profile_image' in data:
        current_user.profile_image = data['profile_image']
    
    if 'password' in data and data['password']:
        current_user.set_password(data['password'])
    
    db.session.commit()
    
    return format_response(
        data=current_user.to_dict(),
        message='Profile updated successfully'
    )

@users_bp.route('/<username>', methods=['GET'])
def get_user_profile(username):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return error_response('User not found', code=404)
    
    return format_response(data=user.to_public_dict())

@users_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Note: JWT is stateless, so we can't actually "logout" on server side
    # In a real app, you might want to implement a token blacklist
    return format_response(message='Logout successful')