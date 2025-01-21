# android_api/android_routes.py
import base64
import datetime
import time
import bcrypt
import ast  
from dateutil import parser 
from flask import jsonify, request
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from flask_pymongo import PyMongo
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices.myserv_update_users_logs import myserv_update_users_logs
from myservices.myserv_update_users_api_logs import myserv_update_users_api_logs
from myservices.myserv_connection_forblueprints import MongoCollection
from shared_api import ngb_apiServices,erp_apiservices
from myservices.myserv_update_dbservices import myserv_update_dbservices
from myservices.myserv_update_actionhistory import myserv_update_actionhistory
from . import android_api
from myservices.myserv_varriable_list import myserv_varriable_list

@android_api.before_request
def before_request():
    request.start_time = time.time() 

@android_api.after_request
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

@android_api.route('/login', methods=['POST'])
def login():
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

                if user_role == myserv_varriable_list.API_USER_ROLE:
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

                elif user_role in [myserv_varriable_list.ANDROID_USER_ROLE, myserv_varriable_list.ADMIN_USER_ROLE]:
                    app_token_fromdb = user['token_app']
                    app_token_expiredon_fromdb = datetime.datetime.fromisoformat(user['token_expiredon'])

                    if app_token_expiredon_fromdb < current_datetime:
                        expires_delta = datetime.timedelta(days=30) if user_role == 'android_user' else datetime.timedelta(days=365)
                        access_token = create_access_token(identity=username, expires_delta=expires_delta)
                        jwt_claims = decode_token(access_token)
                        update_query = {
                            "token_app": access_token,
                            "token_issuedon": datetime.datetime.fromtimestamp(jwt_claims['iat']).isoformat(),
                            "token_expiredon": datetime.datetime.fromtimestamp(jwt_claims['exp']).isoformat(),
                        }
                        mpwz_integration_users_collection.update_one({"username": username}, update_query)
                    else:
                        try:
                            jwt_claims = decode_token(app_token_fromdb)
                            if jwt_claims:
                                access_token = app_token_fromdb
                        except Exception as e:
                            return jsonify({"msg": f"Token is not valid: {str(e)}"}), 401

                    response_data = {"request_by": username, "msg": "Token Issued successfully for Login"}
                    log_entry_event.log_api_call(response_data)

                else:
                    return jsonify({"msg": "Invalid user_role authentication error"}), 401

                response = jsonify(access_token=access_token)
             #    print(f"Request completed successfully: {response_data}")
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

@android_api.route('/login-admin', methods=['POST'])
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
     
