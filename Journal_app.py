import streamlit as st
from time import sleep
from navigation import make_sidebar

st.set_page_config(page_title="Trading Dashboard", layout="centered")

make_sidebar()

st.title("Welcome to Your Trading Journal")

st.write("Please log in to continue (username `admin`, password `admin`).")

# Create a form for login
with st.form(key="login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Form submission button
    submit_button = st.form_submit_button(label="Log in")

    if submit_button:
        if username == "admin" and password == "admin":
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            sleep(0.5)
            st.switch_page("pages/Journal.py")
        else:
            st.error("Incorrect username or password")