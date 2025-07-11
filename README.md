# BingX Telegram Bot

A Telegram bot that helps users register on BingX and join your group after verification.

## Features

- Welcome users with BingX referral link
- Ask about KYC status and guide users accordingly
- Check deposit status
- Admin approval system for group access
- User state management
- Simple JSON-based database

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (you'll need this later)

### 2. Get Your Telegram User ID

1. Send a message to `@userinfobot` on Telegram
2. Copy your user ID (you'll need this for admin notifications)

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# BingX Referral Link
BINGX_REFERRAL_LINK=https://bingx.com/your-referral-link

# Admin Telegram ID (your Telegram user ID)
ADMIN_TELEGRAM_ID=your_telegram_user_id
```

### 5. Customize Messages and Links

Edit `config.py` to customize:

- Your BingX referral link
- Group link (in `bot.py`)
- Referral code (in messages)
- Bot messages

### 6. Run the Bot

```bash
python bot.py
```

## Bot Flow

1. **Welcome**: Bot greets user and provides BingX registration link
2. **KYC Question**: Asks if user has KYC-verified account
   - If yes: Provides instructions for KYC transfer
   - If no: Asks to register through the link
3. **Deposit Question**: Asks if user has made a deposit
   - If yes: Notifies admin for verification
   - If no: Asks to make deposit first
4. **Admin Verification**: Admin receives notification with user details
5. **Approval**: Admin can approve or reject user
6. **Group Access**: Approved users receive group link

## File Structure

```
bingx_telegram/
├── bot.py              # Main bot logic
├── config.py           # Configuration and messages
├── database.py         # User database management
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .env               # Environment variables (create this)
```

## Customization

### Messages

Edit the `MESSAGES` dictionary in `config.py` to customize bot responses.

### Referral Link

Update `BINGX_REFERRAL_LINK` in your `.env` file.

### Group Link

Update the `group_link` variable in the `handle_admin_action` function in `bot.py`.

### Referral Code

Update the referral code in the KYC instructions message in `config.py`.

## Admin Commands

The bot will send notifications to the admin when users complete the verification process. The admin can:

- **Approve**: Send group link to user
- **Reject**: Send rejection message to user

## Database

User data is stored in `users.json` with the following structure:

```json
{
  "user_id": {
    "state": "current_state",
    "has_kyc": true/false,
    "has_deposit": true/false,
    "username": "telegram_username",
    "name": "user_name"
  }
}
```

## Troubleshooting

### Bot not responding

- Check if bot token is correct
- Ensure bot is running (`python bot.py`)
- Check logs for errors

### Admin not receiving notifications

- Verify `ADMIN_TELEGRAM_ID` is correct
- Make sure you've sent at least one message to the bot

### Users not receiving group link

- Check if group link is correct in `bot.py`
- Ensure bot has permission to send messages to users

## Security Notes

- Keep your bot token secret
- Don't commit `.env` file to version control
- Regularly backup `users.json` if needed

## Support

For issues or questions, check the logs or review the code structure. The bot uses the `python-telegram-bot` library version 20.7.
