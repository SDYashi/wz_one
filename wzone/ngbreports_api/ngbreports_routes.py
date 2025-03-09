# android_api/android_routes.py
import base64
import datetime
import random
import time
import bcrypt
import ast  
from dateutil import parser 
from flask import jsonify, request
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from flask_pymongo import PyMongo
import psycopg2
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices.myserv_update_users_logs import myserv_update_users_logs
from myservices.myserv_update_users_api_logs import myserv_update_users_api_logs
from myservices.myserv_connection_forblueprints import MongoCollection
from shared_api import ngb_apiServices,erp_apiservices
from myservices.myserv_update_dbservices import myserv_update_dbservices
from myservices.myserv_update_actionhistory import myserv_update_actionhistory
from . import ngbreports_api
from myservices.myserv_varriable_list import myserv_varriable_list

@ngbreports_api.before_request
def before_request():
    request.start_time = time.time() 

@ngbreports_api.after_request
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
# Database connection parameters
def get_db_connection():
    # For PostgreSQL
    try:
        conn = psycopg2.connect(host=myserv_varriable_list.pg_config_HOST, database=myserv_varriable_list.pg_config_DBNAME, user=myserv_varriable_list.pg_config_USER, password=myserv_varriable_list.pg_config_PASSWORD)
        return conn
    except psycopg2.Error as e:
        print(f"Error while connecting to Postgres DB: {e}")



@ngbreports_api.route('/shared-call/api/v1/ngb/getpassbook/<consumer_no>', methods=['GET'])
def get_data(consumer_no):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(name='get_passbook_data', withhold=True)
        query = """
        SELECT source, location_code, group_no, reading_diary_no, consumer_no, old_service_no, bill_month, due_date,
               current_read_date, current_read, previous_read, difference, mf, metered_unit, assessment, total_unit,
               billed_unit, billed_md, billed_pf, fixed_charge, energy_charge, fca_charge, electricity_duty,
               meter_rent, ccb_adjustment, lock_credit, employee_rebate, subsidy, current_bill, arrear, net_bill,
               asd_billed, asd_arrear, asd_installment, connection_date, tariff_category, connection_type,
               metering_status, premise_type, sanctioned_load, sanctioned_load_unit, contract_demand,
               contract_demand_unit, is_seasonal, purpose_of_installation_id, purpose_of_installation, tariff_code
        FROM reports.view_passbook_bill
        WHERE consumer_no = %s
        """

        cursor.execute(query, (consumer_no,))
        if cursor.description is not None:
            columns = [desc[0] for desc in cursor.description]
            data = [{columns[i]: row[i] for i in range(len(columns))} for row in cursor.fetchall()]
        else:
            data = []
        print(data)
        return jsonify(data)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while fetching data."}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

