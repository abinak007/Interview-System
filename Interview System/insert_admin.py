import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create the admin table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")

# Check if Admin already exists
cursor.execute("SELECT * FROM admin WHERE username = ?", ("Admin",))
existing_admin = cursor.fetchone()

# If Admin does not exist, insert it
if not existing_admin:
    cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("Admin", "Admin@1234"))
    conn.commit()
    print("✅ Admin user inserted successfully!")
else:
    print("⚠️ Admin user already exists.")

# Close the connection
conn.close()
