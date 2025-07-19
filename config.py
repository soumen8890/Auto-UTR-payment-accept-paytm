import os

class Config:
    # Telegram API credentials
    API_ID = int(os.getenv("API_ID", "123456"))  # Your API ID
    API_HASH = os.getenv("API_HASH", "your_api_hash_here")  # Your API Hash
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")  # Your Bot Token
    
    # MongoDB configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://username:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority")
    
    # PayTM Merchant configuration
    PAYTM_MERCHANT_ID = os.getenv("PAYTM_MERCHANT_ID", "your_merchant_id")
    PAYTM_MERCHANT_KEY = os.getenv("PAYTM_MERCHANT_KEY", "your_merchant_key")
    PAYTM_WEBSITE = os.getenv("PAYTM_WEBSITE", "WEBSTAGING")  # Use "DEFAULT" for production
    PAYTM_CALLBACK_URL = os.getenv("PAYTM_CALLBACK_URL", "https://yourdomain.com/callback")
    
    # Premium pricing
    PRICING = {
        'weekly': 3,
        'monthly': 10,
        'yearly': 99
    }
    
    # Group configuration
    PREMIUM_GROUP_LINK = os.getenv("PREMIUM_GROUP_LINK", "https://t.me/yourpremiumgroup")
    ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "123456789").split(",")]
