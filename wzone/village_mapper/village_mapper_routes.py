
import csv
import datetime
import io
import time
import traceback
import bcrypt
from flask import jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
import psycopg2
import pytz
import requests
from village_mapper.village_services import myserv_createuser_userinfofrombiserver
from myservices_oneapp.myserv_varriable_list import myserv_varriable_list
from . import village_mapper
from village_mapper import services_dboperation
local_dboperation = services_dboperation.services_dboperation('localhost')
remote_dboperation = services_dboperation.services_dboperation('remotehost')

@village_mapper.route('/v1/api/getparliamentconstituencies', methods=['GET'], endpoint='getparliamentconstituency_records')
@jwt_required()
def get_parliament_constituencies():
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()    
    query =""" 
        SELECT distinct plasbly.parliament_constituency_eci_code,plasbly.parliament_constituency_name
        FROM public.vill_parliament_assembly_constituencies as plasbly
        order by parliament_constituency_name ASC 
     """
    cursor.execute(query)
    constituencies = cursor.fetchall()    
    cursor.close()
    conn.close()
    result = []
    for constituency in constituencies:
        result.append({  'parliament_constituency_eci_code': constituency[0],
                        'parliament_constituency_name': constituency[1]
        })    
    return jsonify(result), 200

@village_mapper.route('/v1/api/getassemblyconstituencies', methods=['GET'], endpoint='get_getassembliesconstituency_records')
@jwt_required()
def get_assembly_constituencies():
    parliament_name = request.args.get('parliament_name')
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()    
    query = """ 
        SELECT distinct plasbly.assembly_constituency_eci_code,plasbly.assembly_constituency_name
        FROM public.vill_parliament_assembly_constituencies as plasbly
        WHERE parliament_constituency_name = %s order by plasbly.assembly_constituency_name ASC 
       """
    cursor.execute(query, (parliament_name,))
    constituencies = cursor.fetchall()    
    cursor.close()
    conn.close()
    result = []
    for constituency in constituencies:
        result.append({ 'assembly_constituency_eci_code': constituency[0],
                        'assembly_constituency_name': constituency[1] })    
    return jsonify(result), 200

@village_mapper.route('/v1/api/getdistricts', methods=['GET'], endpoint='getdistrict_records')
@jwt_required()
def get_districts():
    parliament_name = request.args.get('parliament_name')
    assembly_name = request.args.get('assembly_name')
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()    
    query = """
    SELECT dist.district_name,dist.district_code FROM public.vill_parliament_assembly_constituencies asmbly
    full join public.vill_districts dist on asmbly.district_id=dist.id
    WHERE asmbly.parliament_constituency_name = %s AND asmbly.assembly_constituency_name = %s
    order by dist.district_name ASC 
    """
    cursor.execute(query, (parliament_name, assembly_name))
    districts = cursor.fetchall()
    cursor.close()
    conn.close()    
    # Convert the fetched data into a list of dictionaries
    result = []
    for district in districts:
        result.append({
            'district_code': district[1],
            'district_name': district[0]
        })
    
    return jsonify(result), 200

@village_mapper.route('/v1/api/getsubdistricts', methods=['GET'], endpoint='get_subdistrict_records')
@jwt_required()
def get_subdistricts():
    conn = remote_dboperation.get_connection()
    parliament_name = request.args.get('parliament_name')
    assembly_name = request.args.get('assembly_name')
    district_name = request.args.get('district_name')
    cursor = conn.cursor()
    query = """
        SELECT distinct subdist.subdistrict_code, subdist.subdistrict_name FROM public.vill_parliament_assembly_constituencies asmbly
        full join public.vill_districts dist on asmbly.district_id=dist.id
        full join public.vill_subdistricts subdist on subdist.district_id=dist.id
        where asmbly.parliament_constituency_name = %s AND asmbly.assembly_constituency_name = %s AND dist.district_name = %s
        order by subdist.subdistrict_name ASC 
     """
    cursor.execute(query, (parliament_name, assembly_name, district_name))
    subdistricts = cursor.fetchall()
    cursor.close()
    conn.close()
    result = []
    for subdistrict in subdistricts:
        result.append({
            'subdistrict_code': subdistrict[0],
            'subdistrict_name': subdistrict[1],
        })
    return jsonify(result), 200

