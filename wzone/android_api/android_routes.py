# android_api/android_routes.py
import base64
import datetime
import time
import bcrypt
import ast  
from flask import jsonify, request
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from flask_pymongo import PyMongo
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices.myserv_update_users_logs import myserv_update_users_logs
from myservices.myserv_update_users_api_logs import myserv_update_users_api_logs
from myservices.myserv_connection_forblueprints import MongoCollection
from . import android_api

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

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        log_entry_event_api.mongo_dbconnect_close()

@android_api.route('/android-api-status', methods=['GET'])
def status():
    return jsonify({"message": "Android API is Working"})

@android_api.route('/login', methods=['POST'])
def login():
    try:
        # Initialize MongoCollection and other Class's  
        mpwz_integration_users_collection = MongoCollection("mpwz_integration_users")
        log_entry_event = myserv_update_users_logs()
        data = request.get_json()
        username = data.get("username") 
        password = data.get("password")  
        access_token=''
        # Retrieve the user from the collection
        user = mpwz_integration_users_collection.find_one({"username": username}) 
        if user:
            stored_hashed_password = user['password']
            user_role = user['user_role']
            
            # Ensure the stored_hashed_password is in bytes
            if isinstance(stored_hashed_password, str):
                stored_hashed_password = stored_hashed_password.encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                   
                current_datetime = datetime.datetime.now()
                if user_role=='api_user' :                
                    token_fromdb = user['token_app'] 
                    token_expiredon_fromdb = user['token_expiredon']                       
                    token_expiredon_fromdb = datetime.datetime.fromisoformat(token_expiredon_fromdb)  

                    if token_expiredon_fromdb < current_datetime:                         
                        print("New Token Issued for integration users only")  
                        access_token = create_access_token(identity=username, expires_delta=datetime.timedelta(days=365))
                        jwt_claims = decode_token(access_token)
                        expired_on = datetime.datetime.fromtimestamp(jwt_claims['exp']).isoformat()
                        issued_on = datetime.datetime.fromtimestamp(jwt_claims['iat']).isoformat() 
                        update_query = {
                            "token_app": access_token,
                            "token_issuedon": issued_on,
                            "token_expiredon": expired_on,
                        }
                        # Find the document and update it
                        mpwz_integration_users_collection.update_one(
                            {"username": username},
                            {"$set": update_query}
                        )
                    else:  # Token already issued so return it
                        try:
                            jwt_claims = decode_token(token_fromdb)
                            if jwt_claims:
                                access_token = token_fromdb
                                # print("Token is valid. Claims:", jwt_claims)
                                print("Token Issued from database only for integration user")
                        except Exception as e:
                            return jsonify({"msg": f"Token is not valid Please login again or contact admin for assistance: {str(e)}"}), 401               
                      
                elif user_role=='android_user' :                           
                    app_token_fromdb = user['token_app'] 
                    app_token_expiredon_fromdb = user['token_expiredon']                       
                    app_token_expiredon_fromdb = datetime.datetime.fromisoformat(app_token_expiredon_fromdb)  

                    if app_token_expiredon_fromdb < current_datetime:                         
                        print("New Token Issued for mobile app users only")  
                        access_token = create_access_token(identity=username, expires_delta=datetime.timedelta(days=1))
                        jwt_claims = decode_token(access_token)
                        expired_on = datetime.datetime.fromtimestamp(jwt_claims['exp']).isoformat()
                        issued_on = datetime.datetime.fromtimestamp(jwt_claims['iat']).isoformat() 
                        update_query = {
                            "token_app": access_token,
                            "token_issuedon": issued_on,
                            "token_expiredon": expired_on,
                        }
                        # Find the document and update it
                        mpwz_integration_users_collection.update_one(
                            {"username": username},
                            {"$set": update_query}
                        )
                    else:  # Token already issued so return it
                        try:
                            jwt_claims = decode_token(app_token_fromdb)
                            if jwt_claims:
                                access_token = app_token_fromdb
                                # print("Token is valid. Claims:", jwt_claims)
                                print("Token Issued from database only for mobile app user")
                        except Exception as e:
                            return jsonify({"msg": f"Token is not valid Please login again or contact admin for assistance: {str(e)}"}), 401 
                        
                        response_data = {"request_by":username,"message": "Token Issued successfully for Login"}
                        log_entry_event.log_api_call(response_data)             
                      
                elif user_role=='admin_user' :                               
                    app_token_fromdb = user['token_app'] 
                    app_token_expiredon_fromdb = user['token_expiredon']                       
                    app_token_expiredon_fromdb = datetime.datetime.fromisoformat(app_token_expiredon_fromdb)  

                    if app_token_expiredon_fromdb < current_datetime:                         
                        print("New Token Issued for mobile app users only")  
                        access_token = create_access_token(identity=username, expires_delta=datetime.timedelta(hours=1))
                        jwt_claims = decode_token(access_token)
                        expired_on = datetime.datetime.fromtimestamp(jwt_claims['exp']).isoformat()
                        issued_on = datetime.datetime.fromtimestamp(jwt_claims['iat']).isoformat() 
                        update_query = {
                            "token_app": access_token,
                            "token_issuedon": issued_on,
                            "token_expiredon": expired_on,
                        }
                        # Find the document and update it
                        mpwz_integration_users_collection.update_one(
                            {"username": username},
                            {"$set": update_query}
                        )
                    else:  # Token already issued so return it
                        try:
                            jwt_claims = decode_token(app_token_fromdb)
                            if jwt_claims:
                                access_token = app_token_fromdb
                                # print("Token is valid. Claims:", jwt_claims)
                                print("Token Issued from database only for mobile app user")
                        except Exception as e:
                            return jsonify({"msg": f"Token is not valid Please login again or contact admin for assistance: {str(e)}"}), 401 
                        
                        response_data = {"request_by":username,"message": "Token Issued successfully for Login"}
                        log_entry_event.log_api_call(response_data)
                else:
                    return jsonify({"msg": "Invalid user_role authentication error"}), 401
                return jsonify(access_token=access_token), 200            
            else:
                return jsonify({"msg": "Invalid username or password"}), 401
        else:
            return jsonify({"msg": "Invalid username or password"}), 401             

    except Exception as error:
        return jsonify({"msg": "An error occurred while processing your request", "error": str(error)}), 500
    
    finally : 
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
        
        mpwz_integration_users.update_one({"username": username}, {"$set": {"password": hashed_password}})

        response_data = {
            "msg": f"Password Changed successfully for {username}",
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
         mpwz_integration_users.mongo_dbconnect_close()

@android_api.route('/userprofile', methods=['GET'])
@jwt_required()
def view_profile():
    try:
        mpwz_integration_users = MongoCollection("mpwz_integration_users")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        # Retrieve the user profile from the database
        user = mpwz_integration_users.find_one({"username": username})

        if user:
            for key, value in user.items():
                if isinstance(value, bytes):
                    user[key] = base64.b64encode(value).decode('utf-8')  
            response_data = {
                "msg": f"User Profile loaded successfully for {username}",
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": datetime.datetime.now().isoformat()
            }
            log_entry_event.log_api_call(response_data)
            return jsonify(user), 200
        else:
            return jsonify({"msg": "User not found in records"}), 404

    except Exception as e:
        return jsonify({"msg": f"An error occurred while retrieving the user profile. error. {str(e)}"}), 500
    
    finally : 
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
                    "response_at": datetime.datetime.now().isoformat()
                } 
                log_entry_event.log_api_call(response_data)
            return jsonify(response_statuses), 200
        else:
            return jsonify({"statuses": "No button_name added by mpwz admin"}), 404
    except Exception as e:
        return jsonify({"msg": f"An error occurred while processing the request. Please try again later. {str(e)}"}), 500
    
    finally : 
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
                    "response_at": datetime.datetime.now().isoformat()
                }                   
                log_entry_event.log_api_call(response_data)
            return jsonify(response_statuses), 200
        else:
            return jsonify({"msg": "No apps added by mpwz admin"}), 404

    except Exception as e:
        return jsonify({"msg": f"An error occurred while processing the request. errors. {str(e)}"}), 500
    
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_integrated_app.mongo_dbconnect_close()   
 
