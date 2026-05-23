"""Dashboard blueprint — admin and professor dashboard views."""
from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')
