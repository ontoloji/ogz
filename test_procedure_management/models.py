"""
Test Procedure Management System - Database Models
SQLAlchemy models for test procedures, results, and related entities
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text, JSON

db = SQLAlchemy()


class TestProcedure(db.Model):
    """Test Procedure Model - TP-001, TP-002, etc."""

    __tablename__ = 'test_procedures'

    id = db.Column(db.Integer, primary_key=True)
    procedure_code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # TP-001
    title_tr = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)

    # Test details
    level = db.Column(db.String(50), nullable=False, index=True)  # Basic, Advanced, Expert
    category = db.Column(db.String(100), nullable=False, index=True)  # Electrical, Mechanical, etc.

    # Purpose/Objective
    purpose_tr = db.Column(Text, nullable=False)
    purpose_en = db.Column(Text, nullable=False)

    # Test steps (stored as JSON array)
    steps_tr = db.Column(JSON, nullable=False)  # [{step: 1, description: "...", expected: "..."}]
    steps_en = db.Column(JSON, nullable=False)

    # Acceptance criteria
    acceptance_criteria_tr = db.Column(Text, nullable=False)
    acceptance_criteria_en = db.Column(Text, nullable=False)

    # Required equipment (stored as JSON array)
    required_equipment = db.Column(JSON, nullable=False)  # ["Equipment 1", "Equipment 2"]

    # ECE Regulation references (stored as JSON array)
    ece_regulations = db.Column(JSON)  # ["ECE R100", "ECE R10"]

    # Estimated duration in minutes
    estimated_duration = db.Column(db.Integer)

    # Prerequisites (other procedures that must be completed first)
    prerequisites = db.Column(JSON)  # [1, 2, 3] - IDs of other procedures

    # Status
    is_active = db.Column(db.Boolean, default=True, index=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))

    # Relationships
    test_results = db.relationship('TestResult', back_populates='procedure', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TestProcedure {self.procedure_code}: {self.title_en}>'

    def to_dict(self, language='en'):
        """Convert to dictionary for API responses"""
        title = self.title_en if language == 'en' else self.title_tr
        purpose = self.purpose_en if language == 'en' else self.purpose_tr
        steps = self.steps_en if language == 'en' else self.steps_tr
        criteria = self.acceptance_criteria_en if language == 'en' else self.acceptance_criteria_tr

        return {
            'id': self.id,
            'procedure_code': self.procedure_code,
            'title': title,
            'level': self.level,
            'category': self.category,
            'purpose': purpose,
            'steps': steps,
            'acceptance_criteria': criteria,
            'required_equipment': self.required_equipment,
            'ece_regulations': self.ece_regulations,
            'estimated_duration': self.estimated_duration,
            'prerequisites': self.prerequisites,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }


class TestResult(db.Model):
    """Test Result Model - Stores test execution results"""

    __tablename__ = 'test_results'

    id = db.Column(db.Integer, primary_key=True)
    procedure_id = db.Column(db.Integer, db.ForeignKey('test_procedures.id'), nullable=False, index=True)

    # Test execution info
    test_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    operator = db.Column(db.String(100), nullable=False, index=True)

    # Result
    status = db.Column(db.String(20), nullable=False, index=True)  # PASS, FAIL, PARTIAL

    # Details
    notes = db.Column(Text)
    observations = db.Column(Text)

    # Step-by-step results (stored as JSON)
    step_results = db.Column(JSON)  # [{step: 1, status: "PASS", notes: "..."}]

    # Measurements/Data (if any)
    measurements = db.Column(JSON)  # {"voltage": 12.5, "current": 2.3, ...}

    # Attached files (stored as JSON array of file paths)
    attachments = db.Column(JSON)  # ["path/to/file1.pdf", "path/to/file2.jpg"]

    # Environmental conditions
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)

    # Duration in minutes
    actual_duration = db.Column(db.Integer)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    procedure = db.relationship('TestProcedure', back_populates='test_results')

    def __repr__(self):
        return f'<TestResult {self.id}: {self.procedure.procedure_code} - {self.status}>'

    def to_dict(self, language='en'):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'procedure_id': self.procedure_id,
            'procedure_code': self.procedure.procedure_code,
            'procedure_title': self.procedure.title_en if language == 'en' else self.procedure.title_tr,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'operator': self.operator,
            'status': self.status,
            'notes': self.notes,
            'observations': self.observations,
            'step_results': self.step_results,
            'measurements': self.measurements,
            'attachments': self.attachments,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'actual_duration': self.actual_duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Category(db.Model):
    """Category Model - For organizing test procedures"""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name_tr = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False, unique=True)
    description_tr = db.Column(Text)
    description_en = db.Column(Text)
    color = db.Column(db.String(20), default='#007bff')  # For UI visualization
    icon = db.Column(db.String(50))  # Icon class name

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Category {self.name_en}>'

    def to_dict(self, language='en'):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name_en if language == 'en' else self.name_tr,
            'description': self.description_en if language == 'en' else self.description_tr,
            'color': self.color,
            'icon': self.icon
        }


class ECERegulation(db.Model):
    """ECE Regulation Model - Reference database"""

    __tablename__ = 'ece_regulations'

    id = db.Column(db.Integer, primary_key=True)
    regulation_code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # ECE R100
    title_tr = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    description_tr = db.Column(Text)
    description_en = db.Column(Text)
    url = db.Column(db.String(500))  # Link to official document

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ECERegulation {self.regulation_code}>'

    def to_dict(self, language='en'):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'regulation_code': self.regulation_code,
            'title': self.title_en if language == 'en' else self.title_tr,
            'description': self.description_en if language == 'en' else self.description_tr,
            'url': self.url
        }


class BackupLog(db.Model):
    """Backup Log Model - Track database backups"""

    __tablename__ = 'backup_logs'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    backup_type = db.Column(db.String(20), default='manual')  # manual, automatic
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_by = db.Column(db.String(100))
    notes = db.Column(Text)

    def __repr__(self):
        return f'<BackupLog {self.filename}>'

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'filename': self.filename,
            'filepath': self.filepath,
            'file_size': self.file_size,
            'file_size_mb': round(self.file_size / (1024 * 1024), 2) if self.file_size else None,
            'backup_type': self.backup_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'notes': self.notes
        }
