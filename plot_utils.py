import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

def get_plot(var, df):
    print("=" * 20)
    print(var)
    print("=" * 20)
    if var == "Stress Level":
        chart = plot_stress_level(df)
    elif var == "Heart Rate":
        chart = plot_heart_rate(df)
    elif var == "Respiration Rate":
        chart = plot_respiration(df)
    return chart

# Define the color ranges based on stress levels
def get_color(stress_level):
    if 0 <= stress_level <= 25:
        return 'dodgerblue'  # Resting state
    elif 26 <= stress_level <= 50:
        return 'gold'  # Low stress
    elif 51 <= stress_level <= 75:
        return 'darkorange'  # Medium stress
    elif 76 <= stress_level <= 100:
        return 'red'  # High stress
    return 'gray'  # Default for out-of-range values


def plot_stress_level(stress: pd.DataFrame):
    '''
    Returns an Altair plot of stress levels over time with interactive zoom based on a given selection.
    '''

    # Add a column for color based on stress level
    stress['color'] = stress['stressLevel'].apply(get_color)

    # Get the minimum and maximum dates for the title
    min_date = stress['isoDate'].min()
    max_date = stress['isoDate'].max()

    # Format the dates to include in the title
    formatted_min_date = pd.to_datetime(min_date).strftime('%Y-%m-%d %H:%M')
    formatted_max_date = pd.to_datetime(max_date).strftime('%Y-%m-%d %H:%M')

    # Create the Altair chart
    chart = alt.Chart(stress).mark_rule(opacity=0.7).encode(
        x=alt.X('isoDate:T', title='Timestamp', axis=alt.Axis(format='%Y-%m-%d %H:%M', labelAngle=45)),
        y=alt.Y('stressLevel:Q', title='Stress level value'),
        color=alt.Color('color:N', legend=None)  # No color legend
    ).properties(
        width=800,
        height=400,
        title=f'Stress level values over time from {formatted_min_date} to {formatted_max_date}'
    )

    return chart  # Return the main chart



def get_hr_zone(age, current_hr):
    max_hr = 220 - age  # Max HR formula
    if (0.5 * max_hr) <= current_hr <= (0.59 * max_hr):
        return 1  # Zone 1: For warm-up and recovery
    elif (0.6 * max_hr) <= current_hr <= (0.69 * max_hr):
        return 2  # Zone 2: For aerobic and base fitness
    elif (0.7 * max_hr) <= current_hr <= (0.79 * max_hr):
        return 3  # Zone 3: For aerobic endurance
    elif (0.8 * max_hr) <= current_hr <= (0.89 * max_hr):
        return 4  # Zone 4: For anaerobic capacity
    elif (0.9 * max_hr) <= current_hr <= (max_hr + 15):  # Zone 5: For short burst speed training
        return 5
    else:
        return 0  # Default for out-of-range values

def plot_heart_rate(df: pd.DataFrame):
    '''
    Returns an Altair plot of heart rate over time with interactive zoom based on a given selection.
    '''
    
    # Define heart rate zone colors
    hr_zone_colors = {
        0: 'gray',         # Zone 0: Out of range or resting
        1: 'gray',         # Zone 1: Warm-up
        2: 'dodgerblue',   # Zone 2: Aerobic and base fitness
        3: 'green',        # Zone 3: Aerobic endurance
        4: 'orange',       # Zone 4: Anaerobic capacity
        5: 'red'           # Zone 5: Speed training
    }

    # Calculate and add heart rate zones as a new column
    df['hr_zone'] = df['beatsPerMinute'].apply(lambda hr: get_hr_zone(23, hr))

    # Add a color column based on heart rate zone
    df['color'] = df['hr_zone'].map(hr_zone_colors)

    min_date = df['isoDate'].min()
    max_date = df['isoDate'].max()

    # Format the dates to include in the title
    formatted_min_date = pd.to_datetime(min_date).strftime('%Y-%m-%d %H:%M')
    formatted_max_date = pd.to_datetime(max_date).strftime('%Y-%m-%d %H:%M')

    # Create the Altair chart
    chart = alt.Chart(df).mark_line(opacity=0.7).encode(
        x=alt.X('isoDate:T', title='Timestamp', axis=alt.Axis(format='%Y-%m-%d %H:%M', labelAngle=45)),
        y=alt.Y('beatsPerMinute:Q', title='Heart rate (bpm)'),
        # color=alt.Color('color:N', 
        #                 legend=alt.Legend(
        #                     title="Heart Rate Zones",
        #                     orient="right",
        #                     titleFontSize=12,
        #                     labelFontSize=10,
        #                     values=['gray', 'dodgerblue', 'green', 'orange', 'red'],
        #                     symbolType='line',
        #                     direction='vertical'
        #                 )
        # )  # Include color legend for heart rate zones
    ).properties(
        width=800,
        height=400,
        title=f'Heart rate (bpm) over time from {formatted_min_date} to {formatted_max_date}'
    )
    return chart  # Return the main chart with the embedded legend

