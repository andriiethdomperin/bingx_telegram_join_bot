# BingX Telegram Bot

A Telegram bot that helps users register on BingX and join your group after verification. The bot guides users through a comprehensive workflow including referral registration, KYC verification, deposit confirmation, and admin approval.

## Features

- **Multi-step workflow** with back navigation
- **Referral registration** verification
- **KYC status handling** with transfer instructions
- **Deposit confirmation** loops
- **UID and Telegram username collection**
- **Multi-admin support** system
- **Support command** for user assistance
- **Back buttons** for easy navigation
- **User state management** with JSON database
- **Automatic Telegram username detection**

## Bot Workflow

### Step 1: Welcome & Referral Link

- Bot greets user with welcome message
- Provides BingX referral link
- Explains that joining is free and trades must be done on the registered account

### Step 2: Referral Registration Check

Bot asks if user registered with the referral link:

- **✅ Yes** → Proceed to KYC completion check
- **❌ No** → Show referral link again and repeat
- **🟡 I already have a BingX account** → Show KYC transfer help

### Step 3: KYC Transfer Help (for existing accounts)

- Provides detailed KYC transfer instructions
- Shows verification screenshots
- Lists requirements (no trading activity in last 7 days, advanced KYC)

### Step 4: KYC Completion Check

- Asks if user completed KYC verification
- **✅ Yes** → Proceed to deposit check
- **❌ No** → Loop until user confirms completion

### Step 5: Deposit Confirmation

- Asks if user made a deposit
- **✅ Yes** → Proceed to UID submission
- **❌ No** → Loop until user confirms deposit

### Step 6: UID and Username Collection

- User submits BingX UID via text message
- Bot automatically captures Telegram username
- Information forwarded to admins for verification

### Step 7: Admin Verification

- Admins receive notification with user details
- Admins can approve or reject users
- Approved users receive group link

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

# Admin Telegram IDs (comma-separated for multiple admins)
ADMIN_TELEGRAM_IDS=123456789,987654321
```

### 5. Add Verification Images

Create an `img/` folder and add:

- `verify_1.png` - First verification screenshot
- `verify_2.png` - Second verification screenshot

### 6. Customize Messages and Links

Edit `config.py` to customize:

- Your BingX referral link
- Group link (in `bot.py`)
- Referral code (in messages)
- Bot messages

### 7. Run the Bot

```bash
python bot.py
```

## Bot Commands

- `/start` - Start the bot workflow
- `/support` - Contact admin for help
- `/help` - Show available commands

## Admin Features

### Multi-Admin Support

- Support for multiple admin IDs (comma-separated)
- All admins receive notifications
- Any admin can approve/reject users

### Admin Notifications

The bot sends notifications to all admins when:

- Users submit UID and username
- Users request support

### Admin Actions

- **Approve**: Send group link to user
- **Reject**: Send rejection message to user

## File Structure

```
bingx_telegram/
├── bot.py              # Main bot logic
├── config.py           # Configuration and messages
├── database.py         # User database management
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .env               # Environment variables (create this)
└── img/               # Verification images
    ├── verify_1.png   # First verification screenshot
    └── verify_2.png   # Second verification screenshot
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

### Admin IDs

Add multiple admin IDs separated by commas in the `ADMIN_TELEGRAM_IDS` environment variable.

## Database

User data is stored in `users.json` with the following structure:

```json
{
  "user_id": {
    "state": "current_state",
    "has_kyc": true/false,
    "has_deposit": true/false,
    "username": "telegram_username",
    "name": "user_name",
    "uid_submission": "UID: 123456\nTelegram: @username"
  }
}
```

## Navigation Features

### Back Buttons

- Users can navigate back to previous steps
- Back buttons are available throughout the workflow
- State is preserved during navigation

### Message Flow

- Bot sends new messages instead of editing previous ones
- Better user experience with clear conversation history
- No message conflicts or editing issues

## Troubleshooting

### Bot not responding

- Check if bot token is correct
- Ensure bot is running (`python bot.py`)
- Check logs for errors

### Admin not receiving notifications

- Verify `ADMIN_TELEGRAM_IDS` is correct (comma-separated)
- Make sure you've sent at least one message to the bot
- Check that admin IDs are valid Telegram user IDs

### Users not receiving group link

- Check if group link is correct in `bot.py`
- Ensure bot has permission to send messages to users
- Verify admin approval process is working

### Images not showing

- Ensure `img/` folder exists
- Check that `verify_1.png` and `verify_2.png` are present
- Verify file permissions

## Security Notes

- Keep your bot token secret
- Don't commit `.env` file to version control
- Regularly backup `users.json` if needed
- Use multiple admin IDs for redundancy

## Support

For issues or questions:

1. Use `/support` command in the bot
2. Check the logs for error messages
3. Review the code structure and configuration

The bot uses the `python-telegram-bot` library version 20.7 and provides a comprehensive workflow for BingX referral management.
