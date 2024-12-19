# admin_api/admin_routes.py
import datetime
import time
import bcrypt
from flask import jsonify, request
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from flask_pymongo import PyMongo
from . import admin_api
from myservices.myserv_update_mpwzintegrationusers_frommpwzusers import myserv_update_mpwzintegrationusers_frommpwzusers
from myservices.myserv_update_mpwzusers_frombiserver import myserv_update_mpwzusers_frombiserver
from myservices.myserv_send_notification import EmailSender
from myservices.myserv_connection_forblueprints import MongoCollection
from myservices import myserv_update_dbproperties
from myservices.myserv_generate_secretkey_forapp import SecretKeyManager
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices.myserv_update_users_logs import myserv_update_users_logs
from myservices.myserv_update_users_api_logs import myserv_update_users_api_logs

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
            return jsonify({"msg": "Data inserted successfully"}), 201
        else:
            return jsonify({"msg": "No Data inserted. Something went wrong"}), 500        
    except Exception as e:
        return jsonify({"msg": str(e)}), 400
  
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_integration_users.mongo_dbconnect_close()
         seq_gen.mongo_dbconnect_close()

@admin_api.route('/change-password-byadminuser', methods=['PUT'])
@jwt_required()
def change_password_byadmin_forany():
    try:
        mpwz_users = MongoCollection("mpwz_users")
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
        return jsonify({"msg": "Password changed successfully!"}), 200
    except Exception as error:
        return jsonify({"msg": f"An error occurred while changing the password.errors {str(error)}."}), 500

    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_users.mongo_dbconnect_close()

@admin_api.route('/notify-integrated-app', methods=['POST'])
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
                response_data = {      "msg": f"New App integrated successfully",
                                    "current_api": request.full_path,
                                    "client_ip": request.remote_addr,
                                    "response_at": datetime.datetime.now().isoformat()
                        } 
                log_entry_event.log_api_call(response_data) 
                return jsonify(app_name_list), 200
            else:
                return jsonify({"msg": "Unable to add new app details in the system, try again..."}), 500
    except Exception as e:
        return jsonify({"msg": f"An error occurred while processing the request. errors. {str(e)}"}), 500

    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_integrated_app.mongo_dbconnect_close()
         seq_gen.mongo_dbconnect_close()

@admin_api.route('/notify-status', methods=['POST'])
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
        
        existing_record = mpwz_notify_status.find_one({"button_name": data["button_name"]})
        if existing_record:      
            return jsonify({"msg": "Records with button_name already existed in database."}), 400
        else: 
            myseq_mpwz_id = seq_gen.get_next_sequence('mpwz_notify_status')   
            new_status = {
                "mpwz_id": myseq_mpwz_id,
                "button_name": data['button_name'],
                "created_by": username,
                "created_on": datetime.datetime.now().isoformat(),
                "updated_by": "NA",
                "updated_on": "NA"
            } 
            result = mpwz_notify_status.insert_one(new_status)
            if result: 
                response_data = {      "msg": f"New Status Added successfully",
                                    "current_api": request.full_path,
                                    "client_ip": request.remote_addr,
                                    "response_at": datetime.datetime.now().isoformat()
                        } 
                log_entry_event.log_api_call(response_data) 
                return jsonify(new_status), 201
            else:
                return jsonify({"msg": "Error while adding new status into database"}), 500
    except Exception as e:
        return jsonify({"msg": f"An error occurred while processing the request. Please try again later. {str(e)}"}), 500
 
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_notify_status.mongo_dbconnect_close()
         seq_gen.mongo_dbconnect_close()

