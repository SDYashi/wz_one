from flask import request, jsonify
import datetime
from myservices.myserv_update_users_logs import myserv_update_users_logs
from myservices.myserv_connection_forblueprints import MongoCollection
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords

class myserv_update_actionhistory:
    def __init__(self):
        self.mpwz_user_action_history = MongoCollection("mpwz_user_action_history")
        self.log_entry_event = myserv_update_users_logs()
        self.seq_gen = myserv_generate_mpwz_id_forrecords()

    def post_actionhistory_request(self, username,data):
            try:
                existing_record = self.mpwz_user_action_history.find_one({"notify_refsys_id": data["notify_refsys_id"]})
                if existing_record:
                    return jsonify({"msg": "Records with notify_refsys_id already existed in database."}), 400
                mpwz_id_actionhistory = self.seq_gen.get_next_sequence('mpwz_user_action_history')
                data['sequence_no'] = str(data['mpwz_id'])
                data['mpwz_id'] = str(mpwz_id_actionhistory)
                data['action_by'] = username
                data['action_at'] = datetime.datetime.now().isoformat()

                response = self.mpwz_user_action_history.insert_one(data)
                if response:
                    response_data = {
                        "msg": f"Action History Updated successfully for {username}",
                        "current_api": request.full_path,
                        "client_ip": request.remote_addr,
                        "response_at": datetime.datetime.now().isoformat()
                    }
                    self.log_entry_event.log_api_call(response_data)
                    return jsonify({"msg": f"Action history updated successfully, mpwz_id: {mpwz_id_actionhistory}"}), 200
                return jsonify({"msg": "Invalid request encountered at server."}), 400
            except Exception as e:
                return jsonify({"msg": f"An error occurred while updating action history: {str(e)}"}), 500
            finally:            
                self.seq_gen.mongo_dbconnect_close()
                self.log_entry_event.mongo_dbconnect_close()
                self.mpwz_user_action_history.mongo_dbconnect_close()
       
            