@village_mapper.route('/v1/api/getlocalbodytype', methods=['GET'], endpoint='getlocalbodytype')
@jwt_required()
def get_localbody_type():
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()
    query = """
        SELECT distinct local_body_type FROM public.vill_localbodies
     """
    cursor.execute(query)
    localbody_types = cursor.fetchall()
    cursor.close()
    conn.close()
    result = []
    for localbody_type in localbody_types:
        result.append({'localbody_type': localbody_type[0]})
    return jsonify(result), 200

@village_mapper.route('/v1/api/getrurallocalbodies', methods=['GET'], endpoint='get_rurallocalbodies')
@jwt_required()
def get_rurallocalbodies():
    parliament_name = request.args.get('parliament_name')
    assembly_name = request.args.get('assembly_name')
    district_name = request.args.get('district_name')
    subdistrict_name = request.args.get('subdistrict_name')
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()
    query = """
    SELECT  distinct locbdy.localbody_name,locbdy.local_body_type 
    FROM public.vill_localbodies as locbdy
    full join public.vill_subdistricts subdist on subdist.id=locbdy.subdistrict_id
    full join public.vill_districts dist on dist.id=subdist.district_id
    full join public.vill_parliament_assembly_constituencies const on const.district_id=locbdy.district_id
    WHERE const.parliament_constituency_name = %s 
    AND const.assembly_constituency_name = %s 
    AND dist.district_name = %s
    AND subdist.subdistrict_name = %s
    """
    cursor.execute(query, (parliament_name, assembly_name, district_name, subdistrict_name))
    localbodies = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for localbody in localbodies:
        result.append({
            'localbody_name': localbody[0],
            'local_body_type': localbody[1],
        })
    
    return jsonify(result), 200

@village_mapper.route('/v1/api/geturbanlocalbodies', methods=['GET'], endpoint='get_urbanlocalbodies')
@jwt_required()
def get_urbanlocalbodies():
    parliament_name = request.args.get('parliament_name')
    assembly_name = request.args.get('assembly_name')
    district_name = request.args.get('district_name')
    locabodytype_name = request.args.get('locabodytype_name')
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()
    query = """
    SELECT  distinct locbdy.localbody_name,locbdy.local_body_type 
    FROM public.vill_localbodies as locbdy
    full join public.vill_districts dist on dist.id=locbdy.district_id
    full join public.vill_parliament_assembly_constituencies const on const.district_id=locbdy.district_id
    WHERE const.parliament_constituency_name = %s 
    AND const.assembly_constituency_name = %s 
    AND dist.district_name = %s
    AND locbdy.local_body_type = %s
    """
    cursor.execute(query, (parliament_name, assembly_name, district_name, locabodytype_name))
    localbodies = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for localbody in localbodies:
        result.append({
            'localbody_name': localbody[0],
            'local_body_type': localbody[1],
        })
    
    return jsonify(result), 200

@village_mapper.route('/v1/api/getvillages', methods=['GET'], endpoint='get_village')
@jwt_required()
def get_villages_records():
    parliament_name = request.args.get('parliament_name')
    assembly_name = request.args.get('assembly_name')
    district_name = request.args.get('district_name')
    subdistrict_name = request.args.get('subdistrict_name')
    localbody_name = request.args.get('localbody_name')
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()

    if subdistrict_name == 'NA':        
        query = """ 
        SELECT distinct vi.village_name, vi.village_code 
        FROM public.vill_villages as vi
        full join public.vill_localbodies as locbdy on locbdy.id=vi.localbody_id
        full join public.vill_districts dist on dist.id=locbdy.district_id
        full join public.vill_parliament_assembly_constituencies const on const.district_id=locbdy.district_id
        WHERE const.parliament_constituency_name = %s AND const.assembly_constituency_name = %s AND dist.district_name = %s 
              AND locbdy.localbody_name = %s 
        """
        cursor.execute(query, (parliament_name, assembly_name, district_name, localbody_name))
    else:        
        query = """ 
        SELECT distinct vi.village_name, vi.village_code 
        FROM public.vill_villages as vi
        full join public.vill_localbodies as locbdy on locbdy.id=vi.localbody_id
        full join public.vill_subdistricts subdist on subdist.id=locbdy.subdistrict_id
        full join public.vill_districts dist on dist.id=subdist.district_id
        full join public.vill_parliament_assembly_constituencies const on const.district_id=locbdy.district_id
        WHERE const.parliament_constituency_name = %s AND const.assembly_constituency_name = %s AND dist.district_name = %s 
              AND subdist.subdistrict_name = %s AND locbdy.localbody_name = %s
        """
        cursor.execute(query, (parliament_name, assembly_name, district_name, subdistrict_name, localbody_name))

    villages = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for village in villages:
        result.append({
            'village_name': village[0],
            'village_code': village[1]
        })
    
    return jsonify(result), 200

