import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.db_manager import insert_message

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and store them in the database."""
    if update.message and update.message.text:
        message_details = extract_message_details(update)
        insert_message(*message_details)
        logging.info(f"Stored message from {message_details[2]} (ID: {message_details[0]}) in the database.")

def extract_message_details(update: Update) -> tuple:
    """Extract and return message details as a tuple."""
    message_id = update.message.message_id
    date = update.message.date.isoformat()
    username = update.effective_user.username or update.effective_user.first_name
    thread_id = update.message.message_thread_id if update.message.is_topic_message else 10000
    message_text = update.message.text

    logging.info(f"Handling message from {username} (ID: {message_id}) in thread {thread_id}.")
    return message_id, date, username, message_text, thread_id
