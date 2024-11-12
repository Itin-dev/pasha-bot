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
    (20, 00),  # 07:05 PM
    (23, 30),  # 07:06 PM
]

# Timezone for scheduling and database (assuming database stores UTC time)
LOCAL_TZ = timezone('Europe/Zurich')
UTC_TZ = timezone('UTC')

# Store the last run time in memory
last_run_time = None

async def send_summary(context: CallbackContext):
    global last_run_time  # Use the global variable to track the last run time

    now = datetime.datetime.now(LOCAL_TZ)
    today = now.date()
    yesterday = today - datetime.timedelta(days=1)

    # Create datetime objects for today’s scheduled times
    scheduled_datetimes_today = [
        datetime.datetime.combine(today, datetime.time(hour, minute), LOCAL_TZ)
        for hour, minute in scheduled_times
    ]
    
    # Include only the last scheduled time from yesterday
    last_scheduled_yesterday = datetime.datetime.combine(
        yesterday, datetime.time(*scheduled_times[-1]), LOCAL_TZ
    )

    # Full schedule: yesterday's last scheduled time + today's scheduled times
    full_schedule = [last_scheduled_yesterday] + scheduled_datetimes_today
    full_schedule = sorted(full_schedule)

    # Set `current_time` to the exact execution time
    current_time = now

    if last_run_time is None:
        # If there's no last run time, it means this is the first run
        if current_time == scheduled_datetimes_today[0]:
            # If it's the first scheduled time of the day (e.g., 7:10 AM), use yesterday's last scheduled time
            previous_time = full_schedule[-1]  # Last element from the previous day
            logger.info(f"First run. Using yesterday's last scheduled time: {previous_time}")
        else:
            # For subsequent times (not the first run), use the last scheduled time for today
            previous_time = max((time for time in full_schedule if time < current_time), default=None)
            logger.info(f"First run, but not at scheduled time. Using previous scheduled time: {previous_time}")
    else:
        # If there is a last run time (i.e., not the first execution), use the previous run time
        previous_time = last_run_time
        logger.info(f"Subsequent run. Using previous run time: {previous_time}")

    if previous_time is None:
        logger.warning("No previous scheduled time found. Exiting.")
        return

    # Ensure both times are in UTC timezone for the database query
    previous_time_utc = previous_time.astimezone(UTC_TZ)
    current_time_utc = current_time.astimezone(UTC_TZ)

    # Log the times being used for fetching messages
    logger.info(f"Fetching messages from {previous_time_utc} to {current_time_utc}")

    try:
        # Fetch messages from the database using the UTC time range
        messages = fetch_messages_by_date_range(previous_time_utc, current_time_utc)
        logger.info(f"Fetched {len(messages)} messages from the database.")

        if not messages:
            logger.warning("No messages found for the specified period. Exiting.")
            return

        # Format and process the messages
        message_block = format_messages(messages)
        prompt = build_prompt(message_block)
        summary = get_gemini_summary(prompt)

        if not summary:
            logger.error("Received an empty summary from the Gemini API.")
            return

        formatted_summary = replace_thread_ids_with_names(summary)
        logger.info(f"Formatted summary: {formatted_summary}")

        # Send the summary via bot
        await context.bot.send_message(
            chat_id=DAILY_SUMMARY_CHAT_ID,
            text=f"📋 Summary from {previous_time_utc.strftime('%Y-%m-%d %H:%M')} to {current_time_utc.strftime('%Y-%m-%d %H:%M')}:\n\n{formatted_summary}",
            message_thread_id=20284
        )
        logger.info("Successfully sent the summary")

        # Update the last run time for future reference
        last_run_time = current_time

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
