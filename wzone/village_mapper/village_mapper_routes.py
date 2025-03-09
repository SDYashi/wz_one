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
from . import village_mapper

@village_mapper.route('/shared-call/api/v1/ngb/post-notifyngb', methods=['POST'])
@jwt_required()
def create_notification_from_ngb():
    notifylist_collection = MongoCollection("mpwz_notifylist")
    mpwz_integrated_app_collection = MongoCollection("mpwz_integrated_app")
    username = get_jwt_identity()
    data = request.get_json()
    application_type = request.args.get('app_source')
    app_request_type = data.get('app_request_type')

    if not mpwz_integrated_app_collection.find_one({"app_name": application_type}):
        return jsonify({"msg": f"Invalid or unregistered application source: {application_type}", "current_api": request.full_path, "client_ip": request.remote_addr}), 400

    seq_gen = myserv_generate_mpwz_id_forrecords()
    mpwz_id_sequenceno = seq_gen.get_next_sequence('mpwz_notifylist')
    if not mpwz_id_sequenceno:
        return jsonify({"msg": "Failed to generate mpwz_id", "current_api": request.full_path, "client_ip": request.remote_addr}), 500

    try:
        common_data = {
            'app_source': application_type,
            "app_request_type": app_request_type,
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
        data.update(common_data)
        data['app_request_type'] = app_request_type
        result = notifylist_collection.insert_one(data)
        if result and result.inserted_id is not None:
            response_data = {
                "msg": f"Data inserted successfully from source {application_type}",
                "current_api": request.full_path,
                "client_ip": request.remote_addr,
                "response_at": str(datetime.datetime.now())
            }
            myserv_update_users_logs().log_api_call(response_data)
            return jsonify({"msg": "Data Recieved successfully", "id": str(result.inserted_id)}), 200
        else:
            seq_gen.reset_sequence('mpwz_notifylist')
            return jsonify({"msg": "Failed to insert data from remote server logs", "current_api": request.full_path, "client_ip": request.remote_addr}), 400
    except Exception as errors:
        seq_gen.reset_sequence('mpwz_notifylist')
        return jsonify({"msg": f"Failed to insert data: {str(errors)}", "current_api": request.full_path, "client_ip": request.remote_addr,"data": data}), 500
    finally:
        seq_gen.mongo_dbconnect_close()
        notifylist_collection.mongo_dbconnect_close()
        mpwz_integrated_app_collection.mongo_dbconnect_close()