@village_mapper.route('/v1/api/getgroups', methods=['GET'], endpoint='get_groups')
@jwt_required()
def get_groups_by_loc_code():
    loc_code = request.args.get('loc_code')
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()
    query = "SELECT distinct group_no FROM vill_cons_groups_info WHERE loc_code = %s"
    cursor.execute(query, (loc_code,))
    groups = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{'group_no': group[0]} for group in groups])

@village_mapper.route('/v1/api/getdistrictslist', methods=['GET'], endpoint='getgroupslist')
@jwt_required()
def get_groups_by_loc_code():
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()
    query = "SELECT distinct district_name FROM public.vill_districts"
    cursor.execute(query)
    district_names = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{'district_name': district_name[0]} for district_name in district_names])

@village_mapper.route('/v1/api/getdairies', methods=['GET'], endpoint='get_dairy_records')
@jwt_required()
def get_dairies_by_group_no():
    group_no = request.args.get('group_no')
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()
    query = "SELECT dairy_no FROM vill_cons_groups_info WHERE group_no = %s"
    cursor.execute(query, (group_no,))
    dairies = cursor.fetchall()
    cursor.close()
    conn.close()
    result = [{'dairy_no': dairy[0]} for dairy in dairies]
    return jsonify(result)

@village_mapper.route('/v1/api/getunmappedconsumers', methods=['GET'], endpoint='getunmappedconsumers')
@jwt_required()
def get_unmapped_consumers():
    try:
        conn = remote_dboperation.get_connection()
        loc_code = request.args.get('loc_code')
        group_no = request.args.get('group_no')
        dairy_no = request.args.get('dairy_no')
        cursor = conn.cursor()
        query = """
        SELECT  loc_code, group_no, dairy_no, consumer_no, consumer_name, address_1, tariff_category, premise_type, sanctioned_load, sanctioned_load_unit
        FROM public.vill_cons_mapping_status
        WHERE is_vill_mapped = false
        AND loc_code = %s
        AND group_no = %s
        AND dairy_no = %s
        """
        cursor.execute(query, (loc_code, group_no, dairy_no))
        unmapped_consumers = cursor.fetchall()
        cursor.close()
        conn.close()
        result = []
        for consumer in unmapped_consumers:
            result.append({
                'loc_code': consumer[0],
                'group_no': consumer[1],
                'dairy_no': consumer[2],
                'consumer_no': consumer[3],
                'consumer_name': consumer[4],
                'address_1': consumer[5],
                'tariff_category': consumer[6],
                'premise_type': consumer[7],
                'sanctioned_load': consumer[8],
                'sanctioned_load_unit': consumer[9]
            })
        return jsonify(result), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while fetching consumers data."}), 500

