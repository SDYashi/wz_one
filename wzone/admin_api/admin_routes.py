# admin_api/admin_routes.py
import datetime
import time
import bcrypt
from flask import Flask, request, jsonify
from functools import wraps
from pymongo import MongoClient
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from flask_pymongo import PyMongo
from . import admin_api
from myservices.myserv_update_mpwzintegrationusers_frommpwzusers import myserv_update_mpwzintegrationusers_frommpwzusers
from myservices.myserv_update_mpwzusers_frombiserver import myserv_update_mpwzusers_frombiserver
from myservices.myserv_send_notification import EmailSender
from myservices.myserv_connection_forblueprints import MongoCollection
from myservices.myserv_generate_secretkey_forapp import SecretKeyManager
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices.myserv_update_users_logs import myserv_update_users_logs
from myservices.myserv_update_users_api_logs import myserv_update_users_api_logs
from myservices.myserv_connection_mongodb import myserv_connection_mongodb

# define class for admin api
# class AdminAPI:
#     def __init__(self, collection_name): 
#         self.mongo_db = myserv_connection_mongodb()  
#         self.dbconnect = self.mongo_db.get_connection() 
#         self.collection = self.dbconnect[collection_name]
#         self.allowed_ips = set()  # Cached set of allowed IPs

#     def get_allowed_ips(self):
#         """Retrieve all allowed IPs from the collection, caching the result."""
#         if not self.allowed_ips:
#             print("Allowed IPs not cached, retrieving from database...")
#             self.allowed_ips = set(self.collection.distinct('ip_address'))
#             print(f"Retrieved allowed IPs: {self.allowed_ips}")
#         else:
#             print("Using cached allowed IPs.")
#         return self.allowed_ips

#     def ip_required(self, f):
#         """Decorator to restrict access based on IP address."""
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             remote_ip = request.remote_addr
#             print(f"Received request from IP: {remote_ip}")
#             allowed_ips = self.get_allowed_ips()
#             print(f"Allowed IPs: {allowed_ips}")

#             if remote_ip not in allowed_ips:
#                 print("Access denied: IP not in allowed list")
#                 return jsonify({"error": "Access denied, you are not allowed"}), 403

#             print("Access granted: IP is in allowed list")
#             return f(*args, **kwargs)

#         return decorated_function
# admin_api_validator = AdminAPI(collection_name="mpwz_iplist_adminpanel")
 
@admin_api.before_request
def before_request():
    request.start_time = time.time() 

@admin_api.after_request
def after_request(response):
    try:
        log_entry_event_api = myserv_update_users_api_logs()
        request_time = request.start_time
        response_time_seconds = time.time() - request_time
        response_time_minutes = response_time_seconds / 60  
        api_name = request.path
        server_load = log_entry_event_api.calculate_server_load() 
        log_entry = log_entry_event_api.log_api_call_status(
            api_name, 
            request_time, 
            response_time_minutes, 
            server_load, 
            response.status_code < 400
        )
        
        if log_entry: 
            print(f"Request executed {api_name} it took {response_time_minutes:.4f} minutes.")
            return response
        else:
            return response

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        log_entry_event_api.mongo_dbconnect_close()

#Admin controller api for web users
@admin_api.route('/shared-call/api/v1/create-integration-users', methods=['POST'])
# @admin_api_validator.ip_required
@jwt_required()
def create_integration_users_data():
    try:
        mpwz_integration_users = MongoCollection("mpwz_integration_users")
        log_entry_event = myserv_update_users_logs()
        seq_gen = myserv_generate_mpwz_id_forrecords()
        data = request.get_json()
        existing_user = mpwz_integration_users.find_one({"username": data.get("username")})
        if existing_user:
            return jsonify({"msg": "Username already exists", "status": "error"}), 400
        data['mpwz_id'] = seq_gen.get_next_sequence('mpwz_integration_users')  
        results = mpwz_integration_users.insert_one(data)        
        if results:
            response_data = {      "msg": f"Integration User Created successfully ",
                                    "current_api": request.full_path,
                                    "client_ip": request.remote_addr,
                                    "response_at": datetime.datetime.now().isoformat()
                        } 
            log_entry_event.log_api_call(response_data)    
            print(f"Request completed {request.full_path}")
            return jsonify({"msg": "Data inserted successfully"}), 201
        else:
            return jsonify({"msg": "No Data inserted. Something went wrong"}), 500        
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({"msg": str(e)}), 400
  
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_integration_users.mongo_dbconnect_close()
         seq_gen.mongo_dbconnect_close()

