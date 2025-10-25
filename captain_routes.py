from flask import Blueprint, request, jsonify
from src.models.admin_models import db, Captain, CaptainRate, CaptainStatus, ServiceType
from src.routes.admin_auth import token_required
from sqlalchemy import or_

captain_bp = Blueprint('captain', __name__)

@captain_bp.route('/captains', methods=['GET'])
@token_required
def get_captains(current_admin):
    try:
        # Get query parameters for filtering
        status_filter = request.args.get('status')
        vehicle_type_filter = request.args.get('vehicle_type')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Captain.query
        
        # Apply filters
        if status_filter:
            query = query.filter(Captain.status == CaptainStatus(status_filter))
        
        if vehicle_type_filter:
            query = query.filter(Captain.vehicle_type == vehicle_type_filter)
        
        if search:
            query = query.filter(or_(
                Captain.name.ilike(f'%{search}%'),
                Captain.email.ilike(f'%{search}%'),
                Captain.phone_number.ilike(f'%{search}%'),
                Captain.plate_number.ilike(f'%{search}%')
            ))
        
        # Paginate
        captains = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'captains': [captain.to_dict() for captain in captains.items],
            'total': captains.total,
            'pages': captains.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch captains: {str(e)}'}), 500

@captain_bp.route('/captains/<int:captain_id>', methods=['GET'])
@token_required
def get_captain_details(current_admin, captain_id):
    try:
        captain = Captain.query.get_or_404(captain_id)
        captain_data = captain.to_dict()
        
        # Include rates
        rates = CaptainRate.query.filter_by(captain_id=captain_id).all()
        captain_data['rates'] = [rate.to_dict() for rate in rates]
        
        # Include booking statistics
        from src.models.admin_models import Booking, BookingStatus
        total_bookings = Booking.query.filter_by(captain_id=captain_id).count()
        completed_bookings = Booking.query.filter_by(
            captain_id=captain_id, 
            status=BookingStatus.COMPLETED
        ).count()
        
        captain_data['statistics'] = {
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'completion_rate': (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
        }
        
        return jsonify(captain_data), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch captain details: {str(e)}'}), 500

@captain_bp.route('/captains/<int:captain_id>/status', methods=['PUT'])
@token_required
def update_captain_status(current_admin, captain_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        captain = Captain.query.get_or_404(captain_id)
        
        try:
            captain.status = CaptainStatus(new_status)
        except ValueError:
            return jsonify({'message': 'Invalid status value'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Captain status updated successfully',
            'captain': captain.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update captain status: {str(e)}'}), 500

@captain_bp.route('/captains/<int:captain_id>/approve', methods=['POST'])
@token_required
def approve_captain(current_admin, captain_id):
    try:
        captain = Captain.query.get_or_404(captain_id)
        
        if captain.status != CaptainStatus.PENDING:
            return jsonify({'message': 'Captain is not in pending status'}), 400
        
        captain.status = CaptainStatus.ACTIVE
        db.session.commit()
        
        return jsonify({
            'message': 'Captain approved successfully',
            'captain': captain.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to approve captain: {str(e)}'}), 500

@captain_bp.route('/captains/<int:captain_id>/reject', methods=['POST'])
@token_required
def reject_captain(current_admin, captain_id):
    try:
        captain = Captain.query.get_or_404(captain_id)
        
        if captain.status != CaptainStatus.PENDING:
            return jsonify({'message': 'Captain is not in pending status'}), 400
        
        captain.status = CaptainStatus.DEACTIVATED
        db.session.commit()
        
        return jsonify({
            'message': 'Captain rejected successfully',
            'captain': captain.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to reject captain: {str(e)}'}), 500

@captain_bp.route('/captains/<int:captain_id>/rates', methods=['GET'])
@token_required
def get_captain_rates(current_admin, captain_id):
    try:
        rates = CaptainRate.query.filter_by(captain_id=captain_id).all()
        return jsonify([rate.to_dict() for rate in rates]), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch captain rates: {str(e)}'}), 500

@captain_bp.route('/captains/<int:captain_id>/rates', methods=['PUT'])
@token_required
def update_captain_rates(current_admin, captain_id):
    try:
        data = request.get_json()
        service_type = data.get('service_type')
        rate_per_km = data.get('rate_per_km')
        minimum_fare = data.get('minimum_fare')
        waiting_time_rate = data.get('waiting_time_rate')
        
        if not all([service_type, rate_per_km is not None, minimum_fare is not None, waiting_time_rate is not None]):
            return jsonify({'message': 'All rate fields are required'}), 400
        
        # Check if captain exists
        captain = Captain.query.get_or_404(captain_id)
        
        # Check if rate already exists for this service type
        existing_rate = CaptainRate.query.filter_by(
            captain_id=captain_id,
            service_type=ServiceType(service_type)
        ).first()
        
        if existing_rate:
            # Update existing rate
            existing_rate.rate_per_km = rate_per_km
            existing_rate.minimum_fare = minimum_fare
            existing_rate.waiting_time_rate = waiting_time_rate
        else:
            # Create new rate
            new_rate = CaptainRate(
                captain_id=captain_id,
                service_type=ServiceType(service_type),
                rate_per_km=rate_per_km,
                minimum_fare=minimum_fare,
                waiting_time_rate=waiting_time_rate
            )
            db.session.add(new_rate)
        
        db.session.commit()
        
        return jsonify({'message': 'Captain rates updated successfully'}), 200
        
    except ValueError as e:
        return jsonify({'message': f'Invalid service type: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update captain rates: {str(e)}'}), 500

@captain_bp.route('/captains/pending/count', methods=['GET'])
@token_required
def get_pending_captains_count(current_admin):
    try:
        count = Captain.query.filter_by(status=CaptainStatus.PENDING).count()
        return jsonify({'pending_count': count}), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch pending captains count: {str(e)}'}), 500
