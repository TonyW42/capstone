import streamlit as st
from sql_utils import get_rds_connection

def create_database():
    # Connect to the RDS database
    conn = get_rds_connection()
    cursor = conn.cursor()

    # SQL query to create the users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            interventions TEXT,
            constraints TEXT,
            events TEXT,
            labfront_name VARCHAR(255)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def create_custom_database(var_name="events"):
    # Connect to the RDS database
    conn = get_rds_connection()
    cursor = conn.cursor()

    # Create the custom table with a foreign key reference to users.name
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {var_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            start_time BIGINT,
            end_time BIGINT,
            {var_name} TEXT,
            FOREIGN KEY(name) REFERENCES users(name) ON DELETE NO ACTION ON UPDATE NO ACTION
        )
    ''')

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()



def insert_user(name, interventions, constraints, events, labfront_name):
    # Connect to the RDS database
    conn = get_rds_connection()
    cursor = conn.cursor()

    # Insert the user into the users table
    cursor.execute('''
        INSERT INTO users (name, interventions, constraints, events, labfront_name)
        VALUES (%s, %s, %s, %s, %s)
    ''', (name, interventions, constraints, events, labfront_name))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def is_name_exists(name):
    # Connect to the RDS database
    conn = get_rds_connection()
    cursor = conn.cursor()

    # Check if a user with the given name exists
    cursor.execute('''SELECT * FROM users WHERE name = %s''', (name,))
    result = cursor.fetchone()

    # Close the connection
    conn.close()
    
    return result is not None


def signup_page():
    create_database()
    create_custom_database("events")
    create_custom_database("interventions")
    st.title('Signup')
    name = st.text_input('Name', key='name')

    st.subheader('Choose interventions:')
    music = st.checkbox('Music', key='music')
    breathing_exercise = st.checkbox('Breathing Exercise', key='breathing_exercise')
    meditation = st.checkbox('Meditation', key='meditation')
    custom_intervention = st.text_input('Or add a custom intervention:', key='custom_intervention')

    st.subheader('Choose constraints:')
    weekends = st.checkbox('Weekends', key='weekends')
    sunny_day = st.checkbox('Sunny Day', key='sunny_day')
    rainy_day = st.checkbox('Rainy Day', key='rainy_day')
    custom_constraint = st.text_input('Or add a custom constraint:', key='custom_constraint')

    st.subheader('Choose Events:')
    events_options = ["Event A", "Event B", "Event C"]
    events_st = [st.checkbox(e, key=e) for e in events_options]
    custom_event = st.text_input('Or add a custom event:', key='custom_event')

    interventions = []  
    if music:
        interventions.append('Music')
    if breathing_exercise:
        interventions.append('Breathing Exercise')
    if meditation:
        interventions.append('Meditation')
    if custom_intervention:
        interventions.append(custom_intervention)

    constraints = []  
    if weekends:
        constraints.append('Weekends')
    if sunny_day:
        constraints.append('Sunny Day')
    if rainy_day:
        constraints.append('Rainy Day')
    if custom_constraint:
        constraints.append(custom_constraint)
    
    ## newly added events 
    events = []  
    for e, e_st in zip(events_options, events_st):
        if e_st:
            events.append(e)
    if custom_event:
        events.append(custom_event)

    st.subheader('Please input your name on Labfront:')
    labfront_name = st.text_input('Input Labfront name:')


    if st.button('Signup'):
        if not is_name_exists(name):
            insert_user(name, "|||".join(interventions), "|||".join(constraints), "|||".join(events), labfront_name)
            st.success("Signup successful. Please login.")
        else:
            st.warning("Name already exists. Please choose a different one.")

if __name__ == '__main__':
    signup_page()
