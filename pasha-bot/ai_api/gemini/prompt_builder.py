
def build_prompt(message_block):

    prompt = (
        "Summarize the following conversations grouped by thread ID (sub-chats). "
        "Sort the threads by the volume of messages, from the most to the least active. "
        "For each thread, extract key points, insights, or decisions in the conversation, ensuring the summary is concise and focused.\n\n"
        "Format the summary as follows for each thread:\n\n"
        "Thread [thread_id]:\n"
        "• Key Point 1\n"
        "• Key Point 2 (if applicable)\n"
        "• Key Point 3 (if applicable)\n\n"
        "Only include threads with meaningful discussions or decisions. Skip trivial threads. "
        "Limit the output to 1-3 bullet points per thread. If a thread has no significant points, omit it entirely.\n\n"
        "Make sure to summarize in Russian, without using any formatting like bold, italics, or headers. "
        "Keep it simple and focused. Ensure that all threads with substantial information are included in the summary.\n\n"
        f"Conversations:\n\n{message_block}"  #  Replace `message_block` with the actual conversatio
    )


    return prompt