import requests
import hashlib
import json
from config import Config
from pymongo import MongoClient
import time

# Initialize MongoDB client
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client[Config.DB_NAME]
payments_collection = db["payments"]

def generate_payment_link(order_id, amount, user_id, plan_type):
    try:
        # Save payment record
        payments_collection.insert_one({
            "order_id": order_id,
            "user_id": user_id,
            "amount": amount,
            "plan_type": plan_type,
            "created_at": time.time(),
            "verified": False
        })
        
        # Generate PayTM payment link
        paytm_params = {
            "MID": Config.PAYTM_MERCHANT_ID,
            "WEBSITE": Config.PAYTM_WEBSITE,
            "INDUSTRY_TYPE_ID": "Retail",
            "CHANNEL_ID": "WEB",
            "ORDER_ID": order_id,
            "CUST_ID": str(user_id),
            "TXN_AMOUNT": str(amount),
            "CALLBACK_URL": Config.PAYTM_CALLBACK_URL,
            "EMAIL": "user@example.com",
            "MOBILE_NO": "9876543210"
        }
        
        # Generate checksum
        checksum = generate_checksum(paytm_params, Config.PAYTM_MERCHANT_KEY)
        paytm_params["CHECKSUMHASH"] = checksum
        
        # For production use: "https://securegw.paytm.in/order/process"
        paytm_url = "https://securegw-stage.paytm.in/order/process"
        
        return f"{paytm_url}?{'&'.join([f'{k}={v}' for k, v in paytm_params.items()])}"
    except Exception as e:
        print(f"Error generating payment link: {e}")
        return None

def generate_checksum(params, merchant_key):
    # Create a string of all parameters in the format "param1=value1&param2=value2"
    param_string = "|".join([str(params[k]) for k in sorted(params.keys())])
    param_string += f"|{merchant_key}"
    
    # Calculate SHA256 hash
    hash_object = hashlib.sha256(param_string.encode())
    return hash_object.hexdigest()

def verify_payment(order_id):
    try:
        # In a real implementation, you would verify with PayTM's API
        # This is a simplified version for demonstration
        
        # Check if payment exists in database
        payment = payments_collection.find_one({"order_id": order_id})
        if not payment:
            return {"success": False, "message": "Payment not found"}
        
        # Simulate verification (in real app, call PayTM's verify API)
        # For demo purposes, we'll just check if the record exists
        return {"success": True, "message": "Payment verified"}
        
        # Actual implementation would look like:
        """
        paytm_params = {
            "MID": Config.PAYTM_MERCHANT_ID,
            "ORDERID": order_id
        }
        
        checksum = generate_checksum(paytm_params, Config.PAYTM_MERCHANT_KEY)
        paytm_params["CHECKSUMHASH"] = checksum
        
        # Verify with PayTM
        response = requests.post(
            "https://securegw-stage.paytm.in/order/status",
            json=paytm_params,
            headers={"Content-Type": "application/json"}
        )
        
        response_data = response.json()
        if response_data["STATUS"] == "TXN_SUCCESS":
            return {"success": True, "message": "Payment verified"}
        else:
            return {"success": False, "message": response_data["RESPMSG"]}
        """
    except Exception as e:
        return {"success": False, "message": str(e)}
