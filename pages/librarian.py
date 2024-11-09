import streamlit as st
import requests
import base64
import os
import pandas as pd

# CSS to hide unwanted elements
hide_css = """
    <style>
    .st-emotion-cache-j7qwjs.eczjsme15 {
        display: none;
    }
    </style>
"""
st.markdown(hide_css, unsafe_allow_html=True)
if os.path.exists("static/bg1.jpg"):
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.6)), 
        url("data:image/png;base64,{base64.b64encode(open('static/bg1.jpg', 'rb').read()).decode()}");
        background-size: cover;
    }}
    </style>
    """, unsafe_allow_html=True)
# Background image handling (unchanged)
if os.path.exists("static/bg1.jpg"):
    with open('static/bg1.jpg', 'rb') as f:
        bg_data = base64.b64encode(f.read()).decode()


if os.path.exists("static/bg3.jpg"):
    with open("static/bg3.jpg", "rb") as f:
        bg_image = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stAppHeader {{
        background-image: linear-gradient(rgba(0, 0, 0, 0), rgba(255, 255, 255, 0.01)),
        url("data:image/jpg;base64,{bg_image}");
        background-size: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)



# Logout button
logout_btn = st.sidebar.button("Logout")
if logout_btn:
    if 'logged_in' in st.session_state:
        st.session_state.clear()
    st.switch_page("app.py")



st.title("Librarian Dashboard")

API_URL = "http://localhost:8000"

# Enhanced sidebar options with category management
option = st.sidebar.selectbox(
    "Choose an option", 
    ["Add Book", "Update Book", "Delete Book", "View All Books", "Manage Categories"]
)

def get_categories():
    """Fetch all categories from the API"""
    response = requests.get(f"{API_URL}/librarian/categories")
    if response.status_code == 200:
        return response.json()
    return []

def add_category():
    """Add a new category"""
    new_category = st.text_input("New Category Name")
    if st.button("Add Category"):
        if new_category:
            response = requests.post(f"{API_URL}/librarian/categories/add", 
                                  json={"name": new_category})
            if response.status_code == 200:
                st.success(f"Category '{new_category}' added successfully.")
                st.rerun()
            else:
                st.error(f"Error adding category: {response.text}")
        else:
            st.warning("Please enter a category name.")

def remove_category():
    """Remove an existing category"""
    categories = get_categories()
    if categories:
        category_to_remove = st.selectbox("Select Category to Remove", categories)
        if st.button("Remove Category"):
            response = requests.delete(f"{API_URL}/librarian/categories/remove/{category_to_remove}")
            if response.status_code == 200:
                st.success(f"Category '{category_to_remove}' removed successfully.")
                st.rerun()
            else:
                st.error(f"Error removing category: {response.text}")
    else:
        st.warning("No categories available.")

def view_categories():
    """Display all categories"""
    categories = get_categories()
    if categories:
        st.write("### Current Categories:")
        df = pd.DataFrame(categories, columns=["Category"])
        st.table(df)
    else:
        st.info("No categories found.")

def add_book():
    """Add a new book with dynamic categories"""
    book_id = st.text_input("Book ID")
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    
    # Fetch categories dynamically
    categories = get_categories()
    category = st.selectbox("Category", categories if categories else ["No categories available"])
    
    quantity = st.number_input("Quantity", min_value=1)

    if st.button("Add Book"):
        if book_id and title and author and category and quantity > 0:
            response = requests.post(f"{API_URL}/librarian/add", json={
                "book_id": book_id,
                "title": title,
                "author": author,
                "category": category,
                "quantity": quantity
            })
            if response.status_code == 200:
                st.success("Book added successfully.")
            else:
                st.error(f"Error adding the book: {response.text}")
        else:
            st.warning("Please fill in all fields!")

def update_book():
    """Update book quantity"""
    book_id = st.text_input("Enter Book ID to Update")
    new_quantity = st.number_input("New Quantity", min_value=1)

    if st.button("Update Book"):
        if book_id and new_quantity > 0:
            response = requests.put(f"{API_URL}/librarian/update", json={
                "book_id": book_id,
                "quantity": new_quantity
            })
            if response.status_code == 200:
                st.success("Book updated successfully.")
            else:
                st.error("Error updating the book. Please check the server.")
        else:
            st.warning("Please provide a valid Book ID and Quantity.")

def delete_book():
    """Delete a book"""
    book_id = st.text_input("Enter Book ID to Delete")

    if st.button("Delete Book"):
        if book_id:
            response = requests.delete(f"{API_URL}/librarian/remove/{book_id}")
            if response.status_code == 200:
                st.success("Book removed successfully.")
            else:
                st.error("Error removing the book. Please check the server.")
        else:
            st.warning("Please provide a valid Book ID.")

def view_books():
    """View all books"""
    response = requests.get(f"{API_URL}/librarian/books")
    try:
        if response.status_code == 200:
            books = response.json()
            books_data = [
                {
                    'book_id': book['book_id'],
                    'title': book['title'],
                    'author': book['author'],
                    'category': book.get('category', 'N/A'),
                    'quantity': book['quantity']
                }
                for book in books
            ]
            df = pd.DataFrame(books_data)
            df = df[['book_id', 'title', 'author', 'category', 'quantity']]
            st.table(df)
        else:
            st.error("Error retrieving books.")
    except:
        st.info("No available books")
# Handle different sidebar options
if option == "Add Book":
    st.write("### Add a Book:")
    add_book()
elif option == "Update Book":
    st.write("### Update a Book:")
    update_book()
elif option == "Delete Book":
    st.write("### Delete a Book:")
    delete_book()
elif option == "View All Books":
    st.write("### All Books:")
    view_books()
elif option == "Manage Categories":
    st.write("### Manage Categories")
    tab1, tab2, tab3 = st.tabs(["Add Category", "Remove Category", "View Categories"])
    
    with tab1:
        add_category()
    with tab2:
        remove_category()
    with tab3:
        view_categories()