def plot_respiration(respiration: pd.DataFrame):
    '''
    Returns an Altair plot of respiration rate over time with interactive zoom based on a given selection.
    '''
    
    # Get the minimum and maximum dates for the title
    min_date = respiration['isoDate'].min()
    max_date = respiration['isoDate'].max()

    # Format the dates to include in the title
    formatted_min_date = pd.to_datetime(min_date).strftime('%Y-%m-%d %H:%M')
    formatted_max_date = pd.to_datetime(max_date).strftime('%Y-%m-%d %H:%M')

    # Create the Altair chart for respiration rate
    chart = alt.Chart(respiration).mark_line(opacity=0.7).encode(
        x=alt.X('isoDate:T', title='Timestamp', axis=alt.Axis(format='%Y-%m-%d %H:%M', labelAngle=45)),
        y=alt.Y('breathsPerMinute:Q', title='Respiration rate (breaths per minute)'),
        color=alt.value('green')  # Use a single color for respiration rate plot
    ).properties(
        width=800,
        height=400,
        title=f'Respiration rate over time from {formatted_min_date} to {formatted_max_date}'
    )
    return chart


def plot_diff(mean_before, var_before, mean_after, var_after):
    """
    Plots a side-by-side bar chart comparing 'before' and 'after' mean values with error bars representing variance.
    
    Args:
    - mean_before: Mean value before
    - var_before: Variance before
    - mean_after: Mean value after
    - var_after: Variance after
    """
    
    # Compute the standard deviation (sqrt of variance)
    std_before = var_before ** 0.5
    std_after = var_after ** 0.5
    
    # Create a DataFrame to hold the data
    data = pd.DataFrame({
        'Condition': ['Before', 'After'],
        'Mean': [mean_before, mean_after],
        'Error': [std_before, std_after]
    })

    # Create the bar plot with error bars
    bars = alt.Chart(data).mark_bar(opacity=0.5).encode(
        x=alt.X('Condition:N', title='Condition'),
        y=alt.Y('Mean:Q', title='Mean Value'),
        color=alt.Color('Condition:N', legend=None)
    )

    # Add error bars using the precomputed standard deviations
    error_bars = bars.mark_errorbar().encode(
        y=alt.Y('Mean:Q'),
        yError='Error:Q'
    )

    # Combine the bars and error bars into a single chart
    chart = bars + error_bars

    # Display the chart using Streamlit
    st.altair_chart(chart.properties(
        width=300,
        height=400
    ))

def plot_sequences(seq_before, seq_after):
    """
    Plots sequences before and after an intervention using Altair.
    Sequences corresponding to the same intervention event share the same color.
    """
    # Prepare data with a shared color ID for matching sequences
    before_data = []
    after_data = []
    print(seq_before)
    
    for i, seq in enumerate(seq_before):
        x_vals = list(range(-len(seq)+1, 1))  # Negative x-values
        # print(x_vals)
        # print(seq)
        # print()
        before_data.extend({"x": x, "value": v, "type": "Before", "event_id": f"Event {i+1}"} 
                           for x, v in zip(x_vals, seq))
    
    for i, seq in enumerate(seq_after):
        x_vals = list(range(0, len(seq) + 1))  # Positive x-values
        after_data.extend({"x": x, "value": v, "type": "After", "event_id": f"Event {i+1}"} 
                          for x, v in zip(x_vals, seq))

    # Combine data into a single DataFrame
    data = pd.DataFrame(before_data + after_data)

    # Create the Altair chart for sequences
    chart = alt.Chart(data).mark_line().encode(
        x=alt.X("x:Q", title="Time (Relative to Intervention)"),
        y=alt.Y("value:Q", title="Indicator Value"),
        color=alt.Color("event_id:N", legend=alt.Legend(title="Intervention Event")),
        detail="type:N"  # Detail ensures differentiation between before and after within the same event
    ).properties(
        title="Sequence of Indicators Before and After Intervention",
        width=800,
        height=400
    )

    # Add a vertical line at x=0 for the intervention point
    rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="red").encode(x="x:Q")

    # Overlay the rule on the main chart
    final_chart = chart + rule

    # Render the chart in Streamlit
    st.altair_chart(final_chart, use_container_width=True)