@village_mapper.route('/v1/api/getmappedconsumers', methods=['GET'], endpoint='getmappedconsumers')
@jwt_required()
def get_mapped_consumers():
    group_no = request.args.get('group_no')
    loc_code = request.args.get('loc_code')
    query_params = []
    query = """
    SELECT id, loc_code, group_no, dairy_no, consumer_no, consumer_name, 
           parliyament_name, assembly_name, district_name, subdistrict_name,
           localbody_name, village_name, village_code, is_vill_mapped,
           created_by, created_on, updated_by, updated_on
    FROM public.vill_cons_mapping 
    WHERE 1=1
    """
    if group_no:
        query += " AND group_no = %s"
        query_params.append(group_no)
    if loc_code:
        query += " AND loc_code = %s"
        query_params.append(loc_code)
    try:
        conn = remote_dboperation.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, query_params)
            consumers = cursor.fetchall()
        result = [
            {
                'id': consumer[0],
                'loc_code': consumer[1],
                'group_no': consumer[2],
                'dairy_no': consumer[3],
                'consumer_no': consumer[4],
                'consumer_name': consumer[5],
                'parliyament_name': consumer[6],
                'assembly_name': consumer[7],
                'district_name': consumer[8],
                'subdistrict_name': consumer[9],
                'localbody_name': consumer[10],
                'village_name': consumer[11],
                'village_code': consumer[12],
                'is_vill_mapped': consumer[13],
                'created_by': consumer[14],
                'created_on': consumer[15],
                'updated_by': consumer[16],
                'updated_on': consumer[17]
            }
            for consumer in consumers
        ]
        return jsonify(result)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while fetching data."}), 500
    finally:
        if conn:
            conn.close()

@village_mapper.route('/v1/api/getmappedconsumersforedit', methods=['GET'], endpoint='getmappedconsumersforedit')
@jwt_required()
def get_mapped_consumersforedit():
    # parliyament_name = request.args.get('parliament_name')
    # assembly_name = request.args.get('assembly_name')
    # district_name = request.args.get('district_name')
    # subdistrict_name = request.args.get('subdistrict_name')
    # localbody_name = request.args.get('localbody_name')
    # village_name = request.args.get('village_name')
    # group_no = request.args.get('group_no')
    # loc_code = request.args.get('loc_code')
    # query_params = [parliyament_name, assembly_name, district_name, subdistrict_name, localbody_name, village_name, group_no, loc_code]
    # print(query_params)
    # query = """
    #         SELECT * FROM public.vill_cons_mapping
    #         WHERE parliyament_name = %s
    #         AND assembly_name = %s
    #         AND district_name = %s
    #         AND subdistrict_name = %s
    #         AND localbody_name = %s
    #         AND village_name = %s
    #         AND group_no = %s
    #         AND loc_code = %s
    # """

    parliyament_name = request.args.get('parliament_name')
    assembly_name = request.args.get('assembly_name')
    district_name = request.args.get('district_name')
    subdistrict_name = request.args.get('subdistrict_name')
    localbody_name = request.args.get('localbody_name')
    village_name = request.args.get('village_name')
    group_no = request.args.get('group_no')
    loc_code = request.args.get('loc_code')

    query_params = [village_name, group_no, loc_code]
    print(query_params)
    query = """
            SELECT * FROM public.vill_cons_mapping
            where village_name = %s
            AND group_no = %s
            AND loc_code = %s
    """
    try:
        conn = remote_dboperation.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, query_params)
            consumers = cursor.fetchall()
        result = [
            {
                'id': consumer[0],
                'loc_code': consumer[1],
                'group_no': consumer[2],
                'dairy_no': consumer[3],
                'consumer_no': consumer[4],
                'consumer_name': consumer[5],
                'parliyament_name': consumer[6],
                'assembly_name': consumer[7],
                'district_name': consumer[8],
                'subdistrict_name': consumer[9],
                'localbody_name': consumer[10],
                'village_name': consumer[11],
                'village_code': consumer[12],
                'is_vill_mapped': consumer[13],
                'created_by': consumer[14],
                'created_on': consumer[15],
                'updated_by': consumer[16],
                'updated_on': consumer[17]
            }
            for consumer in consumers
        ]
        return jsonify(result)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while fetching data."}), 500
    finally:
        if conn:
            conn.close()