@admin_api.route('/notify-integrated-app', methods=['POST'])
# @admin_api_validator.ip_required
@jwt_required()
def post_integrated_app():
    try:
        mpwz_integrated_app = MongoCollection("mpwz_integrated_app")
        log_entry_event = myserv_update_users_logs()
        seq_gen = myserv_generate_mpwz_id_forrecords()
        username = get_jwt_identity()
        data = request.get_json()
        
        if 'app_name' not in data:
            return jsonify({"msg": "app_name is required"}), 400

        existing_record = mpwz_integrated_app.find_one({"app_name": data["app_name"]})
        if existing_record:      
            return jsonify({"msg": "Records with app_name already existed in database."}), 400
        else: 
            mpwz_id_sequenceno = seq_gen.get_next_sequence('mpwz_integrated_app')
            app_name_list = {
                "mpwz_id": mpwz_id_sequenceno,
                "app_name": data['app_name'],
                "created_by": username,
                "created_on": datetime.datetime.now().isoformat(),
                "updated_by": "NA",
                "updated_on": "NA"
            }

            result = mpwz_integrated_app.insert_one(app_name_list)
            if result:
                app_name_list['_id'] = str(result.inserted_id)
                response_data = {  
                    "msg": "New App integrated successfully",
                    "current_api": request.full_path,
                    "client_ip": request.remote_addr,
                    "response_at": datetime.datetime.now().isoformat()
                }
                log_entry_event.log_api_call(response_data) 
                print("Request completed successfully for new app integration.")
                return jsonify(app_name_list), 200
            else:
                return jsonify({"msg": "Unable to add new app details in the system, try again..."}), 500
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({"msg": f"An error occurred while processing the request. {str(e)}"}), 500
    finally: 
        log_entry_event.mongo_dbconnect_close() 
        mpwz_integrated_app.mongo_dbconnect_close()
        seq_gen.mongo_dbconnect_close()

@admin_api.route('/notify-status', methods=['POST'])
# @admin_api_validator.ip_required
@jwt_required()
def post_notify_status():
    try:
        mpwz_notify_status = MongoCollection("mpwz_notify_status")
        log_entry_event = myserv_update_users_logs()
        seq_gen = myserv_generate_mpwz_id_forrecords()
        username = get_jwt_identity()
        data = request.get_json()
        if 'button_name' not in data:
            return jsonify({"msg": "button_name is required"}), 400 
        elif'module_name' not in data:
            return jsonify({"msg": "module_name is required"}), 400 
        else:        
            existing_record = mpwz_notify_status.find_one({"button_name": data["button_name"], "module_name": data["module_name"]})
            if existing_record:      
                return jsonify({"msg": "Records with button_name already existed in database."}), 400
            else: 
                myseq_mpwz_id = seq_gen.get_next_sequence('mpwz_notify_status')   
                new_status = {
                    "mpwz_id": myseq_mpwz_id,
                    "button_name": data['button_name'],
                    "module_name": data['module_name'],
                    "created_by": username,
                    "created_on": datetime.datetime.now().isoformat(),
                    "updated_by": "NA",
                    "updated_on": "NA"
                } 
                result = mpwz_notify_status.insert_one(new_status)
                if result: 
                    # Add _id to the response, converting ObjectId to string
                    new_status['_id'] = str(result.inserted_id)
                    response_data = {   "msg": f"New Status Added successfully",
                                        "current_api": request.full_path,
                                        "client_ip": request.remote_addr,
                                        "response_at": datetime.datetime.now().isoformat()
                            } 
                    log_entry_event.log_api_call(response_data) 
                    print("Request completed successfully for adding new status.")
                    return jsonify(new_status), 201
                else:
                    return jsonify({"msg": "Error while adding new status into database"}), 500
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({"msg": f"An error occurred while processing the request. Please try again later. {str(e)}"}), 500
 
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_notify_status.mongo_dbconnect_close()
         seq_gen.mongo_dbconnect_close()

@admin_api.route('/insert-userlogininfo-from-mpwzusers', methods=['POST'])
# @admin_api_validator.ip_required
@jwt_required()
def update_users():
    user_processor = myserv_update_mpwzintegrationusers_frommpwzusers()
    try:
        response = user_processor.process_users()
        print("Request completed successfully for updating users.")
    except Exception as e:
        print(f"An error occurred while fetching data from mpwz_users tables: {str(e)}")
        return jsonify({"msg": "An error occurred while processing users."}), 500
    finally:
        user_processor.mongo_dbconnect_close() 
    return jsonify(response)                    

@admin_api.route('/insert-userinfo-from-powerbi-warehouse', methods=['POST'])
# @admin_api_validator.ip_required
@jwt_required()
def sync_databases():
    try:
        # Configuration for PostgreSQL and MongoDB
        pg_config = {
            'dbname': 'postgres',
            'user': 'biro',
            'password': 'biro',
            'host': '10.98.0.87',
            'port': '5432'
        }
        mongo_config = {
            'uri': 'mongodb://localhost:27017/',
            'db': 'admin',
            'collection': 'mpwz_users'
        }
        
        # Create an instance of the service
        service = myserv_update_mpwzusers_frombiserver(pg_config, mongo_config)
  
        try:
            service.sync_databases()
            print("Request completed successfully for syncing databases.")
            return jsonify({"msg": "Records updated successfully into mpwz_users table from Power BI warehouse"}), 200
        except Exception as e:
            print(f"An error occurred while processing users: {str(e)}")
            return jsonify({"msg": f"An error occurred while processing users: {str(e)}"}), 500
        finally:
            service.close_connections()
    except Exception as e:
        print(f"An error occurred while connecting to Power BI warehouse: {e}")
        return jsonify({"msg": f"An error occurred while connecting to Power BI warehouse: {str(e)}"}), 500
 
