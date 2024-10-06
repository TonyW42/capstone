import streamlit as st
import pandas as pd
import altair as alt
from sql_utils import *
from plot_utils import *


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
    if 'select_time' not in st.session_state:
        st.session_state['select_time'] = False

    if 'data' not in st.session_state:
        st.session_state['dat_type'] = "Stress Level"

    var_options_dict = {
        "Stress Level" : "stress",
        "Heart Rate" : "daily_heart_rate",
        "Respiration Rate": "respiration"
    }
    var_options = [k for k in var_options_dict]

    selected_var = st.selectbox("Please select an option:", var_options)

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

    selection = alt.selection_interval(encodings=['x'])
    selected = None 
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
    chart = get_plot(selected_var, filtered_df, selection)

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
