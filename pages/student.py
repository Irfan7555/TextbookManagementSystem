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
    
    # Apply the CSS to the main content area
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
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

tab1, tab2 = st.tabs(["Available Books", "My Requests"])

with tab1:
    st.header("Available Books")
    
    # Get all books
    response = requests.get(f"{API_URL}/librarian/books")
    if response.status_code == 200:
        books = response.json()
        # Filter only available books
        available_books = [book for book in books if book['quantity'] > 0]
        
        # Create a search box with a search button in a container for better alignment
        search_container = st.container()
        with search_container:
            col1, col2, col3 = st.columns([3, 1, 2])
            with col1:
                search_query = st.text_input("Search books by title or author", key="search_box")
            with col1:
                search_button = st.button("Search")
        
        # Initialize session state for search and selected book if they don't exist
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""
        if 'selected_book_data' not in st.session_state:
            st.session_state.selected_book_data = None
        
        # Update search query when button is clicked or enter is pressed
        if search_button or search_query != st.session_state.search_query:
            st.session_state.search_query = search_query
        
        # Filter books based on search query
        if st.session_state.search_query:
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
            
            # Create dropdown menu
            selected_book = st.selectbox(
                "Choose a book to request:",
                options=book_options
            )
            
            # If a book is selected (not the default "Select a book" option)
            if selected_book != "Select a book":
                # Find the selected book's details
                st.session_state.selected_book_data = next(
                    book for book in filtered_books
                    if f"{book['title']} by {book['author']}" == selected_book
                )
            
            # Display search results if search was performed
            if st.session_state.search_query and filtered_books:
                st.markdown("### Search Results")
                for book in filtered_books[:3]:  # Show top 3 results
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
            
            # Display selected book details if any
            if st.session_state.selected_book_data:
                st.markdown("---")
                st.markdown("### Book Details")
                st.write(f"**Title:** {st.session_state.selected_book_data['title']}")
                st.write(f"**Author:** {st.session_state.selected_book_data['author']}")
                st.write(f"**Available copies:** {st.session_state.selected_book_data['quantity']}")
                
                # Request button for selected book
                if st.button("Request Selected Book"):
                    response = requests.post(
                        f"{API_URL}/student/request-book",
                        json={
                            "book_id": st.session_state.selected_book_data['book_id'],
                            # "student_username": username
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
    
    if username:  # Only make the request if we have a username
        response = requests.get(f"{API_URL}/student/my-requests/{username}")
        if response.status_code == 200:
            requests_data = response.json()
            if requests_data:
                for req in requests_data:
                    st.write(f"**{req['title']}** by {req['author']}")
                    st.write(f"Status: {req['status']}")
                    st.write(f"Requested on: {req['request_date']}")
                    if req['response_date']:
                        st.write(f"Processed on: {req['response_date']}")
                    st.divider()
            else:
                st.info("You haven't made any requests yet.")
    else:
        st.error("Session error. Please login again.")