@android_api.route('/my-request-notify-count', methods=['GET'])
@jwt_required()
def my_request_notification_count():
    try:
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

        match_stage = {
            'notify_from_id': username
        }
        
        if notification_status:
            match_stage['notify_status'] = notification_status

        # Mongo aggregation pipeline
        pipeline = [
            {
                '$match': match_stage
            },
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
        
        # Fetch notification counts using aggregate
        notification_counts = list(mpwz_notifylist.aggregate(pipeline))  # Ensure it's a list
        
        # Log the aggregation result
        current_time = datetime.datetime.now().isoformat()
        print(f"[{current_time}] Aggregation Result: {notification_counts}")  # Debug log for aggregation result

        if notification_counts:
            # Process each aggregation result
            for doc in notification_counts:
                # Log the structure of each doc
                print(f"[{current_time}] Processing doc: {doc}")  # Debug log for each document
                
                # Parse the string representation of the dict in _id into a real dictionary
                try:
                    doc_id = ast.literal_eval(doc['_id'])  # Safely convert string to dictionary
                except Exception as e:
                    print(f"Error parsing _id: {e}")
                    continue

                if isinstance(doc_id, dict) and 'app_source' in doc_id and 'notify_status' in doc_id:
                    app_source = doc_id['app_source']
                    notify_status = doc_id['notify_status']
                    count = doc['count']

                    # Initialize app_source if not already in response_data
                    if app_source not in response_data['app_notifications_count']:
                        response_data['app_notifications_count'][app_source] = {}

                    # Store the count under the appropriate notify_status
                    response_data['app_notifications_count'][app_source][notify_status] = count

                    # If the notify_status is 'Pending', add to the total count
                    if notify_status == 'PENDING':
                        response_data['total_pending_count'] += count

        # Log the successful response
        log_data = {
            "msg": f"Pending request count loaded successfully for {username}",
            "current_api": request.full_path,
            "client_ip": request.remote_addr,
            "response_at": datetime.datetime.now().isoformat()
        }
        log_entry_event.log_api_call(log_data)

        # Return the response data
        return jsonify(response_data), 200

    except Exception as e:
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
        mpwz_integrated_app = MongoCollection("mpwz_integrated_app")
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
            'notify_from_id': username,
            'notify_status':notification_status
        }
        
        # Fetch data using query
        notifications = mpwz_notifylist.find(query)
        # unique_button_names = mongo.db.mpwz_buttons.distinct('button_name')

        for notification in notifications:
            notification_copy = notification.copy()  
            notification_copy.pop('_id', None) 
            # notification_copy['buttons'] = unique_button_names  
            response_data.append(notification_copy)
        # Log the response statuses
        if notifications:
            response_statuses = []
            for notification in response_data:
                    # Creating new dictionary to remove _id from response
                    status_response = {key: value for key, value in notification.items() if key != '_id'}
                    response_statuses.append(status_response)
                            # Log entry in table 
                    response_data = {
                                "msg": f"my request list loaded successfully for {username}",
                                "current_api": request.full_path,
                                "client_ip": request.remote_addr,
                                "response_at": datetime.datetime.now().isoformat()
                    }                   
                    log_entry_event.log_api_call(response_data)                
            return jsonify(response_statuses), 200             
        else:
            return jsonify({"msg": f"No pending notifications found for {username}."}), 400
    except Exception as e:
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500   
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_notifylist.mongo_dbconnect_close() 
         mpwz_integrated_app.mongo_dbconnect_close() 
   
