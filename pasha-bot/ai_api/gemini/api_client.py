import logging
import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
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

def log_request_and_response(prompt: str, response: str):
    """Log prompt and response to separate files with timestamps."""
    # Get current timestamp for filenames
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Log the prompt
    with open(os.path.join(LOG_FOLDER, f"gemini_request_{timestamp}.log"), "w", encoding="utf-8") as request_log:
        request_log.write(f"Sent to Gemini API at {timestamp}:\n\n{prompt}\n")

    # Log the response
    with open(os.path.join(LOG_FOLDER, f"gemini_response_{timestamp}.log"), "w", encoding="utf-8") as response_log:
        response_log.write(f"Received from Gemini API at {timestamp}:\n\n{response}\n")

def get_gemini_summary(prompt: str) -> str:
    # Define the model configuration
    generation_config = GenerationConfig(
        candidate_count=1,                  # Generate a single response.
        stop_sequences=["\nThread"],        # Stops output generation at thread breaks.
        max_output_tokens=2700,             # Allows for summaries up to your limit.
        temperature=0.3,                    # Keeps responses focused and consistent.
        top_p=0.9,                          # Enables nucleus sampling for diversity.
        top_k=40,                           # Considers the top 40 tokens for diversity.
        response_mime_type="text/plain",    # Ensures plain text output.
        presence_penalty=0.2,               # Discourages token repetition.
        frequency_penalty=0.5               # Penalizes overused tokens for better vocabulary.
    )
    
    try:
        # Log before making the API request
        logging.info("Sending prompt to Gemini API.")
        
        # Create the model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        # Start a conversation and send the prompt
        chat_session = model.start_chat()
        response = chat_session.send_message(f"{prompt}")

        if response:
            logging.info("Response received from Gemini API.")
            # Log the prompt and response to separate files
            log_request_and_response(prompt, response.text)
            return response.text
        else:
            logging.warning("No response from the Gemini API.")
            return "No response from the Gemini API."
    except Exception as e:
        logging.error(f"Error in Gemini API call: {str(e)}")
        return "An error occurred while calling the Gemini API."
