from telegram import Update
from keyboards.buttons import get_start_buttons

# Function to handle the /start command
async def start(update: Update, context):
    user = update.effective_user
    username = user.username if user.username else user.first_name

    try:
        # Send the welcome message with the 'Get summary' button
        await update.message.reply_text(
            f"Hello, {username}! Welcome to the bot.\n"
            "Please click '🚀 Get summary' to get started.", 
            reply_markup=get_start_buttons()
        )
    except Exception as e:
        logging.error(f"Error sending /start message: {str(e)}")
        await update.message.reply_text("An error occurred while starting the bot. Please try again later.")

# Function to handle the /help command
async def help_command(update: Update, context):
    try:
        # Provide detailed help instructions
        await update.message.reply_text(
            "Here are the available commands:\n"
            "/start - Start the bot\n"
            "/help - Get help\n\n"
            "To get a summary of recent discussions, use the '🚀 Get summary' button."
        )
    except Exception as e:
        logging.error(f"Error sending /help message: {str(e)}")
        await update.message.reply_text("An error occurred while fetching help. Please try again later.")