@android_api.route('/pending-notify-count', methods=['GET'])
@jwt_required()
def pending_notification_count():
    try:
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

        match_stage = {
            'notify_to_id': username
        }
        
        if notification_status:
            match_stage['notify_status'] = notification_status

        # Mongo aggregation pipeline
        pipeline = [
            {
                '$match': match_stage
            },
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
        notification_counts = list(mpwz_notifylist.aggregate(pipeline))  
        
        # Log the aggregation result
        current_time = datetime.datetime.now().isoformat()
        print(f"[{current_time}] Aggregation Result: {notification_counts}")  

        if notification_counts:
            for doc in notification_counts:
                print(f"[{current_time}] Processing doc: {doc}")  
                try:
                    doc_id = ast.literal_eval(doc['_id'])  
                except Exception as e:
                    print(f"Error parsing _id: {e}")
                    continue

                if isinstance(doc_id, dict) and 'app_source' in doc_id and 'notify_status' in doc_id:
                    app_source = doc_id['app_source']
                    notify_status = doc_id['notify_status']
                    count = doc['count']
                    
                    if app_source not in response_data['app_notifications_count']:
                        response_data['app_notifications_count'][app_source] = {}

                    # Store the count under the appropriate notify_status
                    response_data['app_notifications_count'][app_source][notify_status] = count

                    # If the notify_status is 'Pending', add to the total count
                    if notify_status == 'PENDING':
                        response_data['total_pending_count'] += count

        # Log the successful response
        log_data = {
            "msg": f"Pending request count loaded successfully for {username}",
            "current_api": request.full_path,
            "client_ip": request.remote_addr,
            "response_at": datetime.datetime.now().isoformat()
        }
        log_entry_event.log_api_call(log_data)

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
        # data = request.get_json()  
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
        unique_button_names = mpwz_buttons.find_distinct('button_name')

        for notification in notifications:
            notification_copy = notification.copy()  
            notification_copy.pop('_id', None) 
            notification_copy['buttons'] = unique_button_names  
            response_data.append(notification_copy) 
            

        # Log the response statuses
        if response_data:
            response_statuses = []
            for notification in response_data:
                    # Creating new dictionary to remove _id from response
                    status_response = {key: value for key, value in notification.items() if key != '_id'}
                    response_statuses.append(status_response)
                        # Log entry in table 
                    response_data = {
                                    "msg": f"pending request list loaded successfully for {username}",
                                    "current_api": request.full_path,
                                    "client_ip": request.remote_addr,
                                    "response_at": datetime.datetime.now().isoformat()
                    }                     
                    log_entry_event.log_api_call(response_data)
     
        else:
            return jsonify({"msg": "No pending notifications found."}), 400
        return jsonify(response_statuses), 200
    except Exception as e:
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_notifylist.mongo_dbconnect_close() 
         mpwz_integrated_app.mongo_dbconnect_close() 
         mpwz_buttons.mongo_dbconnect_close() 
  
@android_api.route('/action-history', methods=['GET', 'POST'])
@jwt_required()
def action_history():
    try:
        mpwz_user_action_history = MongoCollection("mpwz_user_action_history")
        log_entry_event = myserv_update_users_logs()
        seq_gen = myserv_generate_mpwz_id_forrecords()
        username = get_jwt_identity()
        application_type = request.args.get('application_type')
        if request.method == 'GET':
            if application_type:
                action_history_records = list(mpwz_user_action_history.find(
                    {
                        "$and": [
                            {"app_source": application_type},
                            {
                                "$or": [
                                    {"notify_to_id": username},
                                    {"notify_from_id": username}
                                ]
                            }
                        ]
                    }
                ))

                if action_history_records:
                    response_statuses = []
                    for status in action_history_records:
                        # Creating new dictionary to remove _id from response
                        status_response = {key: value for key, value in status.items() if key != '_id'}
                        response_statuses.append(status_response)
                        # Log entry in table 
                        response_data = {
                            "msg": f"Action History List loaded successfully for {username}",
                            "current_api": request.full_path,
                            "client_ip": request.remote_addr,
                            "response_at": datetime.datetime.now().isoformat()
                        }  
                        log_entry_event.log_api_call(response_data)

                    return jsonify(response_statuses), 200
                else:
                    return jsonify({"msg": "No action history found."}), 404
            else:
                return jsonify({"msg": "Application is not integrated with us, please contact admin"}), 400

        elif request.method == 'POST':
            data = request.json
            if application_type:
                required_fields = [
                    "action_datetime", "app_id", "notify_details",
                    "notify_from_id", "notify_from_name",
                    "notify_refsys_id", "notify_remark",
                    "notify_to_id", "notify_to_name", "mpwz_id"
                ]

                if not all(field in data for field in required_fields):
                    return jsonify({"msg": "Missing required fields"}), 400
                else:        
                    existing_record = mpwz_user_action_history.find_one({"notify_refsys_id": data["notify_refsys_id"]})
                    if existing_record:      
                        return jsonify({"msg": "Records with notify_refsys_id already existed in database."}), 400
                    else: 
                        mpwz_id_actionhistory = seq_gen.get_next_sequence('mpwz_user_action_history')
                        data['sequence_no'] = str(data['mpwz_id'])
                        data['mpwz_id'] = str(mpwz_id_actionhistory)
                        data['notify_from_id'] = username
                        data['action_by'] = username
                        data['response_at'] = datetime.datetime.now().isoformat()

                        response = mpwz_user_action_history.insert_one(data)
                        if response:
                            # Log entry in table 
                            response_data = {
                                "msg": f"Action History Updated successfully for {username}",
                                "current_api": request.full_path,
                                "client_ip": request.remote_addr,
                                "response_at": datetime.datetime.now().isoformat()
                            } 
                            log_entry_event.log_api_call(response_data)

                            return jsonify({"msg": f"Action history updated successfully, mpwz_id: {mpwz_id_actionhistory}"}), 200
                        else:
                            return jsonify({"msg": "Failed to update action history logs"}), 400
            else:
                return jsonify({"msg": "Invalid request encountered at server."}), 400
    except Exception as e:
        return jsonify({"msg": f"An error occurred while processing the request. Please try again later.{str(e)}"}), 500
    
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_user_action_history.mongo_dbconnect_close() 

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
        
        match_stage = {
            'notify_to_id': username
        } 
        
        pipeline = [
            {
                '$match': match_stage
            },
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
            if isinstance(doc, dict):
                print("Document:", doc)  # Debugging to check doc structure
                if '_id' in doc:
                    # Try to parse the _id field as a dictionary
                    try:
                        _id = eval(doc['_id'])
                    except Exception as e:
                        # If parsing fails, raise a ValueError
                        raise ValueError(f"Invalid structure for _id field in document: {doc}")
                    
                    # Ensure _id is a dictionary
                    if not isinstance(_id, dict):
                        raise ValueError(f"Invalid structure for _id field in document: {doc}")
                    
                    app_source = _id.get('app_source')
                    notify_status = _id.get('notify_status')
                    count = doc.get('count')
                    
                    if app_source is None or notify_status is None:
                        raise ValueError(f"Missing expected data in document: {doc}")
                    
                    # Initialize the app_source dictionary if it doesn't exist
                    if app_source not in response_data['app_notifications_count']:
                        response_data['app_notifications_count'][app_source] = {}

                    # Set the count for the specific notify_status
                    response_data['app_notifications_count'][app_source][notify_status] = count
                else:
                    raise ValueError(f"Invalid structure for document: {doc}")
            else:
                raise ValueError(f"Expected a dictionary, but got: {type(doc)}")

        # Log the response statuses if results exist
        response_statuses = []
        for status in notification_counts:
            # Make sure that we are only working with a valid structure
            if isinstance(status, dict):
                status_response = {key: value for key, value in status.items() if key != '_id'}
                response_statuses.append(status_response)

        # Log the event
        log_entry_data = {
            "msg": f"Dashboard pending request count loaded successfully for {username}",
            "current_api": request.full_path,
            "client_ip": request.remote_addr,
            "response_at": datetime.datetime.now().isoformat()
        }
        log_entry_event.log_api_call(log_entry_data)       

        return jsonify([response_data['app_notifications_count']]), 200

    except Exception as e:
        # Catch exceptions and provide specific error information
        print("Error:", e)  # This will output to your console
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
                {'notify_from_id': username}
            ]
        } 
        
        pipeline = [
            {
                '$match': match_stage
            },
            {
                '$group': {
                    '_id': {
                        'notify_status': '$notify_status',
                    },
                    'count': {'$sum': 1}
                }
            }
        ] 
        
        notification_counts = mpwz_notifylist.aggregate(pipeline)        
        notification_counts_list = list(notification_counts)  # Convert cursor to list for multiple iterations

        for doc in notification_counts_list:
            # Try to parse the _id field as a dictionary
            try:
                _id = eval(doc['_id'])
            except Exception as e:
                # If parsing fails, raise a ValueError
                raise ValueError(f"Invalid structure for _id field in document: {doc}")
            
            # Ensure _id is a dictionary
            if not isinstance(_id, dict):
                raise ValueError(f"Invalid structure for _id field in document: {doc}")
            
            notify_status = _id.get('notify_status')
            # Initialize status_count for the notify_status if it doesn't exist
            if notify_status not in response_data['status_count']:
                response_data['status_count'][notify_status] = 0

            # Update the count for the specific notify_status
            response_data['status_count'][notify_status] += doc['count']
            response_data['total_count'] += doc['count']

        # Log the response statuses
        if response_data['total_count'] > 0:
            response_data_logs = {
                                    "msg": f"Dashboard Status wise countcount loaded successfully for {username}",
                                    "current_api": request.full_path,
                                    "client_ip": request.remote_addr,
                                    "response_at": datetime.datetime.now().isoformat()
            } 
            # Log entry in table 
            log_entry_event.log_api_call(response_data_logs)

            # Return the response with total counts and status counts
            return jsonify({
                "total_count": response_data['total_count'],
                "status_count": response_data['status_count']
            }), 200
        else:
            return jsonify({"msg": f"No notifications found for the user {username}."}), 404  
    except Exception as e:
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_notifylist.mongo_dbconnect_close()     