@admin_api.route('/update_field_type_from_to', methods=['POST'])
@jwt_required()
def update_field_type():
    # Initialize the database updater
    db_updater = myserv_update_dbproperties() 
    data = request.get_json()    
    # Validate input from json data
    if not data or 'collection_name' not in data or 'field_name' not in data or 'from_property' not in data or 'to_property' not in data:
        return jsonify({'error': 'Invalid input, please provide collection_name, field_name, from_property, and to_property.'}), 400
    
    collection_name = data['collection_name']
    field_name = data['field_name']
    from_property = data['from_property']
    to_property = data['to_property']
    
    try:
        # Call the method to change the field type
        db_updater.change_field_type(collection_name=collection_name, field_name=field_name, from_property=from_property, to_property=to_property)
        return jsonify({'msg': 'Field type updated successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_api.route('/update-fields-to-string', methods=['POST'])
@jwt_required()
def update_fields_to_string(): 
    try:        
        # Initialize the database updater
        db_updater = myserv_update_dbproperties() () 
        data = request.get_json()
        
        # Ensure that 'collection_name' is provided in the JSON data
        if 'collection_name' not in data:
            return jsonify({
                'status': 'error',
                'msg': 'Missing "collection_name" in request body.'
            }), 400
        
        collection_name = data['collection_name']
        
        # Call the function to update fields in the specified collection
        db_updater.change_all_fields_to_string(collection_name)
        
        return jsonify({
            'status': 'success',
            'msg': f'All fields in collection {collection_name} have been updated to strings.'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'msg': str(e)
        }), 500
 
@admin_api.route('/update-secret-key', methods=['POST'])
@jwt_required()
def update_secret_key_for_app():
    new_secret_key = SecretKeyManager.update_secret_key()
    return jsonify({"msg": "Secret key updated successfully.", "new_secret_key": new_secret_key})

@admin_api.route('/insert-userlogininfo-from-mpwzusers', methods=['POST'])
@jwt_required()
def update_users():
    user_processor = myserv_update_mpwzintegrationusers_frommpwzusers()
    try:
        response = user_processor.process_users()
    except Exception as e:
        print(f"An error occurred while fetching data from mpwz_users tables: {str(e)}")
        return jsonify({"msg": "An error occurred while processing users."}), 500
    finally:
        user_processor.mongo_dbconnect_close() 
    return jsonify(response)                    

@admin_api.route('/insert-userinfo-from-powerbi-warehouse', methods=['POST'])
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
            return jsonify({"msg": "Records updated successfully into mpwz_users table from Power BI warehouse"}), 200
        except Exception as e:
            return jsonify({"msg": f"An error occurred while processing users: {str(e)}"}), 500
        finally:
            service.close_connections()
    except Exception as e:
        print(f"An error occurred while connecting to Power BI warehouse: {e}")
        return jsonify({"msg": f"An error occurred while connecting to Power BI warehouse: {str(e)}"}), 500
    
    
@admin_api.route('/send-email', methods=['POST'])
@jwt_required()
def send_email():
    try:
        email_sender = EmailSender()
        data = request.json
        subject = data.get('subject')
        body = data.get('body')
        to_email = data.get('to_email')

        if not subject or not body or not to_email:
            return jsonify({"msg": "Missing required fields"}), 400

    
            if not email_sender.sendemail_connect():
                return jsonify({"msg": "Failed to connect to the SMTP server"}), 500

            result = email_sender.send_email(subject, body, to_email)
            return jsonify({"msg": result})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    finally:
        email_sender.sendemail_disconnect()

@admin_api.route('/update-work-location-foremployee', methods=['PUT'])
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
            {"$set": {"work_location_code": new_work_location_code}}
        )

        if result.matched_count == 0:
            return jsonify({"error": "User  not found"}), 404

        if result.modified_count == 0:
            return jsonify({"message": "No changes made"}), 200

        return jsonify({"message": "Work location code updated successfully"}), 200

    except Exception as e:
        # Handle any other exceptions
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

    finally:
        mpwz_integration_users.mongo_dbconnect_close()
        log_entry_event.mongo_dbconnect_close()

@admin_api.route('/api/add-user-ip-adminpanel', methods=['POST'])
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
    result = collection.insert_one(data)
    return jsonify({"inserted_id": str(result.inserted_id)}), 200       