from flask import Blueprint, request, jsonify
from src.models.admin_models import db, Payment, Booking, BookingStatus, PaymentMethod, PaymentStatus
from src.routes.admin_auth import token_required
from sqlalchemy import func, desc
from datetime import datetime, timedelta

financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/financials/overview', methods=['GET'])
@token_required
def get_financial_overview(current_admin):
    try:
        # Get date range for filtering (default to current month)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if not date_from:
            # Default to current month
            now = datetime.now()
            date_from = datetime(now.year, now.month, 1)
        else:
            date_from = datetime.fromisoformat(date_from)
        
        if not date_to:
            date_to = datetime.now()
        else:
            date_to = datetime.fromisoformat(date_to)
        
        # Get completed bookings in date range
        completed_bookings = Booking.query.filter(
            Booking.status == BookingStatus.COMPLETED,
            Booking.booking_time >= date_from,
            Booking.booking_time <= date_to
        ).all()
        
        # Calculate totals
        total_revenue = sum(booking.final_fare or 0 for booking in completed_bookings)
        total_commission = sum(booking.app_commission or 0 for booking in completed_bookings)
        total_captain_earnings = total_revenue - total_commission
        
        # Payment method breakdown
        cash_payments = sum(
            booking.final_fare or 0 
            for booking in completed_bookings 
            if booking.payment_method == PaymentMethod.CASH
        )
        instapay_payments = sum(
            booking.final_fare or 0 
            for booking in completed_bookings 
            if booking.payment_method == PaymentMethod.INSTAPAY
        )
        
        # Get transaction counts
        total_transactions = len(completed_bookings)
        
        return jsonify({
            'date_range': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'overview': {
                'total_revenue': round(total_revenue, 2),
                'total_commission': round(total_commission, 2),
                'total_captain_earnings': round(total_captain_earnings, 2),
                'commission_percentage': round((total_commission / total_revenue * 100) if total_revenue > 0 else 0, 2)
            },
            'payment_methods': {
                'cash': round(cash_payments, 2),
                'instapay': round(instapay_payments, 2)
            },
            'transaction_count': total_transactions
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch financial overview: {str(e)}'}), 500

@financial_bp.route('/financials/transactions', methods=['GET'])
@token_required
def get_transactions(current_admin):
    try:
        # Get query parameters for filtering
        payment_method_filter = request.args.get('payment_method')
        status_filter = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = Payment.query
        
        # Apply filters
        if payment_method_filter:
            query = query.filter(Payment.method == PaymentMethod(payment_method_filter))
        
        if status_filter:
            query = query.filter(Payment.status == PaymentStatus(status_filter))
        
        if date_from:
            date_from_obj = datetime.fromisoformat(date_from)
            query = query.filter(Payment.payment_date >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to)
            query = query.filter(Payment.payment_date <= date_to_obj)
        
        # Order by payment date (most recent first)
        query = query.order_by(desc(Payment.payment_date))
        
        # Paginate
        payments = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Enhance payment data with booking information
        enhanced_payments = []
        for payment in payments.items:
            payment_data = payment.to_dict()
            if payment.booking:
                payment_data['booking_info'] = {
                    'service_type': payment.booking.service_type.value,
                    'user_name': payment.booking.user.name if payment.booking.user else None,
                    'captain_name': payment.booking.captain.name if payment.booking.captain else None,
                    'pickup_address': payment.booking.pickup_address,
                    'dropoff_address': payment.booking.dropoff_address
                }
            enhanced_payments.append(payment_data)
        
        return jsonify({
            'transactions': enhanced_payments,
            'total': payments.total,
            'pages': payments.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch transactions: {str(e)}'}), 500

@financial_bp.route('/financials/commissions', methods=['GET'])
@token_required
def get_commissions(current_admin):
    try:
        # Get query parameters for filtering
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query for completed bookings
        query = Booking.query.filter(Booking.status == BookingStatus.COMPLETED)
        
        if date_from:
            date_from_obj = datetime.fromisoformat(date_from)
            query = query.filter(Booking.booking_time >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to)
            query = query.filter(Booking.booking_time <= date_to_obj)
        
        # Order by booking time (most recent first)
        query = query.order_by(desc(Booking.booking_time))
        
        # Paginate
        bookings = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Extract commission data
        commission_data = []
        for booking in bookings.items:
            commission_data.append({
                'booking_id': booking.booking_id,
                'booking_time': booking.booking_time.isoformat() if booking.booking_time else None,
                'service_type': booking.service_type.value,
                'user_name': booking.user.name if booking.user else None,
                'captain_name': booking.captain.name if booking.captain else None,
                'final_fare': booking.final_fare,
                'app_commission': booking.app_commission,
                'captain_earning': booking.captain_earning,
                'payment_method': booking.payment_method.value,
                'commission_percentage': round((booking.app_commission / booking.final_fare * 100) if booking.final_fare and booking.app_commission else 0, 2)
            })
        
        return jsonify({
            'commissions': commission_data,
            'total': bookings.total,
            'pages': bookings.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch commission details: {str(e)}'}), 500

@financial_bp.route('/financials/daily-revenue', methods=['GET'])
@token_required
def get_daily_revenue(current_admin):
    try:
        # Get date range (default to last 30 days)
        days = int(request.args.get('days', 30))
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Query for daily revenue
        daily_revenue = db.session.query(
            func.date(Booking.booking_time).label('date'),
            func.sum(Booking.final_fare).label('total_revenue'),
            func.sum(Booking.app_commission).label('total_commission'),
            func.count(Booking.booking_id).label('booking_count')
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
        revenue_data = []
        for row in daily_revenue:
            revenue_data.append({
                'date': row.date.isoformat(),
                'total_revenue': float(row.total_revenue or 0),
                'total_commission': float(row.total_commission or 0),
                'booking_count': row.booking_count
            })
        
        return jsonify({
            'daily_revenue': revenue_data,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch daily revenue: {str(e)}'}), 500

@financial_bp.route('/financials/export', methods=['GET'])
@token_required
def export_financial_data(current_admin):
    try:
        # Get query parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        export_type = request.args.get('type', 'transactions')  # transactions, commissions, revenue
        
        if not date_from:
            date_from = datetime.now() - timedelta(days=30)
        else:
            date_from = datetime.fromisoformat(date_from)
        
        if not date_to:
            date_to = datetime.now()
        else:
            date_to = datetime.fromisoformat(date_to)
        
        if export_type == 'transactions':
            # Export transaction data
            payments = Payment.query.filter(
                Payment.payment_date >= date_from,
                Payment.payment_date <= date_to
            ).all()
            
            export_data = []
            for payment in payments:
                export_data.append({
                    'payment_id': payment.payment_id,
                    'booking_id': payment.booking_id,
                    'amount': payment.amount,
                    'currency': payment.currency,
                    'method': payment.method.value,
                    'status': payment.status.value,
                    'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                    'transaction_ref': payment.transaction_ref
                })
        
        elif export_type == 'commissions':
            # Export commission data
            bookings = Booking.query.filter(
                Booking.status == BookingStatus.COMPLETED,
                Booking.booking_time >= date_from,
                Booking.booking_time <= date_to
            ).all()
            
            export_data = []
            for booking in bookings:
                export_data.append({
                    'booking_id': booking.booking_id,
                    'booking_time': booking.booking_time.isoformat() if booking.booking_time else None,
                    'service_type': booking.service_type.value,
                    'final_fare': booking.final_fare,
                    'app_commission': booking.app_commission,
                    'captain_earning': booking.captain_earning,
                    'payment_method': booking.payment_method.value
                })
        
        return jsonify({
            'export_data': export_data,
            'export_type': export_type,
            'date_range': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'total_records': len(export_data)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to export financial data: {str(e)}'}), 500
