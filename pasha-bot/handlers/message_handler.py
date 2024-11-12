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
    # Ensure the update contains a message before proceeding
    if update.message:
        username = update.effective_user.username if update.effective_user else "Unknown User"
        message_text = update.message.text or "No text content"
        thread_id = update.message.message_thread_id if update.message.is_topic_message else 10000
        
        logger.info(f"Handling message from {username}: {message_text} in thread {thread_id}")

        # Store the message in the database
        if message_text:
            message_details = extract_message_details(update)
            insert_message(*message_details)  # Store the message in the database
            logger.info(f"Stored message from {message_details[2]} (ID: {message_details[0]}) in the database.")
        
        # Check if the message is in the target thread and not from an excluded bot
        if thread_id == TARGET_THREAD_ID:
            if username not in EXCLUDED_BOTS:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=update.message.message_id
                    )
                    logger.info(f"Deleted message from {username}: {message_text}")
                except Exception as e:
                    logger.error(
                        f"Error deleting message: {str(e)} - Message ID: {update.message.message_id}, "
                        f"Thread ID: {thread_id}, Chat ID: {update.effective_chat.id}"
                    )
            else:
                logger.info(f"Message from excluded bot: {username}. Not deleting.")
        else:
            logger.info(f"Message not from target thread ID {TARGET_THREAD_ID}. Ignoring.")
    else:
        logger.warning("Received an update with no message content. Skipping.")

def extract_message_details(update: Update) -> tuple:
    """Extract and return message details as a tuple."""
    message_id = update.message.message_id
    date = update.message.date.isoformat()
    username = update.effective_user.username or update.effective_user.first_name or "Unknown User"
    thread_id = update.message.message_thread_id if update.message.is_topic_message else 10000
    message_text = update.message.text or "No text content"

    logger.info(f"Extracted message details from {username} (ID: {message_id}) in thread {thread_id}.")
    return message_id, date, username, message_text, thread_id
