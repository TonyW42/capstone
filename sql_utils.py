import sqlite3
import pandas as pd
import numpy as np

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


def get_mean_and_variance(user, intervention, var, X, var_dict, db_path="users.db", use = "before"):
    """
    This function selects data from the database based on the user's name and the intervention.
    Then, it queries for var_dict[var] values that occurred between start_time and X minutes before each start_time.
    It aggregates these values into a list and returns the mean and variance.

    Args:
        intervention (str): The intervention to filter in the interventions table.
        var (str): The variable to query in the dynamically generated table.
        X (int): Number of minutes to look back from the start_time.
        var_dict (dict): Dictionary containing variable mappings.
        db_path (str): The path to the SQLite database (default is "users.db").

    Returns:
        mean (float): The mean of the selected variables.
        variance (float): The variance of the selected variables.
    """
    # Convert X minutes to milliseconds
    X_ms = X * 60 * 1000  # X minutes in milliseconds

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the logged-in user's name

    # Query the interventions table to get all start_times for the given user and intervention
    ## NOTE: start or end time of intervention? 
    cursor.execute(f"""
        SELECT start_time
        FROM interventions
        WHERE name = ?
        AND interventions = ?
    """, (user, intervention))

    start_times = cursor.fetchall()  # List of tuples [(start_time_1,), (start_time_2,), ...]

    if not start_times:
        conn.close()
        return None, None  # If no start_times were found, return None for both mean and variance

    selected_values = []

    # Loop over each start_time
    for start_time_tuple in start_times:
        start_time = start_time_tuple[0]  # Extract from tuple (in ms)

        # Calculate the time X minutes before start_time in milliseconds
        if use == "before":
            time_before = start_time - X_ms
            arg_sql = (time_before, start_time)
        if use == "after":
            time_after = start_time + X_ms
            arg_sql = (start_time, time_after)


        # Query the user-specific table to get the variable value where unix_timestamp_cleaned is between start_time and time_before
        cursor.execute(f"""
            SELECT {var_dict[var]}
            FROM {user}_{var}
            WHERE unix_timestamp_cleaned BETWEEN ? AND ?
        """, arg_sql)

        # Fetch all matching rows
        rows = cursor.fetchall()

        # Append all values from the query to the selected_values list
        selected_values.extend([row[0] for row in rows])

    conn.close()  # Close the database connection

    # If there are no selected values, return None
    if not selected_values:
        return None, None

    # Calculate the mean and variance using numpy
    mean = np.mean(selected_values)
    variance = np.var(selected_values)

    return mean, variance


if __name__ == "__main__":
    var_dict = {
        "Stress Level" : "stress",
        "Heart Rate" : "daily_heart_rate",
    }
    df = fetch_data("Stress Level", var_dict, "zw")
    print(df)