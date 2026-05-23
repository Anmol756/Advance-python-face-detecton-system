"""Auth blueprint — login, logout, landing page, and access control decorators."""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='../templates')
