from flask import jsonify
import requests

class shared_apiServices:
        
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
            # Uncomment the following lines to make the actual request
            # response = requests.post("https://ngb.mpwin.co.in:8700/update-notification-ngb", json=data)
            # response.raise_for_status() 
            # return response.json()  
            data = {"message": "Notification sent to NGB successfully for CC4 status update"} 
            return jsonify(data), 200
        except requests.exceptions.RequestException as error_response:
            print(f"ERP Response: {error_response}")
            return jsonify({"msg": f"Failed to connect to NGB Server due to error: {error_response}"}), 401
        
    @staticmethod    
    def notify_ngb_toupdate_ccbstatus(data):
        try:
            # Uncomment the following lines to make the actual request
            # response = requests.post("https://ngb.mpwin.co.in:8700/update-notification-ngb", json=data)
            # response.raise_for_status() 
            # return response.json() 
            data = {"message": "Notification sent to NGB successfully for CCB status update"} 
            return jsonify(data), 200 
        except requests.exceptions.RequestException as error_response:
            print(f"ERP Response: {error_response}")
            return jsonify({"msg": f"Failed to connect to NGB Server due to error: {error_response}"}), 401
        
    @staticmethod
    def notify_ngb_togetdate_cc4status(data):
        try:
            # Uncomment the following lines to make the actual request
            # response = requests.get("https://ngb.mpwin.co.in:8700/get-notification-ngb", json=data)
            # response.raise_for_status() 
            # return response.json()
            data = {"message": "Notification get data sent to NGB successfully for CC4 status update"} 
            return jsonify(data), 200 
        except requests.exceptions.RequestException as error_response:
            print(f"ERP Response: {error_response}")
            return jsonify({"msg": f"Failed to connect to NGB Server due to error: {error_response}"}), 401    
        
    @staticmethod
    def notify_ngb_togetdate_ccbstatus(data):
        try:
            # Uncomment the following lines to make the actual request
            # response = requests.get("https://ngb.mpwin.co.in:8700/get-notification-ngb", json=data)
            # response.raise_for_status() 
            # return response.json()  
            data = {"message": "Notification get data sent to NGB successfully for CCB status update"} 
            return jsonify(data), 200 
        except requests.exceptions.RequestException as error_response:
            print(f"ERP Response: {error_response}")
            return jsonify({"msg": f"Failed to connect to NGB Server due to error: {error_response}"}), 401    