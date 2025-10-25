from flask import Blueprint, request, jsonify
from src.models.admin_models import db, Booking, BookingStatus, ServiceType
from src.routes.admin_auth import token_required
from sqlalchemy import or_, desc
from datetime import datetime, timedelta

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/bookings', methods=['GET'])
@token_required
def get_bookings(current_admin):
    try:
        # Get query parameters for filtering
        status_filter = request.args.get('status')
        service_type_filter = request.args.get('service_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Booking.query
        
        # Apply filters
        if status_filter:
            query = query.filter(Booking.status == BookingStatus(status_filter))
        
        if service_type_filter:
            query = query.filter(Booking.service_type == ServiceType(service_type_filter))
        
        if date_from:
            date_from_obj = datetime.fromisoformat(date_from)
            query = query.filter(Booking.booking_time >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to)
            query = query.filter(Booking.booking_time <= date_to_obj)
        
        if search:
            query = query.join(Booking.user).join(Booking.captain, isouter=True).filter(or_(
                Booking.pickup_address.ilike(f'%{search}%'),
                Booking.dropoff_address.ilike(f'%{search}%'),
                Booking.user.has(name=search),
                Booking.captain.has(name=search)
            ))
        
        # Order by booking time (most recent first)
        query = query.order_by(desc(Booking.booking_time))
        
        # Paginate
        bookings = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'bookings': [booking.to_dict() for booking in bookings.items],
            'total': bookings.total,
            'pages': bookings.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch bookings: {str(e)}'}), 500

@booking_bp.route('/bookings/<int:booking_id>', methods=['GET'])
@token_required
def get_booking_details(current_admin, booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        booking_data = booking.to_dict()
        
        # Include payment information
        from src.models.admin_models import Payment
        payments = Payment.query.filter_by(booking_id=booking_id).all()
        booking_data['payments'] = [payment.to_dict() for payment in payments]
        
        return jsonify(booking_data), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch booking details: {str(e)}'}), 500

@booking_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
@token_required
def update_booking_status(current_admin, booking_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        booking = Booking.query.get_or_404(booking_id)
        
        try:
            booking.status = BookingStatus(new_status)
            if notes:
                booking.notes = notes
        except ValueError:
            return jsonify({'message': 'Invalid status value'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking status updated successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update booking status: {str(e)}'}), 500

@booking_bp.route('/bookings/<int:booking_id>/resolve', methods=['POST'])
@token_required
def resolve_booking_dispute(current_admin, booking_id):
    try:
        data = request.get_json()
        resolution_notes = data.get('resolution_notes', '')
        
        booking = Booking.query.get_or_404(booking_id)
        
        if booking.status != BookingStatus.DISPUTED:
            return jsonify({'message': 'Booking is not in disputed status'}), 400
        
        # Update booking status and add resolution notes
        booking.status = BookingStatus.COMPLETED
        booking.notes = f"RESOLVED: {resolution_notes}\n\nOriginal notes: {booking.notes or ''}"
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking dispute resolved successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to resolve booking dispute: {str(e)}'}), 500

@booking_bp.route('/bookings/live', methods=['GET'])
@token_required
def get_live_bookings(current_admin):
    try:
        # Get bookings that are currently active (not completed, cancelled, or disputed)
        active_statuses = [
            BookingStatus.PENDING,
            BookingStatus.ACCEPTED,
            BookingStatus.EN_ROUTE,
            BookingStatus.ARRIVED
        ]
        
        bookings = Booking.query.filter(
            Booking.status.in_(active_statuses)
        ).order_by(desc(Booking.booking_time)).all()
        
        return jsonify({
            'live_bookings': [booking.to_dict() for booking in bookings],
            'count': len(bookings)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch live bookings: {str(e)}'}), 500

@booking_bp.route('/bookings/stats', methods=['GET'])
@token_required
def get_booking_stats(current_admin):
    try:
        # Get date range for filtering (default to last 30 days)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if not date_from:
            date_from = datetime.now() - timedelta(days=30)
        else:
            date_from = datetime.fromisoformat(date_from)
        
        if not date_to:
            date_to = datetime.now()
        else:
            date_to = datetime.fromisoformat(date_to)
        
        # Base query with date filter
        base_query = Booking.query.filter(
            Booking.booking_time >= date_from,
            Booking.booking_time <= date_to
        )
        
        # Count by status
        total_bookings = base_query.count()
        pending_bookings = base_query.filter_by(status=BookingStatus.PENDING).count()
        accepted_bookings = base_query.filter_by(status=BookingStatus.ACCEPTED).count()
        completed_bookings = base_query.filter_by(status=BookingStatus.COMPLETED).count()
        cancelled_bookings = base_query.filter_by(status=BookingStatus.CANCELLED).count()
        disputed_bookings = base_query.filter_by(status=BookingStatus.DISPUTED).count()
        
        # Count by service type
        service_stats = {}
        for service_type in ServiceType:
            count = base_query.filter_by(service_type=service_type).count()
            service_stats[service_type.value] = count
        
        # Calculate revenue statistics
        completed_bookings_query = base_query.filter_by(status=BookingStatus.COMPLETED)
        total_revenue = sum(booking.final_fare or 0 for booking in completed_bookings_query.all())
        total_commission = sum(booking.app_commission or 0 for booking in completed_bookings_query.all())
        
        return jsonify({
            'date_range': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'booking_counts': {
                'total': total_bookings,
                'pending': pending_bookings,
                'accepted': accepted_bookings,
                'completed': completed_bookings,
                'cancelled': cancelled_bookings,
                'disputed': disputed_bookings
            },
            'service_type_stats': service_stats,
            'revenue_stats': {
                'total_revenue': total_revenue,
                'total_commission': total_commission,
                'captain_earnings': total_revenue - total_commission
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch booking statistics: {str(e)}'}), 500