@android_api.route('/changepassword', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        mpwz_integration_users = MongoCollection("mpwz_integration_users")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        data = request.get_json()
        new_password = data.get("new_password")

        if not new_password:
            return jsonify({"msg": "New password is required"}), 400
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        update_result = mpwz_integration_users.update_one({"username": username}, {"password": hashed_password})
        if update_result.modified_count > 0:
            response_data = {
                "msg": f"Password Changed successfully for {username}",
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": str(datetime.datetime.now())
            } 
            log_entry_event.log_api_call(response_data)
           #  print(f"Request completed successfully: {response_data}")
            return jsonify({"msg": "Password changed successfully!"}), 200
        else:
            return jsonify({"msg": "Password not changed. Please try again."}), 400
    except Exception as error:
        print(f"Request failed with error: {str(error)}")
        return jsonify({"msg": f"An error occurred while changing the password.errors {str(error)}."}), 500
    
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_integration_users.mongo_dbconnect_close()

@android_api.route('/userprofile', methods=['GET'])
@jwt_required()
def view_profile():
    try:
        mpwz_integration_users = MongoCollection("mpwz_users")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        # Retrieve the user profile from the database
        user = mpwz_integration_users.find_one({"employee_number": username})

        if user:
            # Add _id to the response, converting ObjectId to string
            user['_id'] = str(user['_id'])
            for key, value in user.items():
                if isinstance(value, bytes):
                    user[key] = base64.b64encode(value).decode('utf-8')  
                    
            response_data = {
                "msg": f"User Profile loaded successfully for {username}",
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": str(datetime.datetime.now())
            }
            log_entry_event.log_api_call(response_data)
            # print(f"Request completed successfully: {response_data}")
            return jsonify(user), 200
        else:
            return jsonify({"msg": "User not found in records"}), 404

    except Exception as e:
        print(f"Request failed with error: {str(e)}")
        return jsonify({"msg": f"An error occurred while retrieving the user profile. error. {str(e)}"}), 500
    
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_integration_users.mongo_dbconnect_close()
@android_api.route('/userlist', methods=['GET'])
@jwt_required()
def view_user_list():
    try:
        mpwz_integration_users = MongoCollection("mpwz_users")
        log_entry_event = myserv_update_users_logs()

        # Get pagination parameters
        page_no = int(request.args.get('page_no', 1))
        page_size = int(request.args.get('page_size', 100))
        
        # Calculate skip and limit values for pagination
        skip = (page_no - 1) * page_size
        limit = page_size

        # Retrieve paginated user profiles from the database
        users_cursor = mpwz_integration_users.collection.find().skip(skip).limit(limit)
        users = list(users_cursor)

        # Process each user to convert ObjectId to string and handle bytes
        total_count = mpwz_integration_users.count_documents({})
        for user in users:
            user['_id'] = str(user['_id'])
            for key, value in user.items():
                if isinstance(value, bytes):
                    user[key] = base64.b64encode(value).decode('utf-8')

        response_data = {
            "msg": "User list loaded successfully",
            "current_api": request.full_path,
            "client_ip": request.remote_addr,
            "response_at": str(datetime.datetime.now()),
            "user_count": len(users),
            "page_no": page_no,
            "page_size": page_size,
            "total_count": total_count
        }
        log_entry_event.log_api_call(response_data)
       #  print(f"Request completed successfully: {response_data}")

        return jsonify({"users": users, "total_count": total_count,"msg":"profiles loaded successfully"}), 200

    except Exception as e:
        print(f"Request failed with error: {str(e)}")
        return jsonify({"msg": f"An error occurred while retrieving the user list. error: {str(e)}"}), 500

    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_integration_users.mongo_dbconnect_close()

@android_api.route('/notify-status', methods=['GET'])
@jwt_required()
def get_notify_status():
    try:
        mpwz_notify_status = MongoCollection("mpwz_notify_status")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        statuses = list(mpwz_notify_status.find_all())
        if statuses:
            response_statuses = []
            for status in statuses:
                # Creating new dictionary to remove _id from response
                status_response = {key: value for key, value in status.items() if key != '_id'}
                response_statuses.append(status_response)
                # Log entry in table 
                response_data = {
                    "msg": f"notification status loaded successfully for {username}",
                    "current_api": request.full_path,
                    "client_ip": request.remote_addr,
                    "response_at": str(datetime.datetime.now())
                } 
                log_entry_event.log_api_call(response_data)
           #  print("Request completed successfully.")
            return jsonify(response_statuses), 200
        else:
            print("No button_name added by mpwz admin.")
            return jsonify({"statuses": "No button_name added by mpwz admin"}), 404
    except Exception as e:
        print(f"An error occurred while processing the request: {str(e)}")
        return jsonify({"msg": f"An error occurred while processing the request. Please try again later. {str(e)}"}), 500
    
    finally: 
        log_entry_event.mongo_dbconnect_close() 
        mpwz_notify_status.mongo_dbconnect_close()

@android_api.route('/notify-integrated-app', methods=['GET'])
@jwt_required()
def get_integrated_app_list():
    try:
        mpwz_integrated_app = MongoCollection("mpwz_integrated_app")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        statuses = list(mpwz_integrated_app.find_all())
        if statuses:
            response_statuses = []
            for status in statuses:
                # Creating new dictionary to remove _id from response
                status_response = {key: value for key, value in status.items() if key != '_id'}
                response_statuses.append(status_response)
                # Log entry in table 
                response_data = {
                    "msg": f"Integrated App List loaded successfully for {username}",
                    "current_api": request.full_path,
                    "client_ip": request.remote_addr,
                    "response_at": str(datetime.datetime.now())
                }                   
                log_entry_event.log_api_call(response_data)
            # print("Request completed successfully.")
            return jsonify(response_statuses), 200
        else:
            print("No apps added by mpwz admin.")
            return jsonify({"msg": "No apps added by mpwz admin"}), 404

    except Exception as e:
        print(f"An error occurred while processing the request: {str(e)}")
        return jsonify({"msg": f"An error occurred while processing the request. errors. {str(e)}"}), 500
    
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_integrated_app.mongo_dbconnect_close()   
 
@android_api.route('/my-request-notify-count', methods=['GET'])
@jwt_required()
def my_request_notification_count():
    try:
        # Initialize MongoDB collection and logging utility
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
        log_entry_event = myserv_update_users_logs()

        username = get_jwt_identity()
        notification_status = request.args.get('notification_status')

        # Initialize response structure
        response_data = {
            'username': username,
            'total_pending_count': 0,
            'app_notifications_count': {}
        }

        # Match stage for aggregation
        match_stage = {'notify_from_id': username}
        if notification_status:
            match_stage['notify_status'] = notification_status

        # Aggregation pipeline
        pipeline = [
            {'$match': match_stage},
            {
                '$group': {
                    '_id': {
                        'app_source': '$app_source',
                        'notify_status': '$notify_status'
                    },
                    'count': {'$sum': 1}
                }
            }
        ]

        # Execute aggregation
        notification_counts = list(mpwz_notifylist.aggregate(pipeline))

        # Log aggregation result
        current_time = str(datetime.datetime.now())
        print(f"[{current_time}] Aggregation Result: {notification_counts}")

        # Process aggregation results
        for doc in notification_counts:
            print(f"[{current_time}] Processing doc: {doc}")
            if '_id' in doc and isinstance(doc['_id'], dict):
                app_source = doc['_id'].get('app_source')
                notify_status = doc['_id'].get('notify_status')
                count = doc.get('count', 0)

                if app_source and notify_status:
                    # Initialize app_source if not already present
                    if app_source not in response_data['app_notifications_count']:
                        response_data['app_notifications_count'][app_source] = {}

                    # Add count to the respective notify_status
                    response_data['app_notifications_count'][app_source][notify_status] = count

                    # Increment total pending count for 'PENDING' status
                    if notify_status == 'PENDING':
                        response_data['total_pending_count'] += count

        # Log the successful response
        log_data = {
            "msg": f"My request notification count loaded successfully for {username}",
            "current_api": request.full_path,
            "client_ip": request.remote_addr,
            "response_at": str(datetime.datetime.now())
        }
        log_entry_event.log_api_call(log_data)

       #  print("Request completed successfully")
        # Return the response data
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Request failed with error: {str(e)}")
        # Log error for debugging
        print(f"Error occurred: {str(e)}")
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500

    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_notifylist.mongo_dbconnect_close()

@android_api.route('/my-request-notify-list', methods=['GET'])
@jwt_required()
def my_request_notification_list():
    try:
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
        mpwz_buttons = MongoCollection("mpwz_buttons")
        mpwz_integrated_app = MongoCollection("mpwz_integrated_app")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        application_type = request.args.get('application_type')
        notification_status = request.args.get('notification_status')

        # Check if the application type exists
        app_exists = mpwz_integrated_app.find_one({"app_name": application_type})
        if not app_exists:
            return jsonify({"msg": "application type does not exist."}), 400  
        
        response_data = []
        query = {
            'app_source': application_type,  
            'notify_from_id': username,
            'notify_status': notification_status
        }
        
        # Fetch data using query
        notifications = mpwz_notifylist.find(query)
        for notification in notifications:
            # Create a new dictionary with only the required fields
            # if notification_status==myserv_varriable_list.notification_status_PENDING:                
            #     app_type=notification.get("app_source")
            #     unique_button_names = mpwz_buttons.find_distinct("button_name", {"app_source": app_type})
            # else:
            #     unique_button_names=[] 
            unique_button_names=[]     

            filtered_notification = {
                "app_request_type": notification.get("app_request_type"),
                "app_source": notification.get("app_source"),
                "app_source_appid": notification.get("app_source_appid"),
                "buttons": unique_button_names,
                "mpwz_id": notification.get("mpwz_id"),
                "notify_comments": notification.get("notify_comments"),
                "notify_datetime": notification.get("notify_datetime"),
                "notify_description": notification.get("notify_description"),
                "notify_from_id": notification.get("notify_from_id"),
                "notify_from_name": notification.get("notify_from_name"),
                "notify_intiatedby": notification.get("notify_intiatedby"),
                "notify_notes": notification.get("notify_notes"),
                "notify_refsys_id": notification.get("notify_refsys_id"),
                "notify_status": notification.get("notify_status"),
                "notify_to_id": notification.get("notify_to_id"),
                "notify_to_name": notification.get("notify_to_name")
            }
            response_data.append(filtered_notification)
        
        # Log the response statuses
        if response_data:                
                # Log entry in table 
                response_data_log = {
                    "msg": f"my request list loaded successfully for {username}",
                    "current_api": request.full_path,
                    "client_ip": request.remote_addr,
                    "response_at": str(datetime.datetime.now())
                }                   
                log_entry_event.log_api_call(response_data_log)  
                # print("Request completed successfully")
                return jsonify(response_data), 200             
        else:
            print(f"No pending notifications found for {username}.")
            return jsonify({"msg": f"No pending notifications found for {username}."}), 400
    except Exception as e:
        print(f"An error occurred while processing your request: {str(e)}")
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500   
    finally: 
        log_entry_event.mongo_dbconnect_close() 
        mpwz_notifylist.mongo_dbconnect_close() 
        mpwz_integrated_app.mongo_dbconnect_close()
   
@android_api.route('/pending-notify-count', methods=['GET'])
@jwt_required()
def pending_notification_count():
    try:
        # Initialize MongoDB collection and logging utility
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
        log_entry_event = myserv_update_users_logs()

        username = get_jwt_identity()
        notification_status = request.args.get('notification_status')

        # Initialize response structure
        response_data = {
            'username': username,
            'total_pending_count': 0,
            'app_notifications_count': {}
        }

        # Match stage for aggregation
        match_stage = {'notify_to_id': username}
        if notification_status:
            match_stage['notify_status'] = notification_status

        # Aggregation pipeline
        pipeline = [
            {'$match': match_stage},
            {
                '$group': {
                    '_id': {
                        'app_source': '$app_source',
                        'notify_status': '$notify_status'
                    },
                    'count': {'$sum': 1}
                }
            }
        ]

        # Execute aggregation
        notification_counts = list(mpwz_notifylist.aggregate(pipeline))

        # Log aggregation result
        current_time = str(datetime.datetime.now())
        print(f"[{current_time}] Aggregation Result: {notification_counts}")

        # Process aggregation results
        for doc in notification_counts:
            print(f"[{current_time}] Processing doc: {doc}")
            if '_id' in doc and isinstance(doc['_id'], dict):
                app_source = doc['_id'].get('app_source')
                notify_status = doc['_id'].get('notify_status')
                count = doc.get('count', 0)

                if app_source and notify_status:
                    # Initialize app source dictionary if not already present
                    if app_source not in response_data['app_notifications_count']:
                        response_data['app_notifications_count'][app_source] = {}

                    # Add count to the respective notify_status
                    response_data['app_notifications_count'][app_source][notify_status] = count

                    # Add to total pending count if status is 'PENDING'
                    if notify_status == 'PENDING':
                        response_data['total_pending_count'] += count

        # Log the successful response
        log_data = {
            "msg": f"Pending request count loaded successfully for {username}",
            "current_api": request.full_path,
            "client_ip": request.remote_addr,
            "response_at": str(datetime.datetime.now())
        }
        log_entry_event.log_api_call(log_data)

       #  print("Request completed successfully")
        # Return the response data
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500

    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_notifylist.mongo_dbconnect_close()

@android_api.route('/pending-notify-list', methods=['GET'])
@jwt_required()
def pending_notification_list():
    try:
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
        mpwz_integrated_app = MongoCollection("mpwz_integrated_app")
        mpwz_buttons = MongoCollection("mpwz_buttons")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        application_type = request.args.get('application_type')
        notification_status = request.args.get('notification_status')

        # Check if the application type exists
        app_exists = mpwz_integrated_app.find_one({"app_name": application_type})
        if not app_exists:
            return jsonify({"msg": "application type does not exist."}), 400  
        
        response_data=[]
        
        query = {
            'app_source': application_type,  
            'notify_to_id': username,
            'notify_status':notification_status
        }
        
        # Fetch data using query
        notifications = mpwz_notifylist.find(query)
        for notification in notifications:
            # Create a new dictionary with only the required fields
            if notification_status==myserv_varriable_list.notification_status_PENDING:                
                app_type=notification.get("app_source")
                unique_button_names = mpwz_buttons.find_distinct("button_name", {"app_source": app_type})
            else:
                unique_button_names=[]   

            filtered_notification = {
                "app_request_type": notification.get("app_request_type"),
                "app_source": notification.get("app_source"),
                "app_source_appid": notification.get("app_source_appid"),
                "buttons": unique_button_names,
                "mpwz_id": notification.get("mpwz_id"),
                "notify_comments": notification.get("notify_comments"),
                "notify_datetime": notification.get("notify_datetime"),
                "notify_description": notification.get("notify_description"),
                "notify_from_id": notification.get("notify_from_id"),
                "notify_from_name": notification.get("notify_from_name"),
                "notify_intiatedby": notification.get("notify_intiatedby"),
                "notify_notes": notification.get("notify_notes"),
                "notify_refsys_id": notification.get("notify_refsys_id"),
                "notify_status": notification.get("notify_status"),
                "notify_to_id": notification.get("notify_to_id"),
                "notify_to_name": notification.get("notify_to_name")
            }
            response_data.append(filtered_notification)
            

        # Log the response statuses
        if response_data:
            response_data_log = {
                                    "msg": f"pending request list loaded successfully for {username}",
                                    "current_api": request.full_path,
                                    "client_ip": request.remote_addr,
                                    "response_at": str(datetime.datetime.now())
            }                     
            log_entry_event.log_api_call(response_data_log)
           #  print("Request completed successfully")
            return jsonify(response_data), 200   
        else:
            return jsonify({"msg": "No pending notifications found."}), 400
        
    except Exception as e:
        print(f"An error occurred while processing your request: {str(e)}")
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_notifylist.mongo_dbconnect_close() 
         mpwz_integrated_app.mongo_dbconnect_close() 
         mpwz_buttons.mongo_dbconnect_close() 
 

@android_api.route('/update-notify-inhouse-app', methods=['POST'])
@jwt_required()
def update_notify_status_inhouse_app():
    try:
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
        log_entry_event = myserv_update_users_logs()
        update_actionhistory = myserv_update_actionhistory()
        username = get_jwt_identity()
        data = request.get_json()
        remote_response=""
        required_fields = ["mpwz_id", "notify_status", "notify_refsys_id", "remarks_byapprover", "notify_to_id"]

        if not all(field in data for field in required_fields):
            return jsonify({"msg": "All required fields are not present in the request data"}), 400

        query = {
            "mpwz_id": data["mpwz_id"],
            "notify_to_id": data["notify_to_id"],
            "notify_refsys_id": data["notify_refsys_id"]
        }
        db_user_details = mpwz_notifylist.find_one(query)

        if db_user_details is None:
            return jsonify({"msg": "Notification details not found in database"}), 404
        else:
            if db_user_details["notify_status"] != myserv_varriable_list.notification_status_PENDING:
                return jsonify({"msg": "You are not authorized to change notification status otherthan pending"}), 400
            else:
                if db_user_details["notify_to_id"] != username:
                    return jsonify({"msg": "You are not authorized to update this notification ."}), 403
                else:
                    if db_user_details.get("app_source") == myserv_varriable_list.integrated_app_ngb:   
                        if db_user_details.get("app_request_type") == myserv_varriable_list.notification_type_ngb_ccb:
                            shared_api_data = {
                                "id": db_user_details["notify_refsys_id"],
                                "locationCode": db_user_details["notify_refsys_id"],
                                "approver": db_user_details["notify_refsys_id"],
                                "billId": db_user_details["notify_refsys_id"],
                                "billCorrectionProfileInitiatorId": db_user_details["notify_refsys_id"],
                                "status": data["notify_refsys_id"],
                                "remark": db_user_details["notify_refsys_id"],
                                "updatedBy": db_user_details["notify_refsys_id"],
                                "updatedOn": db_user_details["notify_refsys_id"]
                            }
                            remote_response = ngb_apiServices.ngb_apiServices.send_success(shared_api_data)

                        elif db_user_details.get("app_request_type") == myserv_varriable_list.notification_type_ngb_cc4:
                            shared_api_data = {
                                "postingDate": db_user_details["app_request_type"],
                                "amount": db_user_details["app_request_type"],
                                "code": db_user_details["app_request_type"],
                                "ccbRegisterNo": db_user_details["app_request_type"],
                                "remark": db_user_details["app_request_type"],
                                "consumerNo": db_user_details["app_request_type"],
                            }
                            remote_response = ngb_apiServices.ngb_apiServices.send_success(shared_api_data)
                        else:
                             return jsonify({"msg": "App Source is not allowed to push data NGB."}), 400
                        
                    elif db_user_details.get("app_source") == myserv_varriable_list.integrated_app_erp:  
                        if db_user_details.get("app_request_type") == myserv_varriable_list.notification_type_erp_leave:
                            shared_api_data = {
                                "id": db_user_details["notify_refsys_id"],
                                "locationCode": db_user_details["notify_refsys_id"],
                                "approver": db_user_details["notify_refsys_id"],
                                "billId": db_user_details["notify_refsys_id"],
                                "billCorrectionProfileInitiatorId": db_user_details["notify_refsys_id"],
                                "status": data["notify_refsys_id"],
                                "remark": db_user_details["notify_refsys_id"],
                                "updatedBy": db_user_details["notify_refsys_id"],
                                "updatedOn": db_user_details["notify_refsys_id"]
                            }                
                            remote_response = erp_apiservices.erp_apiservices.send_success(shared_api_data)
                        elif db_user_details.get("app_request_type") == myserv_varriable_list.notification_type_erp_tada:
                            shared_api_data = {
                                "postingDate": db_user_details["app_request_type"],
                                "amount": db_user_details["app_request_type"],
                                "code": db_user_details["app_request_type"],
                                "ccbRegisterNo": db_user_details["app_request_type"],
                                "remark": db_user_details["app_request_type"],
                                "consumerNo": db_user_details["app_request_type"],
                            }                   
                            remote_response = erp_apiservices.erp_apiservices.send_success(shared_api_data)
                        else:
                            return jsonify({"msg": "App Source is not allowed to push data ERP."}), 400
                    
                    if remote_response is not None and remote_response['status_code'] == 200:
                        update_query = {
                            "notify_status": data["notify_status"],
                            "notify_refsys_response": remote_response,
                            "notify_refsys_updatedon": str(datetime.datetime.now()),
                        }
                        result = mpwz_notifylist.update_one(query, update_query)

                        if result.modified_count > 0:
                            response_data = {
                                "msg": f"Notification Status Updated successfully for {username}",
                                "current_api": request.full_path,
                                "client_ip": request.remote_addr,
                                "response_at": str(datetime.datetime.now())
                            }
                            try:                    
                                action_history = update_actionhistory.post_actionhistory_request(username, data)
                                if action_history:
                                    log_entry_event.log_api_call(response_data)
                                  #   print(f"Request completed successfully at {request.full_path}")
                                    return jsonify({"msg": f"Notification {data['notify_status']} Successfully {result.modified_count}"}), 200
                                else:
                                    print(f"Request failed with error at {request.full_path}")
                                    return jsonify({"msg": "Failed to update action history,Please Try Again."}), 500
                            except Exception as e:
                                print(f"Request failed with error at {request.full_path}")
                                return jsonify({"msg": str(e)}), 500
                    else:
                        print(f"Request failed with error at {request.full_path}")
                        return jsonify({"msg": "Something went wrong while updating Notification into remote servers"}), 400
    except Exception as e:
        print(f"Request failed with error at {request.full_path}")
        return jsonify({"msg": f"Request failed with error: {str(e)}"}), 500
    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_notifylist.mongo_dbconnect_close()

@android_api.route('/dashboard-total-notify-count', methods=['GET'])
@jwt_required()
def total_notification_count():
    try:
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        
        response_data = {
            'app_notifications_count': {}
        }
        
        # match_stage = {
        #     'notify_to_id': username
        # }
        
        pipeline = [
            # {
            #     '$match': match_stage
            # },
            {
                '$group': {
                    '_id': {
                        'app_source': '$app_source',
                        'notify_status': '$notify_status'
                    },
                    'count': {'$sum': 1}
                }
            }
        ]
        
        # Execute the aggregation pipeline and get the result
        notification_counts = list(mpwz_notifylist.aggregate(pipeline))

        # Debugging - Print the raw notification_counts to check its structure
        print("Notification Counts:", notification_counts)

        if not notification_counts:
            return jsonify({"msg": f"No notifications found for the user {username}."}), 404

        for doc in notification_counts:
            # Ensure `doc` is a dictionary and contains the expected fields
            if '_id' in doc and isinstance(doc['_id'], dict):
                app_source = doc['_id'].get('app_source')
                notify_status = doc['_id'].get('notify_status')
                count = doc.get('count')

                if app_source and notify_status:
                    # Initialize the app_source dictionary if it doesn't exist
                    if app_source not in response_data['app_notifications_count']:
                        response_data['app_notifications_count'][app_source] = {}

                    # Set the count for the specific notify_status
                    response_data['app_notifications_count'][app_source][notify_status] = count
            else:
                raise ValueError(f"Invalid structure for _id field in document: {doc}")

        # Log the event
        log_entry_data = {
            "msg": f"Dashboard pending request count loaded successfully for {username}",
            "current_api": request.full_path,
            "client_ip": request.remote_addr,
            "response_at": str(datetime.datetime.now())
        }
        log_entry_event.log_api_call(log_entry_data)

        # print("Request completed successfully")
        return jsonify(response_data['app_notifications_count']), 200

    except Exception as e:
        print(f"An error occurred while processing the request. Please try again later. {str(e)}")
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500

    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_notifylist.mongo_dbconnect_close()

@android_api.route('/dashboard-statuswise-notify-count', methods=['GET'])
@jwt_required()
def statuswise_notification_count():
    try:
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
        log_entry_event = myserv_update_users_logs()

        username = get_jwt_identity()
        response_data = {
            'total_count': 0,
            'status_count': {}
        }
        
        # Match stage to find notifications either sent to or from the user
        match_stage = {
            '$or': [
                {'notify_to_id': username},
                # {'notify_from_id': username}
            ]
        }
        
        pipeline = [
            {
                '$match': match_stage
            },
            {
                '$group': {
                    '_id': {
                        'notify_status': '$notify_status'
                    },
                    'count': {'$sum': 1}
                }
            }
        ]
        
        # Execute the aggregation pipeline
        notification_counts = list(mpwz_notifylist.aggregate(pipeline))

        # Process the aggregation results
        for doc in notification_counts:
            if '_id' in doc and isinstance(doc['_id'], dict):
                notify_status = doc['_id'].get('notify_status')
                count = doc.get('count', 0)

                if notify_status:
                    # Update the count for the specific notify_status
                    response_data['status_count'][notify_status] = response_data['status_count'].get(notify_status, 0) + count
                    response_data['total_count'] += count
            else:
                raise ValueError(f"Invalid structure for document: {doc}")

        # Log the event
        if response_data['total_count'] > 0:
            log_entry_data = {
                "msg": f"Dashboard status-wise count loaded successfully for {username}",
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": str(datetime.datetime.now())
            }
            log_entry_event.log_api_call(log_entry_data)

           #  print("Request completed successfully")
            # Return the response with total counts and status counts
            return jsonify({
                "total_count": response_data['total_count'],
                "status_count": response_data['status_count']
            }), 200
        else:
            return jsonify({
                "status_count": {
                    "APPROVED": 0,
                    "PENDING": 0,
                    "REJECTED": 0,
                    "REASSIGNED": 0
                },
                "total_count": 0
            }), 404
            # return jsonify({"msg": f"No notifications found for the user {username}."}), 404

    except Exception as e:
        print(f"An error occurred while processing the request. Please try again later. {str(e)}")
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500

    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_notifylist.mongo_dbconnect_close()

@android_api.route('/admin-dashboard-statuswise-notify-count', methods=['GET'])
@jwt_required()
def admin_statuswise_notification_count():
    try:
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
        log_entry_event = myserv_update_users_logs()

        username = get_jwt_identity()
        response_data = {
            'total_count': 0,
            'status_count': {}
        }
        
        # Match stage to find notifications either sent to or from the user
        match_stage = {
            '$or': [
                {'notify_to_id': username},
                {'notify_from_id': username}
            ]
        }
        
        pipeline = [
            # {
            #     '$match': match_stage
            # },
            {
                '$group': {
                    '_id': {
                        'notify_status': '$notify_status'
                    },
                    'count': {'$sum': 1}
                }
            }
        ]
        
        # Execute the aggregation pipeline
        notification_counts = list(mpwz_notifylist.aggregate(pipeline))

        # Process the aggregation results
        for doc in notification_counts:
            if '_id' in doc and isinstance(doc['_id'], dict):
                notify_status = doc['_id'].get('notify_status')
                count = doc.get('count', 0)

                if notify_status:
                    # Update the count for the specific notify_status
                    response_data['status_count'][notify_status] = response_data['status_count'].get(notify_status, 0) + count
                    response_data['total_count'] += count
            else:
                raise ValueError(f"Invalid structure for document: {doc}")

        # Log the event
        if response_data['total_count'] > 0:
            log_entry_data = {
                "msg": f"Dashboard status-wise count loaded successfully for {username}",
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": str(datetime.datetime.now())
            }
            log_entry_event.log_api_call(log_entry_data)

           #  print("Request completed successfully")
            # Return the response with total counts and status counts
            return jsonify({
                "total_count": response_data['total_count'],
                "status_count": response_data['status_count']
            }), 200
        else:
            return jsonify({
                "status_count": {
                    "APPROVED": 0,
                    "PENDING": 0,
                    "REJECTED": 0,
                    "REASSIGNED": 0
                },
                "total_count": 0
            }), 404
            # return jsonify({"msg": f"No notifications found for the user {username}."}), 404

    except Exception as e:
        print(f"An error occurred while processing the request. Please try again later. {str(e)}")
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500

    finally:
        log_entry_event.mongo_dbconnect_close()
        mpwz_notifylist.mongo_dbconnect_close()


@android_api.route('/dashboard-recent-actiondone-history', methods=['GET'])
@jwt_required()
def dashboard_action_history():
    try:
        mpwz_notifylist = MongoCollection("mpwz_user_action_history")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        response_data = []
        query = {
            'notify_status': {'$in': ['APPROVED', 'REJECTED', 'REASSIGNED']},
            # 'notify_to_id': {'$regex': f'^{username}'} 
        }        
        # Fetch data using query
        notifications = mpwz_notifylist.find_sortall(query).sort("action_at", -1).limit(5)

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
                                "msg": f"request List loaded successfully for {username}",
                                "current_api": request.full_path,
                                "client_ip": request.remote_addr,
                                "response_at": str(datetime.datetime.now())
                    } 
                    log_entry_event.log_api_call(response_data_logs) 
                   #  print("Request completed successfully")
                    return jsonify(response_data), 200   
        else:
            return jsonify({"msg": "No notifications found."}), 400
    except Exception as e:
        print(f"An error occurred while processing the request. Exception: {str(e)}")
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_notifylist.mongo_dbconnect_close() 

