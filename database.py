import sqlite3

DATABASE_PATH = "library.db"  # Specify your database path

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This allows access to columns by name
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create books table if it does not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        quantity INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS book_requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id TEXT NOT NULL,
        student_username TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        response_date TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES books (book_id)
    )
    """)

    # You can add more tables here as needed

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()  # Optional: This allows you to create tables by running this script directly



