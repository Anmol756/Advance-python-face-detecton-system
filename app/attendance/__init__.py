"""Attendance blueprint — live, manual, logs, export, and AI insights."""
from flask import Blueprint

attendance_bp = Blueprint('attendance', __name__, template_folder='../templates')
