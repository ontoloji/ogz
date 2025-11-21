"""
Procedures Routes - CRUD operations for test procedures
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from models import db, TestProcedure, Category, ECERegulation
from datetime import datetime
from sqlalchemy import or_

procedures_bp = Blueprint('procedures', __name__)


@procedures_bp.route('/')
def index():
    """List all test procedures with filtering and search"""
    language = g.get('language', 'en')

    # Get filter parameters
    search = request.args.get('search', '')
    level = request.args.get('level', '')
    category = request.args.get('category', '')
    status = request.args.get('status', 'active')
    page = request.args.get('page', 1, type=int)

    # Build query
    query = TestProcedure.query

    # Apply status filter
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)

    # Apply search filter
    if search:
        if language == 'tr':
            query = query.filter(
                or_(
                    TestProcedure.procedure_code.ilike(f'%{search}%'),
                    TestProcedure.title_tr.ilike(f'%{search}%'),
                    TestProcedure.purpose_tr.ilike(f'%{search}%')
                )
            )
        else:
            query = query.filter(
                or_(
                    TestProcedure.procedure_code.ilike(f'%{search}%'),
                    TestProcedure.title_en.ilike(f'%{search}%'),
                    TestProcedure.purpose_en.ilike(f'%{search}%')
                )
            )

    # Apply level filter
    if level:
        query = query.filter_by(level=level)

    # Apply category filter
    if category:
        query = query.filter_by(category=category)

    # Order by procedure code
    query = query.order_by(TestProcedure.procedure_code)

    # Paginate
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    procedures = pagination.items

    # Get unique values for filters
    levels = db.session.query(TestProcedure.level).distinct().all()
    levels = [l[0] for l in levels]

    categories = db.session.query(TestProcedure.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template(
        'procedures/index.html',
        procedures=procedures,
        pagination=pagination,
        levels=levels,
        categories=categories,
        search=search,
        level=level,
        category=category,
        status=status,
        language=language
    )


@procedures_bp.route('/<int:id>')
def view(id):
    """View single test procedure details"""
    language = g.get('language', 'en')
    procedure = TestProcedure.query.get_or_404(id)

    # Get test results for this procedure
    results = procedure.test_results
    results_count = len(results)

    # Calculate statistics
    pass_count = sum(1 for r in results if r.status == 'PASS')
    fail_count = sum(1 for r in results if r.status == 'FAIL')
    pass_rate = round((pass_count / results_count * 100), 1) if results_count > 0 else 0

    return render_template(
        'procedures/view.html',
        procedure=procedure,
        results=results[:10],  # Show only last 10 results
        results_count=results_count,
        pass_count=pass_count,
        fail_count=fail_count,
        pass_rate=pass_rate,
        language=language
    )


@procedures_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create new test procedure"""
    language = g.get('language', 'en')

    if request.method == 'POST':
        try:
            # Parse steps from form
            steps_en = []
            steps_tr = []

            step_index = 1
            while True:
                step_desc_en = request.form.get(f'step_{step_index}_desc_en')
                if not step_desc_en:
                    break

                steps_en.append({
                    'step': step_index,
                    'description': step_desc_en,
                    'expected': request.form.get(f'step_{step_index}_expected_en', '')
                })

                steps_tr.append({
                    'step': step_index,
                    'description': request.form.get(f'step_{step_index}_desc_tr', ''),
                    'expected': request.form.get(f'step_{step_index}_expected_tr', '')
                })

                step_index += 1

            # Parse equipment list
            equipment_raw = request.form.get('required_equipment', '')
            equipment = [e.strip() for e in equipment_raw.split('\n') if e.strip()]

            # Parse ECE regulations
            ece_raw = request.form.get('ece_regulations', '')
            ece_regulations = [e.strip() for e in ece_raw.split(',') if e.strip()]

            # Parse prerequisites
            prereq_raw = request.form.get('prerequisites', '')
            prerequisites = []
            if prereq_raw:
                prerequisites = [int(p.strip()) for p in prereq_raw.split(',') if p.strip().isdigit()]

            # Create new procedure
            procedure = TestProcedure(
                procedure_code=request.form.get('procedure_code'),
                title_en=request.form.get('title_en'),
                title_tr=request.form.get('title_tr'),
                level=request.form.get('level'),
                category=request.form.get('category'),
                purpose_en=request.form.get('purpose_en'),
                purpose_tr=request.form.get('purpose_tr'),
                steps_en=steps_en,
                steps_tr=steps_tr,
                acceptance_criteria_en=request.form.get('acceptance_criteria_en'),
                acceptance_criteria_tr=request.form.get('acceptance_criteria_tr'),
                required_equipment=equipment,
                ece_regulations=ece_regulations,
                estimated_duration=int(request.form.get('estimated_duration', 0)) or None,
                prerequisites=prerequisites,
                is_active=request.form.get('is_active') == 'on',
                created_by=request.form.get('created_by', 'User')
            )

            db.session.add(procedure)
            db.session.commit()

            flash('Test procedure created successfully!', 'success')
            return redirect(url_for('procedures.view', id=procedure.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating procedure: {str(e)}', 'danger')

    # Get available categories and regulations for the form
    categories = Category.query.all()
    regulations = ECERegulation.query.all()

    return render_template(
        'procedures/create.html',
        categories=categories,
        regulations=regulations,
        language=language
    )


@procedures_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit existing test procedure"""
    language = g.get('language', 'en')
    procedure = TestProcedure.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Update basic fields
            procedure.procedure_code = request.form.get('procedure_code')
            procedure.title_en = request.form.get('title_en')
            procedure.title_tr = request.form.get('title_tr')
            procedure.level = request.form.get('level')
            procedure.category = request.form.get('category')
            procedure.purpose_en = request.form.get('purpose_en')
            procedure.purpose_tr = request.form.get('purpose_tr')
            procedure.acceptance_criteria_en = request.form.get('acceptance_criteria_en')
            procedure.acceptance_criteria_tr = request.form.get('acceptance_criteria_tr')

            # Parse steps from form
            steps_en = []
            steps_tr = []

            step_index = 1
            while True:
                step_desc_en = request.form.get(f'step_{step_index}_desc_en')
                if not step_desc_en:
                    break

                steps_en.append({
                    'step': step_index,
                    'description': step_desc_en,
                    'expected': request.form.get(f'step_{step_index}_expected_en', '')
                })

                steps_tr.append({
                    'step': step_index,
                    'description': request.form.get(f'step_{step_index}_desc_tr', ''),
                    'expected': request.form.get(f'step_{step_index}_expected_tr', '')
                })

                step_index += 1

            procedure.steps_en = steps_en
            procedure.steps_tr = steps_tr

            # Parse equipment list
            equipment_raw = request.form.get('required_equipment', '')
            procedure.required_equipment = [e.strip() for e in equipment_raw.split('\n') if e.strip()]

            # Parse ECE regulations
            ece_raw = request.form.get('ece_regulations', '')
            procedure.ece_regulations = [e.strip() for e in ece_raw.split(',') if e.strip()]

            # Parse prerequisites
            prereq_raw = request.form.get('prerequisites', '')
            prerequisites = []
            if prereq_raw:
                prerequisites = [int(p.strip()) for p in prereq_raw.split(',') if p.strip().isdigit()]
            procedure.prerequisites = prerequisites

            procedure.estimated_duration = int(request.form.get('estimated_duration', 0)) or None
            procedure.is_active = request.form.get('is_active') == 'on'
            procedure.updated_at = datetime.utcnow()

            db.session.commit()

            flash('Test procedure updated successfully!', 'success')
            return redirect(url_for('procedures.view', id=procedure.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating procedure: {str(e)}', 'danger')

    # Get available categories and regulations for the form
    categories = Category.query.all()
    regulations = ECERegulation.query.all()

    return render_template(
        'procedures/edit.html',
        procedure=procedure,
        categories=categories,
        regulations=regulations,
        language=language
    )


@procedures_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete test procedure"""
    procedure = TestProcedure.query.get_or_404(id)

    try:
        db.session.delete(procedure)
        db.session.commit()
        flash('Test procedure deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting procedure: {str(e)}', 'danger')

    return redirect(url_for('procedures.index'))


@procedures_bp.route('/<int:id>/toggle-status', methods=['POST'])
def toggle_status(id):
    """Toggle active/inactive status"""
    procedure = TestProcedure.query.get_or_404(id)

    try:
        procedure.is_active = not procedure.is_active
        procedure.updated_at = datetime.utcnow()
        db.session.commit()

        status = 'activated' if procedure.is_active else 'deactivated'
        flash(f'Test procedure {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating status: {str(e)}', 'danger')

    return redirect(url_for('procedures.view', id=id))


@procedures_bp.route('/api/search')
def api_search():
    """API endpoint for autocomplete search"""
    query = request.args.get('q', '')
    language = g.get('language', 'en')

    if len(query) < 2:
        return jsonify([])

    # Search procedures
    if language == 'tr':
        procedures = TestProcedure.query.filter(
            or_(
                TestProcedure.procedure_code.ilike(f'%{query}%'),
                TestProcedure.title_tr.ilike(f'%{query}%')
            )
        ).filter_by(is_active=True).limit(10).all()
    else:
        procedures = TestProcedure.query.filter(
            or_(
                TestProcedure.procedure_code.ilike(f'%{query}%'),
                TestProcedure.title_en.ilike(f'%{query}%')
            )
        ).filter_by(is_active=True).limit(10).all()

    results = [
        {
            'id': p.id,
            'code': p.procedure_code,
            'title': p.title_tr if language == 'tr' else p.title_en
        }
        for p in procedures
    ]

    return jsonify(results)
