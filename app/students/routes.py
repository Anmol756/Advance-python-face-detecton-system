"""
Students routes — CRUD operations for student management.
"""
import sqlite3
import pickle
import base64
from io import BytesIO
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash

from app.students import students_bp
from app.extensions import db_connect, get_distinct_from_db, load_face_encodings, save_face_encodings
from app.extensions import known_face_encodings, known_face_roll_numbers
from app.face_utils import process_and_encode
from app.auth.routes import login_required, role_required


@students_bp.route('/students')
@login_required
@role_required(roles=['admin'])
def view_students():
    """Displays a list of all registered students with filtering options."""
    conn = db_connect()

    filter_branch = request.args.get('branch')
    filter_semester = request.args.get('semester')

    students_query = "SELECT roll_no, name, branch, semester, admission_year FROM students WHERE 1=1"
    student_query_params = []

    if filter_branch and filter_branch != 'all':
        students_query += " AND branch = ?"
        student_query_params.append(filter_branch)

    if filter_semester and filter_semester != 'all':
        students_query += " AND semester = ?"
        student_query_params.append(filter_semester)

    students_query += " ORDER BY name"

    students_list = conn.execute(students_query, student_query_params).fetchall()

    available_branches = get_distinct_from_db('branch', 'students')
    available_semesters = get_distinct_from_db('semester', 'students')

    conn.close()
    return render_template('students/students.html',
                           students=students_list,
                           available_branches=available_branches,
                           available_semesters=available_semesters,
                           selected_branch=filter_branch,
                           selected_semester=filter_semester)


