from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from payment_handler import generate_payment_link, verify_payment
import datetime
from pymongo import MongoClient
import time

# Initialize MongoDB client
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client[Config.DB_NAME]
users_collection = db["users"]
payments_collection = db["payments"]

# Initialize Telegram client
app = Client("premium_group_bot", 
             api_id=Config.API_ID, 
             api_hash=Config.API_HASH, 
             bot_token=Config.BOT_TOKEN)

# Start command
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id
    user = users_collection.find_one({"user_id": user_id})
    
    if user and user.get("is_premium"):
        expiry_date = user.get("expiry_date")
        await message.reply(f"Welcome back! Your premium membership is active until {expiry_date}.")
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Weekly - ₹3", callback_data="plan_weekly"),
            InlineKeyboardButton("Monthly - ₹10", callback_data="plan_monthly")],
            [InlineKeyboardButton("Yearly - ₹99", callback_data="plan_yearly")]
        ])
        await message.reply(
            "Welcome to Premium Group Bot!\n\n"
            "Choose a subscription plan to join our premium group:",
            reply_markup=keyboard
        )

# Callback query handler for payment plans
@app.on_callback_query(filters.regex("^plan_"))
async def handle_plan_selection(client, callback_query):
    plan_type = callback_query.data.split("_")[1]
    amount = Config.PAYMENT_PLANS.get(plan_type)
    user_id = callback_query.from_user.id
    
    if not amount:
        await callback_query.answer("Invalid plan selected!")
        return
    
    # Generate payment link
    order_id = f"ORDER_{user_id}_{int(time.time())}"
    payment_link = generate_payment_link(order_id, amount, user_id, plan_type)
    
    if payment_link:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Pay Now", url=payment_link)],
            [InlineKeyboardButton("Verify Payment", callback_data=f"verify_{order_id}")]
        ])
        await callback_query.message.edit_text(
            f"Please complete your payment of ₹{amount} for {plan_type} plan.\n\n"
            "After payment, click 'Verify Payment' to confirm.",
            reply_markup=keyboard
        )
    else:
        await callback_query.message.edit_text("Failed to generate payment link. Please try again later.")

# Payment verification handler
@app.on_callback_query(filters.regex("^verify_"))
async def verify_payment_handler(client, callback_query):
    order_id = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    
    payment_data = payments_collection.find_one({"order_id": order_id, "user_id": user_id})
    
    if not payment_data:
        await callback_query.answer("Payment record not found!")
        return
    
    if payment_data.get("verified"):
        await callback_query.answer("Payment already verified!")
        return
    
    # Verify payment with PayTM
    verification_result = verify_payment(order_id)
    
    if verification_result["success"]:
        # Update payment status
        payments_collection.update_one(
            {"order_id": order_id},
            {"$set": {"verified": True, "verification_date": datetime.datetime.now()}}
        )
        
        # Calculate expiry date based on plan
        plan_type = payment_data["plan_type"]
        if plan_type == "weekly":
            expiry_date = datetime.datetime.now() + datetime.timedelta(days=7)
        elif plan_type == "monthly":
            expiry_date = datetime.datetime.now() + datetime.timedelta(days=30)
        elif plan_type == "yearly":
            expiry_date = datetime.datetime.now() + datetime.timedelta(days=365)
        
        # Update user premium status
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "is_premium": True,
                "plan_type": plan_type,
                "expiry_date": expiry_date,
                "join_date": datetime.datetime.now()
            }},
            upsert=True
        )
        
        # Send group invite link
        try:
            invite_link = await app.create_chat_invite_link(
                Config.MAIN_GROUP_ID,
                member_limit=1
            )
            
            await callback_query.message.edit_text(
                "Payment verified successfully! Here's your one-time group invite link:\n\n"
                f"{invite_link.invite_link}\n\n"
                "This link will expire after one use or in 24 hours.",
                reply_markup=None
            )
            
            # Log in channel
            await app.send_message(
                Config.LOG_CHANNEL_ID,
                f"New premium user: @{callback_query.from_user.username}\n"
                f"Plan: {plan_type}\n"
                f"Expiry: {expiry_date}"
            )
        except Exception as e:
            await callback_query.message.edit_text(
                "Payment verified but failed to generate invite link. Please contact admin.",
                reply_markup=None
            )
    else:
        await callback_query.answer("Payment not verified yet. Please try again later.")

# Admin command to check premium users
@app.on_message(filters.command("premium_users") & filters.user(Config.ADMINS))
async def premium_users(client, message: Message):
    premium_users = users_collection.find({"is_premium": True})
    count = users_collection.count_documents({"is_premium": True})
    
    text = f"Total Premium Users: {count}\n\n"
    for user in premium_users:
        text += f"User: {user.get('user_id')}\nPlan: {user.get('plan_type')}\nExpiry: {user.get('expiry_date')}\n\n"
    
    await message.reply(text[:4000])  # Telegram message limit

# Run the bot
if __name__ == "__main__":
    print("Bot started...")
    app.run()
