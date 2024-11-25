from telegram import KeyboardButton, ReplyKeyboardMarkup

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