@android_api.route('/statuswise-notify-list', methods=['GET'])
@jwt_required()
def statuswise_notification_list():
    try:
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
        mpwz_buttons = MongoCollection("mpwz_buttons")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        notification_status = request.args.get('notification_status')  
        response_data=[]        
        query = {
            'notify_to_id': username,
            # 'notify_from_id': username,
            'notify_status':notification_status
        }        
        # Fetch data using query
        notifications = mpwz_notifylist.find(query)

        for notification in notifications:
            # Create a new dictionary with only the required fields
            if notification_status==myserv_varriable_list.notification_status_PENDING:                
                app_type=notification.get("app_source")
                unique_button_names = mpwz_buttons.find_distinct("button_name", {"app_source": app_type})
            else:
                unique_button_names=[]   

            filtered_notification = {
                "app_request_type": notification.get("app_request_type"),
                "app_source": notification.get("app_source"),
                "app_source_appid": notification.get("app_source_appid"),
                "buttons": unique_button_names,
                "mpwz_id": notification.get("mpwz_id"),
                "notify_comments": notification.get("notify_comments"),
                "notify_datetime": notification.get("notify_datetime"),
                "notify_description": notification.get("notify_description"),
                "notify_from_id": notification.get("notify_from_id"),
                "notify_from_name": notification.get("notify_from_name"),
                "notify_intiatedby": notification.get("notify_intiatedby"),
                "notify_notes": notification.get("notify_notes"),
                "notify_refsys_id": notification.get("notify_refsys_id"),
                "notify_status": notification.get("notify_status"),
                "notify_to_id": notification.get("notify_to_id"),
                "notify_to_name": notification.get("notify_to_name")
            }
            response_data.append(filtered_notification)
        # Log the response statuses
        if response_data:
                    response_data_logs = {
                                "msg": f"request List loaded successfully for {username}",
                                "current_api": request.full_path,
                                "client_ip": request.remote_addr,
                                "response_at": str(datetime.datetime.now())
                    } 
                    log_entry_event.log_api_call(response_data_logs) 
                   #  print("Request completed successfully")
                    return jsonify(response_data), 200   
        else:
            return jsonify({"msg": "No notifications found."}), 400
    except Exception as e:
        print(f"An error occurred while processing the request. Exception: {str(e)}")
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_notifylist.mongo_dbconnect_close() 

