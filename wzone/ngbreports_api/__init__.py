# admin_api/__init__.py
from flask import Blueprint

ngbreports_api = Blueprint('ngbreports_api', __name__)

from . import ngbreports_routes