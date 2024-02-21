import streamlit as st
from signup_page import signup_page
from login_page import login_page
from visualization_page import visualization_page

def main():
    st.sidebar.title('Navigation')
    page = st.sidebar.radio('Go to', ['Signup', 'Login', 'Visualization'])

    st.session_state.logged_in = st.session_state.get('logged_in', False)

    if page == 'Signup':
        signup_page()
    elif page == 'Login':
        login_successful = login_page()
        if login_successful:
            st.session_state.page = 'Visualization'  # Redirect to visualization page
    elif page == 'Visualization':
        if not st.session_state.logged_in:
            st.warning("You must log in to access this page.")
            return
        visualization_page()

if __name__ == '__main__':
    main()
