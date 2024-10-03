import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import os
import io
from google.cloud import storage
from vega_datasets import data

# Function to directly read CSV from GCS
def read_csv_from_gcs(bucket_name, file_name):
    """Reads a CSV file directly from a GCS bucket and loads it into a Pandas DataFrame."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    # Download the content of the file as a string and convert it to bytes
    csv_data = blob.download_as_text()
    #csv_data = blob.download_as_bytes()
    #loaded_file = io.BytesIO(csv_data)

    # Use io.StringIO to load the data into a pandas DataFrame
    data = io.StringIO(csv_data)
    df = pd.read_csv(data)
    
    return df


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


def questionaire(selected, var_name = "events"):
    # Display the dropdown box immediately without the form so that we can capture changes in real-time
    
    # options = ["Option 1", "Option 2", "Option 3", "Other (please specify)"]
    options = fetch_past_options(st.session_state['user'], var_name = var_name)
    options.append("Other (please specify)")
    options = [o for o in options if o is not None]
    selected_option = st.selectbox("Please select an option:", options)
    
    # Check if the user selects "Other"
    if selected_option == "Other (please specify)":
        st.session_state['other_selected'] = True
    else:
        st.session_state['other_selected'] = False
    
    # If "Other" is selected, show the text input box
    if st.session_state['other_selected']:
        other_response = st.text_input("Please specify:")
    else:
        other_response = selected_option

    start_time = selected["selection"]["param_1"]["isoDate"][0]
    end_time = selected["selection"]["param_1"]["isoDate"][1]
    # Use a form for submission
    with st.form("user_response_form"):
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.session_state['submit_selection'] = False  # Reset selection state after submitting
            st.write("Response submitted:", other_response)
            if st.session_state['other_selected']:
                save_other_response(st.session_state['user'], other_response, var_name = var_name)
            record_event_in_database(st.session_state['user'], start_time, end_time, other_response, var_name = var_name)



def visualization_page():
    st.title("Visualization Page")

    if 'submit_selection' not in st.session_state:
        st.session_state['submit_selection'] = False
    if 'other_selected' not in st.session_state:
        st.session_state['other_selected'] = False

    if 'data' not in st.session_state:
        st.session_state['data'] = None

    # Creating a hyperlink to GCP
    st.markdown("[Access the Google Cloud Bucket](https://console.cloud.google.com/storage/browser?project=apcomp297&prefix=&forceOnBucketsSortingFiltering=true)", unsafe_allow_html=True)
    # Set the path to your sevice account key
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "apcomp297-84a78a17c7a6.json" #replace with your path to the .json credential file
    # Allow the user to input bucke name, subfolder, and file name
    bucket_name = st.text_input("Enter GCP Bucket Name", value="physiological-data")
    subfolder = st.text_input("Enter GCP Subfolder (optional)", value='raw/')
    file_name = st.text_input("Enter CSV File Name (with extension)", value="mock_data.csv")
    #Combine subfolder and file name to create the full file path
    full_file_path  = f"{subfolder}{file_name}" if subfolder else file_name

    if st.button("Load CSV"):
        try:
            # Load the CSV directly from GCS
            st.info(f"Loading {file_name} from bucket {bucket_name}...")
            df_t = read_csv_from_gcs(bucket_name, full_file_path)
            st.success(f"Successfully loaded {file_name}")
            #Display CSV content
            st.dataframe(df_t)
            st.session_state['data'] = df_t

        except Exception as e:
            st.error(f"Error: {str(e)}")


    stress_df = None
    hr_df = None


    df = st.session_state['data']
    # assert df is not None 
    # Dropdown selectors to choose which columns on the Y-axis to plot
    x_axis = x_axis = df.columns[0]
    y_axis_options = df.columns[1:]
    y_axis = st.selectbox('Select the column for the Y-axis', options=y_axis_options)

    # Plot using Altair
    if x_axis and y_axis:
        chart = alt.Chart(df).mark_line().encode(
            x=x_axis,
            y=y_axis,
            tooltip=[x_axis, y_axis]
        ).properties(
            title=f'{y_axis} vs {x_axis}'
        )

        # Display the chart
        st.altair_chart(chart, use_container_width=True)
        
    stress_df = None
    hr_df = None

    df['isoDate'] = pd.to_datetime(df['isoDate'])

    if 'stressLevel' in df.columns:
        stress_df = df
    elif 'beatsPerMinute' in df.columns:
        hr_df = df
    # Initialize start_date, end_date, start_hour, and end_hour variables
    start_date = None
    end_date = None
    start_hour = 0
    end_hour = 23


    # Populate start_date and end_date if both datasets are available
    if stress_df is not None and hr_df is not None:
        start_date = min(stress_df['isoDate'].min(), hr_df['isoDate'].min())
        end_date = max(stress_df['isoDate'].max(), hr_df['isoDate'].max())
    elif stress_df is not None:
        start_date = stress_df['isoDate'].min()
        end_date = stress_df['isoDate'].max()
    elif hr_df is not None:
        start_date = hr_df['isoDate'].min()
        end_date = hr_df['isoDate'].max()

    # Create a range selector for dates
    start_date = st.sidebar.date_input('Start Date', value=start_date)
    end_date = st.sidebar.date_input('End Date', value=end_date)

    # Create range slider for selecting hour ranges
    start_hour, end_hour = st.sidebar.slider("Select Hour Range", 0, 23, (start_hour, end_hour))

    selection = alt.selection_interval(encodings=['x'])

    if stress_df is not None or hr_df is not None:
        # Filter the data based on the selected date range and hour range
        if (stress_df is not None and not stress_df.empty) or (hr_df is not None and not hr_df.empty):
            if start_date and end_date:
                start_date = pd.Timestamp(start_date).tz_localize(None)
                end_date = pd.Timestamp(end_date).tz_localize(None)
                if stress_df is not None and hr_df is not None:
                    filtered_stress_df = stress_df[(stress_df['isoDate'].dt.date >= start_date.date()) &
                                                   (stress_df['isoDate'].dt.date <= end_date.date()) &
                                                   (stress_df['isoDate'].dt.hour >= start_hour) &
                                                   (stress_df['isoDate'].dt.hour <= end_hour)]
                    filtered_hr_df = hr_df[(hr_df['isoDate'].dt.date >= start_date.date()) &
                                           (hr_df['isoDate'].dt.date <= end_date.date()) &
                                           (hr_df['isoDate'].dt.hour >= start_hour) &
                                           (hr_df['isoDate'].dt.hour <= end_hour)]
                elif stress_df is not None:
                    filtered_stress_df = stress_df[(stress_df['isoDate'].dt.date >= start_date.date()) &
                                                   (stress_df['isoDate'].dt.date <= end_date.date()) &
                                                   (stress_df['isoDate'].dt.hour >= start_hour) &
                                                   (stress_df['isoDate'].dt.hour <= end_hour)]
                    filtered_hr_df = None
                elif hr_df is not None:
                    filtered_hr_df = hr_df[(hr_df['isoDate'].dt.date >= start_date.date()) &
                                           (hr_df['isoDate'].dt.date <= end_date.date()) &
                                           (hr_df['isoDate'].dt.hour >= start_hour) &
                                           (hr_df['isoDate'].dt.hour <= end_hour)]
                    filtered_stress_df = None

                # Plot the data
                chart = None

                if filtered_stress_df is not None and not filtered_stress_df.empty:
                    stress_chart = alt.Chart(filtered_stress_df).mark_line(color='blue').encode(
                        x=alt.X('isoDate:T', axis=alt.Axis(title='Date and Time', format='%Y-%m-%d %H:%M:%S')),
                        y=alt.Y('stressLevel:Q', axis=alt.Axis(title='Stress Level')),
                        tooltip=['stressLevel:Q', alt.Tooltip('isoDate:T', format='%Y-%m-%d %H:%M:%S')]
                    ).properties(
                        width=800,
                        height=400,
                        title='Stress Level and Heart Rate over Time'
                    ).add_selection(selection)
                    chart = stress_chart

                if filtered_hr_df is not None and not filtered_hr_df.empty:
                    hr_chart = alt.Chart(filtered_hr_df).mark_line(color='red').encode(
                        x=alt.X('isoDate:T', axis=alt.Axis(title='Date and Time', format='%Y-%m-%d %H:%M:%S')),
                        y=alt.Y('beatsPerMinute:Q', axis=alt.Axis(title='Heart Rate')),
                        tooltip=['beatsPerMinute:Q', alt.Tooltip('isoDate:T', format='%Y-%m-%d %H:%M:%S')]
                    ).properties(
                        width=800,
                        height=400,
                        title='Stress Level and Heart Rate over Time'
                    ).add_selection(selection)
                    chart = hr_chart if chart is None else chart + hr_chart
                
                selected = None

                if chart is not None:
                    selected = st.altair_chart(chart, use_container_width=True, on_select = "rerun")
                # print(chart.selections.interval.values)
                    
                # print(selected)


    if st.button("Confirm Selection"):
        st.session_state['submit_selection'] = True
    print(selected)

    if st.session_state['submit_selection']:
        # Display the dropdown box immediately without the form so that we can capture changes in real-time
        st.write("You've selected a region! Please answer some questions.")

        choice = st.radio("Select an option:", ('Events', 'Interventions'))
        if selected is not None and  len(selected["selection"]["param_1"]) > 0:
            if choice == 'Events':
                questionaire(selected, var_name="events")
            elif choice == 'Interventions':
                questionaire(selected, var_name="interventions")

        # questionaire(selected, var_name = "events")
        
       


if __name__ == '__main__':
    visualization_page()
