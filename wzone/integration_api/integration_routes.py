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
    request.start_time = time.perf_counter()

@integration_api.after_request
def after_request(response):
    log_entry_event_api = myserv_update_users_api_logs()
    try:
        request_time = request.start_time
        response_time_minutes = (time.time() - request_time) / 60
        api_name = request.path
        server_load = log_entry_event_api.calculate_server_load()
        success = response.status_code < 400
        
        log_entry_event_api.log_api_call_status(
            api_name, 
            request_time, 
            response_time_minutes, 
            server_load, 
            success
        )
        print(f"Request executed {api_name} it took {response_time_minutes:.4f} minutes.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        log_entry_event_api.mongo_dbconnect_close()
        
    return response

## Extenal API for Get Data from Remote Servers ##
@integration_api.route('/shared-call/api/v1/ngb/post-notifyngb', methods=['POST'])
@jwt_required()
def create_notification_from_ngb():
    notifylist_collection = MongoCollection("mpwz_notifylist")
    mpwz_integrated_app_collection = MongoCollection("mpwz_integrated_app")
    username = get_jwt_identity()
    data = request.get_json()
    application_type = request.args.get('app_source')
    app_request_type = data.get('app_request_type')

    if application_type != 'ngb' or not mpwz_integrated_app_collection.find_one({"app_name": application_type}):
        return jsonify({"msg": f"Invalid or unregistered application source: {application_type}"}), 400

    seq_gen = myserv_generate_mpwz_id_forrecords()
    mpwz_id_sequenceno = seq_gen.get_next_sequence('mpwz_notifylist')
    if not mpwz_id_sequenceno:
        return jsonify({"msg": "Failed to generate sequence number"}), 500

    common_data = {
        'app_source': "ngb",
        'app_source_appid': mpwz_id_sequenceno,
        'mpwz_id': mpwz_id_sequenceno,
        'notify_comments': "NA",
        'notify_datetime': "01-01-2024",
        'notify_description': "NA",
        'notify_from_id': "34460244",
        'notify_from_name': "Deepak Marskole",
        'notify_intiatedby': "34460244",
        'notify_notes': "NA",
        'notify_refsys_id': mpwz_id_sequenceno,
        "notify_refsys_response": "NA",
        "notify_refsys_updatedon": "NA",
        'notify_status': "PENDING",
        'notify_to_id': "91360238",
        'notify_to_name': "Mr. Sunil Kumar Patodi",
    }

    if app_request_type in ["CC4", "CCB"]:
        data.update(common_data)
        data['app_request_type'] = app_request_type
    # else:
    #     return jsonify({"msg": f"Invalid app request type: {app_request_type}"}), 400

    try:
        result = notifylist_collection.insert_one(data)
        if result and result.inserted_id is not None:
            response_data = {
                "msg": f"Data inserted successfully from source {application_type}",
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": str(datetime.datetime.now())
            }
            myserv_update_users_logs().log_api_call(response_data)
            print("Data insertion request completed successfully.")
            return jsonify({"msg": "Data inserted successfully", "id": str(result.inserted_id)}), 200
        else:
            seq_gen.reset_sequence('mpwz_notifylist_erp')
            return jsonify({"msg": "Failed to insert data from remote server logs"}), 400
    except Exception as errors:
        seq_gen.reset_sequence('mpwz_notifylist_erp')
        print(f"An error occurred during data insertion: {str(errors)}")
        return jsonify({"msg": f"Failed to insert data: {str(errors)}"}), 500
    finally:
        seq_gen.mongo_dbconnect_close()
        notifylist_collection.mongo_dbconnect_close()
        mpwz_integrated_app_collection.mongo_dbconnect_close()

@integration_api.route('/shared-call/api/v1/erp/post-notifyerp', methods=['POST'])
@jwt_required()
def create_notification_from_erp():
    notifylist_collection = MongoCollection("mpwz_notifylist")
    mpwz_integrated_app_collection = MongoCollection("mpwz_integrated_app")
    username = get_jwt_identity()
    data = request.get_json()  
    application_type = request.args.get('app_source')    
    app_request_type = data.get('app_request_type')

    if application_type != 'erp' or not mpwz_integrated_app_collection.find_one({"app_name": application_type}):
        return jsonify({"msg": "incomming request occurred from invalid app_source."}), 400

    seq_gen = myserv_generate_mpwz_id_forrecords()
    mpwz_id_sequenceno = seq_gen.get_next_sequence('mpwz_notifylist')
    if not mpwz_id_sequenceno:
        
        return jsonify({"msg": "Failed to generate sequence number"}), 500

    common_data = {
        'app_source': "erp",
        'app_source_appid': mpwz_id_sequenceno,
        'mpwz_id': mpwz_id_sequenceno,
        'notify_comments': "NA",
        'notify_datetime': "01-01-2024",
        'notify_description': "NA",
        'notify_from_id': "34460244",
        'notify_from_name': "Deepak Marskole",
        'notify_intiatedby': "34460244",
        'notify_notes': "NA",
        'notify_refsys_id': mpwz_id_sequenceno,
        "notify_refsys_response": "NA",
        "notify_refsys_updatedon": "NA",
        'notify_status': "PENDING",
        'notify_to_id': "91360238",
        'notify_to_name': "Mr. Sunil Kumar Patodi",
    }

    if app_request_type in ["LEAVE", "PROJECT"]:
        data.update(common_data)
        data['app_request_type'] = app_request_type
    # else:
    #     return jsonify({"msg": f"Invalid app request type: {app_request_type}"}), 400

    try:
        result = notifylist_collection.insert_one(data)
        if result and result.inserted_id:
            response_data = {
                "msg": f"Data inserted successfully from source {application_type} id:--{str(result.inserted_id)}",
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": str(datetime.datetime.now())
            }
            myserv_update_users_logs().log_api_call(response_data)
            print("Request completed successfully.")
            return jsonify({"msg": "Data inserted successfully", "id": str(result.inserted_id)}), 200
        else:
            seq_gen.reset_sequence('mpwz_notifylist')
            return jsonify({"msg": "Failed to insert data from remote server logs"}), 400
    except Exception as errors:
        seq_gen.reset_sequence('mpwz_notifylist')
        print(f"An error occurred during data insertion: {str(errors)}")
        return jsonify({"msg": f"Failed to insert data: {str(errors)}"}), 500
    finally:
        notifylist_collection.mongo_dbconnect_close()
        mpwz_integrated_app_collection.mongo_dbconnect_close()
        seq_gen.mongo_dbconnect_close()

