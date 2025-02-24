from flask import jsonify
import requests 

class erp_apiservices:
        
    def send_success(data):
        response = {
            "status_code": 200,
            "msg": "Successfully sent to ERP",  
            "data": data
        }
        return response
    
    @staticmethod
    def notify_getgis():
        try:
            response = requests.get("http://mpezgis.in/DWZ/api/proposed_wk_dtls.php?dc_code=3474908", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error_response:
            return jsonify({"msg": f"Failed to connect EZ GIS Server Due to Error: {error_response} at {error_response.request.url}"}), 401


    @staticmethod
    def notify_erp_toupdate_status(data):
        try:
            response = requests.post("https://prodserv.mpwin.co.in:8700/update-notification-erp", json=data, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error_response:
            return jsonify({"msg": f"Failed to connect ERP Server Due to Error: {error_response} at {error_response.request.url}"}), 401

    @staticmethod
    def notify_erp_togetdate_status(data):
        try:
            response = requests.get("https://prodserv.mpwin.co.in:8700/get-notification-erp", json=data, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error_response:
            return jsonify({"msg": f"Failed to connect ERP Server Due to Error: {error_response} at {error_response.request.url}"}), 401

    @staticmethod
    def erp_dologin_token(data):
        try:
            response = requests.post("https://prodserv.mpwin.co.in:8700/login-erp", json=data, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error_response:
            return jsonify({"msg": f"Failed to connect ERP Server Due to Error: {error_response} at {error_response.request.url}"}), 401
