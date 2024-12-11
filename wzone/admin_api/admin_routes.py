# admin_api/admin_routes.py
import datetime
import time
import bcrypt
from flask import jsonify, request
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from flask_pymongo import PyMongo
from . import admin_api
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices.myserv_update_users_logs import myserv_update_users_logs
from myservices.myserv_update_users_api_logs import myserv_update_users_api_logs

seq_gen = myserv_generate_mpwz_id_forrecords()
log_entry_event = myserv_update_users_logs()
log_entry_event_api = myserv_update_users_api_logs()
# mongo = PyMongo(admin_api)

@admin_api.before_request
def before_request():
    request.start_time = time.time() 

@admin_api.after_request
def after_request(response):
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
        print(f"Request executed {api_name} it take {response_time_minutes:.4f} minutes.")
        return response
    else:
        return response

#Admin controller api for web users
@admin_api.route('/dashboard', methods=['GET'])
def dashboard():
    return jsonify({"message": "Admin Dashboard"})


@admin_api.route('/shared-call/api/v1/create-integration-users', methods=['POST'])
def create_integration_users_data():
    try:
        data = request.get_json()
        existing_user = mongo.db.mpwz_integration_users.find_one({"username": data.get("username")})
        if existing_user:
            return jsonify({"message": "Username already exists", "status": "error"}), 400
        data['mpwz_id'] = seq_gen.get_next_sequence('mpwz_integration_users')  
        results = mongo.db.mpwz_integration_users.insert_one(data)        
        if results:
            response_data = {      "msg": f"Integration User Created successfully ",
                                    "current_api": request.full_path,
                                    "client_ip": request.remote_addr,
                                    "response_at": datetime.datetime.now().isoformat()
                        } 
            log_entry_event.log_api_call(response_data)    
            return jsonify({"message": "Data inserted successfully"}), 201
        else:
            return jsonify({"message": "No Data inserted. Something went wrong"}), 500        
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 400

@admin_api.route('/change-password-byadminuser', methods=['PUT'])
@jwt_required()
def change_password_byadmin_forany():
    try:
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
        response = mongo.db.mpwz_users.update_one({"username": username_user}, {"$set": {"password": hashed_password}})
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

@admin_api.route('/notify-integrated-app', methods=['POST'])
@jwt_required()
def post_integrated_app():
    try:
        username = get_jwt_identity()
        data = request.get_json()
        if 'app_name' not in data:
            return jsonify({"msg": "app_name is required"}), 400

        existing_record = mongo.db.mpwz_integrated_app.find_one({"app_name": data["app_name"]})
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

            result = mongo.db.mpwz_integrated_app.insert_one(app_name_list)
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

@admin_api.route('/notify-status', methods=['POST'])
@jwt_required()
def post_notify_status():
    try:
        username = get_jwt_identity()
        data = request.get_json()
        if 'button_name' not in data:
            return jsonify({"msg": "button_name is required"}), 400 
        
        existing_record = mongo.db.mpwz_notify_status.find_one({"button_name": data["button_name"]})
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
            result = mongo.db.mpwz_notify_status.insert_one(new_status)
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
 

