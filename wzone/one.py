# app.py
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from config import Config
from admin_api import admin_api
from android_api import android_api
from integration_api import integration_api

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_object(Config)
mongo = PyMongo(app)
# Register blueprints
app.register_blueprint(admin_api, url_prefix='/admin')
app.register_blueprint(android_api, url_prefix='/android')
app.register_blueprint(integration_api, url_prefix='/integration')

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)