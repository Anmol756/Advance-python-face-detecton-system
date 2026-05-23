"""Professors blueprint — CRUD operations for professor management."""
from flask import Blueprint

professors_bp = Blueprint('professors', __name__, template_folder='../templates')