@admin_api.route('/api/add-user-ip-adminpanel', methods=['POST'])
# @admin_api_validator.ip_required
@jwt_required()
def insert_data_addip_admin():
    collection = MongoCollection("mpwz_iplist_adminpanel")
    data = request.json
    # Validate the incoming data
    if not data or not all(key in data for key in ['username', 'email', 'phone', 'employee_no', 'ip_address']):
        return jsonify({"error": "Invalid data"}), 400

    # Check for duplicate username
    if collection.find_one({"username": data['username']}):
        return jsonify({"error": "Username already exists"}), 400

    # Check for duplicate IP address
    if collection.find_one({"ip_address": data['ip_address']}):
        return jsonify({"error": "IP address already exists"}), 400
    try:
        result = collection.insert_one(data)
        print("Request completed successfully for inserting data into mpwz_iplist_adminpanel.")
        return jsonify({"inserted_id": str(result.inserted_id),"msg":"Data inserted successfully"}), 200  
    except Exception as e:
        print(f"An error occurred while inserting data into mpwz_iplist_adminpanel: {str(e)}")
        return jsonify({"error": f"An error occurred while inserting data into mpwz_iplist_adminpanel: {str(e)}"}), 500

@admin_api.route('/change-password-byadminuser', methods=['PUT'])
# @admin_api_validator.ip_required
@jwt_required()
def change_password_byadmin_forany():
    try:
        mpwz_users = MongoCollection("mpwz_integration_users")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        data = request.get_json()
        # Validate input
        username_user = data.get("username")
        new_password_user = data.get("new_password")
        if not new_password_user:
            return jsonify({"msg": "New password is required"}), 400
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password_user.encode('utf-8'), bcrypt.gensalt())
        # Update the password in the database
        response = mpwz_users.update_one({"username": username_user}, {"$set": {"password": hashed_password}})
        if response.modified_count == 0:
            return jsonify({"msg": "No changes made, password may be the same as the current one"}), 400
        else:
            response_data = {
                "msg": "Password Changed successfully",
                "BearrToken": username,
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": datetime.datetime.now().isoformat()
            }
            log_entry_event.log_api_call(response_data)
        print("Password change request completed successfully.")
        return jsonify({"msg": "Password changed successfully!"}), 200
    except Exception as error:
        print(f"An error occurred: {str(error)}")
        return jsonify({"msg": f"An error occurred while changing the password.errors {str(error)}."}), 500
    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_users.mongo_dbconnect_close()
     
@admin_api.route('/send-email', methods=['POST'])
# @admin_api_validator.ip_required
@jwt_required()
def send_email():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "Invalid JSON data"}), 400

        subject, body, to_email = data.get('subject'), data.get('body'), data.get('to_email')
        if not all([subject, body, to_email]):
            return jsonify({"msg": "Missing required fields"}), 400

        email_sender = EmailSender()
        email_sender.sendemail_connect()
        email_sender.send_email(subject, body, to_email)
        email_sender.sendemail_disconnect()
        print("Email sent request completed successfully.")
        return jsonify({"msg": f"Email sent to {to_email}"}), 200
    except ConnectionError:
        print("An error occurred while connecting to SMTP server.")
        return jsonify({"msg": "Failed to connect to the SMTP server"}), 500
    except Exception as e:
        print(f"An error occurred while sending email: {str(e)}")
        return jsonify({"msg": f"An error occurred while sending email: {str(e)}"}), 500


@admin_api.route('/update-work-location-foremployee', methods=['PUT'])
# @admin_api_validator.ip_required
@jwt_required()
def update_work_location():
    try:
        mpwz_integration_users = MongoCollection("mpwz_integration_users")
        log_entry_event = myserv_update_users_logs()  
        data = request.json
        username = data.get('username')
        new_work_location_code = data.get('work_location_code')

        if not username or not new_work_location_code:
            return jsonify({"error": "Username and work_location_code are required"}), 400

        result = mpwz_integration_users.update_one(
            {"username": username},
            {"work_location_code": new_work_location_code}
        )

        if result.matched_count == 0:
            return jsonify({"error": "User  not found"}), 404

        if result.modified_count == 0:
            return jsonify({"message": "No changes made"}), 200

        print("Work location code updated request completed successfully.")
        return jsonify({"message": "Work location code updated successfully"}), 200

    except Exception as e:
        # Handle any other exceptions
        print(f"An error occurred while updating work location: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

    finally:
        mpwz_integration_users.mongo_dbconnect_close()
        log_entry_event.mongo_dbconnect_close()

@admin_api.route('/update-secret-key', methods=['POST'])
# @admin_api_validator.ip_required
@jwt_required()
def update_secret_key_for_app():
    try:
        new_secret_key = SecretKeyManager.update_secret_key()
        print("Secret key updated request completed successfully.")
        return jsonify({"msg": "Secret key updated successfully.", "new_secret_key": new_secret_key})
    except Exception as e:
        print(f"An error occurred while updating secret key: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


