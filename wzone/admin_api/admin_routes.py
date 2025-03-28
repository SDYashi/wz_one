# admin_api/admin_routes.py
import datetime
import time
import bcrypt
from flask import Flask, request, jsonify
from functools import wraps
from pymongo import DESCENDING
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from flask_pymongo import PyMongo
import pymongo
from . import admin_api
from myservices_oneapp.myserv_update_mpwzintegrationusers_frommpwzusers import myserv_update_mpwzintegrationusers_frommpwzusers
from myservices_oneapp.myserv_update_mpwzusers_frombiserver import myserv_update_mpwzusers_frombiserver
from myservices_oneapp.myserv_sendemail_notification import EmailSender
from myservices_oneapp.myserv_connection_forblueprints import MongoCollection
from myservices_oneapp.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices_oneapp.myserv_update_users_logs import myserv_update_users_logs
from myservices_oneapp.myserv_update_users_api_logs import myserv_update_users_api_logs
from myservices_oneapp.myserv_connection_mongodb import myserv_connection_mongodb
from myservices_oneapp.myserv_varriable_list import myserv_varriable_list

# define class for admin api


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

@admin_api.route('/login', methods=['POST'])
def login_admin():
    try:
        mpwz_integration_users_collection = MongoCollection("mpwz_integration_users")
        log_entry_event = myserv_update_users_logs()
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        access_token = ''
        
        user = mpwz_integration_users_collection.find_one({"username": username})
        if user:
            stored_hashed_password = user['password']
            user_role = user['user_role']
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                current_datetime = datetime.datetime.now()

                if user_role == myserv_varriable_list.ADMIN_USER_ROLE:
                    token_fromdb = user['token_app']
                    token_expiredon_fromdb = datetime.datetime.fromisoformat(user['token_expiredon'])
                    
                    if token_expiredon_fromdb < current_datetime:
                        access_token = create_access_token(identity=username, expires_delta=datetime.timedelta(days=365))
                        jwt_claims = decode_token(access_token)
                        update_query = {
                            "token_app": access_token,
                            "token_issuedon": datetime.datetime.fromtimestamp(jwt_claims['iat']).isoformat(),
                            "token_expiredon": datetime.datetime.fromtimestamp(jwt_claims['exp']).isoformat(),
                        }
                        mpwz_integration_users_collection.update_one({"username": username}, update_query)
                    else:
                        try:
                            jwt_claims = decode_token(token_fromdb)
                            if jwt_claims:
                                access_token = token_fromdb
                        except Exception as e:
                            return jsonify({"msg": f"Token is not valid: {str(e)}"}), 401
                else:
                   return jsonify({"msg": f"Invalid username or password {user_role} not allowed"}), 401

                response = jsonify(access_token=access_token)
              #   print(f"Request completed successfully: {response}")
                return response, 200
            else:
                return jsonify({"msg": "Invalid username or password"}), 401
        else:
            return jsonify({"msg": "Invalid username or password"}), 401

    except Exception as error:
        return jsonify({"msg": "An error occurred while processing your request", "error": str(error)}), 500

    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_integration_users_collection.mongo_dbconnect_close()
 
#Admin controller api for web users
@admin_api.route('/shared-call/api/v1/create-integration-users', methods=['POST'])
#@admin_api_validator.ip_required
@jwt_required()
def create_integration_users_data():
    try:
        mpwz_integration_users = MongoCollection("mpwz_integration_users")
        log_entry_event = myserv_update_users_logs()
        seq_gen = myserv_generate_mpwz_id_forrecords()
        data = request.get_json()
        username=get_jwt_identity()
        
        existing_user = mpwz_integration_users.find_one({"username": data.get("username")})
        if existing_user:
            return jsonify({"msg": "Username already exists", "status": "error"}), 400
        
        else:
            salt = bcrypt.gensalt()
            # Step 3: Hash the password
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), salt)
            hashpassword = hashed_password.decode('utf-8')
            # Add the new fields to the data dictionary
            data['mpwz_id'] = seq_gen.get_next_sequence('mpwz_integration_users')  
            data['status'] = "ACTIVE"         
            data['password'] = hashpassword
            data['token_app'] = "ttttttteeeeeesssssstttttttokenapp"
            data['token_issuedon'] = "2024-12-02T14:01:23"
            data['token_expiredon'] = "2024-12-02T14:01:23"
            data['created_by'] = username
            data['created_on'] = str(datetime.datetime.now())
            data['updated_by'] = "NA"
            data['updated_on'] = "NA"
            
            results = mpwz_integration_users.insert_one(data)        
            if results:
                response_data = {
                    "msg": "Integration User Created successfully",
                    "current_api": request.full_path,
                    "client_ip": request.remote_addr,
                    "response_at": str(datetime.datetime.now())
                } 
                log_entry_event.log_api_call(response_data)    
                print(f"Request completed {request.full_path}")
                return jsonify({"msg": f"User Created successfully"}), 201
            else:
                return jsonify({"msg": "No Data inserted. Something went wrong"}), 500        
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({"msg": str(e)}), 400
  
    finally: 
        log_entry_event.mongo_dbconnect_close() 
        mpwz_integration_users.mongo_dbconnect_close()
        seq_gen.mongo_dbconnect_close()

