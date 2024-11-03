import logging
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone
from telegram import Bot
from config import TG_TOKEN, DAILY_SUMMARY_CHAT_ID
from db.fetchers import fetch_messages_by_date_range
from ai_api.gemini.prompt_builder import build_prompt
from ai_api.gemini.api_client import get_gemini_summary
from utils.formaters.message_formatter import format_messages, replace_thread_ids_with_names

import asyncio

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the bot
bot = Bot(token=TG_TOKEN)

# Define the timezone
LOCAL_TZ = timezone('Europe/Zurich')  # Set your local timezone

# Define the specific times to send summaries (24-hour format)
scheduled_times = [
    (7, 10),  
    (14, 0),  
    (18, 35), 
    (22, 30), 
]

# Track the last execution time
last_execution_time = None

# Define the async function to fetch and send summary
async def send_summary(start_time, end_time):
    try:
        # Fetch messages from the specified time range
        messages = fetch_messages_by_date_range(start_time, end_time)

        # Format the messages into a block and build the prompt
        message_block = format_messages(messages)

        # Create the prompt for the Gemini API
        prompt = build_prompt(message_block)

        # Get the summary from the Gemini API
        summary = get_gemini_summary(prompt)

        # Log the raw summary response
        logging.info(f"Received raw summary from Gemini API: {summary}")

        # Replace thread IDs with thread names in the summary
        formatted_summary = replace_thread_ids_with_names(summary)

        # Log the formatted summary
        logging.info(f"Formatted summary for Telegram: {formatted_summary}")

        # Send the summary to the Daily Summaries chat in a specific thread
        await bot.send_message(
            chat_id=DAILY_SUMMARY_CHAT_ID,
            text=f"📋 Summary from {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}:\n\n{formatted_summary}",
            message_thread_id=20284
        )
        logger.info("Successfully sent the summary")
    
    except Exception as e:
        logger.error(f"Failed to send summary: {str(e)}")

# Wrapper to run async function inside the synchronous APScheduler
def run_async_task(hour, minute):
    global last_execution_time
    # Calculate the current execution time
    current_execution_time = datetime.datetime.now(LOCAL_TZ).replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Determine the start time based on the last execution time
    if last_execution_time is None:
        # If this is the first execution, look back a reasonable default period (e.g., 9 hours)
        start_time = current_execution_time - datetime.timedelta(hours=9)
    else:
        # Calculate the time difference in hours from the last execution time
        time_difference = (current_execution_time - last_execution_time).total_seconds() / 3600
        start_time = last_execution_time

        # Log the time difference
        logger.info(f"Time since last execution: {time_difference:.2f} hours")

    end_time = current_execution_time

    # Update last execution time
    last_execution_time = current_execution_time

    # Run the async summary function
    asyncio.run(send_summary(start_time, end_time))

# Set up the scheduler to run the task at specified times
scheduler = BlockingScheduler(timezone=LOCAL_TZ)

# Schedule the job for each defined time
for hour, minute in scheduled_times:
    scheduler.add_job(run_async_task, 'cron', args=[hour, minute], hour=hour, minute=minute)

# Function to start the scheduler, used in main.py
def run_summary_scheduler():
    logger.info("Starting the summary scheduler")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
