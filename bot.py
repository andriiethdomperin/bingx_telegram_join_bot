import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_IDS, BINGX_REFERRAL_LINK, BotStates, MESSAGES
from database import UserDatabase

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = UserDatabase()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command or back to start/kyc from callback"""
    user = update.effective_user
    user_id = user.id

    # Store user info
    db.set_user_info(user_id, username=user.username, name=user.first_name)
    db.set_user_state(user_id, BotStates.GREETING)

    # Send welcome message
    welcome_text = MESSAGES['welcome'].format(BINGX_REFERRAL_LINK=BINGX_REFERRAL_LINK)
    if update.message:
        await update.message.reply_text(welcome_text)
    elif update.callback_query:
        await update.callback_query.message.reply_text(welcome_text)

    # Ask KYC question
    await ask_referral_registration(update, context)

async def ask_kyc_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask if user has KYC-verified account"""
    keyboard = [
        [
            InlineKeyboardButton("Yes, I have KYC account", callback_data="kyc_yes"),
            InlineKeyboardButton("No, I don't have KYC account", callback_data="kyc_no")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Always show the same KYC question regardless of previous state
    if update.callback_query:
        # Instead of editing, send a new message
        await update.callback_query.message.reply_text(
            MESSAGES['kyc_question'],
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            MESSAGES['kyc_question'],
            reply_markup=reply_markup
        )

async def handle_kyc_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle KYC response"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    response = query.data

    if response == "kyc_yes":
        db.set_kyc_status(user_id, True)
        db.set_user_state(user_id, BotStates.KYC_YES)
        # Combine instructions and confirmation buttons in one new message
        keyboard = [
            [
                InlineKeyboardButton("Yes, I completed the transfer", callback_data="kyc_transfer_yes"),
                InlineKeyboardButton("No, I haven't completed it yet", callback_data="kyc_transfer_no")
            ],
            [
                InlineKeyboardButton("⬅️ Back to start", callback_data="back_to_start")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = await context.bot.send_message(
            chat_id=user_id,
            text=MESSAGES['kyc_yes'],
            reply_markup=reply_markup
        )
        context.user_data['kyc_instruction_msg_id'] = msg.message_id

    elif response == "kyc_no":
        db.set_kyc_status(user_id, False)
        db.set_user_state(user_id, BotStates.KYC_NO)
        # Create keyboard with back button
        keyboard = [
            [
                InlineKeyboardButton("⬅️ Back to KYC Question", callback_data="back_to_kyc")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=user_id,
            text=MESSAGES['kyc_no'],
            reply_markup=reply_markup
        )
        # Wait for user to confirm KYC completion in text message
        
async def ask_kyc_transfer_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask if user has completed KYC transfer to referral"""
    keyboard = [
        [
            InlineKeyboardButton("Yes, I completed the transfer", callback_data="kyc_transfer_yes"),
            InlineKeyboardButton("No, I haven't completed it yet", callback_data="kyc_transfer_no")
        ],
        [
            InlineKeyboardButton("⬅️ Back to KYC Question", callback_data="back_to_kyc")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=MESSAGES['kyc_transfer_confirmation'],
        reply_markup=reply_markup
    )

async def handle_kyc_transfer_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("handle_kyc_transfer_response")
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    response = query.data

    if response == "kyc_transfer_yes":
        db.set_user_state(user_id, BotStates.KYC_YES)
        await context.bot.send_message(
            chat_id=user_id,
            text=MESSAGES['kyc_transfer_yes']
        )
        await ask_deposit_question(update, context)

    elif response == "kyc_transfer_no":
        db.set_user_state(user_id, BotStates.KYC_YES)
        keyboard = [
            [
                InlineKeyboardButton("✅ I have completed it now", callback_data="kyc_transfer_yes"),
                InlineKeyboardButton("⬅️ Back to KYC Question", callback_data="back_to_kyc")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=user_id,
            text=MESSAGES['kyc_transfer_no'],
            reply_markup=reply_markup
        )


async def ask_kyc_completion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 4: Ask if user completed KYC, loop until Yes, then proceed to deposit question"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes", callback_data="kyc_complete_yes"),
            InlineKeyboardButton("❌ No", callback_data="kyc_complete_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Did you complete KYC?",
        reply_markup=reply_markup
    )

async def handle_kyc_completion_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Step 4: KYC completion response, loop until Yes, then proceed to deposit question"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    response = query.data

    if response == "kyc_complete_yes":
        db.set_user_state(user_id, BotStates.KYC_COMPLETION)
        await context.bot.send_message(
            chat_id=user_id,
            text="Great! Now let's check your deposit status."
        )
        await ask_deposit_question(update, context)
    elif response == "kyc_complete_no":
        db.set_user_state(user_id, BotStates.KYC_NO)
        await context.bot.send_message(
            chat_id=user_id,
            text="Please complete your KYC verification first, then let me know when you're ready!"
        )
        # Loop: ask again
        await ask_kyc_completion(update, context)

async def ask_deposit_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 5: Ask if user made a deposit, loop until Yes, then proceed to UID/username submission"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes", callback_data="deposit_yes"),
            InlineKeyboardButton("❌ No", callback_data="deposit_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Did you make a deposit?",
        reply_markup=reply_markup
    )

async def handle_deposit_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Step 5: Deposit response, loop until Yes, then proceed to UID/username submission"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    response = query.data

    if response == "deposit_yes":
        db.set_deposit_status(user_id, True)
        db.set_user_state(user_id, BotStates.DEPOSIT_YES)
        await context.bot.send_message(
            chat_id=user_id,
            text="Great! Please submit your BingX UID and your Telegram username (Step 6)."
        )
        await ask_uid_submission(update, context)
    elif response == "deposit_no":
        db.set_deposit_status(user_id, False)
        db.set_user_state(user_id, BotStates.DEPOSIT_NO)
        await context.bot.send_message(
            chat_id=user_id,
            text="Please make a deposit first, then let me know when you're ready!"
        )
        # Loop: ask again
        await ask_deposit_question(update, context)

async def notify_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Notify admin about new user waiting for verification"""
    if not ADMIN_IDS:
        logger.warning("Admin IDs not set, skipping admin notification")
        return
    
    user_data = db.get_user(user_id)
    user = update.effective_user
    
    notification_text = MESSAGES['admin_notification'].format(
        user_id=user_id,
        username=user.username or "No username",
        name=user.first_name or "No name",
        has_kyc=user_data.get('has_kyc', 'Unknown'),
        has_deposit=user_data.get('has_deposit', 'Unknown')
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send notification to all admins
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=notification_text,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin approval/rejection"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id not in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="❌ You are not authorized to perform this action."
        )
        return
    
    action, user_id = query.data.split("_", 1)
    user_id = int(user_id)
    
    if action == "approve":
        # Send group link to user
        group_link = "https://t.me/your_group_link"  # Replace with actual group link
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Your verification is complete! Here's your group link:\n{group_link}"
        )
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="✅ User approved and group link sent."
        )
        
    elif action == "reject":
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Your verification was not approved. Please contact support for more information."
        )
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="❌ User rejected."
        )

async def ask_uid_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 6: Ask user to submit UID and Telegram username"""
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=(
            "Please reply with your BingX UID.\n"
            "⚠️ To make group management easier, please set a Telegram username in your Telegram settings "
            "if you haven't already."
        )
)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages: collect UID, support requests, or restart flow."""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    current_state = user_data.get('state', BotStates.GREETING)

    # 1. Handle support requests
    if current_state == BotStates.SUPPORT:
        issue_text = update.message.text.strip()
        telegram_username = update.effective_user.username or "(no username)"
        if ADMIN_IDS:
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"Support request from @{telegram_username} (ID: {user_id}):\n{issue_text}"
                    )
                except Exception as e:
                    logger.error(f"Failed to send support request to admin {admin_id}: {e}")
        await update.message.reply_text("Your issue has been forwarded to the admin. Thank you!")
        db.set_user_state(user_id, "COMPLETED")
        return

    # 2. Handle UID submission after deposit
    if current_state == BotStates.DEPOSIT_YES:
        submitted_uid = update.message.text.strip()
        telegram_username = update.effective_user.username
        if not telegram_username:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "❗ You must set a Telegram username before proceeding.\n"
                    "Please go to Telegram Settings > Edit Profile > Username, set a username, then type /start to begin again."
                )
            )
            return  # Do not proceed
        # If username is set, continue as before
        combined_info = f"UID: {submitted_uid}\nTelegram: @{telegram_username}"
        db.update_user(user_id, uid_submission=combined_info)
        if ADMIN_IDS:
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"New user submitted UID and Telegram username:\n{combined_info}\nUser ID: {user_id}"
                    )
                except Exception as e:
                    logger.error(f"Failed to send UID submission to admin {admin_id}: {e}")
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Info received! You will be added to the group."
        )
        db.set_user_state(user_id, "COMPLETED")
        return

    # 3. If user is expected to complete KYC and then confirm
    if current_state == BotStates.KYC_NO:
        db.set_user_state(user_id, BotStates.KYC_QUESTION)  # Prevents repeated triggers
        await ask_kyc_completion(update, context)
        return

    # 4. For any other text, restart the conversation
    if current_state != BotStates.WAITING_FOR_ADMIN:
        await start(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

async def handle_back_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button clicks for each step in the flow."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Optionally: clean up any state/message IDs if you want
    context.user_data['kyc_instruction_msg_id'] = None

    if query.data == "back_to_kyc_transfer":
        # Go back to KYC transfer confirmation step
        await ask_kyc_transfer_confirmation(update, context)
    elif query.data == "back_to_kyc":
        # Go back to KYC question step
        await ask_kyc_question(update, context)
    elif query.data == "back_to_start":
        # Go back to welcome + KYC question (like /start)
        welcome_text = MESSAGES['welcome'].format(BINGX_REFERRAL_LINK=BINGX_REFERRAL_LINK)
        await context.bot.send_message(chat_id=user_id, text=welcome_text)
        await ask_kyc_question(update, context)
    # Add more as needed for other steps

async def ask_referral_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Ask if user registered with the referral link"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes", callback_data="referral_yes"),
            InlineKeyboardButton("❌ No", callback_data="referral_no")
        ],
        [
            InlineKeyboardButton("🟡 I already have a BingX account", callback_data="referral_existing")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Did you register with the referral link?",
        reply_markup=reply_markup
    )

