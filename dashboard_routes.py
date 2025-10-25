from flask import Blueprint, request, jsonify
from src.models.admin_models import db, AppUser, Captain, Booking, Payment, UserStatus, CaptainStatus, BookingStatus
from src.routes.admin_auth import token_required
from sqlalchemy import func, desc
from datetime import datetime, timedelta

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/overview", methods=["GET"])
@token_required
def get_dashboard_overview(current_admin):
    try:
        # Get current date for filtering
        today = datetime.now().date()
        this_month_start = datetime(today.year, today.month, 1)
        
        # User Statistics
        total_users = AppUser.query.count()
        active_users = AppUser.query.filter_by(status=UserStatus.ACTIVE).count()
        new_users_today = AppUser.query.filter(
            func.date(AppUser.created_at) == today
        ).count()
        
        # Captain Statistics
        total_captains = Captain.query.count()
        active_captains = Captain.query.filter_by(status=CaptainStatus.ACTIVE).count()
        pending_captains = Captain.query.filter_by(status=CaptainStatus.PENDING).count()
        new_captains_today = Captain.query.filter(
            func.date(Captain.created_at) == today
        ).count()
        
        # Booking Statistics
        total_bookings = Booking.query.count()
        bookings_today = Booking.query.filter(
            func.date(Booking.booking_time) == today
        ).count()
        active_bookings = Booking.query.filter(
            Booking.status.in_([
                BookingStatus.PENDING,
                BookingStatus.ACCEPTED,
                BookingStatus.EN_ROUTE,
                BookingStatus.ARRIVED
            ])
        ).count()
        completed_bookings_today = Booking.query.filter(
            func.date(Booking.booking_time) == today,
            Booking.status == BookingStatus.COMPLETED
        ).count()
        
        # Revenue Statistics
        revenue_today = db.session.query(
            func.sum(Booking.final_fare)
        ).filter(
            func.date(Booking.booking_time) == today,
            Booking.status == BookingStatus.COMPLETED
        ).scalar() or 0
        
        commission_today = db.session.query(
            func.sum(Booking.app_commission)
        ).filter(
            func.date(Booking.booking_time) == today,
            Booking.status == BookingStatus.COMPLETED
        ).scalar() or 0
        
        revenue_this_month = db.session.query(
            func.sum(Booking.final_fare)
        ).filter(
            Booking.booking_time >= this_month_start,
            Booking.status == BookingStatus.COMPLETED
        ).scalar() or 0
        
        commission_this_month = db.session.query(
            func.sum(Booking.app_commission)
        ).filter(
            Booking.booking_time >= this_month_start,
            Booking.status == BookingStatus.COMPLETED
        ).scalar() or 0
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'new_today': new_users_today
            },
            'captains': {
                'total': total_captains,
                'active': active_captains,
                'pending': pending_captains,
                'new_today': new_captains_today
            },
            'bookings': {
                'total': total_bookings,
                'today': bookings_today,
                'active': active_bookings,
                'completed_today': completed_bookings_today
            },
            'revenue': {
                'today': round(float(revenue_today), 2),
                'commission_today': round(float(commission_today), 2),
                'this_month': round(float(revenue_this_month), 2),
                'commission_this_month': round(float(commission_this_month), 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch dashboard overview: {str(e)}'}), 500

@dashboard_bp.route("/recent-activity", methods=["GET"])
@token_required
def get_recent_activity(current_admin):
    try:
        limit = int(request.args.get('limit', 10))
        
        # Recent bookings
        recent_bookings = Booking.query.order_by(
            desc(Booking.booking_time)
        ).limit(limit).all()
        
        # Recent captain registrations
        recent_captains = Captain.query.order_by(
            desc(Captain.created_at)
        ).limit(limit).all()
        
        # Recent user registrations
        recent_users = AppUser.query.order_by(
            desc(AppUser.created_at)
        ).limit(limit).all()
        
        # Format activity feed
        activities = []
        
        # Add booking activities
        for booking in recent_bookings:
            activities.append({
                'type': 'booking',
                'id': booking.booking_id,
                'title': f'New {booking.service_type.value} booking',
                'description': f'{booking.user.name if booking.user else "Unknown"} booked a ride',
                'timestamp': booking.booking_time.isoformat() if booking.booking_time else None,
                'status': booking.status.value,
                'details': {
                    'user_name': booking.user.name if booking.user else None,
                    'captain_name': booking.captain.name if booking.captain else None,
                    'service_type': booking.service_type.value
                }
            })
        
        # Add captain registration activities
        for captain in recent_captains:
            activities.append({
                'type': 'captain_registration',
                'id': captain.captain_id,
                'title': 'New captain registration',
                'description': f'{captain.name} registered as a captain',
                'timestamp': captain.created_at.isoformat() if captain.created_at else None,
                'status': captain.status.value,
                'details': {
                    'captain_name': captain.name,
                    'vehicle_type': captain.vehicle_type.value if captain.vehicle_type else None
                }
            })
        
        # Add user registration activities
        for user in recent_users:
            activities.append({
                'type': 'user_registration',
                'id': user.user_id,
                'title': 'New user registration',
                'description': f'{user.name} joined the platform',
                'timestamp': user.created_at.isoformat() if user.created_at else None,
                'status': user.status.value,
                'details': {
                    'user_name': user.name
                }
            })
        
        # Sort activities by timestamp (most recent first)
        activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        
        return jsonify({
            'activities': activities[:limit]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch recent activity: {str(e)}'}), 500

@dashboard_bp.route("/charts/bookings-trend", methods=["GET"])
@token_required
def get_bookings_trend(current_admin):
    try:
        # Get date range (default to last 7 days)
        days = int(request.args.get('days', 7))
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Query for daily booking counts
        daily_bookings = db.session.query(
            func.date(Booking.booking_time).label('date'),
            func.count(Booking.booking_id).label('count')
        ).filter(
            func.date(Booking.booking_time) >= start_date,
            func.date(Booking.booking_time) <= end_date
        ).group_by(
            func.date(Booking.booking_time)
        ).order_by(
            func.date(Booking.booking_time)
        ).all()
        
        # Format the data
        trend_data = []
        for row in daily_bookings:
            trend_data.append({
                'date': row.date.isoformat(),
                'bookings': row.count
            })
        
        return jsonify({
            'trend_data': trend_data,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch bookings trend: {str(e)}'}), 500

@dashboard_bp.route("/charts/revenue-trend", methods=["GET"])
@token_required
def get_revenue_trend(current_admin):
    try:
        # Get date range (default to last 7 days)
        days = int(request.args.get('days', 7))
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Query for daily revenue
        daily_revenue = db.session.query(
            func.date(Booking.booking_time).label('date'),
            func.sum(Booking.final_fare).label('revenue'),
            func.sum(Booking.app_commission).label('commission')
        ).filter(
            Booking.status == BookingStatus.COMPLETED,
            func.date(Booking.booking_time) >= start_date,
            func.date(Booking.booking_time) <= end_date
        ).group_by(
            func.date(Booking.booking_time)
        ).order_by(
            func.date(Booking.booking_time)
        ).all()
        
        # Format the data
        trend_data = []
        for row in daily_revenue:
            trend_data.append({
                'date': row.date.isoformat(),
                'revenue': float(row.revenue or 0),
                'commission': float(row.commission or 0)
            })
        
        return jsonify({
            'trend_data': trend_data,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch revenue trend: {str(e)}'}), 500

@dashboard_bp.route("/charts/service-distribution", methods=["GET"])
@token_required
def get_service_distribution(current_admin):
    try:
        # Get date range (default to last 30 days)
        days = int(request.args.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # Query for service type distribution
        service_distribution = db.session.query(
            Booking.service_type,
            func.count(Booking.booking_id).label('count')
        ).filter(
            Booking.booking_time >= start_date
        ).group_by(
            Booking.service_type
        ).all()
        
        # Format the data
        distribution_data = []
        for row in service_distribution:
            distribution_data.append({
                'service_type': row.service_type.value,
                'count': row.count
            })
        
        return jsonify({
            'distribution_data': distribution_data,
            'date_range': {
                'start_date': start_date.date().isoformat(),
                'end_date': datetime.now().date().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch service distribution: {str(e)}'}), 500
