import streamlit as st
import sqlite3

def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE, interventions TEXT, constraints TEXT)''')
    conn.commit()
    conn.close()

def insert_user(name, interventions, constraints):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''INSERT INTO users (name, interventions, constraints) VALUES (?, ?, ?)''', (name, interventions, constraints))
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
    st.title('Signup')
    name = st.text_input('Name')

    st.subheader('Choose interventions:')
    music = st.checkbox('Music')
    breathing_exercise = st.checkbox('Breathing Exercise')
    meditation = st.checkbox('Meditation')

    custom_intervention = st.text_input('Or add a custom intervention:')
    interventions = []  
    if st.button('Add intervention'):
        if music:
            interventions.append('Music')
        if breathing_exercise:
            interventions.append('Breathing Exercise')
        if meditation:
            interventions.append('Meditation')
        if custom_intervention:
            interventions.append(custom_intervention)

    st.subheader('Choose constraints:')
    weekends = st.checkbox('Weekends')
    sunny_day = st.checkbox('Sunny Day')
    rainy_day = st.checkbox('Rainy Day')

    custom_constraint = st.text_input('Or add a custom constraint:')
    constraints = []  
    if st.button('Add constraint'):
        if weekends:
            constraints.append('Weekends')
        if sunny_day:
            constraints.append('Sunny Day')
        if rainy_day:
            constraints.append('Rainy Day')
        if custom_constraint:
            constraints.append(custom_constraint)

    if st.button('Signup'):
        if not is_name_exists(name):
            insert_user(name, ", ".join(interventions), ", ".join(constraints))
            st.success("Signup successful. Please login.")
        else:
            st.warning("Name already exists. Please choose a different one.")

if __name__ == '__main__':
    signup_page()
