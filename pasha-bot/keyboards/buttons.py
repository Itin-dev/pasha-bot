from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext

def get_start_buttons():
    """Returns the buttons for the /start command."""
    buttons = [
        [KeyboardButton("🚀 Get summary")],  # Main start button with an icon
    ]
    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,  # Adjusts the keyboard to fit buttons
        one_time_keyboard=False,  # Keeps the keyboard visible until manually dismissed
        input_field_placeholder="Choose an option"  # Placeholder text
    )

def get_numeric_keyboard():
    """Returns a numeric keyboard for entering the number of messages."""
    buttons = [
        [KeyboardButton("10"), KeyboardButton("20"), KeyboardButton("50")],  # Predefined options
        [KeyboardButton("100"), KeyboardButton("200"), KeyboardButton("500")],  # Larger predefined options
        [KeyboardButton("Cancel")],  # Option to cancel the input
    ]
    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,  # Adjusts the keyboard to fit buttons
        one_time_keyboard=True,  # Hides the keyboard after input
        input_field_placeholder="Введите число или выберите ниже"  # Placeholder text
    )

def start(update: Update, context: CallbackContext):
    """Start command handler that sends the initial menu."""
    update.message.reply_text(
        "Welcome! Choose an option below:",
        reply_markup=get_start_buttons()
    )

def handle_numeric_choice(update: Update, context: CallbackContext):
    """Handle the numeric input."""
    user_choice = update.message.text
    
    # Process the user's choice (for example, if they choose a number or cancel)
    if user_choice == "Cancel":
        update.message.reply_text("Action canceled.")
        # You can send the start menu again after cancellation if needed.
        update.message.reply_text(
            "Main menu:",
            reply_markup=get_start_buttons()
        )
    else:
        # Process the number entered, and then return to the start menu or next steps
        update.message.reply_text(f"You chose: {user_choice}")
        # Send the numeric keyboard again for further input if needed
        update.message.reply_text(
            "Choose another number:",
            reply_markup=get_numeric_keyboard()
        )
