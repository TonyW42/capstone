# Instructions for setup

1. Install streamlit using `pip install streamlit`
2. Check the version: `streamlit --version`
3. If Streamlit is not recognized, it might not be added to your system's PATH variable. You can try adding it manually:
    + On Windows, you can add the path to the Streamlit executable (e.g., C:\Users\YourUsername\AppData\Local\Programs\Python\PythonXX\Scripts) to the PATH variable in System Properties.
    + On macOS and Linux, you can add the path to your ~/.bash_profile or ~/.bashrc file:
export PATH="$PATH:/path/to/streamlit"
4. Install the vega datasets package: `pip install vega_datasets`
5. In the repository's folder, type the following command in the terminal to run the webapp: `streamlit run main.py`
6. If you get a Google Cloud related error when trying to run the webapp, try the following commands:
    + `pip install google-cloud`
    + `pip install google-cloud-vision`
    + `pip install --upgrade google-cloud google-api-core google-auth`

# Data storage structure/hierarchy on GCP

* Our GCP bucket for this project can be accessed via this [link](https://console.cloud.google.com/storage/browser/physiological-data;tab=objects?forceOnBucketsSortingFiltering=true&hl=en-au&project=apcomp297&prefix=&forceOnObjectsSortingFiltering=false&inv=1&invt=AbeDpQ)
* Our physiological-data bucket has the following 5 subfolders:
    - **raw**: This subfolder contains our raw Garmin data exported from Labfront. This is the subfolder to which we will upload our (unzipped) data folders after downloading them from Labfront.
    - **clean**: This subfolder stores all users' cleaned datasets that have undergone data cleaning and preprocessing. This action is triggered in the web app, which writes the cleaned data to this subfolder.
    - **events**: This subfolder stores the start time, end time, and event type for the user. The web app creates a SQL database called events.db for each user, which gets written to this subfolder.
    - **interventions**: This subfolder stores the start time, end time, and intervention type for the user. The web app creates a SQL database called interventions.db for each user, which gets written to this subfolder.
    - **users**: This subfolder stores the username, selected intervention for the user, and selected events (e.g., stress-inducing) for the user. The web app creates a SQL database called users.db for each user, which gets written to this subfolder.
