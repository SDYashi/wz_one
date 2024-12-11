# android_api/__init__.py
from flask import Blueprint

android_api = Blueprint('android_api', __name__)

from . import android_routes