@village_mapper.route('/v1/api/addbulkmappedconsumer', methods=['POST'], endpoint='addbulkmappedconsumer')
@jwt_required()
def add_bulk_mapped_consumer():
    try: 
        current_user = get_jwt_identity()
        current_datetime = datetime.datetime.now()
        data = request.get_json()
        if not data or "consumer_nos" not in data:
            return jsonify({"error": "Invalid payload format. Expected 'consumer_nos' list."}), 400
        consumers = data["consumer_nos"]
        conn = remote_dboperation.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO public.vill_cons_mapping (
            loc_code, group_no, dairy_no, consumer_no, consumer_name,
            parliyament_name, assembly_name, district_name, subdistrict_name,
            localbody_name, village_name, village_code, is_vill_mapped, created_by, created_on, updated_by, updated_on
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """

        inserted_ids = []
        for consumer in consumers:
            values = (
                consumer.get("loc_code", None),
                consumer.get("group_no", None),
                consumer.get("dairy_no", None),
                consumer.get("consumer_no", None),
                consumer.get("consumer_name", None),
                consumer.get("parliyament_name", None),
                consumer.get("assembly_name", None),
                consumer.get("district_name", None),
                consumer.get("subdistrict_name", None),
                consumer.get("localbody_name", None),
                consumer.get("village_name", None),
                consumer.get("village_code", None),
                consumer.get("is_vill_mapped", True),  
                current_user  ,
                current_datetime,
                current_user  ,
                current_datetime
            )
            cursor.execute(query, values)
            inserted_ids.append(cursor.fetchone()[0])   
            print(f"Inserted consumer_no: {consumer.get('consumer_no', None)}")  
        try:
            query = """
            UPDATE public.vill_cons_mapping_status
            SET is_vill_mapped = TRUE,
            updated_on = %s
            WHERE consumer_no = %s
            """
            for consumer in consumers:
                cursor.execute(query, (current_datetime, consumer.get("consumer_no", None)))
        except Exception as e:
            print(f"An error occurred while updating data: {e}")
            conn.rollback()

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'inserted_ids': inserted_ids}), 201

    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "An error occurred while inserting data."}), 500
  
@village_mapper.route('/v1/api/updateexistingmappedconsumer', methods=['PUT'], endpoint='updateexistingmappedconsumer')
@jwt_required()
def update_existing_mapped_consumer():
    try:        
        current_user = get_jwt_identity()
        current_datetime = datetime.datetime.now()
        data = request.get_json()
        if not data or not isinstance(data, dict) or "consumers" not in data:
            return jsonify({"error": "Invalid payload format. Expected 'consumers' list."}), 400
        
        consumers = data["consumers"]
        if not isinstance(consumers, list) or len(consumers) == 0:
            return jsonify({"error": "Consumers list is empty or invalid."}), 400

        conn = remote_dboperation.get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE public.vill_cons_mapping SET
            parliyament_name = %s, assembly_name = %s, district_name = %s, subdistrict_name = %s,
            localbody_name = %s, village_name = %s, village_code = %s, updated_by = %s, updated_on = %s
        WHERE consumer_no = %s
        """
        updated_ids = []       
        new_id=[]
        for consumer in consumers:
            values = (
                consumer.get("parliyament_name"),  
                consumer.get("assembly_name"),
                consumer.get("district_name"),
                consumer.get("subdistrict_name"),
                consumer.get("localbody_name"),
                consumer.get("village_name"),
                consumer.get("village_code"),
                 current_user,
                current_datetime,
                consumer.get("consumer_no"),
            )
            cursor.execute(query, values)
            if cursor.rowcount > 0: 
                updated_ids.append( consumer.get("consumer_no"))            
            print(f"Updated consumer_no: { consumer.get("consumer_no")}")
        conn.commit()
        try: 
            query = """
            INSERT INTO public.vill_cons_mapping_history (
                loc_code, group_no, dairy_no, consumer_no, old_village_name,
                old_village_code, new_village_name, new_village_code, is_vill_mapped, created_by, created_on, updated_by, updated_on
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id    """
            for consumer in consumers:
                consumer_no = consumer.get("consumer_no")
                if not consumer_no:
                    print("Skipping entry with missing consumer_no")
                    continue  
                values2 = (
                    consumer.get("loc_code", None),  
                    consumer.get("group_no" , None),
                    consumer.get("dairy_no" , None),
                    consumer.get("consumer_no" , None),
                    consumer.get("old_village_name" , None),
                    consumer.get("old_village_code" , None),
                    consumer.get("village_name" , None),
                    consumer.get("village_code" , None),
                    consumer.get("is_vill_mapped" , None),
                    consumer.get("created_by" , None),
                    consumer.get("created_on" , None),
                    current_user,
                    current_datetime
                )
                print(f"inserted new record for consumer_no: {consumer_no} with values: {values}")
                cursor.execute(query, values2)    
                new_id.append(cursor.fetchone()[-1])
            print(f"New ID: {new_id}")  
            conn.commit()  
            cursor.close()
            conn.close()                   
        except Exception as e:
            print(f"An error occurred while updating data: {e}")
            conn.rollback()

        if not updated_ids:
            return jsonify({'message': 'No records were updated. Check consumer_no values.', 'updated_ids': updated_ids}), 200
        return jsonify({'updated_ids': updated_ids, 'new_id': new_id}), 200

    except Exception as e:
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "An error occurred. Please try again later."}), 500

