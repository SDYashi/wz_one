import base64
import datetime
import json
import os
import time
from flask import Config, Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager,create_access_token, decode_token, jwt_required, get_jwt_identity,get_jwt
from flask_cors import CORS
import bcrypt
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices.myserv_update_users_logs import myserv_update_users_logs
from myservices.myserv_connection_mongodb import myserv_connection_mongodb
from myservices.myserv_update_users_api_logs import myserv_update_users_api_logs
from admin_api import admin_api
from android_api import android_api
from integration_api import integration_api

#register app with flask
app = Flask(__name__)

# cross origin allow for applications
CORS(app, resources={r"/*": {"origins": "*"}})

# # jwt token configuration
# # app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] ='8ff09627ca698e84a587ccd3ae005f625ece33b3c999062e62dbf6e70c722323'  
jwt = JWTManager(app)

app.config.from_object(Config)
app.register_blueprint(admin_api, url_prefix='/admin')
app.register_blueprint(android_api, url_prefix='/android')
app.register_blueprint(integration_api, url_prefix='/integration')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
