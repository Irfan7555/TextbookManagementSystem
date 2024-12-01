# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import get_db_connection, create_tables
import sqlite3

app = FastAPI()

create_tables()

# Models
class Book(BaseModel):
    book_id: str
    title: str
    author: str
    category: str
    quantity: int

class BookRequest(BaseModel):
    book_id: str
    student_username: str

class Category(BaseModel):
    name: str

# Category Management Routes
@app.get("/librarian/categories")
def get_categories():
    """Get all categories"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM categories")
        categories = cursor.fetchall()
        return [category["name"] for category in categories]
    finally:
        conn.close()




# #Route to view all books
@app.get("/librarian/books")
def view_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    books = cursor.execute("SELECT * FROM books").fetchall()
    conn.close()
    return [{"book_id": book["book_id"], "title": book["title"], "author": book["author"], "quantity": book["quantity"], "category":book["category"]}
            for book in books]
###


@app.get("/librarian/books/category/{category_name}")
def view_books_by_category(category_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    books = cursor.execute("SELECT * FROM books WHERE category = ?", (category_name,)).fetchall()
    conn.close()
    
    if not books:
        raise HTTPException(status_code=404, detail="No books found for the specified category")
    
    return [
        {
            "book_id": book["book_id"],"title": book["title"],"author": book["author"],"quantity": book["quantity"],"category": book["category"]
        }
        for book in books
    ]


@app.post("/librarian/categories/add")
def add_category(category: Category):
    """Add a new category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category.name,))
        conn.commit()
        return {"message": f"Category '{category.name}' added successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Category already exists")
    finally:
        conn.close()

@app.delete("/librarian/categories/remove/{category_name}")
def remove_category(category_name: str):
    """Remove a category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if category is in use
        cursor.execute("SELECT COUNT(*) as count FROM books WHERE category = ?", (category_name,))
        if cursor.fetchone()["count"] > 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete category that is assigned to books"
            )
        
        cursor.execute("DELETE FROM categories WHERE name = ?", (category_name,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        
        conn.commit()
        return {"message": f"Category '{category_name}' removed successfully"}
    finally:
        conn.close()

# Modified Book Routes to work with categories
@app.post("/librarian/add")
def add_book(book: Book):
    """Add a new book with category validation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verify category exists
        cursor.execute("SELECT name FROM categories WHERE name = ?", (book.category,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Invalid category")
        
        cursor.execute(
            "INSERT INTO books (book_id, title, author, category, quantity) VALUES (?, ?, ?, ?, ?)",
            (book.book_id, book.title, book.author, book.category, book.quantity)
        )
        conn.commit()
        return {"message": "Book added successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Book ID already exists")
    finally:
        conn.close()



@app.put("/librarian/update")
def update_book_quantity(book_id: str, quantity: int):
    """Update only book quantity"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE books SET quantity = ? WHERE book_id = ?", 
            (quantity, book_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Book not found")
        
        conn.commit()
        return {"message": "Book quantity updated successfully"}
    finally:
        conn.close()
@app.delete("/librarian/remove/{book_id}")
def remove_book(book_id: str):
    """Remove a book"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Book not found")
        
        conn.commit()
        return {"message": "Book removed successfully"}
    finally:
        conn.close()

# Book Request Routes (unchanged)
@app.post("/student/request-book")
def request_book(book_request: BookRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT quantity FROM books WHERE book_id = ?", (book_request.book_id,))
        book = cursor.fetchone()
        
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        if book["quantity"] <= 0:  # Now accessing quantity as dictionary key due to row factory
            raise HTTPException(status_code=400, detail="Book not available")
        
        cursor.execute(
            "INSERT INTO book_requests (book_id, student_username) VALUES (?, ?)",
            (book_request.book_id, book_request.student_username)
        )
        conn.commit()
        
        return {"message": "Book request submitted successfully"}
    
    except sqlite3.DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        conn.close()

@app.get("/student/my-requests/{username}")
def get_student_requests(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT r.*, b.title, b.author 
            FROM book_requests r 
            JOIN books b ON r.book_id = b.book_id 
            WHERE r.student_username = ?
        """, (username,))
        requests = cursor.fetchall()
        return [dict(r) for r in requests]
    finally:
        conn.close()


##Delete my request

@app.delete("/student/my-requests/{username}")
def delete_student_requests(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Delete all requests for the given username
        cursor.execute("DELETE FROM book_requests WHERE student_username = ?", (username,))
        conn.commit()  # Commit the transaction to apply changes
        return {"message": f"Requests for student '{username}' deleted successfully"}
    finally:
        conn.close()

@app.get("/admin/pending-requests")
def get_pending_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT r.*, b.title, b.author 
            FROM book_requests r 
            JOIN books b ON r.book_id = b.book_id 
            WHERE r.status = 'pending'
        """)
        requests = cursor.fetchall()
        return [dict(r) for r in requests]
    finally:
        conn.close()


# Delete pending request
@app.delete("/admin/pending-requests")
def delete_pending_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Delete all requests with status 'pending'
        cursor.execute("DELETE FROM book_requests WHERE status = 'pending'")
        conn.commit()  # Commit the transaction to make changes permanent
        return {"message": "Pending requests deleted successfully"}
    finally:
        conn.close()

@app.put("/admin/process-request/{request_id}")
def process_request(request_id: int, status: str):
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM book_requests WHERE request_id = ?", (request_id,))
        request = cursor.fetchone()
        
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if status == "approved":
            cursor.execute("SELECT quantity FROM books WHERE book_id = ?", (request['book_id'],))
            book = cursor.fetchone()
            
            if book['quantity'] <= 0:
                raise HTTPException(status_code=400, detail="Book no longer available")
            
            cursor.execute(
                "UPDATE books SET quantity = quantity - 1 WHERE book_id = ?",
                (request['book_id'],)
            )
        
        cursor.execute(
            "UPDATE book_requests SET status = ?, response_date = ? WHERE request_id = ?",
            (status, datetime.now(), request_id)
        )
        
        conn.commit()
        return {"message": f"Request {status} successfully"}
    finally:
        conn.close()