@admin_api.route('/notify-integrated-app', methods=['POST'])
#@admin_api_validator.ip_required
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
                "created_on": str(datetime.datetime.now()),
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
                    "response_at": str(datetime.datetime.now())
                }
                log_entry_event.log_api_call(response_data) 
                # print("Request completed successfully for new app integration.")                
                app_name=data['app_name']
                return jsonify({"msg": f"New App {app_name} Add Successfully "}), 201
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
#@admin_api_validator.ip_required
@jwt_required()
def post_notify_status():
    try:
        mpwz_notify_status = MongoCollection("mpwz_notify_status")
        mpwz_integrated_app_collection = MongoCollection("mpwz_integrated_app")
        log_entry_event = myserv_update_users_logs()
        seq_gen = myserv_generate_mpwz_id_forrecords()
        username = get_jwt_identity()
        data = request.get_json()
        if 'button_name' not in data:
            return jsonify({"msg": "button_name is required"}), 400 
        elif'module_name' not in data:
            return jsonify({"msg": "module_name is required"}), 400 
        else:           

            if not mpwz_integrated_app_collection.find_one({"app_name": data['module_name']}):
                return jsonify({"msg": "Incoming request occurred from invalid app_source."}), 400
            
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
                    "created_on": str(datetime.datetime.now()),
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
                                        "response_at": str(datetime.datetime.now())
                            } 
                    log_entry_event.log_api_call(response_data) 
                    # print("Request completed successfully for adding new status.")
                    app_name=data['button_name']
                    module_name=data['module_name']
                    return jsonify({"msg": f"New Status {module_name} for App {app_name} "}), 201
                else:
                    return jsonify({"msg": "Error while adding new status into database"}), 500
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({"msg": f"An error occurred while processing the request. Please try again later. {str(e)}"}), 500
 
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_notify_status.mongo_dbconnect_close()
         seq_gen.mongo_dbconnect_close()

@admin_api.route('/add-button-status', methods=['POST'])
#@admin_api_validator.ip_required
@jwt_required()
def post_add_button_status():
    try:
        mpwz_buttons = MongoCollection("mpwz_buttons")
        mpwz_integrated_app_collection = MongoCollection("mpwz_integrated_app")
        log_entry_event = myserv_update_users_logs()
        seq_gen = myserv_generate_mpwz_id_forrecords()
        username = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        required_fields = ['button_name', 'app_source']
        for field in required_fields:
            if field not in data:
                return jsonify({"msg": f"{field} is required"}), 400 
                     

        if not mpwz_integrated_app_collection.find_one({"app_name": data['app_source']}):
                return jsonify({"msg": "Incoming request occurred from invalid app_source."}), 400

        # Check for existing record
        existing_record = mpwz_buttons.find_one({"button_name": data["button_name"]})
        if existing_record:      
            return jsonify({"msg": "Record with button_name already exists in the database."}), 400

        # Generate new mpwz_id
        myseq_mpwz_id = seq_gen.get_next_sequence('mpwz_buttons')   
        new_status = {
            "mpwz_id": myseq_mpwz_id,
            "button_name": data['button_name'],
            "app_source": data['app_source'],
            "created_by": username,
            "created_on": str(datetime.datetime.now()),
            "updated_by": "NA",
            "updated_on": "NA"
        } 

        # Insert new record into the database
        result = mpwz_buttons.insert_one(new_status)
        if result: 
            # Add _id to the response, converting ObjectId to string
            new_status['_id'] = str(result.inserted_id)
            response_data = {
                "msg": "New Button Status Added successfully",
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": str(datetime.datetime.now())
            } 
            log_entry_event.log_api_call(response_data) 
            
            app_name=data['button_name']
            module_name=data['app_source']
            return jsonify({"msg": f"New Status button {module_name} for App {app_name} "}), 201
        else:
            return jsonify({"msg": "Error while adding new button status into database"}), 500

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({"msg": f"An error occurred while processing the request. Please try again later. {str(e)}"}), 500
 
    finally: 
        log_entry_event.mongo_dbconnect_close() 
        mpwz_buttons.mongo_dbconnect_close()
        seq_gen.mongo_dbconnect_close()

@admin_api.route('/insert-userlogininfo-from-mpwzusers', methods=['POST'])
#@admin_api_validator.ip_required
@jwt_required()
def update_users():
    user_processor = myserv_update_mpwzintegrationusers_frommpwzusers()
    try:
        response = user_processor.process_users()
        # print("Request completed successfully for updating users.")
    except Exception as e:
        print(f"An error occurred while fetching data from mpwz_users tables: {str(e)}")
        return jsonify({"msg": "An error occurred while processing users."}), 500
    finally:
        user_processor.mongo_dbconnect_close() 
    return jsonify(response)                    

