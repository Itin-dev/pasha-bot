import logging
import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from ai_api.gemini.prompt_builder import build_prompt
from config import GEMINI_API_KEY
from datetime import datetime

# Load the Gemini API key
genai.configure(api_key=GEMINI_API_KEY)

# Create a log folder if it doesn't exist
LOG_FOLDER = "log"
os.makedirs(LOG_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_FOLDER, "api_debug.log")),  # Main debug log file
        logging.StreamHandler()  # Output logs to the console
    ]
)

def log_request(prompt: str):
    """Log the request to a separate file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(os.path.join(LOG_FOLDER, f"gemini_request_{timestamp}.log"), "w", encoding="utf-8") as request_log:
        request_log.write(f"Sent to Gemini API at {timestamp}:\n\n{prompt}\n")

def log_response(response: str):
    """Log the response to a separate file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(os.path.join(LOG_FOLDER, f"gemini_response_{timestamp}.log"), "w", encoding="utf-8") as response_log:
        response_log.write(f"Received from Gemini API at {timestamp}:\n\n{response}\n")

def get_gemini_summary(message_block: str) -> str:
    # Replace thread IDs with names in the message block before building the prompt
    prompt = build_prompt(message_block)

    # Define the model configuration
    generation_config = GenerationConfig(
        candidate_count=1,
        stop_sequences=["\nThread"],  # Stops output generation at thread breaks.
        max_output_tokens=3500,       # Increased to allow for larger responses.
        temperature=0.3,
        top_p=0.9,
        top_k=40,
        response_mime_type="text/plain",
        presence_penalty=0.3,
        frequency_penalty=0.6
    )

    try:
        # Log the request before sending it
        logging.info("Sending request to Gemini API:")
        log_request(prompt)  # Log the request to the separate file

        # Create the model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        # Start a conversation and send the prompt
        chat_session = model.start_chat()

        # Send the message (request)
        response = chat_session.send_message(f"{prompt}")

        if response:
            # Log the final response after receiving it
            log_response(response.text)  # Log the response to a separate file
            logging.info("Response received from Gemini API.")
            return response.text
        else:
            logging.warning("No response from the Gemini API.")
            return "No response from the Gemini API."
    except Exception as e:
        logging.error(f"Error in Gemini API call: {str(e)}")
        return "An error occurred while calling the Gemini API."
