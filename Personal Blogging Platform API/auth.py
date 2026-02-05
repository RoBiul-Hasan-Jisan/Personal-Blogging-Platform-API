from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from flask import jsonify
from functools import wraps

jwt = JWTManager()

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'status': 'error',
        'message': 'Token has expired',
        'code': 'TOKEN_EXPIRED'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'status': 'error',
        'message': 'Invalid token',
        'code': 'INVALID_TOKEN'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'status': 'error',
        'message': 'Authorization token is missing',
        'code': 'MISSING_TOKEN'
    }), 401

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    from models import User
    identity = jwt_data["sub"]
    return User.query.get(identity)

@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    from models import User
    user = User.query.get(identity)
    if user:
        return {
            'is_admin': user.is_admin,
            'username': user.username,
            'email': user.email
        }
    return {}