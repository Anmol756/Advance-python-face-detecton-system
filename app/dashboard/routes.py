"""
Dashboard routes — admin and professor dashboard views with enhanced data queries.
"""
import json
from datetime import datetime, timedelta

import pytz
from flask import render_template, redirect, url_for, session

from app.dashboard import dashboard_bp
from app.extensions import db_connect
from app.auth.routes import login_required, role_required
import config


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Redirects to the specific admin or professor dashboard."""
    if session.get('role') == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    elif session.get('role') == 'professor':
        return redirect(url_for('dashboard.professor_dashboard'))
    else:
        from flask import flash
        flash("Unauthorized access. Your role is not recognized.", "danger")
        return redirect(url_for('auth.login'))


@dashboard_bp.route('/admin_dashboard')
@login_required
@role_required(roles=['admin'])
def admin_dashboard():
    """Renders the admin dashboard with summary statistics, charts, and recent activity."""
    local_tz = pytz.timezone(config.TIMEZONE)
    local_now = datetime.now(local_tz)
    local_today_str = local_now.strftime('%Y-%m-%d')

    conn = db_connect()

    # --- Basic Counts ---
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_professors = conn.execute("SELECT COUNT(*) FROM professors").fetchone()[0]
    total_periods = conn.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]
    today_attendance = conn.execute(
        "SELECT COUNT(*) FROM attendance_logs WHERE date(timestamp) = ?",
        (local_today_str,)
    ).fetchone()[0]

    # --- Last 7 Days Attendance Data (for Chart) ---
    attendance_chart_labels = []
    attendance_chart_data = []
    for i in range(6, -1, -1):
        day = local_now - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        day_label = day.strftime('%a %d')  # e.g., "Mon 19"
        count = conn.execute(
            "SELECT COUNT(*) FROM attendance_logs WHERE date(timestamp) = ?",
            (day_str,)
        ).fetchone()[0]
        attendance_chart_labels.append(day_label)
        attendance_chart_data.append(count)

    # --- Branch Distribution (for Doughnut Chart) ---
    branch_rows = conn.execute(
        "SELECT branch, COUNT(*) as cnt FROM students WHERE branch IS NOT NULL GROUP BY branch ORDER BY cnt DESC"
    ).fetchall()
    branch_labels = [row['branch'] for row in branch_rows]
    branch_data = [row['cnt'] for row in branch_rows]

    # --- Recent Activity (last 10 logs) ---
    recent_logs = conn.execute(
        "SELECT student_name, student_roll_no, period_name, prof_name, timestamp "
        "FROM attendance_logs ORDER BY timestamp DESC LIMIT 10"
    ).fetchall()
    recent_activity = []
    for log in recent_logs:
        recent_activity.append({
            'name': log['student_name'],
            'roll_no': log['student_roll_no'],
            'period': log['period_name'],
            'professor': log['prof_name'],
            'time': log['timestamp']
        })

    # --- Current Active Period ---
    current_period = None
    local_now_time = local_now.strftime('%H:%M')
    periods = conn.execute(
        "SELECT period_name, start_time, end_time, prof_name, branch, semester FROM schedule ORDER BY start_time"
    ).fetchall()
    for p in periods:
        if p['start_time'] <= local_now_time <= p['end_time']:
            current_period = {
                'name': p['period_name'],
                'professor': p['prof_name'],
                'start': p['start_time'],
                'end': p['end_time'],
                'branch': p['branch'],
                'semester': p['semester']
            }
            break

    conn.close()

    return render_template(
        'dashboard/admin_dashboard.html',
        total_students=total_students,
        total_professors=total_professors,
        total_periods=total_periods,
        today_attendance=today_attendance,
        attendance_chart_labels=json.dumps(attendance_chart_labels),
        attendance_chart_data=json.dumps(attendance_chart_data),
        branch_labels=json.dumps(branch_labels),
        branch_data=json.dumps(branch_data),
        recent_activity=recent_activity,
        current_period=current_period,
        current_date=local_now.strftime('%A, %B %d, %Y'),
        current_time=local_now.strftime('%I:%M %p')
    )


@dashboard_bp.route('/professor_dashboard')
@login_required
@role_required(roles=['professor', 'admin'])
def professor_dashboard():
    """Renders the professor dashboard with schedule and recent activity."""
    local_tz = pytz.timezone(config.TIMEZONE)
    local_now = datetime.now(local_tz)
    local_today_str = local_now.strftime('%Y-%m-%d')
    local_now_time = local_now.strftime('%H:%M')

    conn = db_connect()

    # --- Today's Stats ---
    today_attendance = conn.execute(
        "SELECT COUNT(*) FROM attendance_logs WHERE date(timestamp) = ?",
        (local_today_str,)
    ).fetchone()[0]

    total_periods = conn.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]

    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]

    # --- Today's Schedule ---
    schedule_today = conn.execute(
        "SELECT period_name, start_time, end_time, prof_name, branch, semester "
        "FROM schedule ORDER BY start_time"
    ).fetchall()

    schedule_items = []
    for p in schedule_today:
        is_active = p['start_time'] <= local_now_time <= p['end_time']
        is_past = p['end_time'] < local_now_time
        schedule_items.append({
            'name': p['period_name'],
            'professor': p['prof_name'],
            'start': p['start_time'],
            'end': p['end_time'],
            'branch': p['branch'],
            'semester': p['semester'],
            'is_active': is_active,
            'is_past': is_past,
        })

    # --- Recent Attendance Logs ---
    recent_logs = conn.execute(
        "SELECT student_name, student_roll_no, period_name, timestamp "
        "FROM attendance_logs ORDER BY timestamp DESC LIMIT 5"
    ).fetchall()
    recent_activity = []
    for log in recent_logs:
        recent_activity.append({
            'name': log['student_name'],
            'roll_no': log['student_roll_no'],
            'period': log['period_name'],
            'time': log['timestamp']
        })

    conn.close()

    return render_template(
        'dashboard/professor_dashboard.html',
        today_attendance=today_attendance,
        total_periods=total_periods,
        total_students=total_students,
        schedule_items=schedule_items,
        recent_activity=recent_activity,
        current_date=local_now.strftime('%A, %B %d, %Y'),
        current_time=local_now.strftime('%I:%M %p')
    )
