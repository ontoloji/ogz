"""
Dashboard Routes - Overview and statistics
"""

from flask import Blueprint, render_template, g
from sqlalchemy import func
from models import db, TestProcedure, TestResult, Category
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Dashboard home page with statistics"""
    language = g.get('language', 'en')

    # Statistics
    total_procedures = TestProcedure.query.filter_by(is_active=True).count()
    total_results = TestResult.query.count()

    # Results by status
    pass_count = TestResult.query.filter_by(status='PASS').count()
    fail_count = TestResult.query.filter_by(status='FAIL').count()
    partial_count = TestResult.query.filter_by(status='PARTIAL').count()

    # Calculate pass rate
    pass_rate = round((pass_count / total_results * 100), 1) if total_results > 0 else 0

    # Recent test results (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_results = TestResult.query.filter(
        TestResult.test_date >= seven_days_ago
    ).order_by(TestResult.test_date.desc()).limit(10).all()

    # Tests by category
    category_stats = db.session.query(
        TestProcedure.category,
        func.count(TestProcedure.id).label('count')
    ).filter(
        TestProcedure.is_active == True
    ).group_by(
        TestProcedure.category
    ).all()

    # Tests by level
    level_stats = db.session.query(
        TestProcedure.level,
        func.count(TestProcedure.id).label('count')
    ).filter(
        TestProcedure.is_active == True
    ).group_by(
        TestProcedure.level
    ).all()

    # Most tested procedures (top 5)
    most_tested = db.session.query(
        TestProcedure,
        func.count(TestResult.id).label('test_count')
    ).join(
        TestResult
    ).group_by(
        TestProcedure.id
    ).order_by(
        func.count(TestResult.id).desc()
    ).limit(5).all()

    # Recent activity (procedures updated in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_procedures = TestProcedure.query.filter(
        TestProcedure.updated_at >= thirty_days_ago
    ).order_by(TestProcedure.updated_at.desc()).limit(5).all()

    # Test completion trend (last 30 days)
    completion_trend = []
    for i in range(30, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        count = TestResult.query.filter(
            TestResult.test_date >= date_start,
            TestResult.test_date <= date_end
        ).count()

        completion_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })

    return render_template(
        'dashboard/index.html',
        total_procedures=total_procedures,
        total_results=total_results,
        pass_count=pass_count,
        fail_count=fail_count,
        partial_count=partial_count,
        pass_rate=pass_rate,
        recent_results=recent_results,
        category_stats=category_stats,
        level_stats=level_stats,
        most_tested=most_tested,
        recent_procedures=recent_procedures,
        completion_trend=completion_trend,
        language=language
    )


@dashboard_bp.route('/statistics')
def statistics():
    """Detailed statistics page"""
    language = g.get('language', 'en')

    # Comprehensive statistics
    stats = {
        'procedures': {
            'total': TestProcedure.query.count(),
            'active': TestProcedure.query.filter_by(is_active=True).count(),
            'inactive': TestProcedure.query.filter_by(is_active=False).count(),
        },
        'results': {
            'total': TestResult.query.count(),
            'pass': TestResult.query.filter_by(status='PASS').count(),
            'fail': TestResult.query.filter_by(status='FAIL').count(),
            'partial': TestResult.query.filter_by(status='PARTIAL').count(),
        },
        'categories': Category.query.count(),
    }

    # Operator statistics
    operator_stats = db.session.query(
        TestResult.operator,
        func.count(TestResult.id).label('total_tests'),
        func.sum(func.case((TestResult.status == 'PASS', 1), else_=0)).label('pass_count')
    ).group_by(
        TestResult.operator
    ).order_by(
        func.count(TestResult.id).desc()
    ).all()

    # Monthly test trend (last 12 months)
    monthly_trend = []
    for i in range(11, -1, -1):
        # Calculate first day of month
        target_date = datetime.utcnow().replace(day=1) - timedelta(days=i * 30)
        month_start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate last day of month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(seconds=1)

        count = TestResult.query.filter(
            TestResult.test_date >= month_start,
            TestResult.test_date <= month_end
        ).count()

        monthly_trend.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })

    return render_template(
        'dashboard/statistics.html',
        stats=stats,
        operator_stats=operator_stats,
        monthly_trend=monthly_trend,
        language=language
    )
