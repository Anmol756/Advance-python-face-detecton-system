"""Students blueprint — CRUD operations for student management."""
from flask import Blueprint

students_bp = Blueprint('students', __name__, template_folder='../templates')
