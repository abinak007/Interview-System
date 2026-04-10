import sqlite3

conn = sqlite3.connect('database.db')  # Creates or opens the database
cursor = conn.cursor()

# Create users table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

conn.commit()
conn.close()

print("Database and table created successfully.")
