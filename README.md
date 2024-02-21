Instructions for setup:
1. Install streamlit using pip install streamlit
2. Check the version: streamlit --version
If Streamlit is not recognized, it might not be added to your system's PATH variable. You can try adding it manually:
On Windows, you can add the path to the Streamlit executable (e.g., C:\Users\YourUsername\AppData\Local\Programs\Python\PythonXX\Scripts) to the PATH variable in System Properties.
On macOS and Linux, you can add the path to your ~/.bash_profile or ~/.bashrc file:
export PATH="$PATH:/path/to/streamlit"
3. from within the STREAMLIT folder type the following command in the terminal to run the webapp:
streamlit run main.py