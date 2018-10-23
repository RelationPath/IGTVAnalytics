import argparse
import datetime
import pprint

# [START storage_upload_file]
from google.cloud import storage

# [END storage_upload_file]

bucketSet = "igtv-input-data"

def make_blob_public(bucket_name, blob_name):
    """Makes a blob publicly accessible."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.make_public()

    print('Blob {} is publicly accessible at {}'.format(
        blob.name, blob.public_url))

def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs()

    for blob in blobs:
        make_blob_public(bucketSet, blob.name)

list_blobs(bucketSet)