@admin_api.route('/insert-userinfo-from-powerbi-warehouse', methods=['POST'])
#@admin_api_validator.ip_required
@jwt_required()
def sync_databases():
    try:
        # Configuration for PostgreSQL and MongoDB
        pg_config = {
            'dbname': myserv_varriable_list.pg_config_DBNAME,
            'user': myserv_varriable_list.pg_config_USER,
            'password': myserv_varriable_list.pg_config_PASSWORD,
            'host': myserv_varriable_list.pg_config_HOST,
            'port': myserv_varriable_list.pg_config_PORT
        }
        mongo_config = {
            'uri': myserv_varriable_list.mongo_config_URI,
            'db': myserv_varriable_list.mongo_config_DB,
            'collection': myserv_varriable_list.mongo_config_COLLECTION
        }
        
        # Create an instance of the service
        service = myserv_update_mpwzusers_frombiserver(pg_config, mongo_config)
  
        try:
            service.sync_databases()
            # print("Request completed successfully for syncing databases.")
            return jsonify({"msg": "Records updated successfully into mpwz_users table from Power BI warehouse"}), 200
        except Exception as e:
            print(f"An error occurred while processing users: {str(e)}")
            return jsonify({"msg": f"An error occurred while processing users: {str(e)}"}), 500
        finally:
            service.close_connections()
    except Exception as e:
        print(f"An error occurred while connecting to Power BI warehouse: {e}")
        return jsonify({"msg": f"An error occurred while connecting to Power BI warehouse: {str(e)}"}), 500
 
@admin_api.route('/change-password-byadminuser', methods=['PUT'])
#@admin_api_validator.ip_required
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
        response = mpwz_users.update_one({"username": username_user},{"password": hashed_password})
        if response.modified_count == 0:
            return jsonify({"msg": "No changes made, password may be the same as the current one"}), 400
        else:
            response_data = {
                "msg": "Password Changed successfully",
                "BearrToken": username,
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": str(datetime.datetime.now())
            }
            log_entry_event.log_api_call(response_data)
       #  print("Password change request completed successfully.")
        return jsonify({"msg": "Password changed successfully!"}), 200
    except Exception as error:
        print(f"An error occurred: {str(error)}")
        return jsonify({"msg": f"An error occurred while changing the password.errors {str(error)}."}), 500
    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_users.mongo_dbconnect_close()
     
@admin_api.route('/send-email', methods=['POST'])
#@admin_api_validator.ip_required
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
        # print("Email sent request completed successfully.")
        return jsonify({"msg": f"Email sent to {to_email}"}), 200
    except ConnectionError:
        print("An error occurred while connecting to SMTP server.")
        return jsonify({"msg": "Failed to connect to the SMTP server"}), 500
    except Exception as e:
        print(f"An error occurred while sending email: {str(e)}")
        return jsonify({"msg": f"An error occurred while sending email: {str(e)}"}), 500

@admin_api.route('/update-work-location-foremployee', methods=['PUT'])
#@admin_api_validator.ip_required
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
            return jsonify({"msg": "No changes made"}), 200

       #  print("Work location code updated request completed successfully.")
        return jsonify({"msg": "Work location code updated successfully"}), 200

    except Exception as e:
        # Handle any other exceptions
        print(f"An error occurred while updating work location: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

    finally:
        mpwz_integration_users.mongo_dbconnect_close()
        log_entry_event.mongo_dbconnect_close()

@admin_api.route('/admin-dashboard-recent-actiondone-history', methods=['GET'])
@jwt_required()
def admin_dashboard_action_history():
    try:
        mpwz_notifylist = MongoCollection("mpwz_user_action_history")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        response_data = []
        query = {
            'notify_status': {'$in': ['APPROVED', 'REJECTED', 'REASSIGNED']},
            # 'notify_to_id': username
        }

        notifications = mpwz_notifylist.find_sortall(
            query=query,
            sort=[("action_at", pymongo.DESCENDING)],
            limit=3
        )

        # notifications = mpwz_notifylist.find_sortall(query).sort("action_at", DESCENDING).limit(5)

        for notification in notifications:
            filtered_notification = {
                "mpwz_id": notification.get("mpwz_id"),
                "notify_status": notification.get("notify_status"),
                "notify_refsys_id": notification.get("notify_refsys_id"),
                "notify_to_id": notification.get("notify_to_id"),
                "sequence_no": notification.get("sequence_no"),
                "action_by": notification.get("action_by"),
                "action_at": notification.get("action_at")
            }
            response_data.append(filtered_notification)

        # Log the response statuses
        if response_data:
            response_data_logs = {
                "msg": f"Request List loaded successfully for {username}",
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": str(datetime.datetime.now())
            }
            log_entry_event.log_api_call(response_data_logs)
            print("Request completed successfully")
            return jsonify(response_data), 200
        else:
            return jsonify({"msg": "No notifications found."}), 400
    except Exception as e:
        print(f"An error occurred while processing the request. Exception: {str(e)}")
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500
    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_notifylist.mongo_dbconnect_close()



