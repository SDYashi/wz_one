import base64
import datetime
import json
import os
import time
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager,create_access_token, decode_token, jwt_required, get_jwt_identity,get_jwt
from flask_cors import CORS
import bcrypt
from shared_api.erp_postapi_services import erp_apiservices
from shared_api.ngb_postapi_services import ngb_apiservices
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices.myserv_update_users_logs import myserv_update_users_logs
from myservices.myserv_connection_mongodb import myserv_connection_mongodb
from myservices.myserv_update_users_api_logs import myserv_update_users_api_logs

#register app with flask
app = Flask(__name__)
# cross origin allow for applications
CORS(app, resources={r"/*": {"origins": "*"}})

# intialize all class's for use app 
seq_gen = myserv_generate_mpwz_id_forrecords()
log_entry_event = myserv_update_users_logs()
log_entry_event_api = myserv_update_users_api_logs()
# mongo_db=myserv_connection_mongodb('admin')

# mongo database's configuration informations
app.config["MONGO_URI"] = "mongodb://localhost:27017/admin"
mongo = PyMongo(app)

# jwt token configuration
# app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] ='8ff09627ca698e84a587ccd3ae005f625ece33b3c999062e62dbf6e70c722323'  
jwt = JWTManager(app)

@app.before_request
def before_request():
    request.start_time = time.time() 

