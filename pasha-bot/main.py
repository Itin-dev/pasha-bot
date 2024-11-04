import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from config import TG_TOKEN
from handlers.commands import start, help_command
from handlers.message_handler import handle_and_clean_messages
from handlers.summary_handler import get_summary, process_message_count, ASK_MESSAGE_COUNT
from db.db_manager import setup_database
from cron.scheduler import schedule_jobs

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Main function to set up and run the bot
def main():
    if not TG_TOKEN:
        logging.error("Bot token not found in .env file")
        return

    # Set up the database
    setup_database()

    # Initialize the bot
    application = ApplicationBuilder().token(TG_TOKEN).build()

    # Schedule jobs for sending summaries
    schedule_jobs(application)

    # Add conversation handler for summarization input in private bot part
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex(r"🚀 Get summary"), get_summary)],
        states={
            ASK_MESSAGE_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_message_count)],
        },
        fallbacks=[]
    )

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP), handle_and_clean_messages))
    application.add_handler(conv_handler)

    logger.info("Starting the bot and job scheduler...")
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