async def handle_referral_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Step 2 options and branch accordingly"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    response = query.data

    if response == "referral_yes":
        # Go to Step 4 (KYC completion)
        await ask_kyc_completion(update, context)
    elif response == "referral_no":
        # Send referral link again, then repeat Step 2
        welcome_text = MESSAGES['welcome'].format(BINGX_REFERRAL_LINK=BINGX_REFERRAL_LINK)
        await context.bot.send_message(chat_id=user_id, text=welcome_text)
        await ask_referral_registration(update, context)
    elif response == "referral_existing":
        # Go to Step 3 (KYC transfer help)
        await show_kyc_transfer_help(update, context)

async def show_kyc_transfer_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 3: Show KYC transfer help and then proceed to KYC completion question"""
    help_text = (
        "To transfer your KYC:\n"
        "1. Your old account must not have had any trading activity in the last 7 days\n"
        "2. Your old account must have advanced KYC\n"
        "3. Log into your old account and transfer your KYC to the newly created account as shown in the image"
    )
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=help_text
    )
    # Optionally, send screenshots here using send_photo
    await context.bot.send_photo(chat_id=update.effective_user.id, photo=open('img/verify_1.png', 'rb'))
    await context.bot.send_photo(chat_id=update.effective_user.id, photo=open('img/verify_2.png', 'rb'))
    # Proceed to Step 4 (ask KYC completion)
    await ask_kyc_completion(update, context)
    
async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.set_user_state(user_id, BotStates.SUPPORT)
    await update.message.reply_text(
        "Please describe your issue or question. Our admin will contact you soon."
    )
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Start the bot\n"
        "/support - Contact admin for help\n"
        # Add more commands as needed
    )
    await update.message.reply_text(help_text)

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("No bot token provided!")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_kyc_transfer_response, pattern="^kyc_transfer_"))
    application.add_handler(CallbackQueryHandler(handle_kyc_completion_response, pattern="^kyc_complete_"))
    application.add_handler(CallbackQueryHandler(handle_kyc_response, pattern="^kyc_"))
    application.add_handler(CallbackQueryHandler(handle_deposit_response, pattern="^deposit_"))
    application.add_handler(CallbackQueryHandler(handle_admin_action, pattern="^(approve|reject)_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(CallbackQueryHandler(handle_back_button, pattern="^back_to_"))
    application.add_handler(CallbackQueryHandler(handle_referral_registration, pattern="^referral_"))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 