import sqlite3

connection = sqlite3.connect("users.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    dob TEXT NOT NULL,
    password TEXT NOT NULL,
    is_verified INTEGER DEFAULT 0,
    otp TEXT
)
""")

connection.commit()

connection.close()