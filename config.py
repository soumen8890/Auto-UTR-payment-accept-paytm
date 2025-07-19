import os

class Config:
    # Telegram API credentials
    API_ID = int(os.getenv("API_ID", 123456))  # Your API ID
    API_HASH = os.getenv("API_HASH", "your_api_hash")  # Your API Hash
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")  # Your Bot Token
    
    # MongoDB configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # MongoDB URI
    DB_NAME = os.getenv("DB_NAME", "premium_group_bot")  # Database name
    
    # PayTM Merchant configuration
    PAYTM_MERCHANT_ID = os.getenv("PAYTM_MERCHANT_ID", "your_merchant_id")
    PAYTM_MERCHANT_KEY = os.getenv("PAYTM_MERCHANT_KEY", "your_merchant_key")
    PAYTM_WEBSITE = os.getenv("PAYTM_WEBSITE", "WEBSTAGING")
    PAYTM_CALLBACK_URL = os.getenv("PAYTM_CALLBACK_URL", "https://yourdomain.com/callback")
    
    # Payment plans
    PAYMENT_PLANS = {
        "weekly": 3,
        "monthly": 10,
        "yearly": 99
    }
    
    # Admin user IDs
    ADMINS = [123456789]  # Add your admin user IDs here
    
    # Group configuration
    MAIN_GROUP_ID = -1001234567890  # Your main group ID
    LOG_CHANNEL_ID = -1001234567891  # Channel for logging
