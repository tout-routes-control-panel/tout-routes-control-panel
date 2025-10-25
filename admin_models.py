from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

# Enums for status fields
class UserStatus(Enum):
    ACTIVE = "Active"
    DEACTIVATED = "Deactivated"
    BLOCKED = "Blocked"

class CaptainStatus(Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    DEACTIVATED = "Deactivated"
    ON_HOLD = "OnHold"

class VehicleType(Enum):
    CAR = "Car"
    SCOOTER = "Scooter"
    NONE = "None"

class ServiceType(Enum):
    INSIDE_CITY = "InsideCity"
    CROSS_CITY = "CrossCity"
    AIRPORT_DROPOFF = "AirportDropoff"
    SCOOTER_RIDE = "ScooterRide"
    PACKAGE_DELIVERY = "PackageDelivery"
    BOOK_CAPTAIN = "BookCaptain"

class BookingStatus(Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    EN_ROUTE = "EnRoute"
    ARRIVED = "Arrived"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    DISPUTED = "Disputed"

class PaymentMethod(Enum):
    CASH = "Cash"
    INSTAPAY = "InstaPay"

class PaymentStatus(Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    FAILED = "Failed"
    REFUNDED = "Refunded"

class Admin(db.Model):
    __tablename__ = 'admins'
    
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'admin_id': self.admin_id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AppUser(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    face_id_enabled = db.Column(db.Boolean, default=False)
    status = db.Column(db.Enum(UserStatus), default=UserStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with bookings
    bookings = db.relationship('Booking', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'face_id_enabled': self.face_id_enabled,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Captain(db.Model):
    __tablename__ = 'captains'
    
    captain_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    face_id_enabled = db.Column(db.Boolean, default=False)
    vehicle_type = db.Column(db.Enum(VehicleType), nullable=False)
    vehicle_model = db.Column(db.String(100))
    vehicle_color = db.Column(db.String(50))
    plate_number = db.Column(db.String(20), unique=True)
    profile_image_url = db.Column(db.String(255))
    vehicle_image_url = db.Column(db.String(255))
    rating = db.Column(db.Float, default=5.0)
    status = db.Column(db.Enum(CaptainStatus), default=CaptainStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rates = db.relationship('CaptainRate', backref='captain', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='captain', lazy=True)
    
    def to_dict(self):
        return {
            'captain_id': self.captain_id,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'face_id_enabled': self.face_id_enabled,
            'vehicle_type': self.vehicle_type.value if self.vehicle_type else None,
            'vehicle_model': self.vehicle_model,
            'vehicle_color': self.vehicle_color,
            'plate_number': self.plate_number,
            'profile_image_url': self.profile_image_url,
            'vehicle_image_url': self.vehicle_image_url,
            'rating': self.rating,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CaptainRate(db.Model):
    __tablename__ = 'captain_rates'
    
    rate_id = db.Column(db.Integer, primary_key=True)
    captain_id = db.Column(db.Integer, db.ForeignKey('captains.captain_id'), nullable=False)
    service_type = db.Column(db.Enum(ServiceType), nullable=False)
    rate_per_km = db.Column(db.Float, nullable=False)
    minimum_fare = db.Column(db.Float, nullable=False)
    waiting_time_rate = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'rate_id': self.rate_id,
            'captain_id': self.captain_id,
            'service_type': self.service_type.value if self.service_type else None,
            'rate_per_km': self.rate_per_km,
            'minimum_fare': self.minimum_fare,
            'waiting_time_rate': self.waiting_time_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    captain_id = db.Column(db.Integer, db.ForeignKey('captains.captain_id'))
    service_type = db.Column(db.Enum(ServiceType), nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING)
    pickup_location_lat = db.Column(db.Float, nullable=False)
    pickup_location_lon = db.Column(db.Float, nullable=False)
    dropoff_location_lat = db.Column(db.Float, nullable=False)
    dropoff_location_lon = db.Column(db.Float, nullable=False)
    pickup_address = db.Column(db.String(255))
    dropoff_address = db.Column(db.String(255))
    distance_km = db.Column(db.Float)
    estimated_fare = db.Column(db.Float)
    final_fare = db.Column(db.Float)
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    app_commission = db.Column(db.Float)
    captain_earning = db.Column(db.Float)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_time = db.Column(db.DateTime)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    user_rating = db.Column(db.Integer)
    captain_rating = db.Column(db.Integer)
    notes = db.Column(db.Text)
    
    # Relationship with payments
    payments = db.relationship('Payment', backref='booking', lazy=True)
    
    def to_dict(self):
        return {
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'captain_id': self.captain_id,
            'service_type': self.service_type.value if self.service_type else None,
            'status': self.status.value if self.status else None,
            'pickup_location_lat': self.pickup_location_lat,
            'pickup_location_lon': self.pickup_location_lon,
            'dropoff_location_lat': self.dropoff_location_lat,
            'dropoff_location_lon': self.dropoff_location_lon,
            'pickup_address': self.pickup_address,
            'dropoff_address': self.dropoff_address,
            'distance_km': self.distance_km,
            'estimated_fare': self.estimated_fare,
            'final_fare': self.final_fare,
            'payment_method': self.payment_method.value if self.payment_method else None,
            'app_commission': self.app_commission,
            'captain_earning': self.captain_earning,
            'booking_time': self.booking_time.isoformat() if self.booking_time else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'user_rating': self.user_rating,
            'captain_rating': self.captain_rating,
            'notes': self.notes,
            'user_name': self.user.name if self.user else None,
            'captain_name': self.captain.name if self.captain else None
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='EGP')
    method = db.Column(db.Enum(PaymentMethod), nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_ref = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))
    
    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'booking_id': self.booking_id,
            'amount': self.amount,
            'currency': self.currency,
            'method': self.method.value if self.method else None,
            'status': self.status.value if self.status else None,
            'transaction_ref': self.transaction_ref,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'processed_by': self.processed_by
        }
