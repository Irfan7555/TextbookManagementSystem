
import streamlit as st
import pandas as pd
from PIL import Image
import os

# Hide default Streamlit menu
hide_css = """
    <style>
    .st-emotion-cache-j7qwjs.eczjsme15{
        display: none;
    } 
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .main > div {
        padding: 2rem;
    }
    div[data-testid="stImage"] {
        width: 400px;
        height: 400px;
        display: grid;
        justify-content: center;
        align-items: center;
        min-height: 400px;
    }
    div[data-testid="stImage"] img {
        max-width: 400px;
        max-height: 400px;
        object-fit: contain;
    }
   
    .stButton {
        width: 100%;
    }
    .role-btn {
        width: 100%;
        padding: 0.5rem;
        border: none;
        border-radius: 8px;
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #dddddd;
        cursor: pointer;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .role-btn.selected {
        background-color: #ff4b4b;
        color: white;
        border: none;
    }
    /* Center the form content */
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        margin: 0 auto;
    }
    /* Make the sign-in form more compact */
    div[data-testid="stVerticalBlock"] > div {
        padding-bottom: 0.5rem;
    }
    </style>
"""

st.markdown(hide_css, unsafe_allow_html=True)

# Hardcoded user data (in practice, this would be loaded from Excel)

def load_user_data():
    """Load user data from Excel file"""
    try:
        # Read the Excel file
        df = pd.read_excel('users.xlsx')
        
        # Convert DataFrame to dictionary format
        users = {}
        for _, row in df.iterrows():
            users[row['username']] = {
                'password': row['password'],
                'role': row['role'],
                'student_id': row['student_id'] if pd.notna(row['student_id']) else None
            }
        return users
    except Exception as e:
        st.error(f"Error loading user data: {str(e)}")
        return {}

def login():
    st.title("Textbook Management System")
    
    # Create two-column layout with more space for the image
    col1, col2 = st.columns([3,4])
    
    with col1:
        if os.path.exists("static/pmu1.png"):
            st.image("static/pmu1.png", use_column_width=True)
    
    with col2:
        st.subheader("Sign In")
        
        # Initialize selected role in session state if not present
        if 'selected_role' not in st.session_state:
            st.session_state.selected_role = 'Student'
        
        # Create three columns for role buttons with proper spacing
        role_col1, role_col2, role_col3 = st.columns(3)
        
        # Role selection buttons
        with role_col1:
            if st.button("👨‍🎓\nStudent", key="student_btn", 
                        type="primary" if st.session_state.selected_role == "Student" else "secondary"):
                st.session_state.selected_role = "Student"
                st.rerun()
                
        with role_col2:
            if st.button("📚\nLibrarian", key="librarian_btn",
                        type="primary" if st.session_state.selected_role == "Librarian" else "secondary"):
                st.session_state.selected_role = "Librarian"
                st.rerun()
                
        with role_col3:
            if st.button("⚙️\nAdmin", key="admin_btn",
                        type="primary" if st.session_state.selected_role == "Admin" else "secondary"):
                st.session_state.selected_role = "Admin"
                st.rerun()
        
        # Add some space after buttons
        st.write("")
        
        # Login form
        username = st.text_input("Username")
        
        # Show student ID field only for students
        student_id = None
        if st.session_state.selected_role == 'Student':
            student_id = st.text_input("Student ID")
        
        password = st.text_input("Password", type="password")
        
        # Add some space before sign in button
        st.write("")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            # Load user data from Excel
            users = load_user_data()
            
            # Debug print
            st.write(f"Selected role: {st.session_state.selected_role}")
            
            if username in users:
                user_data = users[username]
                # Debug print
                # st.write(f"Found user: {user_data}")
                
                if user_data['password'] == password and user_data['role'] == st.session_state.selected_role:
                    # Additional check for student ID if role is Student
                    if st.session_state.selected_role == 'Student':
                        if user_data['student_id'] == student_id:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.role = user_data['role']
                            st.success(f"Welcome, {username}! You are logged in as {user_data['role']}.")
                            
                            # Redirect based on role
                            if st.session_state.role == 'Student':
                                st.switch_page("pages/student.py")
                            elif st.session_state.role == 'Librarian':
                                st.switch_page("pages/librarian.py")
                            elif st.session_state.role == 'Admin':
                                st.switch_page("pages/admin.py")
                        else:
                            st.error("Invalid Student ID!")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = user_data['role']
                        st.success(f"Welcome, {username}! You are logged in as {user_data['role']}.")
                        
                        # Redirect based on role
                        if st.session_state.role == 'Student':
                            st.switch_page("pages/student.py")
                        elif st.session_state.role == 'Librarian':
                            st.switch_page("pages/librarian.py")
                        elif st.session_state.role == 'Admin':
                            st.switch_page("pages/admin.py")
                else:
                    if user_data['role'] != st.session_state.selected_role:
                        st.error("Selected role doesn't match your account type!")
                    else:
                        st.error("Invalid password!")
            else:
                st.error("Username not found!")

def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    
    login()

if __name__ == "__main__":
    main()