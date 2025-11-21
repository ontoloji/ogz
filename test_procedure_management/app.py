"""
Test Procedure Management System - Main Application
Flask application initialization and configuration
"""

import os
from pathlib import Path
from flask import Flask, render_template, session, g
from config import config
from models import db


def create_app(config_name=None):
    """Application factory pattern"""

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Ensure instance folder exists
    instance_path = Path(app.root_path) / 'instance'
    instance_path.mkdir(exist_ok=True)

    # Ensure required folders exist
    for folder in ['UPLOAD_FOLDER', 'EXPORT_FOLDER', 'BACKUP_FOLDER']:
        folder_path = Path(app.config[folder])
        folder_path.mkdir(exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()
        # Initialize with sample data if empty
        initialize_sample_data()

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register template filters and context processors
    register_template_helpers(app)

    # Language handling
    @app.before_request
    def before_request():
        """Set language before each request"""
        if 'language' not in session:
            session['language'] = app.config['DEFAULT_LANGUAGE']
        g.language = session.get('language', app.config['DEFAULT_LANGUAGE'])

    # Main routes
    @app.route('/')
    def index():
        """Home page - redirect to dashboard"""
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))

    @app.route('/language/<lang>')
    def set_language(lang):
        """Set application language"""
        from flask import redirect, request
        if lang in app.config['LANGUAGES']:
            session['language'] = lang
        return redirect(request.referrer or '/')

    return app


def register_blueprints(app):
    """Register application blueprints"""
    from routes.dashboard import dashboard_bp
    from routes.procedures import procedures_bp
    from routes.results import results_bp
    from routes.backup import backup_bp
    from routes.pdf_routes import pdf_bp

    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(procedures_bp, url_prefix='/procedures')
    app.register_blueprint(results_bp, url_prefix='/results')
    app.register_blueprint(backup_bp, url_prefix='/backup')
    app.register_blueprint(pdf_bp, url_prefix='/pdf')


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500


def register_template_helpers(app):
    """Register template filters and context processors"""

    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """Format datetime for templates"""
        if value is None:
            return ''
        return value.strftime(format)

    @app.template_filter('date')
    def format_date(value, format='%Y-%m-%d'):
        """Format date for templates"""
        if value is None:
            return ''
        return value.strftime(format)

    @app.context_processor
    def inject_globals():
        """Inject global template variables"""
        return {
            'app_name': 'Test Procedure Management',
            'current_language': g.get('language', app.config['DEFAULT_LANGUAGE'])
        }


