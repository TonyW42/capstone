import streamlit as st
from data_utils import update_database
from sql_utils import *
from sql_utils import get_admin_name

# Authenticate user by checking against the RDS database
def authenticate_user(name):
    conn = get_rds_connection()
    c = conn.cursor()
    # Execute a query to check if the user exists
    c.execute("SELECT * FROM users WHERE name = %s", (name,))
    result = c.fetchone()
    conn.close()
    return result

# Streamlit login page function
def login_page():
    st.title('Login')
    name = st.text_input('Name')
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "apcomp297-84a78a17c7a6.json" 

    if st.button('Login'):
        user = authenticate_user(name)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user[1]  # Save the logged-in user's name
            # update_database()  # Call the database update function
            return True  # Indicate successful login
        elif name.strip() == get_admin_name():
            st.session_state.logged_in = True
            st.session_state.user = name.strip()
            return True 



        else:
            st.error("Invalid name. Please try again.")
            return False  # Indicate unsuccessful login

    return False  # Default: indicate unsuccessful login

# Main function to run the app
if __name__ == '__main__':
    login_page()