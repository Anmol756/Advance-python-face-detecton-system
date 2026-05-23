"""
Auth routes — login, logout, landing page, and access control decorators.
"""
from functools import wraps
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash

from app.auth import auth_bp
from app.extensions import db_connect


# --- Authentication Decorators ---

def login_required(f):
    """Decorator to protect routes requiring a logged-in user."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(roles):
    """Decorator to protect routes based on user roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session or not session['logged_in']:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))

            if 'role' not in session or session['role'] not in roles:
                flash(f'Access denied. You do not have the required role ({", ".join(roles)}).', 'danger')
                if session.get('role') == 'admin':
                    return redirect(url_for('dashboard.admin_dashboard'))
                elif session.get('role') == 'professor':
                    return redirect(url_for('dashboard.professor_dashboard'))
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# --- Routes ---

@auth_bp.route('/landing')
def landing():
    """Renders the landing page."""
    return render_template('landing.html')


@auth_bp.route('/')
def index():
    """Redirects to the landing page or the appropriate dashboard based on session."""
    if 'logged_in' in session and session['logged_in']:
        if session['role'] == 'admin':
            return redirect(url_for('dashboard.admin_dashboard'))
        elif session['role'] == 'professor':
            return redirect(url_for('dashboard.professor_dashboard'))
    return redirect(url_for('auth.landing'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if 'logged_in' in session and session['logged_in']:
        if session['role'] == 'admin':
            return redirect(url_for('dashboard.admin_dashboard'))
        elif session['role'] == 'professor':
            return redirect(url_for('dashboard.professor_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = db_connect()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Logged in as {user["username"]} ({user["role"]}).', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('dashboard.admin_dashboard'))
            elif user['role'] == 'professor':
                return redirect(url_for('dashboard.professor_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logs out the current user."""
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
