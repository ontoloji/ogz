"""
Backup Routes - Database backup and restore functionality
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g, send_file, current_app
from models import db, BackupLog
from datetime import datetime
import shutil
import os
from pathlib import Path

backup_bp = Blueprint('backup', __name__)


@backup_bp.route('/')
def index():
    """List all backups"""
    language = g.get('language', 'en')

    # Get all backup logs
    backups = BackupLog.query.order_by(BackupLog.created_at.desc()).all()

    # Check if backup files still exist
    for backup in backups:
        backup.file_exists = os.path.exists(backup.filepath)

    return render_template(
        'backup/index.html',
        backups=backups,
        language=language
    )


@backup_bp.route('/create', methods=['POST'])
def create():
    """Create a new database backup"""
    language = g.get('language', 'en')

    try:
        # Get database path
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        if not db_uri.startswith('sqlite:///'):
            flash('Backup is only supported for SQLite databases', 'warning')
            return redirect(url_for('backup.index'))

        db_path = db_uri.replace('sqlite:///', '')

        # Create backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.db'
        backup_folder = Path(current_app.config['BACKUP_FOLDER'])
        backup_filepath = backup_folder / backup_filename

        # Copy database file
        shutil.copy2(db_path, backup_filepath)

        # Get file size
        file_size = os.path.getsize(backup_filepath)

        # Create backup log entry
        backup_log = BackupLog(
            filename=backup_filename,
            filepath=str(backup_filepath),
            file_size=file_size,
            backup_type=request.form.get('backup_type', 'manual'),
            created_by=request.form.get('created_by', 'User'),
            notes=request.form.get('notes', '')
        )

        db.session.add(backup_log)
        db.session.commit()

        # Clean up old backups if limit exceeded
        cleanup_old_backups()

        flash('Database backup created successfully!', 'success')

    except Exception as e:
        flash(f'Error creating backup: {str(e)}', 'danger')

    return redirect(url_for('backup.index'))


@backup_bp.route('/download/<int:id>')
def download(id):
    """Download a backup file"""
    backup = BackupLog.query.get_or_404(id)

    if not os.path.exists(backup.filepath):
        flash('Backup file not found', 'danger')
        return redirect(url_for('backup.index'))

    return send_file(
        backup.filepath,
        as_attachment=True,
        download_name=backup.filename,
        mimetype='application/octet-stream'
    )


@backup_bp.route('/restore/<int:id>', methods=['POST'])
def restore(id):
    """Restore database from backup"""
    language = g.get('language', 'en')
    backup = BackupLog.query.get_or_404(id)

    try:
        # Verify backup file exists
        if not os.path.exists(backup.filepath):
            flash('Backup file not found', 'danger')
            return redirect(url_for('backup.index'))

        # Get database path
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        if not db_uri.startswith('sqlite:///'):
            flash('Restore is only supported for SQLite databases', 'warning')
            return redirect(url_for('backup.index'))

        db_path = db_uri.replace('sqlite:///', '')

        # Create a backup of current database before restoring
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pre_restore_backup = f'pre_restore_{timestamp}.db'
        backup_folder = Path(current_app.config['BACKUP_FOLDER'])
        pre_restore_path = backup_folder / pre_restore_backup

        shutil.copy2(db_path, pre_restore_path)

        # Create log for pre-restore backup
        pre_restore_log = BackupLog(
            filename=pre_restore_backup,
            filepath=str(pre_restore_path),
            file_size=os.path.getsize(pre_restore_path),
            backup_type='automatic',
            created_by='System',
            notes='Automatic backup before restore operation'
        )
        db.session.add(pre_restore_log)
        db.session.commit()

        # Close all database connections
        db.session.close()
        db.engine.dispose()

        # Restore the backup
        shutil.copy2(backup.filepath, db_path)

        flash('Database restored successfully! Application will restart...', 'success')

    except Exception as e:
        flash(f'Error restoring backup: {str(e)}', 'danger')

    return redirect(url_for('backup.index'))


@backup_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """Delete a backup"""
    backup = BackupLog.query.get_or_404(id)

    try:
        # Delete file if exists
        if os.path.exists(backup.filepath):
            os.remove(backup.filepath)

        # Delete log entry
        db.session.delete(backup)
        db.session.commit()

        flash('Backup deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting backup: {str(e)}', 'danger')

    return redirect(url_for('backup.index'))


def cleanup_old_backups():
    """Clean up old backups if limit exceeded"""
    max_backups = current_app.config.get('MAX_BACKUP_FILES', 10)

    # Get all backups ordered by date
    backups = BackupLog.query.order_by(BackupLog.created_at.desc()).all()

    # If we have more than max, delete oldest ones
    if len(backups) > max_backups:
        backups_to_delete = backups[max_backups:]

        for backup in backups_to_delete:
            try:
                # Delete file if exists
                if os.path.exists(backup.filepath):
                    os.remove(backup.filepath)

                # Delete log entry
                db.session.delete(backup)

            except Exception as e:
                print(f"Error deleting old backup {backup.filename}: {e}")

        db.session.commit()


@backup_bp.route('/upload', methods=['POST'])
def upload():
    """Upload a backup file"""
    language = g.get('language', 'en')

    if 'backup_file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('backup.index'))

    file = request.files['backup_file']

    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('backup.index'))

    if not file.filename.endswith('.db'):
        flash('Invalid file format. Only .db files are allowed', 'danger')
        return redirect(url_for('backup.index'))

    try:
        # Save uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'uploaded_{timestamp}.db'
        backup_folder = Path(current_app.config['BACKUP_FOLDER'])
        backup_filepath = backup_folder / backup_filename

        file.save(backup_filepath)

        # Get file size
        file_size = os.path.getsize(backup_filepath)

        # Create backup log entry
        backup_log = BackupLog(
            filename=backup_filename,
            filepath=str(backup_filepath),
            file_size=file_size,
            backup_type='manual',
            created_by=request.form.get('created_by', 'User'),
            notes=f'Uploaded file: {file.filename}'
        )

        db.session.add(backup_log)
        db.session.commit()

        flash('Backup file uploaded successfully!', 'success')

    except Exception as e:
        flash(f'Error uploading backup: {str(e)}', 'danger')

    return redirect(url_for('backup.index'))
