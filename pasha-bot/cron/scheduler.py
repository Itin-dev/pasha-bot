import logging
import datetime
from telegram.ext import CallbackContext
from pytz import timezone
from config import DAILY_SUMMARY_CHAT_ID
from db.fetchers import fetch_messages_by_date_range
from ai_api.gemini.prompt_builder import build_prompt
from ai_api.gemini.api_client import get_gemini_summary
from utils.formaters.message_formatter import format_messages, replace_thread_ids_with_names

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the specific times to send summaries (24-hour format)
scheduled_times = [
    (7, 10),  # 07:10 AM
    (14, 0),  # 02:00 PM
    (21, 59), # 09:48 PM
    (22, 0), # 09:50 PM
]

# Timezone for scheduling
LOCAL_TZ = timezone('Europe/Zurich')

async def send_summary(context: CallbackContext):
    now = datetime.datetime.now(LOCAL_TZ)
    today = now.date()

    # Convert scheduled times to datetime objects for today
    scheduled_datetimes = sorted(
        [datetime.datetime.combine(today, datetime.time(hour, minute), LOCAL_TZ)
         for hour, minute in scheduled_times]
    )

    # Find the most recent scheduled time that is less than or equal to now
    current_time = max(
        (time for time in scheduled_datetimes if time <= now),
        default=None
    )

    if current_time is None:
        logger.warning("No valid scheduled time found before now. Exiting.")
        return

    # Find the previous scheduled time that is strictly less than current_time
    previous_time = max(
        (time for time in scheduled_datetimes if time < current_time),
        default=None
    )

    # If there is no previous time, then set it to the earliest scheduled time
    if previous_time is None:
        previous_time = scheduled_datetimes[0]

    # Log the times being used for fetching messages
    logger.info(f"Fetching messages from {previous_time} to {current_time}")

    try:
        messages = fetch_messages_by_date_range(previous_time, current_time)
        logger.info(f"Fetched {len(messages)} messages from the database.")

        if not messages:
            logger.warning("No messages found for the specified period. Exiting.")
            return

        message_block = format_messages(messages)
        prompt = build_prompt(message_block)
        summary = get_gemini_summary(prompt)

        if not summary:
            logger.error("Received an empty summary from the Gemini API.")
            return

        formatted_summary = replace_thread_ids_with_names(summary)
        logger.info(f"Formatted summary: {formatted_summary}")

        await context.bot.send_message(
            chat_id=DAILY_SUMMARY_CHAT_ID,
            text=f"📋 Summary from {previous_time.strftime('%Y-%m-%d %H:%M')} to {current_time.strftime('%Y-%m-%d %H:%M')}:\n\n{formatted_summary}",
            message_thread_id=20284
        )
        logger.info("Successfully sent the summary")

    except Exception as e:
        logger.error(f"Failed to send summary due to error: {str(e)}")


# Function to schedule jobs
def schedule_jobs(application):
    for hour, minute in scheduled_times:
        job_time = datetime.time(hour=hour, minute=minute, tzinfo=LOCAL_TZ)
        application.job_queue.run_daily(
            callback=send_summary,
            time=job_time,
            name=f"daily_summary_{hour}_{minute}",
        )
        logger.info(f"Scheduled job to run daily at {job_time.isoformat()} in timezone {LOCAL_TZ.zone}")
