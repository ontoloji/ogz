"""
PDF Export Routes - Generate PDF reports
"""

from flask import Blueprint, send_file, flash, redirect, url_for, g, current_app
from models import TestProcedure, TestResult
from pdf_export import export_procedure_pdf, export_result_pdf
from pathlib import Path
import os

pdf_bp = Blueprint('pdf', __name__)


@pdf_bp.route('/procedure/<int:id>')
def export_procedure(id):
    """Export procedure to PDF"""
    language = g.get('language', 'en')
    procedure = TestProcedure.query.get_or_404(id)

    try:
        # Create exports folder if not exists
        exports_folder = Path(current_app.config['EXPORT_FOLDER'])
        exports_folder.mkdir(exist_ok=True)

        # Generate filename
        filename = exports_folder / f"procedure_{procedure.procedure_code}_{language}.pdf"

        # Export to PDF
        export_procedure_pdf(procedure, language=language, filename=str(filename))

        # Send file
        return send_file(
            filename,
            as_attachment=True,
            download_name=f"{procedure.procedure_code}_{language}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('procedures.view', id=id))


@pdf_bp.route('/result/<int:id>')
def export_result(id):
    """Export test result to PDF"""
    language = g.get('language', 'en')
    result = TestResult.query.get_or_404(id)

    try:
        # Create exports folder if not exists
        exports_folder = Path(current_app.config['EXPORT_FOLDER'])
        exports_folder.mkdir(exist_ok=True)

        # Generate filename
        filename = exports_folder / f"result_{result.procedure.procedure_code}_{result.id}_{language}.pdf"

        # Export to PDF
        export_result_pdf(result, language=language, filename=str(filename))

        # Send file
        return send_file(
            filename,
            as_attachment=True,
            download_name=f"result_{result.procedure.procedure_code}_{result.id}_{language}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('results.view', id=id))