def initialize_sample_data():
    """Initialize database with sample data if empty"""
    from models import Category, ECERegulation, TestProcedure

    # Check if data already exists
    if Category.query.first() is not None:
        return

    # Add default categories
    categories = [
        Category(
            name_en='Electrical Systems',
            name_tr='Elektrik Sistemleri',
            description_en='Electrical and electronic system tests',
            description_tr='Elektrik ve elektronik sistem testleri',
            color='#007bff',
            icon='fa-bolt'
        ),
        Category(
            name_en='Mechanical Systems',
            name_tr='Mekanik Sistemler',
            description_en='Mechanical component tests',
            description_tr='Mekanik bileşen testleri',
            color='#28a745',
            icon='fa-cog'
        ),
        Category(
            name_en='Safety',
            name_tr='Güvenlik',
            description_en='Safety and compliance tests',
            description_tr='Güvenlik ve uyumluluk testleri',
            color='#dc3545',
            icon='fa-shield-alt'
        ),
        Category(
            name_en='Performance',
            name_tr='Performans',
            description_en='Performance and efficiency tests',
            description_tr='Performans ve verimlilik testleri',
            color='#ffc107',
            icon='fa-tachometer-alt'
        ),
        Category(
            name_en='Environmental',
            name_tr='Çevresel',
            description_en='Environmental condition tests',
            description_tr='Çevresel koşul testleri',
            color='#17a2b8',
            icon='fa-leaf'
        )
    ]

    for category in categories:
        db.session.add(category)

    # Add sample ECE regulations
    regulations = [
        ECERegulation(
            regulation_code='ECE R100',
            title_en='Electric Power Trained Vehicles',
            title_tr='Elektrikli Güç Aktarımlı Araçlar',
            description_en='Uniform provisions concerning the approval of vehicles with regard to specific requirements for the electric power train',
            description_tr='Elektrikli güç aktarım sistemi için özel gereksinimlere ilişkin araçların onayına ilişkin tekdüzen hükümler',
            url='https://unece.org/transport/standards/transport/vehicle-regulations-wp29/regulation-ece-100'
        ),
        ECERegulation(
            regulation_code='ECE R10',
            title_en='Electromagnetic Compatibility',
            title_tr='Elektromanyetik Uyumluluk',
            description_en='Uniform provisions concerning the approval of vehicles with regard to electromagnetic compatibility',
            description_tr='Elektromanyetik uyumluluk açısından araçların onayına ilişkin tekdüzen hükümler',
            url='https://unece.org/transport/standards/transport/vehicle-regulations-wp29/regulation-ece-10'
        )
    ]

    for regulation in regulations:
        db.session.add(regulation)

    # Add a sample test procedure
    sample_procedure = TestProcedure(
        procedure_code='TP-001',
        title_en='Battery Voltage Test',
        title_tr='Batarya Voltaj Testi',
        level='Basic',
        category='Electrical Systems',
        purpose_en='Verify that the battery voltage is within acceptable range under various load conditions',
        purpose_tr='Batarya voltajının çeşitli yük koşulları altında kabul edilebilir aralıkta olduğunu doğrulamak',
        steps_en=[
            {
                'step': 1,
                'description': 'Ensure vehicle is in safe condition and all systems are off',
                'expected': 'Vehicle is secure and safe to test'
            },
            {
                'step': 2,
                'description': 'Connect voltmeter to battery terminals',
                'expected': 'Voltmeter properly connected'
            },
            {
                'step': 3,
                'description': 'Measure voltage with no load',
                'expected': 'Voltage between 12.4V - 12.8V'
            },
            {
                'step': 4,
                'description': 'Start vehicle and measure voltage under load',
                'expected': 'Voltage between 13.5V - 14.5V'
            },
            {
                'step': 5,
                'description': 'Turn on all electrical systems and measure voltage',
                'expected': 'Voltage remains above 13.0V'
            }
        ],
        steps_tr=[
            {
                'step': 1,
                'description': 'Aracın güvenli durumda olduğundan ve tüm sistemlerin kapalı olduğundan emin olun',
                'expected': 'Araç güvenli ve teste hazır'
            },
            {
                'step': 2,
                'description': 'Voltmetreyi batarya terminallerine bağlayın',
                'expected': 'Voltmetre doğru şekilde bağlandı'
            },
            {
                'step': 3,
                'description': 'Yüksüz voltajı ölçün',
                'expected': 'Voltaj 12.4V - 12.8V arasında'
            },
            {
                'step': 4,
                'description': 'Aracı çalıştırın ve yük altında voltajı ölçün',
                'expected': 'Voltaj 13.5V - 14.5V arasında'
            },
            {
                'step': 5,
                'description': 'Tüm elektrik sistemlerini açın ve voltajı ölçün',
                'expected': 'Voltaj 13.0V\'un üzerinde kalıyor'
            }
        ],
        acceptance_criteria_en='All voltage measurements must be within specified ranges. No abnormal fluctuations or drops.',
        acceptance_criteria_tr='Tüm voltaj ölçümleri belirtilen aralıklarda olmalıdır. Anormal dalgalanma veya düşüş olmamalıdır.',
        required_equipment=['Digital Voltmeter', 'Safety Equipment', 'Test Documentation'],
        ece_regulations=['ECE R100', 'ECE R10'],
        estimated_duration=30,
        prerequisites=[],
        is_active=True,
        created_by='System'
    )

    db.session.add(sample_procedure)

    try:
        db.session.commit()
        print("Sample data initialized successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing sample data: {e}")


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
