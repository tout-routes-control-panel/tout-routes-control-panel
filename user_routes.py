from flask import Blueprint, request, jsonify
from src.models.admin_models import db, AppUser, UserStatus
from src.routes.admin_auth import token_required
from sqlalchemy import or_

user_routes_bp = Blueprint('user_routes', __name__)

@user_routes_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_admin):
    try:
        # Get query parameters for filtering
        status_filter = request.args.get('status')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = AppUser.query
        
        # Apply filters
        if status_filter:
            query = query.filter(AppUser.status == UserStatus(status_filter))
        
        if search:
            query = query.filter(or_(
                AppUser.name.ilike(f'%{search}%'),
                AppUser.email.ilike(f'%{search}%'),
                AppUser.phone_number.ilike(f'%{search}%')
            ))
        
        # Paginate
        users = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch users: {str(e)}'}), 500

@user_routes_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user_details(current_admin, user_id):
    try:
        user = AppUser.query.get_or_404(user_id)
        user_data = user.to_dict()
        
        # Include booking statistics
        from src.models.admin_models import Booking, BookingStatus
        total_bookings = Booking.query.filter_by(user_id=user_id).count()
        completed_bookings = Booking.query.filter_by(
            user_id=user_id, 
            status=BookingStatus.COMPLETED
        ).count()
        
        # Calculate total spent
        completed_bookings_query = Booking.query.filter_by(
            user_id=user_id,
            status=BookingStatus.COMPLETED
        ).all()
        total_spent = sum(booking.final_fare or 0 for booking in completed_bookings_query)
        
        user_data['statistics'] = {
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'total_spent': total_spent
        }
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch user details: {str(e)}'}), 500

@user_routes_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@token_required
def update_user_status(current_admin, user_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        user = AppUser.query.get_or_404(user_id)
        
        try:
            user.status = UserStatus(new_status)
        except ValueError:
            return jsonify({'message': 'Invalid status value'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'User status updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update user status: {str(e)}'}), 500

@user_routes_bp.route('/users/<int:user_id>/bookings', methods=['GET'])
@token_required
def get_user_bookings(current_admin, user_id):
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        from src.models.admin_models import Booking
        bookings = Booking.query.filter_by(user_id=user_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'bookings': [booking.to_dict() for booking in bookings.items],
            'total': bookings.total,
            'pages': bookings.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch user bookings: {str(e)}'}), 500

@user_routes_bp.route('/users/stats', methods=['GET'])
@token_required
def get_users_stats(current_admin):
    try:
        total_users = AppUser.query.count()
        active_users = AppUser.query.filter_by(status=UserStatus.ACTIVE).count()
        deactivated_users = AppUser.query.filter_by(status=UserStatus.DEACTIVATED).count()
        blocked_users = AppUser.query.filter_by(status=UserStatus.BLOCKED).count()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'deactivated_users': deactivated_users,
            'blocked_users': blocked_users
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch user statistics: {str(e)}'}), 500