@village_mapper.route('/v1/api/getlocationcode', methods=['GET'], endpoint='get_location_code')
@jwt_required()
def get_location_code():
    try:
        conn = remote_dboperation.get_connection()
        cursor = conn.cursor()
        query = "SELECT location_code FROM public.vill_locs"
        cursor.execute(query)
        loc_code = cursor.fetchone()[0]
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"An error occurred while getting location code: {e}")
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()
        return jsonify({"error": "An error occurred. Please try again later."}), 500
    
    # Wrap the location code in an object or array
    return jsonify({"location_code": loc_code}), 200

@village_mapper.route('/v1/api/getdashboordstatus', methods=['GET'], endpoint='getdashboordstatusnow')
@jwt_required()
def getdashboordstatus():
    try:
        conn = remote_dboperation.get_connection()
        cursor = conn.cursor()        
        queries = {
            "parliament_count": """
                SELECT COUNT(DISTINCT parliament_constituency_eci_code)
                FROM public.vill_parliament_assembly_constituencies
            """,
            "assembly_count": """
                SELECT COUNT(DISTINCT assembly_constituency_eci_code)
                FROM public.vill_parliament_assembly_constituencies
            """,
            "district_count": """
                SELECT COUNT(DISTINCT district_code)
                FROM public.vill_districts
            """,
            "subdistrict_count": """
                SELECT COUNT(DISTINCT subdistrict_code)
                FROM public.vill_subdistricts
            """,
            "localbody_count": """
                SELECT COUNT(DISTINCT localbody_code)
                FROM public.vill_localbodies
            """,
            "village_count": """
                SELECT COUNT(DISTINCT village_code)
                FROM public.vill_villages
            """,
            "total_consumers": """
                SELECT COUNT(consumer_no)
                FROM public.vill_cons_mapping_status
            """,
            "unmapped_villages": """
                SELECT COUNT(consumer_no)
                FROM public.vill_cons_mapping_status WHERE is_vill_mapped = false
            """,
            "mapped_villages": """
                SELECT COUNT(consumer_no)
                FROM public.vill_cons_mapping_status WHERE is_vill_mapped = true
            """
        }
        
        results = {}
        for key, query in queries.items():
            cursor.execute(query)
            results[key] = cursor.fetchone()[0]
        
        total_villages_count = results['unmapped_villages'] + results['mapped_villages']
        results['villagemapped_percentage'] = round((results['mapped_villages'] * 100) / total_villages_count, 2) if total_villages_count > 0 else 0
        
        cursor.close()
        conn.close()

        return jsonify(results), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"msg": str(e)}), 500

