"""
Professors routes — CRUD operations for professor management.
"""
import sqlite3

from flask import render_template, request, redirect, url_for, flash

from app.professors import professors_bp
from app.extensions import db_connect
from app.face_utils import image_to_base64
from app.auth.routes import login_required, role_required


@professors_bp.route('/professors')
@login_required
@role_required(roles=['admin'])
def view_professors():
    """Displays a list of all registered professors."""
    conn = db_connect()
    prof_list = conn.execute("SELECT * FROM professors ORDER BY name").fetchall()
    conn.close()
    return render_template('professors/professors.html', professors=prof_list)


@professors_bp.route('/add_professor', methods=['GET', 'POST'])
@login_required
@role_required(roles=['admin'])
def add_professor():
    """Handles adding a new professor, including their photo (base64)."""
    if request.method == 'POST':
        prof_id = request.form['prof_id'].strip()
        name = request.form['name'].strip()
        department = request.form['department'].strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        qualification = request.form.get('qualification', '').strip()
        experience = request.form.get('experience', '').strip()
        achievements = request.form.get('achievements', '').strip()
        others = request.form.get('others', '').strip()

        photo_upload_method = request.form.get('photo_upload_method')
        photo_data_b64 = None

        if photo_upload_method == 'file_upload':
            photo_file = request.files.get('photo_file')
            if photo_file and photo_file.filename != '':
                photo_data_b64 = image_to_base64(photo_file.stream)
                if photo_data_b64 is None:
                    flash("Could not process the uploaded photo file.", "danger")
                    return render_template('professors/add_professor.html', **request.form)
            else:
                flash("No photo file was uploaded.", "warning")
                return render_template('professors/add_professor.html', **request.form)
        elif photo_upload_method == 'camera_capture':
            captured_photo_data = request.form.get('photo_data_capture')
            if captured_photo_data:
                if ',' in captured_photo_data:
                    header, base64_string = captured_photo_data.split(',', 1)
                    photo_data_b64 = base64_string
                else:
                    photo_data_b64 = captured_photo_data

                if photo_data_b64 is None or photo_data_b64 == "":
                    flash("Could not process captured photo.", "danger")
                    return render_template('professors/add_professor.html', **request.form)
            else:
                flash("No photo was captured from the camera.", "warning")
                return render_template('professors/add_professor.html', **request.form)
        else:
            flash("No photo upload method selected.", "danger")
            return render_template('professors/add_professor.html', **request.form)

        if not all((prof_id, name, department)):
            flash("Professor ID, Name, and Department are required.", "danger")
            return render_template('professors/add_professor.html', **request.form)

        try:
            conn = db_connect()
            conn.execute("""
                INSERT INTO professors
                (prof_id, name, department, email, mobile, qualification, experience, achievements, others, photo_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (prof_id, name, department, email, mobile, qualification, experience, achievements, others, photo_data_b64))
            conn.commit()
            conn.close()
            flash(f"Professor '{name}' added successfully!", "success")
            return redirect(url_for('professors.view_professors'))
        except sqlite3.IntegrityError:
            flash(f"A professor with ID '{prof_id}' already exists.", "danger")
            return render_template('professors/add_professor.html', **request.form)
        except Exception as e:
            flash(f"An unexpected error occurred: {e}", "danger")
            return render_template('professors/add_professor.html', **request.form)

    return render_template('professors/add_professor.html')


@professors_bp.route('/edit_professor_profile/<prof_id>', methods=['GET', 'POST'])
@login_required
@role_required(roles=['admin'])
def edit_professor_profile(prof_id):
    conn = db_connect()
    professor = conn.execute("SELECT * FROM professors WHERE prof_id = ?", (prof_id,)).fetchone()
    conn.close()

    if not professor:
        flash(f"Professor with ID {prof_id} not found.", "danger")
        return redirect(url_for('professors.view_professors'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        department = request.form['department'].strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        qualification = request.form.get('qualification', '').strip()
        experience = request.form.get('experience', '').strip()
        achievements = request.form.get('achievements', '').strip()
        others = request.form.get('others', '').strip()

        photo_upload_method = request.form.get('photo_upload_method')
        photo_data_to_save = None

        if photo_upload_method == 'file_upload':
            photo_file = request.files.get('photo_file')
            if photo_file and photo_file.filename != '':
                photo_data_to_save = image_to_base64(photo_file.stream)
                if photo_data_to_save is None:
                    flash("Could not process the uploaded photo file.", "danger")
                    return render_template('professors/edit_professor_profile.html', professor=professor, **request.form)
            else:
                photo_data_to_save = professor['photo_data']
        elif photo_upload_method == 'camera_capture':
            captured_photo_data = request.form.get('photo_data_capture')
            if captured_photo_data:
                if ',' in captured_photo_data:
                    header, base64_string = captured_photo_data.split(',', 1)
                    photo_data_to_save = base64_string
                else:
                    photo_data_to_save = captured_photo_data
                if photo_data_to_save is None or photo_data_to_save == "":
                    flash("Could not process captured photo.", "danger")
                    return render_template('professors/edit_professor_profile.html', professor=professor, **request.form)
            else:
                photo_data_to_save = professor['photo_data']
        elif photo_upload_method == 'keep_current':
            photo_data_to_save = professor['photo_data']
        elif photo_upload_method == 'clear_photo':
            photo_data_to_save = None
        else:
            flash("Invalid photo upload method selected.", "danger")
            return render_template('professors/edit_professor_profile.html', professor=professor, **request.form)

        try:
            conn = db_connect()
            conn.execute("""
                UPDATE professors SET
                    name = ?, department = ?, email = ?, mobile = ?,
                    qualification = ?, experience = ?, achievements = ?, others = ?, photo_data = ?
                WHERE prof_id = ?
            """, (name, department, email, mobile, qualification, experience, achievements, others, photo_data_to_save, prof_id))
            conn.commit()
            conn.close()
            flash(f"Professor '{name}' profile updated successfully!", "success")
            return redirect(url_for('professors.view_professor_profile', prof_id=prof_id))
        except Exception as e:
            flash(f"Error updating professor profile: {e}", "danger")
            return render_template('professors/edit_professor_profile.html', professor=professor, **request.form)

    return render_template('professors/edit_professor_profile.html', professor=professor)


@professors_bp.route('/delete_professor/<prof_id>', methods=['POST'])
@login_required
@role_required(roles=['admin'])
def delete_professor(prof_id):
    conn = db_connect()
    try:
        schedule_count = conn.execute("SELECT COUNT(*) FROM schedule WHERE prof_id = ?", (prof_id,)).fetchone()[0]
        if schedule_count > 0:
            flash(f"Cannot delete professor {prof_id}. They are assigned to {schedule_count} periods.", "danger")
            return redirect(url_for('professors.view_professors'))

        attendance_count = conn.execute(
            "SELECT COUNT(*) FROM attendance_logs WHERE prof_name = (SELECT name FROM professors WHERE prof_id = ?)",
            (prof_id,)
        ).fetchone()[0]
        if attendance_count > 0:
            flash(f"Cannot delete professor {prof_id}. They are referenced in {attendance_count} attendance records.", "danger")
            return redirect(url_for('professors.view_professors'))

        cursor = conn.cursor()
        cursor.execute("DELETE FROM professors WHERE prof_id = ?", (prof_id,))
        conn.commit()
        flash(f"Professor {prof_id} deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting professor {prof_id}: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('professors.view_professors'))


@professors_bp.route('/professor_profile/<prof_id>', methods=['GET'])
@login_required
@role_required(roles=['admin'])
def view_professor_profile(prof_id):
    conn = db_connect()
    professor = conn.execute("SELECT * FROM professors WHERE prof_id = ?", (prof_id,)).fetchone()
    conn.close()
    if not professor:
        flash(f"Professor with ID {prof_id} not found.", "danger")
        return redirect(url_for('professors.view_professors'))

    return render_template('professors/professor_profile.html', professor=professor)
