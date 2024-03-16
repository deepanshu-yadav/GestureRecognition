from azure.storage.blob import BlobClient

def download_data(sas_url):
    """
        This function takes a sas url from azure blob storage and download that blob in the current working directory.
    """
    blob_client = BlobClient.from_blob_url(sas_url)
    with open(file=blob_client.blob_name, mode="wb") as blob_file:
        download_stream = blob_client.download_blob()
        blob_file.write(download_stream.readall())