"""
Schedule routes — period management and session configuration.
"""
from flask import render_template, request, redirect, url_for, flash, session

from app.schedule import schedule_bp
from app.extensions import db_connect, get_distinct_from_db
from app.auth.routes import login_required, role_required


@schedule_bp.route('/schedule', methods=['GET', 'POST'])
@login_required
@role_required(roles=['admin', 'professor'])
def manage_schedule():
    conn = db_connect()
    if request.method == 'POST':
        period_name = request.form['period_name'].strip()
        start_time = request.form['start_time'].strip()
        end_time = request.form['end_time'].strip()
        prof_id = request.form['prof_id']
        period_description = request.form.get('description', '').strip()

        branch = request.form.get('branch', '').strip()
        semester = request.form.get('semester')
        try:
            semester = int(semester) if semester else None
        except ValueError:
            flash("Semester must be a valid number.", "danger")
            schedule_list = conn.execute("SELECT * FROM schedule ORDER BY start_time").fetchall()
            prof_list = conn.execute("SELECT prof_id, name FROM professors ORDER BY name").fetchall()
            available_branches = get_distinct_from_db('branch', 'students')
            available_semesters = get_distinct_from_db('semester', 'students')
            conn.close()
            return render_template('schedule/schedule.html',
                                   schedule=schedule_list,
                                   professors=prof_list,
                                   available_branches=available_branches,
                                   available_semesters=available_semesters,
                                   form_data=request.form)

        prof_record = conn.execute("SELECT name FROM professors WHERE prof_id = ?", (prof_id,)).fetchone()
        prof_name = prof_record['name'] if prof_record else "N/A"

        try:
            conn.execute("""
                INSERT INTO schedule (period_name, start_time, end_time, prof_id, prof_name, description, branch, semester)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (period_name, start_time, end_time, prof_id, prof_name, period_description, branch, semester))
            conn.commit()
            conn.close()
            flash(f"Period '{period_name}' added to the schedule.", "success")
            return redirect(url_for('schedule.manage_schedule'))
        except Exception as e:
            flash(f"Error adding period: {e}", "danger")
            schedule_list = conn.execute("SELECT * FROM schedule ORDER BY start_time").fetchall()
            prof_list = conn.execute("SELECT prof_id, name FROM professors ORDER BY name").fetchall()
            available_branches = get_distinct_from_db('branch', 'students')
            available_semesters = get_distinct_from_db('semester', 'students')
            conn.close()
            return render_template('schedule/schedule.html',
                                   schedule=schedule_list,
                                   professors=prof_list,
                                   available_branches=available_branches,
                                   available_semesters=available_semesters,
                                   form_data=request.form)

    schedule_list = conn.execute("SELECT * FROM schedule ORDER BY start_time").fetchall()
    prof_list = conn.execute("SELECT prof_id, name FROM professors ORDER BY name").fetchall()
    available_branches = get_distinct_from_db('branch', 'students')
    available_semesters = get_distinct_from_db('semester', 'students')
    conn.close()
    return render_template('schedule/schedule.html',
                           schedule=schedule_list,
                           professors=prof_list,
                           available_branches=available_branches,
                           available_semesters=available_semesters,
                           form_data={})


@schedule_bp.route('/delete_period/<int:period_id>', methods=['POST'])
@login_required
@role_required(roles=['admin', 'professor'])
def delete_period(period_id):
    conn = db_connect()
    try:
        period_record = conn.execute("SELECT period_name FROM schedule WHERE period_id = ?", (period_id,)).fetchone()
        period_name = period_record['period_name'] if period_record else f"Period ID {period_id}"

        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance_logs WHERE period_name = ?", (period_name,))
        cursor.execute("DELETE FROM schedule WHERE period_id = ?", (period_id,))
        conn.commit()
        flash(f"Period '{period_name}' and its attendance logs deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting period '{period_name}': {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('schedule.manage_schedule'))


@schedule_bp.route('/configure', methods=['GET', 'POST'])
@login_required
@role_required(roles=['admin', 'professor'])
def configure_session():
    current_config = session.get('attendance_config')
    if request.method == 'POST':
        selected_branches = request.form.getlist('branches')
        selected_semester = request.form.get('semester')
        selected_subject = request.form.get('subject')

        if not selected_branches or not selected_semester:
            flash("You must select at least one branch and a semester.", "warning")
            return redirect(url_for('schedule.configure_session'))

        session['attendance_config'] = {
            'branches': selected_branches,
            'semester': int(selected_semester),
            'subject': selected_subject
        }
        flash(f"Session configured for Branch: {', '.join(selected_branches)}, Semester: {selected_semester}.", "success")
        return redirect(url_for('attendance.live_attendance'))

    available_branches = get_distinct_from_db('branch', 'students')
    available_semesters = get_distinct_from_db('semester', 'students')
    available_subjects = get_distinct_from_db('subject', 'students')

    return render_template('schedule/configure_session.html',
                           current_config=current_config,
                           available_branches=available_branches,
                           available_semesters=available_semesters,
                           available_subjects=available_subjects)
