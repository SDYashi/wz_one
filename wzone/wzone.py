import base64
import datetime
import json
import os
import socket
import subprocess
import time
from flask import Config, Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, decode_token, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
import bcrypt
import requests
from myservices_oneapp.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices_oneapp.myserv_update_users_logs import myserv_update_users_logs
from myservices_oneapp.myserv_connection_mongodb import myserv_connection_mongodb
from myservices_oneapp.myserv_update_users_api_logs import myserv_update_users_api_logs
from admin_api import admin_api
from android_api import android_api
from integration_api import integration_api
from ngbreports_api import ngbreports_api
from village_mapper import village_mapper
from myservices_oneapp.myserv_varriable_list import myserv_varriable_list
import pymongo
# register app with flask
app = Flask(__name__)
startup_executed = False
CORS(app, resources={r"*": {"origins": "http://localhost:4200"}})
app.config['JWT_SECRET_KEY'] = myserv_varriable_list.JWT_SECRET_KEY
jwt = JWTManager(app)
app.register_blueprint(admin_api, url_prefix='/admin')
app.register_blueprint(android_api, url_prefix='/android')
app.register_blueprint(integration_api, url_prefix='/integration')
app.register_blueprint(ngbreports_api, url_prefix='/ngbreports_api')
app.register_blueprint( village_mapper, url_prefix='/village_mapping')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, debug=True, threaded=True)

