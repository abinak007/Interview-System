import sqlite3

# Connect to the existing database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create interview_session table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS interview_session (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        questions TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create response table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS response (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_session_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        score INTEGER,
        FOREIGN KEY (interview_session_id) REFERENCES interview_session(id)
    )
''')

# Create emotions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS emotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_session_id INTEGER NOT NULL,
        confidence_level REAL,
        expression_analysis TEXT,
        FOREIGN KEY (interview_session_id) REFERENCES interview_session(id)
    )
''')

# Save changes and close connection
conn.commit()
conn.close()

print("New tables added successfully!")
