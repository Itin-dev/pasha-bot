import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from db.fetchers import fetch_last_n_messages
from ai_api.gemini.prompt_builder import build_prompt
from ai_api.gemini.api_client import get_gemini_summary
from utils.formaters.message_formatter import format_messages, replace_thread_ids_with_names

# Constants
ASK_MESSAGE_COUNT = 1
POSITIVE_NUMBER_ERROR = "Пожалуйста, введите положительное число."
INVALID_INPUT_ERROR = "Пожалуйста, введите действительное число."
SUMMARY_NOT_FOUND_MESSAGE = "Сообщения для обобщения не найдены."
PROCESSING_ERROR_MESSAGE = "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз."
REQUEST_SUMMARY_MESSAGE = "Сколько сообщений вы хотите обобщить?"
SUMMARY_RESPONSE_PREFIX = "Ключевые обсуждения:\n\n"

async def get_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user how many messages they want summarized."""
    await update.message.reply_text(REQUEST_SUMMARY_MESSAGE)
    return ASK_MESSAGE_COUNT

async def process_message_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the user's input for the number of messages to summarize."""
    user_input = update.message.text.strip()
    logging.info(f"Received user input: {user_input}")

    try:
        message_count = validate_message_count(user_input)
        messages = fetch_last_n_messages(message_count)
        return await handle_fetched_messages(update, messages)
    except ValueError:
        await update.message.reply_text(INVALID_INPUT_ERROR)
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
