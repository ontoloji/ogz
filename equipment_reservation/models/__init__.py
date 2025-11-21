from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    role = db.Column(db.String(20), default='user')  # user, admin, manager
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_manager(self):
        return self.role in ['admin', 'manager']

    def __repr__(self):
        return f'<User {self.username}>'


class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    equipment_type = db.Column(db.String(100))  # Kvaser, Oscilloscope, Power Supply, etc.
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='available')  # available, in_use, maintenance, faulty
    location = db.Column(db.String(200))
    purchase_date = db.Column(db.Date)
    last_calibration_date = db.Column(db.Date)
    next_calibration_date = db.Column(db.Date)
    calibration_interval_days = db.Column(db.Integer, default=365)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reservations = db.relationship('Reservation', backref='equipment', lazy='dynamic')
    maintenance_records = db.relationship('MaintenanceRecord', backref='equipment', lazy='dynamic')

    def is_available(self):
        return self.status == 'available'

    def needs_calibration(self):
        if not self.next_calibration_date:
            return False
        return datetime.now().date() >= self.next_calibration_date

    def __repr__(self):
        return f'<Equipment {self.name}>'


class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    purpose = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_active(self):
        now = datetime.utcnow()
        return self.status in ['pending', 'confirmed'] and self.end_time > now

    def is_current(self):
        now = datetime.utcnow()
        return self.status == 'confirmed' and self.start_time <= now <= self.end_time

    def __repr__(self):
        return f'<Reservation {self.id} - Equipment {self.equipment_id}>'


class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_records'

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    maintenance_type = db.Column(db.String(50))  # calibration, repair, routine_check
    description = db.Column(db.Text)
    performed_by = db.Column(db.String(200))
    performed_at = db.Column(db.DateTime, nullable=False)
    cost = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MaintenanceRecord {self.id} - Equipment {self.equipment_id}>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_type = db.Column(db.String(50))  # reservation_confirmed, calibration_due, etc.
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.id}>'
