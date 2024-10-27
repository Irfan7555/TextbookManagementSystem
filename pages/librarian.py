
import streamlit as st
import requests, base64, os 

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

logout_btn = st.sidebar.button("Logout")
if logout_btn:
    if 'logged_in' in st.session_state:
        st.session_state.clear()
    st.switch_page("app.py")

if os.path.exists("static/bg3.jpg"):
    # Load and encode the background image
    bg_image = base64.b64encode(open("static/bg3.jpg", "rb").read()).decode()
    
    # Apply the CSS to the main content area
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)),
        url("data:image/jpg;base64,{bg_image}");
        background-size: 100%;  /* Adjust this to control the size */
        
       
    }}
    </style>
    """, unsafe_allow_html=True)

# Inject the CSS into the Streamlit app
st.markdown(hide_css, unsafe_allow_html=True)
st.title("Librarian Dashboard")



def librarian_dashboard():
    st.title("Librarian Dashboard")
    st.subheader("Welcome, librarian!")



API_URL = "http://localhost:8000"
# Sidebar for selecting an option
option = st.sidebar.selectbox("Choose an option", ["Add Book", "Update Book", "Delete Book", "View All Books"])

# Function to add a book
def add_book(book_id, title, author, quantity):
    if book_id and title and author and quantity > 0:  # Basic validation
        response = requests.post(f"{API_URL}/librarian/add", json={
            "book_id": book_id,
            "title": title,
            "author": author,
            "quantity": quantity
        })
        if response.status_code == 200:
            st.success("Book added successfully.")
        else:
            st.error("Error adding the book. Please check the server.")
    else:
        st.warning("Please fill in all fields correctly!")

# Function to update a book
def update_book(book_id, new_quantity):
    if book_id and new_quantity > 0:  # Basic validation
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

# Function to delete a book
def delete_book(book_id):
    if book_id:  # Basic validation
        response = requests.delete(f"{API_URL}/librarian/remove/{book_id}")
        if response.status_code == 200:
            st.success("Book removed successfully.")
        else:
            st.error("Error removing the book. Please check the server.")
    else:
        st.warning("Please provide a valid Book ID.")

# Function to view all books
def view_books():
    response = requests.get(f"{API_URL}/librarian/books")
    if response.status_code == 200:
        books = response.json()
        for book in books:
            st.write(f"ID: {book['book_id']}, Title: {book['title']}, Author: {book['author']}, Quantity: {book['quantity']}")
    else:
        st.error("Error retrieving books.")

# Handle different sidebar options
if option == "Add Book":
    st.write("### Add a Book:")
    book_id = st.text_input("Book ID")
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    quantity = st.number_input("Quantity", min_value=1)

    if st.button("Add Book"):
        add_book(book_id, title, author, quantity)

elif option == "Update Book":
    st.write("### Update a Book:")
    book_id = st.text_input("Enter Book ID to Update")
    new_quantity = st.number_input("New Quantity", min_value=1)

    if st.button("Update Book"):
        update_book(book_id, new_quantity)

elif option == "Delete Book":
    st.write("### Delete a Book:")
    book_id = st.text_input("Enter Book ID to Delete")

    if st.button("Delete Book"):
        delete_book(book_id)

elif option == "View All Books":
    st.write("### All Books:")
    view_books()