# Telegram Premium Group Bot with PayTM Gateway

A Telegram bot that manages premium group access with PayTM payment gateway integration.

## Features

- Three subscription plans: Weekly (₹3), Monthly (₹10), Yearly (₹99)
- PayTM payment gateway integration
- MongoDB backend for user and payment tracking
- Automatic premium expiration
- Admin commands for user management

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `config.py` file with your credentials (use `config.py.example` as template)
4. Set up MongoDB Atlas or local MongoDB instance
5. Configure PayTM merchant account and get credentials

## Environment Variables

- `API_ID`: Your Telegram API ID
- `API_HASH`: Your Telegram API Hash
- `BOT_TOKEN`: Your Telegram bot token
- `MONGO_URI`: MongoDB connection string
- `PAYTM_MERCHANT_ID`: Your PayTM merchant ID
- `PAYTM_MERCHANT_KEY`: Your PayTM merchant key
- `PAYTM_WEBSITE`: PayTM website (WEBSTAGING for testing, DEFAULT for production)
- `PAYTM_CALLBACK_URL`: URL for PayTM callback
- `PREMIUM_GROUP_LINK`: Link to your premium Telegram group
- `ADMIN_IDS`: Comma-separated list of admin user IDs

## Deployment

### Render.com (Free Tier)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Use the following build command: `pip install -r requirements.txt`
5. Start command: `python bot.py`
6. Deploy!

## Bot Commands

- `/start` - Start the bot and view premium plans
- `/premium_users` (Admin only) - List all premium users

## Payment Flow

1. User selects a plan
2. Bot generates PayTM payment link
3. User completes payment on PayTM
4. PayTM calls your callback URL (needs to be implemented)
5. User verifies payment in bot
6. Bot grants access to premium group

## License

MIT