@android_api.route('/dashboard-api-logs-hits-count', methods=['GET'])
@jwt_required()
def get_api_hits_count():
    try:
        mpwz_users_api_logs = MongoCollection("mpwz_users_api_logs")
        hits_count = mpwz_users_api_logs.count_documents({})
       #  print(f"Request completed successfully: total_api_hits = {hits_count}")
        return jsonify({"total_api_hits": hits_count}), 200
    except Exception as e:
        print(f"Request failed with error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        mpwz_users_api_logs.mongo_dbconnect_close()

@android_api.route('/dashboard-collection-size-status', methods=['GET'])
@jwt_required()
def collection_status():    
    db_service = myserv_update_dbservices()   
    try:
        total_rows, total_size_gb, collection_stats = db_service.get_collection_status()   
        # Return the response as JSON
       #  print(f"Request completed successfully: total_rows = {total_rows}, total_size_gb = {total_size_gb}, collection_stats = {collection_stats}")
        return jsonify({
            "total_rows": total_rows,
            "total_size_gb": total_size_gb,
            "collection_stats": collection_stats
        }), 200
    except Exception as e:
        print(f"Request failed with error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        db_service.mongo_dbconnect_close()  # Ensure this method exists

@android_api.route('/dashboard-active-users-count', methods=['GET'])
@jwt_required()
def get_user_count():    
    mpwz_integration_users = MongoCollection("mpwz_integration_users")
    try:
        user_count = mpwz_integration_users.count_documents({})
       #  print(f"Request completed successfully: total_users = {user_count}")
        return jsonify({"total_users": user_count}), 200
    except Exception as e:
        print(f"Request failed with error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        mpwz_integration_users.mongo_dbconnect_close()

@android_api.route('/verify-oneapp-url', methods=['GET'])
def verify_oneapp_url():
    """Verify that the one app backend is working fine"""
    return jsonify({"msg": "one app backend is working fine"}), 200
