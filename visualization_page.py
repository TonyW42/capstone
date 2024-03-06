import streamlit as st
import pandas as pd
import altair as alt

def visualization_page():
    st.title("Visualization Page")

    # Upload both CSV files
    uploaded_files = st.file_uploader("Upload Stress and Heart Rate Data CSV", type=["csv"], accept_multiple_files=True)

    stress_df = None
    hr_df = None

    for uploaded_file in uploaded_files:
        header_length = 5
        df = pd.read_csv(uploaded_file, skiprows=header_length)
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
                    )
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
                    )
                    chart = hr_chart if chart is None else chart + hr_chart

                if chart is not None:
                    st.altair_chart(chart, use_container_width=True)

if __name__ == '__main__':
    visualization_page()
