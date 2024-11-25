
def build_prompt(message_block):

    prompt = (
        "Summarize the following conversations grouped by threadID (sub-chats), "
        "sorted by the volume of messages. For each thread, extract key points, "
        "insights, or decisions, and keep the summary concise.\n\n"
        "Format the summary as follows:\n\n"
        "Thread [thread_uid]:\n"
        "• Key Point 1\n"
        "• Key Point 2 (if applicable)\n\n"
        "Only include threads with meaningful discussions or decisions. Omit trivial threads. "
        "Limit the output to 1-3 bullet points per thread. Write the summary in Russian. "
        "Do not use any formatting (e.g., bold, italics, headers). Keep it simple and focused.\n\n"
        f"Conversations:\n\n{message_block}"  # Replace `message_block` with your data
    )


    return prompt