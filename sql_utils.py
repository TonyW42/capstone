import pandas as pd
import numpy as np
import pymysql

def get_rds_connection():
    return pymysql.connect(
        host="apcomp297.chg8skogwghf.us-east-2.rds.amazonaws.com",  # Your RDS endpoint
        user="yilinw",  # Your RDS username
        password="wearable42",  # Your RDS password
        database="wearable",  # Database name on RDS
        port=3306
    )

def fetch_past_options(user_name, var_name="events"):
    conn = get_rds_connection()
    cursor = conn.cursor()

    # Fetch distinct options based on the user name from the RDS database
    cursor.execute(f"SELECT DISTINCT {var_name} FROM users WHERE name = %s", (user_name,))
    past_responses = cursor.fetchall()

    conn.close()

    # Convert the results into a flat list of strings
    if past_responses:
        options = past_responses[0][0].split("|||")  # Split on delimiter used in your database
    else:
        options = []  # Return an empty list if no responses are found

    return options


def save_other_response(user_name, response, var_name="events"):
    conn = get_rds_connection()
    cursor = conn.cursor()

    # Fetch existing responses from the specified column for the user
    cursor.execute(f"SELECT DISTINCT {var_name} FROM users WHERE name = %s", (user_name,))
    past_responses = cursor.fetchall()

    # Convert the results into a flat list of strings
    if past_responses and past_responses[0][0]:  # Check if past responses exist and are not None
        options = past_responses[0][0].split("|||")
    else:
        options = []
    options.append(response)
    new_options = "|||".join(options)

    # Update the user's response in the RDS database
    cursor.execute(f"UPDATE users SET {var_name} = %s WHERE name = %s", (new_options, user_name))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()


def record_event_in_database(user, start_time, end_time, event_type, var_name):
    # Connect to the RDS database
    conn = get_rds_connection()
    cursor = conn.cursor()

    # Insert the event details into the specified table
    cursor.execute(f'''
        INSERT INTO {var_name} (name, start_time, end_time, {var_name})
        VALUES (%s, %s, %s, %s)
    ''', (user, start_time, end_time, event_type))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()



def fetch_data(var, var_dict, user_name):
    '''
    var: str
    var_dict: dict : str -> str
    Connects to RDS database to fetch all data from the table
    corresponding to user_name and var_dict[var].
    Returns the selected data as a pandas DataFrame.
    '''
    
    # Ensure the variable exists in the dictionary
    if var not in var_dict:
        raise ValueError(f"Variable '{var}' not found in var_dict.")
    
    # Get the table name from var_dict
    table_name = f"{user_name}_{var_dict[var]}"
    
    # Open connection to the RDS database
    conn = get_rds_connection()
    
    # SQL query to select data from the specified table
    query = f"SELECT * FROM {table_name}"
    
    # Execute the query and load data into a pandas DataFrame
    df = pd.read_sql_query(query, conn)
    
    # Close the connection
    conn.close()
    
    return df

def labfront_name_to_username():
    '''
    Connects to the RDS database to select name and labfront_name from the users table.
    Returns a dictionary d such that d[labfront_name] = name.
    '''
    
    # Open connection to the RDS database
    conn = get_rds_connection()
    
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


def get_mean_and_variance(user, intervention, var, X, var_dict, use="before"):
    """
    This function selects data from the RDS database based on the user's name and the intervention.
    Then, it queries for var_dict[var] values that occurred between start_time and X minutes before each start_time.
    It aggregates these values into a list and returns the mean and variance.

    Args:
        user (str): The user's name.
        intervention (str): The intervention to filter in the interventions table.
        var (str): The variable to query in the dynamically generated table.
        X (int): Number of minutes to look back from the start_time.
        var_dict (dict): Dictionary containing variable mappings.
        use (str): Specifies whether to look "before" or "after" the start_time.

    Returns:
        mean (float): The mean of the selected variables.
        variance (float): The variance of the selected variables.
    """
    # Convert X minutes to milliseconds
    X_ms = X * 60 * 1000  # X minutes in milliseconds

    # Connect to the RDS database
    conn = get_rds_connection()
    cursor = conn.cursor()

    # Query the interventions table to get all start_times for the given user and intervention
    cursor.execute("""
        SELECT start_time
        FROM interventions
        WHERE name = %s
        AND interventions = %s
    """, (user, intervention))

    start_times = cursor.fetchall()  # List of tuples [(start_time_1,), (start_time_2,), ...]

    if not start_times:
        conn.close()
        return None, None  # If no start_times were found, return None for both mean and variance

    selected_values = []

    # Loop over each start_time
    for start_time_tuple in start_times:
        start_time = start_time_tuple[0]  # Extract from tuple (in ms)

        # Calculate the time X minutes before or after start_time in milliseconds
        if use == "before":
            time_before = start_time - X_ms
            arg_sql = (time_before, start_time)
        elif use == "after":
            time_after = start_time + X_ms
            arg_sql = (start_time, time_after)
        else:
            raise ValueError("Invalid value for 'use'. Expected 'before' or 'after'.")
        # arg_sql = (0, 1000000000000000000)

        # Query the user-specific table to get the variable value within the specified time range
        cursor.execute(f"""
            SELECT {var_dict[var]}
            FROM {user}_{var}
            WHERE unix_timestamp_cleaned BETWEEN %s AND %s
        """, arg_sql)

        # Fetch all matching rows
        rows = cursor.fetchall()
        print(arg_sql)

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