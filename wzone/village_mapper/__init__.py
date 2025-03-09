# android_api/__init__.py
from flask import Blueprint
village_mapper = Blueprint('village_mapper', __name__)
from . import village_mapper_routes