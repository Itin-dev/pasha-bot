import logging
from utils.mappers.thread_name_mappings import THREAD_MAPPING

def format_messages(messages):
    formatted_messages = []

    try:
        # Group messages by thread_id
        grouped_messages = {}
        for thread_id, username, date, message_content in messages:
            if thread_id not in grouped_messages:
                grouped_messages[thread_id] = []
            grouped_messages[thread_id].append((username, date, message_content))

        # Sort threads by the number of messages (optional)
        sorted_threads = sorted(grouped_messages.items(), key=lambda x: len(x[1]), reverse=True)

        # Format messages for each thread using thread_id
        for thread_id, msgs in sorted_threads:
            formatted_messages.append(f"Thread {thread_id}")  # Include thread ID as title
            for username, date, message_content in reversed(msgs):  # Reverse for chronological order
                logging.info(f"Formatting message: {username}, {date}, {message_content}")
                formatted_messages.append(f"  - {username}: {message_content}")  # Removed timestamp
            formatted_messages.append("")  # Add a blank line between threads
    except Exception as e:
        logging.error(f"Error formatting messages: {str(e)}")
        raise e  # Rethrow the exception after logging it

    return "\n".join(formatted_messages)


def replace_thread_ids_with_names(message_block: str) -> str:
    """Replaces thread IDs with their corresponding names in a message block."""
    for thread_id, thread_name in THREAD_MAPPING.items():
        thread_id_str = f"Thread {thread_id}" if thread_id is not None else "Thread None"
        message_block = message_block.replace(thread_id_str, thread_name)
    return message_block
