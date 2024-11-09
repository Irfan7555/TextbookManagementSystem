import streamlit as st
import requests, os, base64
import pandas as pd

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



if os.path.exists("static/bg4.jpg"):
    # Load and encode the background image
    bg_image = base64.b64encode(open("static/bg4.jpg", "rb").read()).decode()
    
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

st.title("Admin Dashboard")

# Get pending requests
response = requests.get(f"{API_URL}/admin/pending-requests")
if response.status_code == 200:
    pending_requests = response.json()
    
    if pending_requests:
        st.header("Pending Book Requests")
        for req in pending_requests:
            with st.expander("All Requests") as expander:
                st.write(f"Book: **{req['title']}** by {req['author']}")
                st.write(f"Student: {req.get('student_username', 'N/A')}") 
                st.write(f"Requested on: {req['request_date']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve", key=f"app_{req['request_id']}"):
                        response = requests.put(
                            f"{API_URL}/admin/process-request/{req['request_id']}",
                            params={"status": "approved"}
                        )
                        if response.status_code == 200:
                            st.success("Request approved!")
                            st.rerun()
                        else:
                            st.error("Failed to approve request.")
                
                with col2:
                    if st.button("Reject", key=f"rej_{req['request_id']}"):
                        response = requests.put(
                            f"{API_URL}/admin/process-request/{req['request_id']}",
                            params={"status": "rejected"}
                        )
                        if response.status_code == 200:
                            st.success("Request rejected!")
                            st.rerun()
                        else:
                            st.error("Failed to reject request.")
    else:
        st.info("No pending requests.")