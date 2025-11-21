"""
Results Routes - Test result tracking and management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify, send_file
from models import db, TestResult, TestProcedure
from datetime import datetime, timedelta
from sqlalchemy import or_, func
import json

results_bp = Blueprint('results', __name__)


@results_bp.route('/')
def index():
    """List all test results with filtering"""
    language = g.get('language', 'en')

    # Get filter parameters
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    operator = request.args.get('operator', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    procedure_id = request.args.get('procedure_id', '')
    page = request.args.get('page', 1, type=int)

    # Build query
    query = TestResult.query.join(TestProcedure)

    # Apply search filter
    if search:
        query = query.filter(
            or_(
                TestProcedure.procedure_code.ilike(f'%{search}%'),
                TestResult.operator.ilike(f'%{search}%'),
                TestResult.notes.ilike(f'%{search}%')
            )
        )

    # Apply status filter
    if status:
        query = query.filter(TestResult.status == status)

    # Apply operator filter
    if operator:
        query = query.filter(TestResult.operator.ilike(f'%{operator}%'))

    # Apply procedure filter
    if procedure_id:
        query = query.filter(TestResult.procedure_id == int(procedure_id))

    # Apply date filters
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(TestResult.test_date >= date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(TestResult.test_date <= date_to_obj)
        except ValueError:
            pass

    # Order by test date (most recent first)
    query = query.order_by(TestResult.test_date.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=50, error_out=False)
    results = pagination.items

    # Get unique operators for filter
    operators = db.session.query(TestResult.operator).distinct().order_by(TestResult.operator).all()
    operators = [o[0] for o in operators]

    # Get all procedures for filter
    procedures = TestProcedure.query.filter_by(is_active=True).order_by(TestProcedure.procedure_code).all()

    return render_template(
        'results/index.html',
        results=results,
        pagination=pagination,
        operators=operators,
        procedures=procedures,
        search=search,
        status=status,
        operator=operator,
        date_from=date_from,
        date_to=date_to,
        procedure_id=procedure_id,
        language=language
    )


@results_bp.route('/<int:id>')
def view(id):
    """View single test result details"""
    language = g.get('language', 'en')
    result = TestResult.query.get_or_404(id)

    return render_template(
        'results/view.html',
        result=result,
        language=language
    )


@results_bp.route('/create', methods=['GET', 'POST'])
@results_bp.route('/create/<int:procedure_id>', methods=['GET', 'POST'])
def create(procedure_id=None):
    """Create new test result"""
    language = g.get('language', 'en')

    if request.method == 'POST':
        try:
            # Parse step results from form
            step_results = []
            step_index = 1
            while True:
                step_status = request.form.get(f'step_{step_index}_status')
                if not step_status:
                    break

                step_results.append({
                    'step': step_index,
                    'status': step_status,
                    'notes': request.form.get(f'step_{step_index}_notes', '')
                })
                step_index += 1

            # Parse measurements (JSON format)
            measurements_raw = request.form.get('measurements', '{}')
            try:
                measurements = json.loads(measurements_raw)
            except json.JSONDecodeError:
                measurements = {}

            # Create new result
            result = TestResult(
                procedure_id=int(request.form.get('procedure_id')),
                test_date=datetime.strptime(request.form.get('test_date'), '%Y-%m-%dT%H:%M') if request.form.get('test_date') else datetime.utcnow(),
                operator=request.form.get('operator'),
                status=request.form.get('status'),
                notes=request.form.get('notes'),
                observations=request.form.get('observations'),
                step_results=step_results,
                measurements=measurements,
                temperature=float(request.form.get('temperature')) if request.form.get('temperature') else None,
                humidity=float(request.form.get('humidity')) if request.form.get('humidity') else None,
                actual_duration=int(request.form.get('actual_duration')) if request.form.get('actual_duration') else None
            )

            db.session.add(result)
            db.session.commit()

            flash('Test result created successfully!', 'success')
            return redirect(url_for('results.view', id=result.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating test result: {str(e)}', 'danger')

    # Get procedure for pre-filling the form
    procedure = None
    if procedure_id:
        procedure = TestProcedure.query.get_or_404(procedure_id)
    else:
        # Get all active procedures for dropdown
        procedures = TestProcedure.query.filter_by(is_active=True).order_by(TestProcedure.procedure_code).all()

    return render_template(
        'results/create.html',
        procedure=procedure,
        procedures=procedures if not procedure else None,
        language=language
    )


@results_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit existing test result"""
    language = g.get('language', 'en')
    result = TestResult.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Update fields
            result.test_date = datetime.strptime(request.form.get('test_date'), '%Y-%m-%dT%H:%M') if request.form.get('test_date') else result.test_date
            result.operator = request.form.get('operator')
            result.status = request.form.get('status')
            result.notes = request.form.get('notes')
            result.observations = request.form.get('observations')

            # Parse step results from form
            step_results = []
            step_index = 1
            while True:
                step_status = request.form.get(f'step_{step_index}_status')
                if not step_status:
                    break

                step_results.append({
                    'step': step_index,
                    'status': step_status,
                    'notes': request.form.get(f'step_{step_index}_notes', '')
                })
                step_index += 1

            result.step_results = step_results

            # Parse measurements (JSON format)
            measurements_raw = request.form.get('measurements', '{}')
            try:
                result.measurements = json.loads(measurements_raw)
            except json.JSONDecodeError:
                result.measurements = {}

            result.temperature = float(request.form.get('temperature')) if request.form.get('temperature') else None
            result.humidity = float(request.form.get('humidity')) if request.form.get('humidity') else None
            result.actual_duration = int(request.form.get('actual_duration')) if request.form.get('actual_duration') else None
            result.updated_at = datetime.utcnow()

            db.session.commit()

            flash('Test result updated successfully!', 'success')
            return redirect(url_for('results.view', id=result.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating test result: {str(e)}', 'danger')

    return render_template(
        'results/edit.html',
        result=result,
        language=language
    )


@results_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete test result"""
    result = TestResult.query.get_or_404(id)

    try:
        db.session.delete(result)
        db.session.commit()
        flash('Test result deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting test result: {str(e)}', 'danger')

    return redirect(url_for('results.index'))


@results_bp.route('/export')
def export():
    """Export test results to CSV"""
    import csv
    import io
    from flask import make_response

    language = g.get('language', 'en')

    # Get filter parameters (same as index)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    operator = request.args.get('operator', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    procedure_id = request.args.get('procedure_id', '')

    # Build query (same logic as index)
    query = TestResult.query.join(TestProcedure)

    if search:
        query = query.filter(
            or_(
                TestProcedure.procedure_code.ilike(f'%{search}%'),
                TestResult.operator.ilike(f'%{search}%'),
                TestResult.notes.ilike(f'%{search}%')
            )
        )

    if status:
        query = query.filter(TestResult.status == status)

    if operator:
        query = query.filter(TestResult.operator.ilike(f'%{operator}%'))

    if procedure_id:
        query = query.filter(TestResult.procedure_id == int(procedure_id))

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(TestResult.test_date >= date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(TestResult.test_date <= date_to_obj)
        except ValueError:
            pass

    query = query.order_by(TestResult.test_date.desc())
    results = query.all()

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    header = ['ID', 'Procedure Code', 'Procedure Title', 'Test Date', 'Operator', 'Status', 'Duration (min)', 'Temperature', 'Humidity', 'Notes']
    writer.writerow(header)

    # Write data
    for result in results:
        procedure_title = result.procedure.title_tr if language == 'tr' else result.procedure.title_en
        row = [
            result.id,
            result.procedure.procedure_code,
            procedure_title,
            result.test_date.strftime('%Y-%m-%d %H:%M') if result.test_date else '',
            result.operator,
            result.status,
            result.actual_duration or '',
            result.temperature or '',
            result.humidity or '',
            result.notes or ''
        ]
        writer.writerow(row)

    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response


@results_bp.route('/api/procedure/<int:procedure_id>')
def api_procedure_details(procedure_id):
    """API endpoint to get procedure details for result form"""
    language = g.get('language', 'en')
    procedure = TestProcedure.query.get_or_404(procedure_id)

    return jsonify(procedure.to_dict(language=language))