@android_api.route('/dashboard-recent-actiondone-history', methods=['GET'])
@jwt_required()
def dashboard_action_history():
    try:
        mpwz_user_action_history = MongoCollection("mpwz_user_action_history")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        if request.method == 'GET':          
                query = {
                        "$or": [
                            {"notify_to_id": username},
                            {"notify_from_id": username}
                        ]
                }
                # sort_query = [("action_datetime", -1)]
                limit = 5
                action_history_records = mpwz_user_action_history.find(query)
                if action_history_records:
                    action_history_records = sorted(action_history_records, key=lambda x: x['action_datetime'], reverse=True)[:limit]

                if action_history_records:
                    response_statuses = []
                    for status in action_history_records:
                        # Ensure `status` is a dictionary
                        if isinstance(status, dict):
                            # Creating new dictionary to remove _id from response
                            status_response = {key: value for key, value in status.items() if key != '_id'}
                            response_statuses.append(status_response)
                        else:
                            raise ValueError(f"Expected a dictionary, but got: {type(status)}")
                    
                    # Log entry in table 
                    response_data = {
                            "msg": f"History loaded successfully for {username}",
                            "current_api": request.full_path,
                            "client_ip": request.remote_addr,
                            "response_at": datetime.datetime.now().isoformat()
                    } 
                    log_entry_event.log_api_call(response_data) 
                    return jsonify(response_statuses), 200
                else:
                    return jsonify({"msg": "No action history found."}), 404            
    except Exception as e:
        return jsonify({"msg": f"An error occurred while processing the request. Please try again later.{str(e)}"}), 500
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_user_action_history.mongo_dbconnect_close()

