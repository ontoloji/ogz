from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from functools import wraps
import os

from config import Config
from models import db, User, Equipment, Reservation, MaintenanceRecord, Notification
from email_utils import mail, send_reservation_confirmation, send_reservation_cancellation

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
mail.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bu sayfaya erişim izniniz yok.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_manager():
            flash('Bu sayfaya erişim izniniz yok.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Kullanıcı adı veya şifre hatalı.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')

        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kayıtlı.', 'error')
            return render_template('register.html')

        user = User(username=username, email=email, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Main Routes
@app.route('/')
@login_required
def index():
    equipment_list = Equipment.query.all()
    recent_reservations = Reservation.query.filter_by(user_id=current_user.id)\
        .order_by(Reservation.created_at.desc()).limit(5).all()

    # Statistics
    total_equipment = Equipment.query.count()
    available_equipment = Equipment.query.filter_by(status='available').count()
    my_active_reservations = Reservation.query.filter_by(user_id=current_user.id)\
        .filter(Reservation.end_time > datetime.utcnow())\
        .filter(Reservation.status.in_(['pending', 'confirmed'])).count()

    return render_template('index.html',
                         equipment_list=equipment_list,
                         recent_reservations=recent_reservations,
                         stats={
                             'total_equipment': total_equipment,
                             'available_equipment': available_equipment,
                             'my_active_reservations': my_active_reservations
                         })


# Equipment Routes
@app.route('/equipment')
@login_required
def equipment_list():
    equipment_type = request.args.get('type', None)
    status = request.args.get('status', None)

    query = Equipment.query

    if equipment_type:
        query = query.filter_by(equipment_type=equipment_type)
    if status:
        query = query.filter_by(status=status)

    equipment = query.all()
    equipment_types = db.session.query(Equipment.equipment_type)\
        .distinct().all()

    return render_template('equipment_list.html',
                         equipment=equipment,
                         equipment_types=[t[0] for t in equipment_types if t[0]])


@app.route('/equipment/<int:id>')
@login_required
def equipment_detail(id):
    equipment = Equipment.query.get_or_404(id)
    reservations = Reservation.query.filter_by(equipment_id=id)\
        .filter(Reservation.end_time > datetime.utcnow())\
        .order_by(Reservation.start_time).all()
    maintenance_history = MaintenanceRecord.query.filter_by(equipment_id=id)\
        .order_by(MaintenanceRecord.performed_at.desc()).limit(10).all()

    return render_template('equipment_detail.html',
                         equipment=equipment,
                         reservations=reservations,
                         maintenance_history=maintenance_history)


@app.route('/equipment/add', methods=['GET', 'POST'])
@manager_required
def add_equipment():
    if request.method == 'POST':
        equipment = Equipment(
            name=request.form.get('name'),
            equipment_type=request.form.get('equipment_type'),
            model=request.form.get('model'),
            serial_number=request.form.get('serial_number'),
            description=request.form.get('description'),
            location=request.form.get('location'),
            status=request.form.get('status', 'available'),
            calibration_interval_days=int(request.form.get('calibration_interval_days', 365))
        )

        db.session.add(equipment)
        db.session.commit()

        flash('Ekipman başarıyla eklendi.', 'success')
        return redirect(url_for('equipment_detail', id=equipment.id))

    return render_template('equipment_form.html', equipment=None)


@app.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
@manager_required
def edit_equipment(id):
    equipment = Equipment.query.get_or_404(id)

    if request.method == 'POST':
        equipment.name = request.form.get('name')
        equipment.equipment_type = request.form.get('equipment_type')
        equipment.model = request.form.get('model')
        equipment.serial_number = request.form.get('serial_number')
        equipment.description = request.form.get('description')
        equipment.location = request.form.get('location')
        equipment.status = request.form.get('status')
        equipment.calibration_interval_days = int(request.form.get('calibration_interval_days', 365))

        db.session.commit()

        flash('Ekipman bilgileri güncellendi.', 'success')
        return redirect(url_for('equipment_detail', id=equipment.id))

    return render_template('equipment_form.html', equipment=equipment)


# Reservation Routes
@app.route('/reservations')
@login_required
def reservation_list():
    status_filter = request.args.get('status', 'all')

    query = Reservation.query

    if not current_user.is_manager():
        query = query.filter_by(user_id=current_user.id)

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    reservations = query.order_by(Reservation.start_time.desc()).all()

    return render_template('reservation_list.html',
                         reservations=reservations,
                         status_filter=status_filter)


@app.route('/equipment/<int:equipment_id>/reserve', methods=['GET', 'POST'])
@login_required
def reserve_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)

    if request.method == 'POST':
        start_time = datetime.fromisoformat(request.form.get('start_time'))
        end_time = datetime.fromisoformat(request.form.get('end_time'))
        purpose = request.form.get('purpose')

        # Check for conflicts
        conflicts = Reservation.query.filter(
            Reservation.equipment_id == equipment_id,
            Reservation.status.in_(['pending', 'confirmed']),
            db.or_(
                db.and_(Reservation.start_time <= start_time, Reservation.end_time > start_time),
                db.and_(Reservation.start_time < end_time, Reservation.end_time >= end_time),
                db.and_(Reservation.start_time >= start_time, Reservation.end_time <= end_time)
            )
        ).first()

        if conflicts:
            flash('Seçtiğiniz zaman aralığında bu ekipman başka bir rezervasyon ile çakışıyor.', 'error')
            return render_template('reserve_equipment.html', equipment=equipment)

        reservation = Reservation(
            equipment_id=equipment_id,
            user_id=current_user.id,
            start_time=start_time,
            end_time=end_time,
            purpose=purpose,
            status='confirmed'
        )

        db.session.add(reservation)
        db.session.commit()

        flash('Rezervasyon başarıyla oluşturuldu.', 'success')
        return redirect(url_for('equipment_detail', id=equipment_id))

    return render_template('reserve_equipment.html', equipment=equipment)


