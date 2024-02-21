import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_option('deprecation.showPyplotGlobalUse', False)

def visualization_page():
    st.title("Visualization Page")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        header_length = 5
        df = pd.read_csv(uploaded_file, skiprows=header_length)
        df['isoDate'] = pd.to_datetime(df['isoDate'])
        fig = plot_data(df)
        st.pyplot(fig)

def plot_data(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['isoDate'].values, df['stressLevel'].values, label='Original Data', color='blue')
    ax.set_xlabel('Date')
    ax.set_ylabel('Stress Level')
    ax.set_title('Stress Level over Time')
    ax.legend()
    return fig

if __name__ == '__main__':
    visualization_page()