@android_api.route('/statuswise-notify-list', methods=['GET'])
@jwt_required()
def statuswise_notification_list():
    try:
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
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
            notification_copy = notification.copy()  
            notification_copy.pop('_id', None) 
            response_data.append(notification_copy) 
            

        # Log the response statuses
        if response_data:
            response_statuses = []
            for notification in response_data:
                    # Creating new dictionary to remove _id from response
                    status_response = {key: value for key, value in notification.items() if key != '_id'}
                    response_statuses.append(status_response)
                            # Log entry in table 
                    response_data = {
                                "msg": f"request List loaded successfully for {username}",
                                "current_api": request.full_path,
                                "client_ip": request.remote_addr,
                                "response_at": datetime.datetime.now().isoformat()
                    } 
                    log_entry_event.log_api_call(response_data)    
        else:
            return jsonify({"msg": "No notifications found."}), 400
        return jsonify(response_statuses), 200
    except Exception as e:
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_notifylist.mongo_dbconnect_close() 

@android_api.route('/update-notify-inhouse-app', methods=['POST'])
@jwt_required()
def update_notify_status_inhouse_app():
    try:
        mpwz_notifylist = MongoCollection("mpwz_notifylist")
        mpwz_integrated_app = MongoCollection("mpwz_integrated_app")
        log_entry_event = myserv_update_users_logs()
        username = get_jwt_identity()
        data = request.get_json() 
        remote_response = "ok cofirm"
        ngb_user_details = "" 
        app_source = request.args.get('app_source')
        app_exists = mpwz_integrated_app.find_one({"app_name": app_source})

        if not app_exists:
            return jsonify({"msg": f"Requesting application is not integrated with our server:- {app_exists}"}), 400
       
        required_fields = ["mpwz_id", "notify_status", "notify_refsys_id", "remarks_byapprover","notify_to_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"msg": f"{field} is required"}), 400

        notify_to_id = data["notify_to_id"]
        if notify_to_id != username:
            return jsonify({"msg": "You are not authorized to update this notification status."}), 403
        if app_source == 'ngb':
            print(f"Searching for record with mpwz_id: {data['mpwz_id']}, notify_to_id: {data['notify_to_id']}, notify_refsys_id: {data['notify_refsys_id']}")
            ngb_user_details = mpwz_notifylist.find_one({
                "mpwz_id": data['mpwz_id'],
                "notify_to_id": data['notify_to_id'],
                "notify_refsys_id": data['notify_refsys_id']
            })
            print(ngb_user_details)

            # if ngb_user_details is None:
            #     return jsonify({"msg": "Notification details not found in databaase"}), 404

            # if ngb_user_details.get("notify_type") == "CC4":
            #     shared_api_data = {
            #         "id": ngb_user_details["notify_refsys_id"],
            #         "locationCode": ngb_user_details["locationCode"],
            #         "approver": ngb_user_details["approver"],
            #         "billId": ngb_user_details["billId"],
            #         "billCorrectionProfileInitiatorId": ngb_user_details["billCorrectionProfileInitiatorId"],
            #         "status": data["notify_status"],
            #         "remark": ngb_user_details["remark"],
            #         "updatedBy": ngb_user_details["updatedBy"],
            #         "updatedOn": ngb_user_details["updatedOn"]
            #     }
            #     remote_response = ngb_postapi_services.notify_ngb_toupdate_cc4status(shared_api_data)

            # elif ngb_user_details.get("notify_type") == "CCB":
            #     shared_api_data = {
            #         "postingDate": ngb_user_details["postingDate"],
            #         "amount": ngb_user_details["amount"],
            #         "code": ngb_user_details["code"],
            #         "ccbRegisterNo": ngb_user_details["ccbRegisterNo"],
            #         "remark": ngb_user_details["remark"],
            #         "consumerNo": ngb_user_details["consumerNo"],
            #     }
            #     remote_response = ngb_postapi_services.notify_ngb_toupdate_ccbstatus(shared_api_data)
            # else:
            #     return jsonify({"msg": "Notification Type is not allowed to push data to NGB."}), 400

        # elif app_source == 'erp':
        #     return jsonify({"msg": "Notification Type is not allowed to push data to ERP."}), 400

        else:
            return jsonify({"msg": f"Something went wrong while verifying remote servers: {app_source}"}), 200
        
        if ngb_user_details:            
        # if remote_response is not None and remote_response.status_code == 200:
            update_query = {
                "notify_status": data["notify_status"],
                "notify_refsys_response": ngb_user_details,
                "notify_status_updatedon": datetime.datetime.now().isoformat(),
            }

            # Find the document and update it
            result = mpwz_notifylist.update_one(
                {"mpwz_id": data["mpwz_id"], "notify_to_id": data["notify_to_id"]},
                {"$set": update_query}            )

            if result.modified_count > 0:
                response_statuses = []
                for status in result:
                        status_response = {key: value for key, value in status.items() if key != '_id'}
                        response_statuses.append(status_response)
                        # Log entry in table 
                        response_data = {
                                    "msg": f"Notification Status Updated successfully for {username}",
                                    "current_api": request.full_path,
                                    "client_ip": request.remote_addr,
                                    "response_at": datetime.datetime.now().isoformat()
                        } 
                        log_entry_event.log_api_call(response_data)

                return jsonify({"msg": f"Notification Status Updated Successfully {result.modified_count}"}), 200
            else:
                return jsonify({"msg": f"Something went wrong while updating Notification in own servers: {app_source}"}), 400
        else:
            return jsonify({"msg": f"Something went wrong while updating Notification into remote servers: {app_source}"}), 200
    except Exception as e:
        return jsonify({"msg": f"Something went wrong while processing request in primary stage {str(e)}"}), 500
    finally : 
         log_entry_event.mongo_dbconnect_close() 
         mpwz_integrated_app.mongo_dbconnect_close() 
         mpwz_notifylist.mongo_dbconnect_close() 


