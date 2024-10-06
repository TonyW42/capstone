from google.cloud import storage
import os
def list_all_files_in_bucket(bucket_name):
    """
    Lists all the files in a given Google Cloud Storage bucket.

    Args:
        bucket_name (str): The name of the GCS bucket.
        
    Returns:
        List of file paths in the bucket.
    """
    # Initialize the GCS client
    client = storage.Client()

    # Get the bucket
    bucket = client.bucket(bucket_name)

    # List all blobs (files) in the bucket
    blobs = bucket.list_blobs()

    # Collect file names (file paths)
    file_list = [blob.name for blob in blobs]

    return file_list

if __name__ == "__main__":
    # Example usage:
    bucket_name="physiological-data"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "apcomp297-84a78a17c7a6.json" 
    files = list_all_files_in_bucket(bucket_name)
    for file in files:
        print(file)
