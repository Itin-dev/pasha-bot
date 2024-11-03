import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.db_manager import insert_message

# Set up logging for this module
logger = logging.getLogger(__name__)

# List of bot usernames to exclude from deletion
EXCLUDED_BOTS = ['SummaryProBot', 'NokolayDevBot']  # Replace with actual bot usernames

# Specify the thread ID from which you want to delete messages
TARGET_THREAD_ID = 20284  # Replace with your specific thread ID

async def handle_and_clean_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle incoming messages and store them in the database
    if update.message and update.message.text:
        message_details = extract_message_details(update)
        insert_message(*message_details)  # Store the message in the database
        logger.info(f"Stored message from {message_details[2]} (ID: {message_details[0]}) in the database.")

        # Log the incoming message
        logger.info(f"Handling message from {update.effective_user.username}: {update.message.text} in thread {update.message.message_thread_id}")

        # Check if the message is in the target thread
        if update.message.message_thread_id == TARGET_THREAD_ID:
            username = update.effective_user.username if update.effective_user.username else "Unknown User"
            if username not in EXCLUDED_BOTS:
                try:
                    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
                    logger.info(f"Deleted message from {username}: {update.message.text}")
                except Exception as e:
                    logger.error(f"Error deleting message: {str(e)}")
            else:
                logger.info(f"Message from excluded bot: {username}. Not deleting.")
        else:
            logger.info(f"Message not from target thread ID {TARGET_THREAD_ID}. Ignoring.")

def extract_message_details(update: Update) -> tuple:
    """Extract and return message details as a tuple."""
    message_id = update.message.message_id
    date = update.message.date.isoformat()
    username = update.effective_user.username or update.effective_user.first_name
    thread_id = update.message.message_thread_id if update.message.is_topic_message else 10000
    message_text = update.message.text

    logger.info(f"Handling message from {username} (ID: {message_id}) in thread {thread_id}.")
    return message_id, date, username, message_text, thread_id
