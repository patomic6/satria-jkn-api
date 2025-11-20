"""
Authentication and Authorization Module
Provides JWT-based authentication for SATRIA JKN API
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

# Secret key for JWT - In production, use environment variable
SECRET_KEY = "satria-jkn-secret-key-2025-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def generate_token(user_id, username, role):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def decode_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def get_user_by_username(username):
    """Get user from database by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user from database by user_id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def update_last_login(user_id):
    """Update user's last login timestamp"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()

def token_required(f):
    """Decorator to protect routes - requires valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Format: "Bearer <token>"
                token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Decode and validate token
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Verify user still exists and is active
        user = get_user_by_id(payload['user_id'])
        if not user or not user['is_active']:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        # Add user info to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to protect routes - requires admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Decode and validate token
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Verify user exists, is active, and is admin
        user = get_user_by_id(payload['user_id'])
        if not user or not user['is_active']:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        if user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Add user info to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated

def role_required(*allowed_roles):
    """Decorator to protect routes - requires specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            # Check for token in Authorization header
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
                except IndexError:
                    return jsonify({'error': 'Invalid token format'}), 401
            
            if not token:
                return jsonify({'error': 'Token is missing'}), 401
            
            # Decode and validate token
            payload = decode_token(token)
            if not payload:
                return jsonify({'error': 'Token is invalid or expired'}), 401
            
            # Verify user exists, is active
            user = get_user_by_id(payload['user_id'])
            if not user or not user['is_active']:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Check if user has required role
            if user['role'] not in allowed_roles:
                return jsonify({'error': f'Access denied. Required roles: {", ".join(allowed_roles)}'}), 403
            
            # Add user info to request context
            request.current_user = user
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator
