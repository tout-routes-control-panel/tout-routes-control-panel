from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from src.models.admin_models import db, Admin
import jwt
import datetime
from functools import wraps

admin_auth_bp = Blueprint('admin_auth', __name__)

# JWT secret key (in production, use environment variable)
JWT_SECRET = 'your-secret-key-here'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_admin = Admin.query.get(data['admin_id'])
            if not current_admin:
                return jsonify({'message': 'Invalid token'}), 401
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_admin, *args, **kwargs)
    return decorated

@admin_auth_bp.route('/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        admin = Admin.query.filter_by(email=email).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            # Generate JWT token
            token = jwt.encode({
                'admin_id': admin.admin_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, JWT_SECRET, algorithm='HS256')
            
            return jsonify({
                'token': token,
                'admin_id': admin.admin_id,
                'name': admin.name,
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@admin_auth_bp.route('/admin/logout', methods=['POST'])
@token_required
def admin_logout(current_admin):
    return jsonify({'message': 'Logged out successfully'}), 200

@admin_auth_bp.route('/admin/profile', methods=['GET'])
@token_required
def admin_profile(current_admin):
    return jsonify(current_admin.to_dict()), 200

@admin_auth_bp.route('/admin/create', methods=['POST'])
def create_admin():
    """Create initial admin account - remove this in production"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([name, email, password]):
            return jsonify({'message': 'Name, email and password are required'}), 400
        
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            return jsonify({'message': 'Admin with this email already exists'}), 400
        
        # Create new admin
        password_hash = generate_password_hash(password)
        new_admin = Admin(
            name=name,
            email=email,
            password_hash=password_hash
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        return jsonify({
            'message': 'Admin created successfully',
            'admin_id': new_admin.admin_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create admin: {str(e)}'}), 500