@app.after_request
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

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get("username") 
        password = data.get("password")  
        access_token=''
        # Retrieve the user from the collection
        user = mongo.db.mpwz_integration_users.find_one({"username": username}) 
        if user:
            stored_hashed_password = user['password']
            user_role = user['user_role']
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
                        mongo.db.mpwz_integration_users.update_one(
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
                        mongo.db.mpwz_integration_users.update_one(
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
                        mongo.db.mpwz_integration_users.update_one(
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
    
@app.route('/change_password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        username = get_jwt_identity()
        data = request.get_json()
        new_password = data.get("new_password")
        if not new_password:
            return jsonify({"msg": "New password is required"}), 400
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        # Update the password in the database
        response = mongo.db.mpwz_users.update_one({"username": username}, {"$set": {"password": hashed_password}})
        if response.modified_count == 0:
            return jsonify({"msg": "No changes made, password may be the same as the current one"}), 400        
        else: 
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

@app.route('/userprofile', methods=['GET'])
@jwt_required()
def view_profile():
    try:
        username = get_jwt_identity()
        # Retrieve the user profile from the database
        user = mongo.db.mpwz_users.find_one({"employee_number": username}, {"_id": 0})

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

@app.route('/notify-status', methods=['GET'])
@jwt_required()
def get_notify_status():
    try:
        username = get_jwt_identity()
        statuses = list(mongo.db.mpwz_notify_status.find())
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

@app.route('/notify-integrated-app', methods=['GET'])
@jwt_required()
def get_integrated_app_list():
    try:
        username = get_jwt_identity()
        statuses = list(mongo.db.mpwz_integrated_app.find())
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
   
@app.route('/action-history', methods=['GET', 'POST'])
@jwt_required()
def action_history():
    try:
        username = get_jwt_identity()
        application_type = request.args.get('application_type')
        if request.method == 'GET':
            if application_type:
                action_history_records = list(mongo.db.mpwz_user_action_history.find(
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
                    },
                    {"_id": 0}
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
                    existing_record = mongo.db.mpwz_user_action_history.find_one({"notify_refsys_id": data["notify_refsys_id"]})
                    if existing_record:      
                        return jsonify({"msg": "Records with notify_refsys_id already existed in database."}), 400
                    else: 
                        mpwz_id_actionhistory = seq_gen.get_next_sequence('mpwz_user_action_history')
                        data['sequence_no'] = str(data['mpwz_id'])
                        data['mpwz_id'] = str(mpwz_id_actionhistory)
                        data['notify_from_id'] = username
                        data['action_by'] = username
                        data['response_at'] = datetime.datetime.now().isoformat()

                        response = mongo.db.mpwz_user_action_history.insert_one(data)
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

@app.route('/my-request-notify-count', methods=['GET'])
@jwt_required()
def my_request_notification_count():
    try:
        username = get_jwt_identity()
        notification_status = request.args.get('notification_status')

        # Initialize response data
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

        notification_counts = mongo.db.mpwz_notifylist.aggregate(pipeline)

        # Process the aggregation results
        for doc in notification_counts:
            app_source = doc['_id']['app_source']
            notify_status = doc['_id']['notify_status']

            if app_source not in response_data['app_notifications_count']:
                response_data['app_notifications_count'][app_source] = {}
                response_data['app_notifications_count'][app_source][notify_status] = doc['count']
                response_data['total_pending_count'] += doc['count']

        # Log the response statuses
        if notification_counts:
            response_statuses = []
            for status in notification_counts:
                        status_response = {key: value for key, value in status.items() if key != '_id'}
                        response_statuses.append(status_response)
                            # Log entry in table 
                        response_data = {
                                "msg": f"my request count loaded successfully for {username}",
                                "current_api": request.full_path,
                                "client_ip": request.remote_addr,
                                "response_at": datetime.datetime.now().isoformat()
                        } 
                        log_entry_event.log_api_call(response_data)  
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"msg": f"An error occurred while processing the request. Please try again later.{str(e)}"}), 500

@app.route('/my-request-notify-list', methods=['GET'])
@jwt_required()
def my_request_notification_list():
    try:
        username = get_jwt_identity()
        application_type = request.args.get('application_type')
        notification_status = request.args.get('notification_status')

        # Check if the application type exists
        app_exists = mongo.db.mpwz_integrated_app.find_one({"app_name": application_type})
        if not app_exists:
            return jsonify({"msg": "application type does not exist."}), 400  
        response_data=[]
        
        query = {
            'app_source': application_type,  
            'notify_from_id': username,
            'notify_status':notification_status
        }
        
        # Fetch data using query
        notifications = mongo.db.mpwz_notifylist.find(query)
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
     
@app.route('/pending-notify-count', methods=['GET'])
@jwt_required()
def pending_notification_count():
    try:
        username = get_jwt_identity()
        notification_status = request.args.get('notification_status')
        response_data = {
            'username': username,
            'total_pending_count': 0,
            'app_notifications_count': {}
        }
        match_stage = {
            'notify_to_id': username,
            'notify_status':notification_status
        }        
        # if notification_status:
        #     match_stage['notify_status'] = notification_status

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
        
        notification_counts = mongo.db.mpwz_notifylist.aggregate(pipeline)        
        for doc in notification_counts:
            app_source = doc['_id']['app_source']
            notify_status = doc['_id']['notify_status']
            
            if app_source not in response_data['app_notifications_count']:
                response_data['app_notifications_count'][app_source] = {}

            response_data['app_notifications_count'][app_source][notify_status] = doc['count']
            response_data['total_pending_count'] += doc['count']

        # Log the response statuses
        if notification_counts:
            response_statuses = []
            for status in notification_counts:
                        status_response = {key: value for key, value in status.items() if key != '_id'}
                        response_statuses.append(status_response)
                        # Log entry in table 
                        response_data = {
                                    "msg": f"pending request count loaded successfully for {username}",
                                    "current_api": request.full_path,
                                    "client_ip": request.remote_addr,
                                    "response_at": datetime.datetime.now().isoformat()
                        } 
                        log_entry_event.log_api_call(response_data)       
        else:
          return jsonify({"msg": f"No notifications found for the user {username}."}), 404   
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500

@app.route('/pending-notify-list', methods=['GET'])
@jwt_required()
def pending_notification_list():
    try:
        username = get_jwt_identity()
        # data = request.get_json()  
        application_type = request.args.get('application_type')
        notification_status = request.args.get('notification_status')

        # Check if the application type exists
        app_exists = mongo.db.mpwz_integrated_app.find_one({"app_name": application_type})
        if not app_exists:
            return jsonify({"msg": "application type does not exist."}), 400  
        
        response_data=[]
        
        query = {
            'app_source': application_type,  
            'notify_to_id': username,
            'notify_status':notification_status
        }
        
        # Fetch data using query
        notifications = mongo.db.mpwz_notifylist.find(query)
        unique_button_names = mongo.db.mpwz_buttons.distinct('button_name')

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

@app.route('/dashboard-total-notify-count', methods=['GET'])
@jwt_required()
def total_notification_count():
    try:
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
        
        notification_counts = mongo.db.mpwz_notifylist.aggregate(pipeline)        
        for doc in notification_counts:
            app_source = doc['_id']['app_source']
            notify_status = doc['_id']['notify_status']
            count = doc['count']
            
            # Initialize the app_source dictionary if it doesn't exist
            if app_source not in response_data['app_notifications_count']:
                response_data['app_notifications_count'][app_source] = {}

            # Set the count for the specific notify_status
            response_data['app_notifications_count'][app_source][notify_status] = count

        # Log the response statuses
        if notification_counts:
            response_statuses = []
            for status in notification_counts:
                status_response = {key: value for key, value in status.items() if key != '_id'}
                response_statuses.append(status_response)
                        # Log entry in table 
                response_data = {
                                    "msg": f"Dashboard pending request count loaded successfully for {username}",
                                    "current_api": request.full_path,
                                    "client_ip": request.remote_addr,
                                    "response_at": datetime.datetime.now().isoformat()
                } 
                log_entry_event.log_api_call(response_data)       
        else:
            return jsonify({"msg": f"No notifications found for the user {username}."}), 404 
        return jsonify([response_data['app_notifications_count']]), 200
    except Exception as e:
        return jsonify({"msg": "An error occurred while processing your request", "error": str(e)}), 500

@app.route('/dashboard-statuswise-notify-count', methods=['GET'])
@jwt_required()
def statuswise_notification_count():
    try:
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
        
        notification_counts = mongo.db.mpwz_notifylist.aggregate(pipeline)        
        notification_counts_list = list(notification_counts)  # Convert cursor to list for multiple iterations

        for doc in notification_counts_list:
            notify_status = doc['_id']['notify_status']
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
     
@app.route('/dashboard-recent-actiondone-history', methods=['GET'])
@jwt_required()
def dashboard_action_history():
    try:
        username = get_jwt_identity()
        if request.method == 'GET':
                action_history_records = list(mongo.db.mpwz_user_action_history.find(
                    {
                    
                                "$or": [
                                    {"notify_to_id": username},
                                    {"notify_from_id": username}
                                ]
                    },
                    {"_id": 0}
                ).sort("action_datetime", -1).limit(5))

                if action_history_records:
                    response_statuses = []
                    for status in action_history_records:
                        # Creating new dictionary to remove _id from response
                        status_response = {key: value for key, value in status.items() if key != '_id'}
                        response_statuses.append(status_response)
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

@app.route('/statuswise-notify-list', methods=['GET'])
@jwt_required()
def statuswise_notification_list():
    try:
        username = get_jwt_identity()
        notification_status = request.args.get('notification_status')  
        response_data=[]        
        query = {
            'notify_to_id': username,
            # 'notify_from_id': username,
            'notify_status':notification_status
        }        
        # Fetch data using query
        notifications = mongo.db.mpwz_notifylist.find(query)

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

@app.route('/update-notify-inhouse-app', methods=['POST'])
@jwt_required()
def update_notify_status_inhouse_app():
    try:
        username = get_jwt_identity()
        data = request.get_json() 
        remote_response = "ok cofirm"
        ngb_user_details = "" 
        app_source = request.args.get('app_source')
        app_exists = mongo.db.mpwz_integrated_app.find_one({"app_name": app_source})

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
            ngb_user_details = mongo.db.mpwz_notifylist.find_one({
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
            result = mongo.db.mpwz_notifylist.update_one(
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


#Admin controller api for web users
@app.route('/shared-call/api/v1/create-integration-users', methods=['POST'])
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

@app.route('/change-password-byadminuser', methods=['PUT'])
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

@app.route('/notify-integrated-app', methods=['POST'])
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

@app.route('/notify-status', methods=['POST'])
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
 

## Extenal API for Get Data from Remote Servers ##
@app.route('/shared-call/api/v1/ngb/post-notifyngb', methods=['POST'])
@jwt_required()
def create_notification_from_ngb():
    username = get_jwt_identity()
    data = request.get_json()   
    application_type = request.args.get('app_source')    
    app_request_type =  data['app_request_type']
    print(f"requesting data for {app_request_type} and request comming from {application_type}")   

    app_exists = mongo.db.mpwz_integrated_app.find_one({"app_name": application_type})
    if application_type != 'ngb':
         return jsonify({"msg": "incomming request occurred from invalid app_source."}), 400 
    elif not app_exists:
        return jsonify({"msg": "requesting application is not integrated with our server."}), 400 
    else: 

        # required_fields_map = {
        #     "CC4": ["id", "locationCode", "approver", "billId", "billCorrectionProfileInitiatorId", "status", "remark", "updatedBy", "updatedOn"],
        #     "CCB": ["id", "postingDate", "amount", "code", "ccbRegisterNo", "remark", "consumerNo"]
        # }
        # # Check if the data_type exists in the required fields map
        # if app_request_type in required_fields_map:
        #     required_fields = required_fields_map[app_request_type]
        #     for field in required_fields:
        #         if field not in data:
        #             return jsonify({"msg": f"{field} is required for {app_request_type}."}), 400
        # else:
        #     return jsonify({"msg": f"Invalid data type: {app_request_type}."}), 400  
        
        # existing_record = mongo.db.mpwz_notifylist.find_one({"notify_refsys_id": data["notify_refsys_id"]})
        # if existing_record:      
        #     return jsonify({"msg": "Records with notify_refsys_id already existed in database."}), 400
        # else:  
            mpwz_id_sequenceno = seq_gen.get_next_sequence('mpwz_notifylist')
            if mpwz_id_sequenceno:  
                if app_request_type=="CC4":
                    data['mpwz_id'] = mpwz_id_sequenceno
                    data['app_source'] = "ngb"
                    data['app_source_appid'] =  seq_gen.generate_secretcode()
                    data['notify_status'] =  "PENDING"
                    data['notify_refsys_id'] =  seq_gen.generate_secretcode()
                    data['notify_to_id'] =  "91360238"
                    data['notify_from_id'] =  "34460244"
                    data['notify_to_name'] =  "Mr. Sunil Kumar Patodi"
                    data['notify_from_name'] =  "Deepak Marskole"
                    data['notify_datetime'] =  "01-01-2024"
                    data['app_request_type'] =  "TADA" 
                    data['notify_description'] =  "NA"
                    data['notify_comments'] =  "NA"
                    data['notify_notes'] =  "NA"

                if app_request_type=="CCB":
                    data['mpwz_id'] = mpwz_id_sequenceno
                    data['app_source'] = "ngb"
                    data['app_source_appid'] =  seq_gen.generate_secretcode()
                    data['notify_status'] =  "PENDING"
                    data['notify_refsys_id'] =  seq_gen.generate_secretcode()
                    data['notify_to_id'] =  "91360238"
                    data['notify_from_id'] =  "34460244"
                    data['notify_to_name'] =  "Mr. Sunil Kumar Patodi"
                    data['notify_from_name'] =  "Deepak Marskole"
                    data['notify_datetime'] =  "01-01-2024"
                    data['app_request_type'] =  "TADA" 
                    data['notify_description'] =  "NA"
                    data['notify_comments'] =  "NA"
                    data['notify_notes'] =  "NA"
                else:
                     return jsonify({"msg": f"invalid app request type not register here:- {app_request_type}"}), 200 
            try:
                result = mongo.db.mpwz_notifylist.insert_one(data)
                if result:
                    response_data = {   "msg": f"Data inserted successfully from source {application_type} id:--{str(result.inserted_id)}",
                                        "current_api": request.full_path,
                                        "client_ip": request.remote_addr,
                                        "response_at": datetime.datetime.now().isoformat()
                            } 
                    log_entry_event.log_api_call(response_data) 
                    return jsonify({"msg": "Data inserted successfully", "id": str(result.inserted_id)}), 200
                else:
                    seq_gen.reset_sequence('mpwz_notifylist_erp')
                    return jsonify({"msg": "Failed to insert data from remote server logs"}), 400 
                
            except Exception as errors:
                seq_gen.reset_sequence('mpwz_notifylist_erp')
                return jsonify({"msg": f"Failed to insert data: {str(errors)}"}), 500

@app.route('/shared-call/api/v1/erp/post-notifyerp', methods=['POST'])
@jwt_required()
def create_notification_from_erp():
    username = get_jwt_identity()
    data = request.get_json()  
    application_type = request.args.get('app_source')    
    # app_request_type = request.args.get('app_request_type')     
    # print(f"requesting data for {app_request_type} and request comming from {application_type}")     

    app_exists = mongo.db.mpwz_integrated_app.find_one({"app_name": application_type})
    if application_type != 'erp':
         return jsonify({"msg": "incomming request occurred from invalid app_source."}), 400 
    elif not app_exists:
        return jsonify({"msg": "requesting application is not integrated with our server."}), 400 
    else: 
        # required_fields_map = {
        #     "LEAVE": ["id", "locationCode", "approver", "billId", "billCorrectionProfileInitiatorId", "status", "remark", "updatedBy", "updatedOn"],
        #     "PROJECT": ["id", "locationCode", "approver", "billId", "billCorrectionProfileInitiatorId", "status", "remark", "updatedBy", "updatedOn"],
        #     "TADA": ["id", "locationCode", "approver", "billId", "billCorrectionProfileInitiatorId", "status", "remark", "updatedBy", "updatedOn"],
        #     "BILL": ["id", "locationCode", "approver", "billId", "billCorrectionProfileInitiatorId", "status", "remark", "updatedBy", "updatedOn"]
        # }

        # if app_request_type in required_fields_map:
        #     required_fields = required_fields_map[app_request_type]
        #     for field in required_fields:
        #         if field not in data:
        #             return jsonify({"msg": f"{field} is required for {app_request_type}."}), 400
        # else:
        #     return jsonify({"msg": f"Invalid data type: {app_request_type}."}), 400          
        # existing_record = mongo.db.mpwz_notifylist.find_one({"notify_refsys_id": data["notify_refsys_id"]})
        # if existing_record:      
        #     return jsonify({"msg": "Records with notify_refsys_id already existed in database."}), 400
        # else:  

            # Generate sequence number for mpwz_id
            mpwz_id_sequenceno = seq_gen.get_next_sequence('mpwz_notifylist')
            if mpwz_id_sequenceno:
                    data['mpwz_id'] = mpwz_id_sequenceno
                    data['app_source'] = "erp"
                    data['app_source_appid'] =  seq_gen.generate_secretcode()
                    data['notify_status'] =  "PENDING"
                    data['notify_refsys_id'] =  seq_gen.generate_secretcode()
                    data['notify_to_id'] =  "91360238"
                    data['notify_from_id'] =  "34460244"
                    data['notify_to_name'] =  "Mr. Sunil Kumar Patodi"
                    data['notify_from_name'] =  "Deepak Marskole"
                    data['notify_datetime'] =  "01-01-2024"
                    data['app_request_type'] =  "TADA" 
                    data['notify_description'] =  "NA"
                    data['notify_comments'] =  "NA"
                    data['notify_notes'] =  "NA"
            try:
                result = mongo.db.mpwz_notifylist.insert_one(data)
                if result:
                            response_data = {   "msg": f"Data inserted successfully from source {application_type} id:--{str(result.inserted_id)}",
                                                "current_api": request.full_path,
                                                "client_ip": request.remote_addr,
                                                "response_at": datetime.datetime.now().isoformat()
                                    } 
                            log_entry_event.log_api_call(response_data) 
                            return jsonify({"msg": "Data inserted successfully", "id": str(result.inserted_id)}), 200
                else:
                    seq_gen.reset_sequence('mpwz_notifylist')
                    return jsonify({"msg": "Failed to insert data from remote server logs"}), 400 
                
            except Exception as errors:
                seq_gen.reset_sequence('mpwz_notifylist')
                return jsonify({"msg": f"Failed to insert data: {str(errors)}"}), 500

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
