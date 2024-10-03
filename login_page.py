import streamlit as st
import sqlite3
from data_utils import update_database
import os

def authenticate_user(name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM users WHERE name = ?''', (name,))
    result = c.fetchone()
    conn.close()
    return result

def login_page():
    st.title('Login')
    name = st.text_input('Name')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "apcomp297-84a78a17c7a6.json" 

    if st.button('Login'):
        user = authenticate_user(name)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user[1]  # Save the logged-in user's name
            update_database()
            return True  # Indicate successful login
        else:
            st.error("Invalid name. Please try again.")
            return False  # Indicate unsuccessful login

    return False  # Default: indicate unsuccessful login

if __name__ == '__main__':
    login_page()
