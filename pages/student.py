import streamlit as st
import requests
import pandas as pd
import base64
import os


if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first")
    st.switch_page("app.py")

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

if os.path.exists("static/bg2.jpg"):
    # Load and encode the background image
    bg_image = base64.b64encode(open("static/bg2.jpg", "rb").read()).decode()
    
    # Apply the CSS to both main content area and header using a single selector
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stAppHeader {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)),
        url("data:image/jpg;base64,{bg_image}");
        background-size: 100%;  /* Adjust this to control the size */
    }}
    </style>
    """, unsafe_allow_html=True)

API_URL = "http://localhost:8000"

st.title("Student Dashboard")

# Get username from session state
username = st.session_state.username

# Display welcome message
st.write(f"Welcome, {username}!")

tab1, tab2 = st.tabs(["Books", "My Requests"])

def get_categories():
    """Fetch all categories from the API"""
    response = requests.get(f"{API_URL}/librarian/categories")
    if response.status_code == 200:
        return response.json()
    return []

with tab1:
    st.header("Search Books")
    
    # Get all books
    response = requests.get(f"{API_URL}/librarian/books")
    if response.status_code == 200:
        books = response.json()
        # Filter only available books
        available_books = [book for book in books if book['quantity'] > 0]
        
        # Create a search box with a search button in a container for better alignment
        col1, col2 = st.columns([1, 2])
    search_container = st.container()

    with search_container:
        if "search_type" not in st.session_state:
            st.session_state.search_type = "title"
            
        with col1:
            st.session_state.search_type = st.selectbox("Search by", ["title", "author", "category"])
            search_button = st.button("Search")
            
        with col2:
            if st.session_state.search_type == "category":
                categories = get_categories()
                selected_category = st.selectbox("Select a category", categories, index=0)
                st.session_state.selected_category = selected_category
                search_query = ""  # Define search_query as an empty string in case of category search
            else:
                search_query = st.text_input("", value="")

            if 'search_query' not in st.session_state:
                st.session_state.search_query = ""
            if 'selected_book_data' not in st.session_state:
                st.session_state.selected_book_data = None

            if search_button or (search_query and search_query != st.session_state.search_query):
                st.session_state.search_query = search_query

            if st.session_state.search_type == "category" and st.session_state.selected_category:
                filtered_books = [
                    book for book in available_books
                    if book['category'] == st.session_state.selected_category
                ]

            elif st.session_state.search_query:
                filtered_books = [
                    book for book in available_books
                    if st.session_state.search_query.lower() in book['title'].lower() or 
                    st.session_state.search_query.lower() in book['author'].lower()
                ]
            
            else:
                filtered_books = available_books        
        # Create book options for dropdown
        book_options = [f"{book['title']} by {book['author']}" for book in filtered_books]

        if filtered_books:
            # Add a "Select a book" option at the beginning
            book_options.insert(0, "Select a book")
            
            
            
        # Display search results if search was performed
        if st.session_state.search_query and filtered_books:
            st.markdown("### Search Results")
            for book in filtered_books[:5]:  # Show top 3 results
                with st.expander(f"{book['title']} by {book['author']}"):
                    st.write(f"**Title:** {book['title']}")
                    st.write(f"**Author:** {book['author']}")
                    st.write(f"**Available copies:** {book['quantity']}")
                    if st.button("Request Book", key=f"search_req_{book['book_id']}"):
                        response = requests.post(
                            f"{API_URL}/student/request-book",
                            json={
                                "book_id": book['book_id'],
                                "student_username": username
                            }
                        )
                        if response.status_code == 200:
                            st.success("Request submitted successfully!")
                        else:
                            st.error("Failed to submit request.")
            
                
                
        else:
            st.info("No books found matching your search.")

with tab2:
    st.header("My Requests")
    
    if username:
        try:
            response = requests.get(f"{API_URL}/student/my-requests/{username}")
            if response.status_code == 200:
                requests_data = response.json()
                if requests_data:
                    for idx, req in enumerate(requests_data):
                        if isinstance(req, dict) and 'title' in req and 'author' in req:
                            with st.expander(f"**{req['title']}** by {req['author']}"):
                                st.write(f"Status: {req.get('status', 'Unknown')}")
                                st.write(f"Requested on: {req.get('request_date', 'Unknown')}")
                                if req.get('response_date'):
                                    st.write(f"Processed on: {req['response_date']}")
                                
                                # Show download button if request is approved
                                if req.get('status', '').lower() == 'approved':
                                    book_filename = "sample_book.pdf"
                                    book_path = os.path.join('static', 'books', book_filename)
                                    
                                    if os.path.exists(book_path):
                                        with open(book_path, "rb") as file:
                                            # Create unique key using request ID or index
                                            button_key = f"download_btn_{req.get('request_id', idx)}"
                                            btn = st.download_button(
                                                label="Download Ebook",
                                                data=file,
                                                file_name=book_filename,
                                                mime="application/pdf",
                                                key=button_key  # Add unique key here
                                            )
                                    else:
                                        st.error("Ebook file not found. Please contact administrator.")
                                st.divider()
                else:
                    st.info("You haven't made any requests yet.")
            else:
                st.error(f"Failed to fetch requests. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching requests: {str(e)}")
    else:
        st.error("Session error. Please login again.")