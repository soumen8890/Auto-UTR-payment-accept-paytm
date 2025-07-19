import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from payment_handler import generate_paytm_payment_link
import pymongo
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MongoDB client
mongo_client = pymongo.MongoClient(Config.MONGO_URI)
db = mongo_client.get_database()
users_collection = db.users
payments_collection = db.payments

# Initialize Telegram client
app = Client(
    "premium_group_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Start command
@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    user = users_collection.find_one({"user_id": user_id})
    
    if user and user.get("premium_until", datetime.now()) > datetime.now():
        remaining_time = user["premium_until"] - datetime.now()
        await message.reply(
            f"🌟 You already have premium access!\n"
            f"⏳ Your premium expires in {remaining_time.days} days.\n"
            f"Join the premium group: {Config.PREMIUM_GROUP_LINK}"
        )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Weekly - ₹3", callback_data="premium_weekly")],
            [InlineKeyboardButton("Monthly - ₹10", callback_data="premium_monthly")],
            [InlineKeyboardButton("Yearly - ₹99", callback_data="premium_yearly")]
        ])
        await message.reply(
            "💰 **Premium Membership Plans**\n\n"
            "🔹 Weekly: ₹3\n"
            "🔹 Monthly: ₹10\n"
            "🔹 Yearly: ₹99\n\n"
            "Click a plan to subscribe:",
            reply_markup=keyboard
        )

# Callback query handler for premium plans
@app.on_callback_query(filters.regex("^premium_"))
async def premium_callback(client, callback_query):
    plan = callback_query.data.split("_")[1]
    amount = Config.PRICING[plan]
    user_id = callback_query.from_user.id
    
    # Generate order ID
    order_id = f"PREMIUM_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Generate PayTM payment link
    payment_link = generate_paytm_payment_link(
        order_id=order_id,
        amount=amount,
        user_id=user_id,
        plan=plan
    )
    
    # Save payment details to MongoDB
    payments_collection.insert_one({
        "order_id": order_id,
        "user_id": user_id,
        "amount": amount,
        "plan": plan,
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    
    # Send payment link to user
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Pay Now", url=payment_link)],
        [InlineKeyboardButton("Verify Payment", callback_data=f"verify_{order_id}")]
    ])
    
    await callback_query.message.edit_text(
        f"🛒 **Payment for {plan} plan (₹{amount})**\n\n"
        "Click the button below to complete your payment:\n\n"
        f"Order ID: `{order_id}`",
        reply_markup=keyboard
    )

# Verify payment callback
@app.on_callback_query(filters.regex("^verify_"))
async def verify_payment(client, callback_query):
    order_id = callback_query.data.split("_")[1]
    payment = payments_collection.find_one({"order_id": order_id})
    
    if not payment:
        await callback_query.answer("Payment not found!", show_alert=True)
        return
    
    if payment["status"] == "success":
        user_id = callback_query.from_user.id
        user = users_collection.find_one({"user_id": user_id})
        
        # Calculate premium expiration
        if payment["plan"] == "weekly":
            premium_until = datetime.now() + timedelta(days=7)
        elif payment["plan"] == "monthly":
            premium_until = datetime.now() + timedelta(days=30)
        elif payment["plan"] == "yearly":
            premium_until = datetime.now() + timedelta(days=365)
        
        # Update user premium status
        if user:
            users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"premium_until": premium_until}}
            )
        else:
            users_collection.insert_one({
                "user_id": user_id,
                "premium_until": premium_until,
                "joined_at": datetime.now()
            })
        
        await callback_query.message.edit_text(
            f"✅ Payment verified!\n\n"
            f"🎉 You now have {payment['plan']} premium access!\n"
            f"Join the premium group: {Config.PREMIUM_GROUP_LINK}\n\n"
            f"Your premium will expire on {premium_until.strftime('%Y-%m-%d')}"
        )
    else:
        await callback_query.answer("Payment not completed yet!", show_alert=True)

# Admin command to check premium users
@app.on_message(filters.command("premium_users") & filters.user(Config.ADMIN_IDS))
async def premium_users(client, message):
    premium_users = users_collection.find({
        "premium_until": {"$gt": datetime.now()}
    }).sort("premium_until", -1)
    
    response = "🌟 Premium Users:\n\n"
    for user in premium_users:
        response += f"👤 User ID: {user['user_id']}\n"
        response += f"⏳ Expires: {user['premium_until'].strftime('%Y-%m-%d')}\n\n"
    
    await message.reply(response if len(response) > 20 else "No premium users found.")

# Run the bot
if __name__ == "__main__":
    logger.info("Starting bot...")
    app.run()
