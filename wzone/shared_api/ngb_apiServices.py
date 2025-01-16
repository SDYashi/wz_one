from flask import jsonify
import requests

class ngb_apiServices:
        
    def send_success(data):
        response = {
            "status_code": 200,
            "msg": "Successfully sent to NGB",  
            "data": data
        }
        return response

    @staticmethod
    def notify_ngb_toupdate_cc4status(data):
        try:
            response = requests.post("https://ngb.mpwin.co.in:8700/update-notification-ngb", json=data, timeout=5)
            response.raise_for_status() 
            return response.json()  
        except requests.exceptions.RequestException as error_response:
            print(f"ERROR: Failed to connect to NGB Server due to error: {error_response} at {error_response.request.url}")
            return jsonify({"msg": f"Failed to connect to NGB Server due to error: {error_response}"}), 401
        
    @staticmethod    
    def notify_ngb_toupdate_ccbstatus(data):
        try:
            response = requests.post("https://ngb.mpwin.co.in:8700/update-notification-ngb", json=data, timeout=5)
            response.raise_for_status() 
            return response.json() 
        except requests.exceptions.RequestException as error_response:
            print(f"ERROR: Failed to connect to NGB Server due to error: {error_response} at {error_response.request.url}")
            return jsonify({"msg": f"Failed to connect to NGB Server due to error: {error_response}"}), 401
        
    @staticmethod
    def notify_ngb_togetdate_cc4status(data):
        try:
            response = requests.get("https://ngb.mpwin.co.in:8700/get-notification-ngb", json=data, timeout=5)
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as error_response:
            print(f"ERROR: Failed to connect to NGB Server due to error: {error_response} at {error_response.request.url}")
            return jsonify({"msg": f"Failed to connect to NGB Server due to error: {error_response}"}), 401    
        
    @staticmethod
    def notify_ngb_togetdate_ccbstatus(data):
        try:
            response = requests.get("https://ngb.mpwin.co.in:8700/get-notification-ngb", json=data, timeout=5)
            response.raise_for_status() 
            return response.json()  
        except requests.exceptions.RequestException as error_response:
            print(f"ERROR: Failed to connect to NGB Server due to error: {error_response} at {error_response.request.url}")
            return jsonify({"msg": f"Failed to connect to NGB Server due to error: {error_response}"}), 401    
