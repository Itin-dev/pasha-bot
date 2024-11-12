import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.db_manager import insert_message
from ai_api.gemini.api_client import get_gemini_summary  # Import the existing Gemini integration

# Set up logging for this module
logger = logging.getLogger(__name__)

# List of bot usernames to exclude from deletion
EXCLUDED_BOTS = ['SummaryProBot', 'NokolayDevBot']  # Replace with actual bot usernames

# Specify the thread ID from which you want to delete messages
TARGET_THREAD_ID = 20284  # Replace with your specific thread ID

# Bot mention keyword
BOT_NICKNAME = '@NokolayDevBot'  # The nickname of the bot to look for in messages

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
        
        # Check if the message contains the bot's nickname
        if BOT_NICKNAME in message_text:
            response_text = await handle_bot_mention(message_text)
            if response_text:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=response_text,
                    reply_to_message_id=update.message.message_id
                )
                logger.info(f"Replied to mention from {username} with message: {response_text}")

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

async def handle_bot_mention(message_text: str) -> str:
    """Send the message content to Gemini API if the bot is mentioned, and return the response text."""
    try:
        # Send the message content to Gemini for a summary or response
        response_text = get_gemini_summary(message_text)

        # Return the response from Gemini or a fallback message if there is no response
        return response_text if response_text else "Sorry, I didn't get a proper response from the Gemini API."

    except Exception as e:
        logger.error(f"Exception when processing bot mention: {str(e)}")
        return "An error occurred while processing your request. Please try again later."

def extract_message_details(update: Update) -> tuple:
    """Extract and return message details as a tuple."""
    message_id = update.message.message_id
    date = update.message.date.isoformat()
    username = update.effective_user.username or update.effective_user.first_name or "Unknown User"
    thread_id = update.message.message_thread_id if update.message.is_topic_message else 10000
    message_text = update.message.text or "No text content"

    logger.info(f"Extracted message details from {username} (ID: {message_id}) in thread {thread_id}.")
    return message_id, date, username, message_text, thread_id
