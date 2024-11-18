import streamlit as st
import pandas as pd
import altair as alt
from sql_utils import *
from plot_utils import *

var_dict = {
    "stress": "stressLevel",
    "daily_heart_rate": "beatsPerMinute",
    "respiration": "breathsPerMinute"
}

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


def add_annotations(table_name):
    # Connect to the RDS database
    conn = get_rds_connection()
    
    # Query the specified table for the logged-in user's data
    query = f"SELECT * FROM {table_name} WHERE name = %s"
    annotations_df = pd.read_sql_query(query, conn, params=(st.session_state.user,))
    
    # Close the connection
    conn.close()

    # Convert start and end times to datetime format
    annotations_df['start_time'] = pd.to_datetime(annotations_df['start_time'], unit="ms")
    annotations_df['end_time'] = pd.to_datetime(annotations_df['end_time'], unit="ms")

    # Define color schemes for different tables
    color_scheme = {
        'events': 'reds',
        'interventions': 'blues',
        # Add more tables and their respective color schemes as needed
    }

    # Use the color scheme corresponding to the current table_name
    chosen_color_scheme = color_scheme.get(table_name, 'category10') 

    # Create the annotation chart
    annotation = alt.Chart(annotations_df).mark_rect(opacity=0.25).encode(
        x='start_time:T',
        x2='end_time:T',
        color=alt.Color(f'{table_name}', legend=alt.Legend(title=table_name), scale=alt.Scale(scheme=chosen_color_scheme))
    )
    
    return annotation


def diff_plot_util(selected_var_dfname):
    options = fetch_past_options(st.session_state['user'], var_name = "interventions")
    options = [o for o in options if o is not None]
    selected_option = st.selectbox("Please select an option:", options)
    # Ask the user for an integer input
    minutes_input_before = st.text_input("How many minutes before (X) should be:", "10")
    minutes_input_after = st.text_input("How many minutes after (X) should be:", "10")
    X_before, X_after = None, None 
    if minutes_input_before and minutes_input_after:
    # Validate if the input is an integer
        if minutes_input_before:
            try:
                # Convert the input to an integer
                X_before = int(minutes_input_before)
                st.write(f"You entered {X_before} minutes.")
            except ValueError:
                st.error("Please enter a valid integer.")
        if minutes_input_before:
            try:
                # Convert the input to an integer
                X_after = int(minutes_input_after)
                st.write(f"You entered {X_after} minutes.")
            except ValueError:
                st.error("Please enter a valid integer.")
    if X_before and X_after is not None:
        mean_before, var_before, sequence_before = get_mean_and_variance(
            st.session_state.user, selected_option, selected_var_dfname, X_before, var_dict, use="before"
        )

        mean_after, var_after, sequence_after = get_mean_and_variance(
            st.session_state.user, selected_option, selected_var_dfname, X_after, var_dict, use="after"
        )
        # print(mean_before, var_before, mean_after, var_after)
        # print(sequence_before)
        if mean_before is not None and var_before is not None and mean_after is not None and var_after is not None:
            plot_diff(mean_before, var_before, mean_after, var_after)
            plot_sequences(sequence_before, sequence_after)
            ## Write a function called plot_sequences(seq_before, seq_after)
            '''
            seq_before: [[], []], inner list is the sequence of the indicator before intervention 
            seq_after: [[], []], inner list is the sequence of the indicator after intervention 
            want a plot that: 
                - have a red vertical line at x = 0
                - for x < 0: should be the sequence of indicators before intervenion (closer to intevention start time, x -> 0)
                - for x > 0: should be the sequence of indicators after intervenion (closer to intevention end time, x -> 0)
            '''