@students_bp.route('/add_student', methods=['GET', 'POST'])
@login_required
@role_required(roles=['admin'])
def add_student():
    current_year = datetime.now().year

    if request.method == 'POST':
        roll_no = request.form['roll_no'].strip()
        name = request.form['name'].strip()
        branch = request.form.get('branch', '').strip()
        semester = request.form.get('semester')
        admission_year = request.form.get('admission_year')
        subject = request.form.get('subject', '').strip()

        photo_upload_method = request.form.get('photo_upload_method')

        if not all([roll_no, name, branch, semester, admission_year]):
            flash("All fields (Roll Number, Name, Branch, Semester, Year of Admission) are required.", "danger")
            return render_template('students/add_student.html', current_year=current_year, **request.form)

        face_encoding = None
        if photo_upload_method == 'file_upload':
            photo_file = request.files.get('photo_file')
            if photo_file and photo_file.filename != '':
                face_encoding = process_and_encode(photo_file.stream)
            else:
                flash("No photo file was uploaded. Please select a photo file.", "warning")
                return render_template('students/add_student.html', current_year=current_year, **request.form)
        elif photo_upload_method == 'camera_capture':
            photo_data = request.form.get('photo_data')
            if photo_data:
                header, base64_string = photo_data.split(',', 1)
                image_bytes = base64.b64decode(base64_string)
                face_encoding = process_and_encode(BytesIO(image_bytes))
            else:
                flash("No photo was captured from the camera. Please capture a photo.", "warning")
                return render_template('students/add_student.html', current_year=current_year, **request.form)
        else:
            flash("No photo upload method selected.", "danger")
            return render_template('students/add_student.html', current_year=current_year, **request.form)

        if face_encoding is None:
            return render_template('students/add_student.html', current_year=current_year, **request.form)

        try:
            encoding_blob = pickle.dumps(face_encoding)

            with db_connect() as conn:
                conn.execute("""
                    INSERT INTO students (roll_no, name, branch, semester, admission_year, subject, face_encoding)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (roll_no, name, branch, semester, admission_year, subject, encoding_blob))
                conn.commit()

            flash(f"Student '{name}' ({roll_no}) and their face encoding have been added successfully!", "success")
            load_face_encodings()
            return redirect(url_for('students.view_students'))

        except sqlite3.IntegrityError:
            flash(f"A student with Roll Number '{roll_no}' already exists. Please use a unique Roll Number.", "danger")
        except Exception as e:
            flash(f"A database error occurred while adding student: {e}", "danger")

        return render_template('students/add_student.html', current_year=current_year, **request.form)

    return render_template('students/add_student.html', current_year=current_year)


@students_bp.route('/edit_student/<roll_no>', methods=['GET', 'POST'])
@login_required
@role_required(roles=['admin'])
def edit_student(roll_no):
    conn = db_connect()
    student = conn.execute(
        "SELECT roll_no, name, branch, semester, admission_year, subject, face_encoding FROM students WHERE roll_no = ?",
        (roll_no,)
    ).fetchone()
    conn.close()

    if not student:
        flash(f"Student with Roll Number '{roll_no}' not found.", "danger")
        return redirect(url_for('students.view_students'))

    current_year = datetime.now().year

    if request.method == 'POST':
        submitted_roll_no = request.form['roll_no'].strip()
        if submitted_roll_no != roll_no:
            flash("Attempted to change Roll Number, which is not allowed.", "danger")
            return render_template('students/edit_student.html', student=student, current_year=current_year, **request.form)

        name = request.form['name'].strip()
        branch = request.form.get('branch', '').strip()
        semester = request.form.get('semester')
        admission_year = request.form.get('admission_year')
        subject = request.form.get('subject', '').strip()

        if not all([submitted_roll_no, name, branch, semester, admission_year]):
            flash("All required fields are necessary for update.", "danger")
            return render_template('students/edit_student.html', student=student, current_year=current_year, **request.form)

        photo_upload_method = request.form.get('photo_upload_method')
        new_face_encoding_blob = None
        face_encoding_updated = False

        if photo_upload_method == 'file_upload':
            photo_file = request.files.get('photo_file')
            if photo_file and photo_file.filename != '':
                new_face_encoding = process_and_encode(photo_file.stream)
                if new_face_encoding is None:
                    return render_template('students/edit_student.html', student=student, current_year=current_year, **request.form)
                new_face_encoding_blob = pickle.dumps(new_face_encoding)
                face_encoding_updated = True
            elif student['face_encoding']:
                new_face_encoding_blob = student['face_encoding']
            else:
                flash("No photo uploaded and no existing face encoding. A photo is required.", "danger")
                return render_template('students/edit_student.html', student=student, current_year=current_year, **request.form)

        elif photo_upload_method == 'camera_capture':
            photo_data = request.form.get('photo_data')
            if photo_data:
                header, base64_string = photo_data.split(',', 1)
                image_bytes = base64.b64decode(base64_string)
                new_face_encoding = process_and_encode(BytesIO(image_bytes))
                if new_face_encoding is None:
                    return render_template('students/edit_student.html', student=student, current_year=current_year, **request.form)
                new_face_encoding_blob = pickle.dumps(new_face_encoding)
                face_encoding_updated = True
            elif student['face_encoding']:
                new_face_encoding_blob = student['face_encoding']
            else:
                flash("No photo captured and no existing face encoding. A photo is required.", "danger")
                return render_template('students/edit_student.html', student=student, current_year=current_year, **request.form)

        elif photo_upload_method == 'keep_current':
            if student['face_encoding']:
                new_face_encoding_blob = student['face_encoding']
            else:
                flash("Cannot keep current photo: no existing encoding found. Please upload a new photo.", "danger")
                return render_template('students/edit_student.html', student=student, current_year=current_year, **request.form)
        else:
            flash("Invalid photo upload method selected.", "danger")
            return render_template('students/edit_student.html', student=student, current_year=current_year, **request.form)

        try:
            conn = db_connect()
            conn.execute("""
                UPDATE students SET
                    name = ?, branch = ?, semester = ?, admission_year = ?, subject = ?, face_encoding = ?
                WHERE roll_no = ?
            """, (name, branch, semester, admission_year, subject, new_face_encoding_blob, roll_no))
            conn.commit()
            conn.close()

            flash(f"Student '{name}' ({roll_no}) details updated successfully!", "success")

            if face_encoding_updated:
                load_face_encodings()
                flash("Face encodings reloaded for live recognition.", "info")

            return redirect(url_for('students.view_students'))

        except Exception as e:
            flash(f"A database error occurred while updating student: {e}", "danger")
            return render_template('students/edit_student.html', student=student, current_year=current_year, **request.form)

    return render_template('students/edit_student.html', student=student, current_year=current_year)


@students_bp.route('/delete_student/<roll_no>', methods=['POST'])
@login_required
@role_required(roles=['admin'])
def delete_student(roll_no):
    import app.extensions as ext

    conn = db_connect()
    try:
        attendance_count = conn.execute(
            "SELECT COUNT(*) FROM attendance_logs WHERE student_roll_no = ?", (roll_no,)
        ).fetchone()[0]
        if attendance_count > 0:
            flash(f"Cannot delete student {roll_no}. They have {attendance_count} attendance records.", "danger")
            return redirect(url_for('students.view_students'))

        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
        conn.commit()

        load_face_encodings()
        flash(f"Student {roll_no} deleted successfully!", "success")

    except Exception as e:
        flash(f"Error deleting student {roll_no}: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('students.view_students'))
