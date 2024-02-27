import sqlite3


def init_db():
    conn = sqlite3.connect("AirConditionerAlert.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()


def save_message(message):
    conn = sqlite3.connect("AirConditionerAlert.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (message, timestamp) VALUES (?, datetime('now'))", (message,))
    conn.commit()
    conn.close()


def fetch_data():
    conn = sqlite3.connect("AirConditionerAlert.db")
    c = conn.cursor()
    c.execute("SELECT message, timestamp FROM messages")
    data = c.fetchall()
    print_data(data)
    conn.close()
    return data

def print_data(data):
    if data:
        print("Log of Data:")
        for row in data:
            message, timestamp = row
            print(f"Timestamp: {timestamp}, Message: {message}")
    else:
        print("No data found in the database.")