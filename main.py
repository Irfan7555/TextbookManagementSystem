from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import create_tables
import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
# from database import  BookRequest
from typing import List


app = FastAPI()

create_tables()
# SQLite database connection
def get_db_connection():
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    return conn

# Book model
class Book(BaseModel):
    book_id: int
    title: str
    author: str
    quantity: int

# Route to add a book
@app.post("/librarian/add")
def add_book(book: Book):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (book_id, title, author, quantity) VALUES (?, ?, ?, ?)",
                   (book.book_id, book.title, book.author, book.quantity))
    conn.commit()
    conn.close()
    return {"message": "Book added successfully"}

# Route to view all books
@app.get("/librarian/books")
def view_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    books = cursor.execute("SELECT * FROM books").fetchall()
    conn.close()
    return [{"book_id": book["book_id"], "title": book["title"], "author": book["author"], "quantity": book["quantity"]}
            for book in books]

# Route to update a book
@app.put("/librarian/update")
def update_book(book: Book):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET quantity = ? WHERE book_id = ?", (book.quantity, book.book_id))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book updated successfully"}

# Route to remove a book
@app.delete("/librarian/remove/{book_id}")
def remove_book(book_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book removed successfully"}





###

from datetime import datetime
from typing import List

class BookRequest(BaseModel):
    book_id: str
    student_username: str

class RequestResponse(BaseModel):
    request_id: int
    status: str

@app.post("/student/request-book")
def request_book(book_request: BookRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if book exists and has available quantity
    cursor.execute("SELECT quantity FROM books WHERE book_id = ?", (book_request.book_id,))
    book = cursor.fetchone()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book['quantity'] <= 0:
        raise HTTPException(status_code=400, detail="Book not available")
    
    # Create request
    cursor.execute(
        "INSERT INTO book_requests (book_id, student_username) VALUES (?, ?)",
        (book_request.book_id, book_request.student_username)
    )
    conn.commit()
    conn.close()
    return {"message": "Book request submitted successfully"}

@app.get("/student/my-requests/{username}")
def get_student_requests(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, b.title, b.author 
        FROM book_requests r 
        JOIN books b ON r.book_id = b.book_id 
        WHERE r.student_username = ?
    """, (username,))
    requests = cursor.fetchall()  # Remove .execute - just call fetchall() directly
    conn.close()
    return [dict(r) for r in requests]

@app.get("/admin/pending-requests")
def get_pending_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, b.title, b.author 
        FROM book_requests r 
        JOIN books b ON r.book_id = b.book_id 
        WHERE r.status = 'pending'
    """)
    requests = cursor.fetchall()
    conn.close()
    return [dict(r) for r in requests]

@app.put("/admin/process-request/{request_id}")
def process_request(request_id: int, status: str):
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get request details
    cursor.execute("SELECT * FROM book_requests WHERE request_id = ?", (request_id,))
    request = cursor.fetchone()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if status == "approved":
        # Check book availability
        cursor.execute("SELECT quantity FROM books WHERE book_id = ?", (request['book_id'],))
        book = cursor.fetchone()
        
        if book['quantity'] <= 0:
            raise HTTPException(status_code=400, detail="Book no longer available")
        
        # Update book quantity
        cursor.execute(
            "UPDATE books SET quantity = quantity - 1 WHERE book_id = ?",
            (request['book_id'],)
        )
    
    # Update request status
    cursor.execute(
        "UPDATE book_requests SET status = ?, response_date = ? WHERE request_id = ?",
        (status, datetime.now(), request_id)
    )
    
    conn.commit()
    conn.close()
    return {"message": f"Request {status} successfully"}
