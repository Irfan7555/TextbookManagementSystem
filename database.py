# database.py
import sqlite3
from datetime import datetime

DATABASE_PATH = "library.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create categories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        name TEXT PRIMARY KEY
    )
    """)
    
    # Create books table with foreign key to categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (category) REFERENCES categories (name)
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
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()