@village_mapper.route('/v1/api/getvillageslistuptoblock', methods=['GET'], endpoint='getvillageslistuptoblock')
@jwt_required()
def getvillageslistuptoblock():
    parliament_name = request.args.get('parliament_name')
    assembly_name = request.args.get('assembly_name')
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()
    print(parliament_name, assembly_name)
    query = """
        SELECT vi.village_name , vi.village_code, vi.area_type, vi.pincode, vi.is_ward,
        vblk.block_code, vblk.block_name,
        vbrcrd.bhu_tehsil_name,vbrcrd.bhu_village_name,
        vpolu.household_count, vpolu.population_total,
        locbdy.localbody_code,locbdy.localbody_name,locbdy.local_body_type,
        subdist.subdistrict_code, subdist.subdistrict_name,
        dist.district_code, dist.district_name,
        const.assembly_constituency_eci_code,const.assembly_constituency_name,
        const.parliament_constituency_eci_code,const.parliament_constituency_name
        FROM public.vill_villages vi
        full join public.vill_blocks vblk on vblk.id=vi.block_id
        full join public.vill_bhu_records vbrcrd on vbrcrd.id=vi.bhuabhilekh_id
        full join public.vill_population vpolu on vpolu.id=vi.population_id
        full join public.vill_localbodies  locbdy on locbdy.id=vi.localbody_id
        full join public.vill_subdistricts subdist on subdist.id=locbdy.subdistrict_id
        full join public.vill_districts dist on dist.id=subdist.district_id
        full join public.vill_parliament_assembly_constituencies const on const.district_id=locbdy.district_id
        where const.parliament_constituency_name = %s AND const.assembly_constituency_name = %s
    """
    cursor.execute(query, (parliament_name, assembly_name))
    villages = cursor.fetchall()
    cursor.close()
    conn.close()
    result = [{
        'village_name': village[0],
        'village_code': village[1],
        'area_type': village[2],
        'pincode': village[3],
        'is_ward': village[4],
        'block_code': village[5],
        'block_name': village[6],
        'bhu_tehsil_name': village[7],
        'bhu_village_name': village[8],
        'household_count': village[9],
        'population_total': village[10],
        'localbody_code': village[11],
        'localbody_name': village[12],
        'local_body_type': village[13],
        'subdistrict_code': village[14],
        'subdistrict_name': village[15],
        'district_code': village[16],
        'district_name': village[17],
        'assembly_constituency_eci_code': village[18],
        'assembly_constituency_name': village[19],
        'parliament_constituency_eci_code': village[20],
        'parliament_constituency_name': village[21]  
    } for village in villages]

    return jsonify(result), 200

@village_mapper.route('/v1/api/getconstituencies', methods=['GET'], endpoint='getconstituencies')
@jwt_required()
def getconstituenciesuptovillages():
    district_name = request.args.get('district_name')
    if not district_name:
        return jsonify({"error": "Missing 'district_name' parameter"}), 400

    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()
    query = """
    SELECT 
    locbdy.localbody_code,locbdy.localbody_name,locbdy.local_body_type,
    subdist.subdistrict_code, subdist.subdistrict_name,
    dist.district_code, dist.district_name,
    const.assembly_constituency_eci_code,const.assembly_constituency_name,
    const.parliament_constituency_eci_code,const.parliament_constituency_name
    FROM public.vill_localbodies  locbdy 
    full join public.vill_subdistricts subdist on subdist.id=locbdy.subdistrict_id
    full join public.vill_districts dist on dist.id=subdist.district_id
    full join public.vill_parliament_assembly_constituencies const on const.district_id=locbdy.district_id
    where dist.district_name = %s
    """
    cursor.execute(query, (district_name,))
    constituencies = cursor.fetchall()
    result = [{
        'localbody_code': consti[0],
        'localbody_name': consti[1],
        'local_body_type': consti[2],
        'subdistrict_code': consti[3],
        'subdistrict_name': consti[4],
        'district_code': consti[5],
        'district_name': consti[6],
        'assembly_constituency_eci_code': consti[7],
        'assembly_constituency_name': consti[8],
        'parliament_constituency_eci_code': consti[9],
        'parliament_constituency_name': consti[10]
    } for consti in constituencies]
    cursor.close()
    conn.close()   
    return jsonify(result), 200

@village_mapper.route('/v1/api/getexistingvillagemapping', methods=['GET'], endpoint='getexistingvillagemapping')
@jwt_required()
def getexistingvillagemapping():
    loc_code = request.args.get('location_code')

    if not loc_code:
        return jsonify({"error": "Missing 'location_code' parameter"}), 400

    query = """
    SELECT id, loc_code, group_no, dairy_no, consumer_no, consumer_name, 
           parliyament_name, assembly_name, district_name, subdistrict_name,
           localbody_name, village_name, village_code, is_vill_mapped,
           created_by, created_on, updated_by, updated_on
    FROM public.vill_cons_mapping 
    WHERE loc_code = %s
    """

    try:
        conn = remote_dboperation.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, (loc_code,)) 
            consumers = cursor.fetchall()

            # Get column names dynamically
            column_names = [desc[0] for desc in cursor.description]

        result = [dict(zip(column_names, consumer)) for consumer in consumers]
        
        return jsonify(result), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": f"An error occurred while fetching data -> {e}"}), 500

    finally:
        if conn:
            conn.close()