@app.route('/reservation/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_reservation(id):
    reservation = Reservation.query.get_or_404(id)

    if reservation.user_id != current_user.id and not current_user.is_manager():
        flash('Bu rezervasyonu iptal etme yetkiniz yok.', 'error')
        return redirect(url_for('reservation_list'))

    reservation.status = 'cancelled'
    db.session.commit()

    flash('Rezervasyon iptal edildi.', 'success')
    return redirect(url_for('reservation_list'))


# Calendar View
@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')


@app.route('/api/calendar/events')
@login_required
def calendar_events():
    start = request.args.get('start')
    end = request.args.get('end')

    query = Reservation.query

    if start:
        query = query.filter(Reservation.end_time >= datetime.fromisoformat(start))
    if end:
        query = query.filter(Reservation.start_time <= datetime.fromisoformat(end))

    reservations = query.all()

    events = []
    for res in reservations:
        events.append({
            'id': res.id,
            'title': f"{res.equipment.name} - {res.user.username}",
            'start': res.start_time.isoformat(),
            'end': res.end_time.isoformat(),
            'backgroundColor': '#3788d8' if res.status == 'confirmed' else '#6c757d',
            'extendedProps': {
                'equipment': res.equipment.name,
                'user': res.user.username,
                'purpose': res.purpose,
                'status': res.status
            }
        })

    return jsonify(events)


# Maintenance Routes
@app.route('/equipment/<int:equipment_id>/maintenance/add', methods=['GET', 'POST'])
@manager_required
def add_maintenance(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)

    if request.method == 'POST':
        maintenance = MaintenanceRecord(
            equipment_id=equipment_id,
            maintenance_type=request.form.get('maintenance_type'),
            description=request.form.get('description'),
            performed_by=request.form.get('performed_by', current_user.full_name),
            performed_at=datetime.fromisoformat(request.form.get('performed_at')),
            cost=float(request.form.get('cost', 0)),
            notes=request.form.get('notes')
        )

        # Update calibration date if this is a calibration maintenance
        if maintenance.maintenance_type == 'calibration':
            equipment.last_calibration_date = maintenance.performed_at.date()
            equipment.next_calibration_date = (
                maintenance.performed_at.date() +
                timedelta(days=equipment.calibration_interval_days)
            )

        db.session.add(maintenance)
        db.session.commit()

        flash('Bakım kaydı eklendi.', 'success')
        return redirect(url_for('equipment_detail', id=equipment_id))

    return render_template('maintenance_form.html', equipment=equipment)


# Statistics Routes
@app.route('/statistics')
@manager_required
def statistics():
    # Equipment statistics
    total_equipment = Equipment.query.count()
    equipment_by_status = db.session.query(
        Equipment.status, db.func.count(Equipment.id)
    ).group_by(Equipment.status).all()

    # Reservation statistics
    total_reservations = Reservation.query.count()
    active_reservations = Reservation.query.filter(
        Reservation.end_time > datetime.utcnow(),
        Reservation.status.in_(['pending', 'confirmed'])
    ).count()

    # Equipment usage statistics
    equipment_usage = db.session.query(
        Equipment.name,
        db.func.count(Reservation.id).label('reservation_count')
    ).join(Reservation).group_by(Equipment.id).order_by(
        db.desc('reservation_count')
    ).limit(10).all()

    # Maintenance costs
    total_maintenance_cost = db.session.query(
        db.func.sum(MaintenanceRecord.cost)
    ).scalar() or 0

    # Calibration warnings
    calibration_warnings = Equipment.query.filter(
        Equipment.next_calibration_date <= datetime.now().date() + timedelta(days=30)
    ).all()

    return render_template('statistics.html',
                         total_equipment=total_equipment,
                         equipment_by_status=equipment_by_status,
                         total_reservations=total_reservations,
                         active_reservations=active_reservations,
                         equipment_usage=equipment_usage,
                         total_maintenance_cost=total_maintenance_cost,
                         calibration_warnings=calibration_warnings)


# User Management Routes
@app.route('/users')
@admin_required
def user_list():
    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        user.is_active = request.form.get('is_active') == 'on'

        db.session.commit()

        flash('Kullanıcı bilgileri güncellendi.', 'success')
        return redirect(url_for('user_list'))

    return render_template('user_form.html', user=user)


# Initialize database
@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized.')


@app.cli.command()
def seed_db():
    """Seed the database with sample data."""
    # Create admin user
    admin = User(username='admin', email='admin@example.com', full_name='Admin User', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    # Create sample user
    user = User(username='user', email='user@example.com', full_name='Test User', role='user')
    user.set_password('user123')
    db.session.add(user)

    # Create sample equipment
    equipment_items = [
        Equipment(
            name='Kvaser Leaf Light v2',
            equipment_type='CAN Interface',
            model='Leaf Light v2',
            serial_number='KVL-001',
            description='USB to CAN interface device',
            status='available',
            location='Lab A - Shelf 1',
            calibration_interval_days=365
        ),
        Equipment(
            name='Tektronix MSO44 Oscilloscope',
            equipment_type='Oscilloscope',
            model='MSO44',
            serial_number='OSC-001',
            description='4-channel mixed signal oscilloscope',
            status='available',
            location='Lab B - Bench 2',
            calibration_interval_days=180
        ),
        Equipment(
            name='Keysight E36312A Power Supply',
            equipment_type='Power Supply',
            model='E36312A',
            serial_number='PS-001',
            description='Triple output DC power supply',
            status='available',
            location='Lab A - Bench 1',
            calibration_interval_days=365
        ),
        Equipment(
            name='Fluke 87V Multimeter',
            equipment_type='Multimeter',
            model='87V',
            serial_number='MM-001',
            description='Industrial multimeter',
            status='maintenance',
            location='Lab A - Drawer 3',
            calibration_interval_days=365
        ),
    ]

    for item in equipment_items:
        db.session.add(item)

    db.session.commit()
    print('Database seeded with sample data.')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
