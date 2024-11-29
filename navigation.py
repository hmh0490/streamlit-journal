import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages

# Identify the name of the currently active page
def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]

# Render a custom sidebar with navigation logic and control access based on authentication
def make_sidebar():
    with st.sidebar:
        st.title("📑 Trading Journal")
        st.write("")
        st.write("")

        if st.session_state.get("logged_in", False):
            st.page_link("pages/Journal.py", label="Journal", icon="📘")
            st.page_link("pages/Calendar.py", label="Calendar",  icon="🗓️")
            st.page_link("pages/Dashboard.py", label="Dashboard",  icon="📊")
            st.page_link("pages/Reporting.py", label="Reporting", icon="📈")

            st.write("")
            st.write("")

            if st.button("Log out"):
                logout()

        elif get_current_page_name() != "Journal_app":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("Journal_app.py")

# Log out by resetting the logged_in session state and redirect to the login page
def logout():
    st.session_state.logged_in = False
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("Journal_app.py")