@village_mapper.route('/v1/api/getchangehistoryvillagemapping', methods=['GET'], endpoint='getchangehistoryvillagemapping')
@jwt_required()
def getchangehistoryvillagemapping():
    location_code = request.args.get('location_code')    
    if not location_code:
        return jsonify({"error": "Missing 'loc_code' parameter"}), 400
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()
    query = """
    SELECT loc_code, group_no, dairy_no, consumer_no, old_village_name, 
           old_village_code, new_village_name, new_village_code, 
           is_vill_mapped, created_by, created_on, updated_by, updated_on
    FROM public.vill_cons_mapping_history
    WHERE loc_code = %s
    """    
    cursor.execute(query, (location_code,))
    districts = cursor.fetchall()
    cursor.close()
    conn.close()
    result = [ {
        'loc_code': district[0],
        'group_no': district[1],
        'dairy_no': district[2],
        'consumer_no': district[3],
        'old_village_name': district[4],
        'old_village_code': district[5],
        'new_village_name': district[6],
        'new_village_code': district[7],
        'is_vill_mapped': district[8],
        'created_by': district[9],
        'created_on': district[10],
        'updated_by': district[11],
        'updated_on': district[12]
    } for district in districts]
    return jsonify(result), 200

@village_mapper.route('/v1/api/gettagedvillagesindc', methods=['GET'],endpoint='gettagedvillagesindc')
@jwt_required()
def get_allvillages():    
    location_code = request.args.get('location_code')   
    conn = remote_dboperation.get_connection()
    cursor = conn.cursor()
    query = """
    SELECT * FROM public.vill_dc_villages WHERE loc_code = %s
    """
    cursor.execute(query, (location_code,))
    villages = cursor.fetchall()
    cursor.close()
    conn.close()
    # Convert the result to a list of dictionaries
    village_list = []
    for village in villages:
        village_dict = {
            'id': village[0],
            'loc_code': village[1],
            'parliyament_name': village[2],
            'parliyament_code': village[3],
            'assembly_name': village[4],
            'assembly_code': village[5],
            'district_name': village[6],
            'district_code': village[7],
            'subdistrict_name': village[8],
            'subdistrict_code': village[9],
            'localbody_name': village[10],
            'localbody_code': village[11],
            'village_name': village[12],
            'village_code': village[13],
            'created_by': village[14],
            'created_on': village[15],
            'updated_by': village[16],
            'updated_on': village[17]
        }
        village_list.append(village_dict)

    return jsonify(village_list)

@village_mapper.route('/v1/api/addvillageswithdc', methods=['POST'], endpoint='addvillageswithdc')
@jwt_required()
def add_village_with_dc():
    try:
        current_user = get_jwt_identity()
        current_datetime = datetime.datetime.now()
        data = request.json
        conn = remote_dboperation.get_connection()
        cursor = conn.cursor()

        # Check if the combination of loc_code and village_code already exists
        check_query = """
            SELECT 1 FROM public.vill_dc_villages WHERE loc_code = %s AND village_code = %s
        """
        cursor.execute(check_query, (data['loc_code'], data['village_code']))
        exists = cursor.fetchone()

        if exists:
            cursor.close()
            conn.close()
            return jsonify({'message': f'Village already added here DC/Zone Code{data['loc_code']} with Village Code {data['village_code']}!'}), 409  # 409 Conflict status

        # Insert the village if it does not exist
        insert_query = """
            INSERT INTO public.vill_dc_villages (
                loc_code, parliyament_name, parliyament_code, 
                assembly_name, assembly_code, district_name, 
                district_code, subdistrict_name, subdistrict_code, 
                localbody_name, localbody_code, village_name, 
                village_code, created_by, created_on, updated_by, updated_on
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """  
        cursor.execute(insert_query, (
            data['loc_code'],
            data['parliyament_name'],
            data['parliyament_code'],
            data['assembly_name'],
            data['assembly_code'],
            data['district_name'],
            data['district_code'],
            data['subdistrict_name'],
            data['subdistrict_code'],
            data['localbody_name'],
            data['localbody_code'],
            data['village_name'],
            data['village_code'],
            current_user,
            current_datetime,
            current_user,
            current_datetime
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Village added successfully!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
