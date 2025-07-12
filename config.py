import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_TELEGRAM_ID', 0))
BINGX_REFERRAL_LINK = os.getenv('BINGX_REFERRAL_LINK', 'https://bingx.com/your-referral-link')

# Bot states
class BotStates:
    GREETING = "GREETING"
    KYC_QUESTION = "KYC_QUESTION"
    KYC_YES = "KYC_YES"
    KYC_NO = "KYC_NO"
    KYC_COMPLETION = "KYC_COMPLETION"
    DEPOSIT_QUESTION = "DEPOSIT_QUESTION"
    DEPOSIT_YES = "DEPOSIT_YES"
    DEPOSIT_NO = "DEPOSIT_NO"
    WAITING_FOR_ADMIN = "WAITING_FOR_ADMIN"
    SUPPORT = "SUPPORT"

# Messages
MESSAGES = {
    'welcome': "Hello, welcome! 👋\n\nJoining this group is completely free, and all trades must be done on the BingX account you open.\n\nTo join the group, register on BingX using this link:\n{BINGX_REFERRAL_LINK}",
    'kyc_question': "Do you already have a KYC-verified BingX account?",
    'kyc_yes': "Great! To transfer your KYC to our referral, please follow these steps:\n\n1. Log into your BingX account\n2. Go to Settings > Referral\n3. Enter our referral code: YOUR_REFERRAL_CODE\n4. Complete the transfer process\n\nLet me know when you've completed this step!",
    'kyc_no': "No problem! Please register through the link I provided above and complete your KYC verification.",
    'kyc_completion_question': "Have you completed your KYC verification?",
    'kyc_completion_yes': "Great! Now let's check your deposit status.",
    'kyc_completion_no': "Please complete your KYC verification first, then let me know when you're ready!",
    'kyc_transfer_confirmation': "Have you completed the KYC transfer to our referral?",
    'kyc_transfer_yes': "Great! Now let's check your deposit status.",
    'kyc_transfer_no': "Please complete the KYC transfer first, then let me know when you're ready!",
    'deposit_question': "Have you made a deposit?",
    'deposit_yes': "Perfect! I'm forwarding your information to our admin for verification. You'll receive the group link once verified.",
    'deposit_no': "Please make a deposit first, then let me know when you're ready!",
    'admin_notification': "New user waiting for verification:\nUser ID: {user_id}\nUsername: @{username}\nName: {name}\nHas KYC: {has_kyc}\nHas Deposit: {has_deposit}"
} 