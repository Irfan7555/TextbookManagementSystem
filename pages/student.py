import streamlit as st
import requests
import os
import base64

API_URL = "http://localhost:8000"

# Verify login state
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first")
    st.switch_page("app.py")

# Hide unwanted UI elements with CSS
hide_css = """
    <style>
    .st-emotion-cache-j7qwjs.eczjsme15 {
        display: none;
    }
    </style>
"""
st.markdown(hide_css, unsafe_allow_html=True)

# Sidebar background
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

# Logout button
logout_btn = st.sidebar.button("Logout")
if logout_btn:
    if 'logged_in' in st.session_state:
        st.session_state.clear()
    st.switch_page("app.py")

# Main background
if os.path.exists("static/bg2.jpg"):
    bg_image = base64.b64encode(open("static/bg2.jpg", "rb").read()).decode()
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stAppHeader {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)),
        url("data:image/jpg;base64,{bg_image}");
        background-size: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

# Main content
st.title("Student Dashboard")
username = st.session_state.username
st.write(f"Welcome, {username}!")

tab1, tab2 = st.tabs(["Books", "My Requests"])

# Helper functions
import streamlit as st
import requests


def fetch_books_by_category(selected_category):
    """Fetches books based on category if provided; otherwise fetches all books."""
    if selected_category and selected_category != "Select":
        response = requests.get(f"{API_URL}/librarian/books/category/{selected_category}")
    else:
        response = requests.get(f"{API_URL}/librarian/books")
    
    return response.json() if response.status_code == 200 else []

# Load initial books in tab1
# Load initial books in tab1
with tab1:
    st.header("Search Books")
    
    # Initialize session state for filtered books
    if "filtered_books" not in st.session_state:
        st.session_state.filtered_books = []

    # Dropdown for search type
    search_type = st.selectbox("Search by", ["title", "author", "course"], key="search_type")  # Renamed "category" to "course"

    # Search input and course filter
    if search_type in ["title", "author"]:
        search_query = st.text_input("Search", "")
        search_button = st.button("Search")
        
        # Update filtered_books based on search query
        if search_button:
            all_books = fetch_books_by_category(None)  # Fetch all books
            st.session_state.filtered_books = [
                book for book in all_books if search_query.lower() in book[search_type].lower()
            ]
    elif search_type == "course":  # Renamed "category" to "course" here as well
        # Fetch categories (courses) directly for dropdown
        response = requests.get(f"{API_URL}/librarian/categories")
        categories = response.json() if response.status_code == 200 else []
        categories.insert(0, "Select")  # Add 'Select' as default

        selected_course = st.selectbox("Select Course", categories, key="course_select")  # Renamed "category" to "course" in UI
        
        # Fetch books by selected course (category)
        if selected_course != "Select":
            st.session_state.filtered_books = fetch_books_by_category(selected_course)
    
    # Display results
    st.subheader(f"Books in {selected_course}" if search_type == "course" and selected_course != "Select" else "Search Results")
    if st.session_state.filtered_books:
        for book in st.session_state.filtered_books[:5]:  # Show top 5 results
            with st.expander(f"{book['title']} by {book['author']}"):
                st.write(f"**Title:** {book['title']}")
                st.write(f"**Author:** {book['author']}")
                st.write(f"**Available Copies:** {book['quantity']}")
                if st.button("Request Book", key=f"search_req_{book['book_id']}"):
                    response = requests.post(
                        f"{API_URL}/student/request-book",
                        json={"book_id": book['book_id'], "student_username": username}
                    )
                    if response.status_code == 200:
                        st.success("Request submitted successfully!")
                    else:
                        st.error("Failed to submit request.")
    else:
        st.info("No books found matching your search.")
# My Requests Tab
with tab2:
    st.header("My Requests")
    response = requests.get(f"{API_URL}/student/my-requests/{username}")
    if response.status_code == 200:
        requests_data = response.json()
        if requests_data:
            for req in requests_data:
                with st.expander(f"{req['title']} by {req['author']}"):
                    st.write(f"Status: {req.get('status', 'Unknown')}")
                    st.write(f"Requested on: {req.get('request_date', 'Unknown')}")
                    if req.get('response_date'):
                        st.write(f"Processed on: {req['response_date']}")
                    if req.get('status', '').lower() == 'approved':
                        book_filename = "sample_book.pdf"
                        book_path = os.path.join('static', 'books', book_filename)
                        button_key = f"download_btn_{req.get('request_id')}"
                        if os.path.exists(book_path):
                            with open(book_path, "rb") as file:
                                st.download_button("Download Ebook", data=file, file_name=book_filename, mime="application/pdf",key=button_key)
                        else:
                            st.error("Ebook file not found.")
        else:
            st.info("You haven't made any requests yet.")
    else:
        st.error("Failed to fetch requests.")
