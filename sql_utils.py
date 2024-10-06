import sqlite3
import pandas as pd

def fetch_past_options(user_name, var_name = "events"):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Example SQL query to fetch user options based on the user's name
    cursor.execute(f"SELECT DISTINCT {var_name} FROM users WHERE name = ?", (user_name,))
    past_responses = cursor.fetchall()

    conn.close()

    # Convert the results into a flat list of strings
    options = past_responses[0][0].split("|||")
    # options = [response[0] for response in past_responses]
    # print(options)
    return options


def save_other_response(user_name, response, var_name = "events"):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT DISTINCT {var_name} FROM users WHERE name = ?", (user_name,))
    past_responses = cursor.fetchall()

    # Convert the results into a flat list of strings
    options = past_responses[0][0].split("|||")
    options.append(response)
    new_options = "|||".join(options)

    # Insert the new response into the user_responses table linked to the user's name
    cursor.execute(f"UPDATE users SET {var_name} = ? WHERE name = ?", (new_options, user_name))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def record_event_in_database(user, start_time, end_time, event_type, var_name):
    # Connect to events.db
    conn = sqlite3.connect(f'users.db')
    c = conn.cursor()

    # Insert the event details into the events table
    c.execute(f'''
        INSERT INTO {var_name} (name, start_time, end_time, {var_name})
        VALUES (?, ?, ?, ?)
    ''', (user, start_time, end_time, event_type))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def fetch_data(var, var_dict, user_name):
    '''
    var: str:
    var_dict: dict : str -> str
    open users.db
    select * from var_dict[var] where name == user_name
    return the selected data as a pandas dataframe with name aligned
    '''
    
    # Ensure the variable exists in the dictionary
    if var not in var_dict:
        raise ValueError(f"Variable '{var}' not found in var_dict.")
    
    # Get the table name from var_dict
    table_name = f"{user_name}_{var_dict[var]}"
    
    # Open connection to the SQLite database
    conn = sqlite3.connect('users.db')
    
    # SQL query to select data based on user name
    query = f"SELECT * FROM {table_name}"
    
    # Execute the query and load data into a pandas dataframe
    df = pd.read_sql_query(query, conn)
    
    # Close the connection
    conn.close()
    
    return df

def labfront_name_to_username():
    '''
    open users.db 
    select name, labfront_name from users
    return a dict d such that d[labfront_name] = name
    '''
    
    # Open connection to the SQLite database
    conn = sqlite3.connect('users.db')
    
    # SQL query to fetch name and labfront_name from users table
    query = "SELECT name, labfront_name FROM users"
    
    # Execute the query and fetch all results
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Close the connection
    conn.close()
    
    # Create a dictionary where labfront_name is the key and name is the value
    labfront_dict = {labfront_name: name for name, labfront_name in rows}
    
    return labfront_dict

if __name__ == "__main__":
    var_dict = {
        "Stress Level" : "stress",
        "Heart Rate" : "daily_heart_rate",
    }
    df = fetch_data("Stress Level", var_dict, "zw")
    print(df)