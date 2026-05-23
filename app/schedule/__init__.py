"""Schedule blueprint — period management and session configuration."""
from flask import Blueprint

schedule_bp = Blueprint('schedule', __name__, template_folder='../templates')
