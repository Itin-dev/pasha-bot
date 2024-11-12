import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from db.fetchers import fetch_last_n_messages
from ai_api.gemini.prompt_builder import build_prompt
from ai_api.gemini.api_client import get_gemini_summary
from utils.formaters.message_formatter import format_messages, replace_thread_ids_with_names
from collections import defaultdict
import time

# Constants
ASK_MESSAGE_COUNT = 1
POSITIVE_NUMBER_ERROR = "Пожалуйста, введите положительное число."
INVALID_INPUT_ERROR = "Пожалуйста, введите действительное число."
SUMMARY_NOT_FOUND_MESSAGE = "Сообщения для обобщения не найдены."
PROCESSING_ERROR_MESSAGE = "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз."
REQUEST_SUMMARY_MESSAGE = "Сколько сообщений вы хотите обобщить?"
SUMMARY_RESPONSE_PREFIX = "Ключевые обсуждения:\n\n"
MAX_MESSAGE_COUNT = 1000  # Limit the number of messages to 1000
QUERY_LIMIT = 3  # Maximum queries per minute
QUERY_TIMEOUT = 60  # Time window for query limit (in seconds)

# To keep track of user queries
user_queries = defaultdict(list)

async def get_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user how many messages they want summarized."""
    await update.message.reply_text(REQUEST_SUMMARY_MESSAGE)
    return ASK_MESSAGE_COUNT

async def process_message_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the user's input for the number of messages to summarize."""
    user_input = update.message.text.strip()
    user_id = update.message.from_user.id  # Get the user ID
    logging.info(f"Received user input: {user_input} from user {user_id}")

    # Check the frequency of user queries
    if not is_query_allowed(user_id):
        await update.message.reply_text("Превышен лимит запросов. Пожалуйста, подождите минуту и попробуйте снова.")
        return ASK_MESSAGE_COUNT

    try:
        message_count = validate_message_count(user_input)
        messages = fetch_last_n_messages(message_count)
        return await handle_fetched_messages(update, messages)
    except ValueError as e:
        await update.message.reply_text(str(e))  # Provide custom error message based on validation
        return ASK_MESSAGE_COUNT
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        await update.message.reply_text(PROCESSING_ERROR_MESSAGE)
        return ConversationHandler.END

def validate_message_count(user_input: str) -> int:
    """Validate and return the number of messages."""
    message_count = int(user_input)
    if message_count <= 0:
        raise ValueError(POSITIVE_NUMBER_ERROR)
    if message_count > MAX_MESSAGE_COUNT:
        raise ValueError(f"Максимум {MAX_MESSAGE_COUNT} сообщений. Пожалуйста, введите меньшее количество.")
    return message_count

async def handle_fetched_messages(update: Update, messages: list) -> int:
    """Handle the messages fetched from the database."""
    if not messages:
        await update.message.reply_text(SUMMARY_NOT_FOUND_MESSAGE)
        return ConversationHandler.END

    message_block = format_messages(messages)
    prompt = build_prompt(message_block)
    logging.info(f"Generated prompt for Gemini API: {prompt}")

    summary = get_gemini_summary(prompt)
    logging.info(f"Received summary from Gemini API: {summary}")

    summary = replace_thread_ids_with_names(summary)
    await update.message.reply_text(f"{SUMMARY_RESPONSE_PREFIX}{summary}")
    
    return ConversationHandler.END

def is_query_allowed(user_id: int) -> bool:
    """Check if the user is allowed to make a request based on query frequency."""
    current_time = time.time()
    # Remove timestamps older than 60 seconds
    user_queries[user_id] = [timestamp for timestamp in user_queries[user_id] if current_time - timestamp < QUERY_TIMEOUT]

    # Allow the query if the user hasn't made 3 queries in the last minute
    if len(user_queries[user_id]) >= QUERY_LIMIT:
        return False
    
    # Add current timestamp to the list of queries
    user_queries[user_id].append(current_time)
    return True