def visualization_page(annotation = False, diff_plot = False):
    st.title("Visualization Page")

    if 'submit_selection' not in st.session_state:
        st.session_state['submit_selection'] = False
    if 'other_selected' not in st.session_state:
        st.session_state['other_selected'] = False
    if 'select_time' not in st.session_state:
        st.session_state['select_time'] = False

    if 'data' not in st.session_state:
        st.session_state['dat_type'] = "Stress Level"
    
    # if "show_events" not in st.session_state:
    #     st.session_state["show_events"] = False
    # if "show_interventions" not in st.session_state:
    #     st.session_state["show_interventions"] = False

    var_options_dict = {
        "Stress Level" : "stress",
        "Heart Rate" : "daily_heart_rate",
        "Respiration Rate": "respiration"
    }
    var_options = [k for k in var_options_dict]

    selected_var = st.selectbox("Please select an option:", var_options)
    selected_var_dfname = var_options_dict[selected_var]

    df = fetch_data(selected_var, var_options_dict, st.session_state.user)
    # print(max(df["stressLevel"]))
    print(df)
        

    df['isoDate'] = pd.to_datetime(df['timestamp_cleaned'])

    # Initialize start_date, end_date, start_hour, and end_hour variables
    start_date = None
    end_date = None
    start_hour = 0
    end_hour = 23


    # Populate start_date and end_date if both datasets are available
    start_date = df['isoDate'].min()
    end_date = df['isoDate'].max()
    # print(df['timestamp_cleaned'])

    # Create a range selector for dates
    start_date = st.sidebar.date_input('Start Date', value=start_date)
    end_date = st.sidebar.date_input('End Date', value=end_date)


    print(start_date)
    # Create range slider for selecting hour ranges
    start_hour, end_hour = st.sidebar.slider("Select Hour Range", 0, 23, (start_hour, end_hour))

    # if selected is not None and len(selected["selection"]["param_1"]) > 0:
    #     start_date = pd.to_datetime(selected["selection"]["param_1"]["isoDate"][0], unit = "ms")
    #     end_date = pd.to_datetime(selected["selection"]["param_1"]["isoDate"][1], unit = "ms")
        

    start_date = pd.Timestamp(start_date).tz_localize(None)
    end_date = pd.Timestamp(end_date).tz_localize(None)
    filtered_df = df[(df['isoDate'].dt.date >= start_date.date()) &
                    (df['isoDate'].dt.date <= end_date.date()) &
                    (df['isoDate'].dt.hour >= start_hour) &
                    (df['isoDate'].dt.hour <= end_hour)]
    # if not st.session_state['select_time']:
    chart = get_plot(selected_var, filtered_df)

    if annotation:
        show_events = st.sidebar.checkbox('Show Events')
        show_interventions = st.sidebar.checkbox('Show Interventions')


        if show_events:
            # chart += add_annotations('events')
            event_annotation = add_annotations('events')
            chart = alt.layer(chart, event_annotation).resolve_scale(
                color='independent'  # Ensures separate legends for different encodings
            )

        if show_interventions:
            # chart += add_annotations('interventions')
            interventions_annotation = add_annotations('interventions')
            chart = alt.layer(chart, interventions_annotation).resolve_scale(
                color='independent'  # Ensures separate legends for different encodings
            )
        st.altair_chart(chart, use_container_width=True)
    elif diff_plot:
        diff_plot_util(selected_var_dfname)

    else:
        selection = alt.selection_interval(encodings=['x'])
        selected = None 
        chart = chart.add_selection(selection)
        selected = st.altair_chart(chart, use_container_width=True, on_select = "rerun")
        print(selected)

        


        if st.button("Enter Events"):
            st.session_state['submit_selection'] = True
        # if st.button("Select Time"):
        #     st.session_state["select_time"] = True
        
        # if st.session_state["select_time"] == True:
        #     start_date = pd.to_datetime(selected["selection"]["param_1"]["isoDate"][0], unit = "ms")
        #     print(start_date)
        #     end_date = pd.to_datetime(selected["selection"]["param_1"]["isoDate"][1], unit = "ms")
        #     filtered_df = df[(df['isoDate'].dt.date >= start_date.date()) &
        #                 (df['isoDate'].dt.date <= end_date.date()) &
        #                 (df['isoDate'].dt.hour >= start_hour) &
        #                 (df['isoDate'].dt.hour <= end_hour)]
        #     chart = get_plot(selected_var, filtered_df, selection)
        #     st.session_state["select_time"] = False
        #     st.altair_chart(chart)

        if st.session_state['submit_selection']:
            # Display the dropdown box immediately without the form so that we can capture changes in real-time
            st.write("You've selected a region! Please answer some questions.")

            choice = st.radio("Select an option:", ('Events', 'Interventions'))
            if selected is not None and len(selected["selection"]["param_1"]) > 0:
                if choice == 'Events':
                    questionaire(selected, var_name="events")
                elif choice == 'Interventions':
                    questionaire(selected, var_name="interventions")

            # questionaire(selected, var_name = "events")
        

if __name__ == '__main__':
    visualization_page()
