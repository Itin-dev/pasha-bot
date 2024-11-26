from utils.formaters.message_formatter import replace_thread_ids_with_names

def build_prompt(message_block):
    # Replace thread IDs with names in the message block before building the prompt
    message_block = replace_thread_ids_with_names(message_block)

    # Create the final prompt for the Gemini API
    prompt = (
        "Summarize the following conversations grouped by thread ID (sub-chats). "
        "Sort the threads by the volume of messages, from the most to the least active. "
        "For each thread, extract key points, insights, or decisions in the conversation, ensuring the summary is concise and focused.\n\n"
        "Format the summary as follows for each thread:\n\n"
        "[thread_id]\n"
        "Summary of the thread.\n\n"
        "Ensure there is an empty line between each thread block. Threads with no significant points should be omitted entirely.\n\n"
        "Make sure to summarize in Russian, without using any formatting like bold, italics, or headers. "
        "Keep it simple and focused. Ensure that all threads with substantial information are included in the summary.\n\n"
        "Here is the data to summarize:\n\n"
        f"{message_block}"  # Use the processed message block
    )

    return prompt
