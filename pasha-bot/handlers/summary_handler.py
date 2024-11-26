import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from db.fetchers import fetch_last_n_messages
from ai_api.gemini.prompt_builder import build_prompt
from ai_api.gemini.api_client import get_gemini_summary
from keyboards.buttons import get_start_buttons
from keyboards.buttons import get_numeric_keyboard
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
    """Ask the user how many messages they want summarized, with a numeric keyboard."""
    await update.message.reply_text(
        REQUEST_SUMMARY_MESSAGE,
        reply_markup=get_numeric_keyboard()  # Add the numeric keyboard here
    )
    return ASK_MESSAGE_COUNT

async def process_message_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.strip()
    user_id = update.message.from_user.id
    logging.info(f"Received user input: {user_input} from user {user_id}")

    # Handle "Cancel"
    if user_input.lower() == "cancel":
        await update.message.reply_text("Запрос отменен.")
        return ConversationHandler.END

    # Check query limits
    if not is_query_allowed(user_id):
        await update.message.reply_text("Превышен лимит запросов. Пожалуйста, подождите минуту и попробуйте снова.")
        return ASK_MESSAGE_COUNT

    try:
        # Validate input
        message_count = validate_message_count(user_input)

        # Fetch and handle messages
        messages = fetch_last_n_messages(message_count)
        return await handle_fetched_messages(update, messages)
    except ValueError as e:
        await update.message.reply_text(str(e))
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
    """Handle the messages fetched from the database and respond with a summary."""
    if not messages:
        await update.message.reply_text("No messages found for summary.")
        # Send the start button again after the response
        await update.message.reply_text(
            "Main menu:",
            reply_markup=get_start_buttons()  # Send the main menu buttons again
        )
        return ConversationHandler.END

    # Step 1: Format the messages (Format once, and only here)
    formatted_message_block = format_messages(messages)
    logging.info(f"Formatted message block:\n{formatted_message_block}")

    # Step 2: Replace thread IDs with names (optional, done once here)
    formatted_message_block_with_names = replace_thread_ids_with_names(formatted_message_block)
    logging.info(f"Formatted message block with names:\n{formatted_message_block_with_names}")

    # Step 3: Build the final prompt using the formatted message block (Only once)
    prompt = build_prompt(formatted_message_block_with_names)  # Here, we use the formatted message only once
    logging.info(f"Generated prompt for Gemini API:\n{prompt}")

    # Step 4: Send the prompt to Gemini API (only once)
    summary = get_gemini_summary(prompt)
    logging.info(f"Received summary from Gemini API:\n{summary}")

    # Step 5: Replace thread IDs with names in the summary (if needed)
    summary_with_names = replace_thread_ids_with_names(summary)
    logging.info(f"Summary with thread names:\n{summary_with_names}")

    # Step 6: Send the summarized message to the user
    await update.message.reply_text(f"Ключевые обсуждения:\n\n{summary_with_names}")

    # Ensure the "Get summary" button is displayed after the summary response
    await update.message.reply_text(
        "\n\n Используйте кнопку внизу для нового запроса:",
        reply_markup=get_start_buttons()  # Send the main menu buttons again
    )

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
