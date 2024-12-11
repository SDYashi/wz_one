# integration_api/__init__.py
from flask import Blueprint

integration_api = Blueprint('integration_api', __name__)

from . import integration_routes