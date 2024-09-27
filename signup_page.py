import streamlit as st
import sqlite3

def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE, interventions TEXT, constraints TEXT, events TEXT)''')
    conn.commit()
    conn.close()

def create_custom_database(var_name = "events"):
    # Connect to events.db
    conn = sqlite3.connect(f'{var_name}.db')
    c = conn.cursor()

    # Enable foreign key constraint support
    c.execute('PRAGMA foreign_keys = ON;')

    # Create the events table with a foreign key reference to users.name
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {var_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            start_time INTEGER,
            end_time INTEGER,
            {var_name} TEXT,
            FOREIGN KEY(name) REFERENCES users(name) ON DELETE NO ACTION ON UPDATE NO ACTION
        )
    ''')

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()


def insert_user(name, interventions, constraints, events = ""):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''INSERT INTO users (name, interventions, constraints, events) VALUES (?, ?, ?, ?)''', (name, interventions, constraints, events))
    conn.commit()
    conn.close()

def is_name_exists(name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM users WHERE name = ?''', (name,))
    result = c.fetchone()
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

    if st.button('Signup'):
        if not is_name_exists(name):
            insert_user(name, "|||".join(interventions), "|||".join(constraints), "|||".join(events))
            st.success("Signup successful. Please login.")
        else:
            st.warning("Name already exists. Please choose a different one.")

if __name__ == '__main__':
    signup_page()
