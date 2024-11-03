import sqlite3
import os
from config import DB_PATH

# Function to set up the database (create tables if not exist)
def setup_database():
    # Ensure the directory for the database file exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create a table for storing messages
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER,
                        date TEXT,
                        username TEXT,
                        message_content TEXT,
                        thread_id INTEGER
                    )''')
    conn.commit()
    conn.close()

# Function to insert message data into the SQLite database
def insert_message(message_id, date, username, message_content, thread_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert message details into the table
    cursor.execute('''INSERT INTO messages (message_id, date, username, message_content, thread_id)
                      VALUES (?, ?, ?, ?, ?)''',
                   (message_id, date, username, message_content, thread_id))
    conn.commit()
    conn.close()