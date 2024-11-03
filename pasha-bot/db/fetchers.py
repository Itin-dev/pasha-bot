# Fetch the last N messages ordered by date
import sqlite3
from config import DB_PATH

def fetch_last_n_messages(n):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch the last N messages ordered by date, including thread_id = None
    cursor.execute("""
        SELECT thread_id, username, date, message_content
        FROM messages
        ORDER BY date DESC
        LIMIT ?
    """, (n,))

    messages = cursor.fetchall()
    conn.close()

    return messages

# Fetch messages within the given date range
def fetch_messages_by_date_range(start_time, end_time):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Exclude 20284 as this is the thread for summaries
    cursor.execute("""
        SELECT thread_id, username, date, message_content
        FROM messages
        WHERE date BETWEEN ? AND ?
        AND thread_id != 20284
        ORDER BY date DESC
    """, (start_time.isoformat(), end_time.isoformat()))

    messages = cursor.fetchall()
    conn.close()

    return messages