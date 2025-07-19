import hashlib
import urllib.parse
from config import Config

def generate_paytm_payment_link(order_id, amount, user_id, plan):
    paytm_params = {
        "MID": Config.PAYTM_MERCHANT_ID,
        "WEBSITE": Config.PAYTM_WEBSITE,
        "INDUSTRY_TYPE_ID": "Retail",
        "CHANNEL_ID": "WEB",
        "ORDER_ID": order_id,
        "CUST_ID": str(user_id),
        "TXN_AMOUNT": str(amount),
        "CALLBACK_URL": Config.PAYTM_CALLBACK_URL,
        "EMAIL": "user@example.com",  # You can get this from Telegram if available
        "MOBILE_NO": "9876543210",    # You can request this from user
    }
    
    # Generate checksum
    checksum = generate_checksum_by_str(paytm_params, Config.PAYTM_MERCHANT_KEY)
    paytm_params["CHECKSUMHASH"] = checksum
    
    # Generate payment URL
    base_url = "https://securegw-stage.paytm.in/theia/processTransaction" if Config.PAYTM_WEBSITE == "WEBSTAGING" else "https://securegw.paytm.in/theia/processTransaction"
    payment_url = base_url + "?" + urllib.parse.urlencode(paytm_params)
    
    return payment_url

def generate_checksum_by_str(param_dict, merchant_key):
    param_str = get_param_string(param_dict)
    salt = merchant_key
    final_str = param_str + "&" + salt
    hasher = hashlib.sha256(final_str.encode())
    return hasher.hexdigest()

def get_param_string(param_dict):
    param_str = ""
    for key in sorted(param_dict.keys()):
        if param_dict[key] is not None and param_dict[key] != "":
            param_str += f"{key}={param_dict[key]}&"
    return param_str[:-1]  # Remove trailing &
