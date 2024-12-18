# integration_api/integration_api_routes.py

import datetime
import time
import bcrypt
from flask import jsonify, request
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices.myserv_update_users_logs import myserv_update_users_logs
from myservices.myserv_update_users_api_logs import myserv_update_users_api_logs
from myservices.myserv_connection_forblueprints import MongoCollection
from . import integration_api

@integration_api.before_request
def before_request():
    request.start_time = time.time() 

@integration_api.after_request
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

@integration_api.route('/sync', methods=['GET'])
def sync():
    return jsonify({"message": "Testing Integration Sync Records"})

## Extenal API for Get Data from Remote Servers ##
@integration_api.route('/shared-call/api/v1/ngb/post-notifyngb', methods=['POST'])
@jwt_required()
def create_notification_from_ngb():
    # Initialize MongoCollection Class
    notifylist_collection = MongoCollection("mpwz_notifylist")
    mpwz_integrated_app_collection = MongoCollection("mpwz_integrated_app")
    
    username = get_jwt_identity()
    data = request.get_json()   

    application_type = request.args.get('app_source')    
    app_request_type =  data['app_request_type']
    print(f"requesting data for {app_request_type} and request comming from {application_type}")   

    app_exists = mpwz_integrated_app_collection.find_one({"app_name": application_type})
    print(app_exists)
    if application_type != 'ngb':
         return jsonify({"msg": "incomming request occurred from invalid app_source."}), 400 
    elif not app_exists:
        return jsonify({"msg": f"requesting application is not integrated with our server.{application_type}"}), 400 
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
        
        # existing_record = notifylist_collection.find_one({"notify_refsys_id": data["notify_refsys_id"]})
        # if existing_record:      
        #     return jsonify({"msg": "Records with notify_refsys_id already existed in database."}), 400
        # else:  
            seq_gen = myserv_generate_mpwz_id_forrecords()
            mpwz_id_sequenceno = seq_gen.get_next_sequence('mpwz_notifylist')
            if mpwz_id_sequenceno:  
                if app_request_type=="CC4":
                    data['mpwz_id'] = mpwz_id_sequenceno
                    data['app_source'] = "ngb"
                    data['app_source_appid'] =  mpwz_id_sequenceno
                    data['notify_status'] =  "PENDING"
                    data['notify_refsys_id'] =  mpwz_id_sequenceno
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
                    data['app_source_appid'] =  mpwz_id_sequenceno
                    data['notify_status'] =  "PENDING"
                    data['notify_refsys_id'] = mpwz_id_sequenceno
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
                result = notifylist_collection.insert_one(data)
                if result:
                    response_data = {   "msg": f"Data inserted successfully from source {application_type} id:--{str(result.inserted_id)}",
                                        "current_api": request.full_path,
                                        "client_ip": request.remote_addr,
                                        "response_at": datetime.datetime.now().isoformat()
                            } 
                    log_entry_event = myserv_update_users_logs()
                    log_entry_event.log_api_call(response_data) 
                    return jsonify({"msg": "Data inserted successfully", "id": str(result.inserted_id)}), 200
                else:
                    seq_gen.reset_sequence('mpwz_notifylist_erp')
                    return jsonify({"msg": "Failed to insert data from remote server logs"}), 400 
                
            except Exception as errors:
                seq_gen.reset_sequence('mpwz_notifylist_erp')
                return jsonify({"msg": f"Failed to insert data: {str(errors)}"}), 500

@integration_api.route('/shared-call/api/v1/erp/post-notifyerp', methods=['POST'])
@jwt_required()
def create_notification_from_erp():
    # Initialize MongoCollection Class
    notifylist_collection = MongoCollection("mpwz_notifylist")
    mpwz_integrated_app_collection = MongoCollection("mpwz_integrated_app")
    username = get_jwt_identity()
    data = request.get_json()  
    application_type = request.args.get('app_source')    
    # app_request_type = request.args.get('app_request_type')     
    # print(f"requesting data for {app_request_type} and request comming from {application_type}")     

    app_exists =mpwz_integrated_app_collection.find_one({"app_name": application_type})
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
        # existing_record = notifylist_collection.find_one({"notify_refsys_id": data["notify_refsys_id"]})
        # if existing_record:      
        #     return jsonify({"msg": "Records with notify_refsys_id already existed in database."}), 400
        # else:  

            # Generate sequence number for mpwz_id
            seq_gen = myserv_generate_mpwz_id_forrecords()
            mpwz_id_sequenceno = seq_gen.get_next_sequence('mpwz_notifylist')
            if mpwz_id_sequenceno:
                    data['mpwz_id'] = mpwz_id_sequenceno
                    data['app_source'] = "erp"
                    data['app_source_appid'] =  mpwz_id_sequenceno
                    data['notify_status'] =  "PENDING"
                    data['notify_refsys_id'] = mpwz_id_sequenceno
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
                result = notifylist_collection.insert_one(data)
                if result:
                            response_data = {   "msg": f"Data inserted successfully from source {application_type} id:--{str(result.inserted_id)}",
                                                "current_api": request.full_path,
                                                "client_ip": request.remote_addr,
                                                "response_at": datetime.datetime.now().isoformat()
                                    } 
                            log_entry_event = myserv_update_users_logs()
                            log_entry_event.log_api_call(response_data) 
                            return jsonify({"msg": "Data inserted successfully", "id": str(result.inserted_id)}), 200
                else:
                    seq_gen.reset_sequence('mpwz_notifylist')
                    return jsonify({"msg": "Failed to insert data from remote server logs"}), 400 
                
            except Exception as errors:
                seq_gen.reset_sequence('mpwz_notifylist')
                return jsonify({"msg": f"Failed to insert data: {str(errors)}"}), 500

