import sqlite3

# Connect to SQLite database (or create if it doesn't exist)
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create Users Table (Doctors & Patients)
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Insert dummy users (for testing)
c.execute("INSERT OR IGNORE INTO users (role, email, password) VALUES ('doctor', 'doctor@example.com', 'password')")
c.execute("INSERT OR IGNORE INTO users (role, email, password) VALUES ('patient', 'patient@example.com', 'password')")

# Save & close connection
conn.commit()
conn.close()

print("✅ Database and Users Table Created Successfully!")
