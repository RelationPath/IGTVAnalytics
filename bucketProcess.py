#By: Brayton Kerekffy
import argparse
import datetime
import pprint
import redis
import argparse
import io
import re
import os

from google.cloud import storage
from google.cloud import vision
from google.protobuf import json_format


# [START storage_upload_file]
from google.cloud import storage

# [END storage_upload_file]

bucketSet = "igtv-input-data"

r = redis.StrictRedis(
   host='127.0.0.1',
   port=6379,
   password='')

def detect_text_uri(uri):
   """Collects input when user calls on program to detect text from the command line and saves the uri given after the call as the variable to be called on in the program"""

   client = vision.ImageAnnotatorClient()
   image = vision.types.Image()
   image.source.image_uri = uri

   """defines the uri to be called on as what the user defined it to be in the command call"""

   response = client.text_detection(image=image)
   texts = response.text_annotations
   print('Indexed!')

   account = 'was not found'
   date = 'was not found'
   length = 'was not found'
   title = 'was not found'
   views = 'was not found'
   comments = 'was not found'

   progressDate = ''
   date = ''
   title = ''
   lastStore = ''
   onTitle = True
   onAccount = True

   for text in texts:
      textDescription = u'{}'.format(text.description)
      #print(textDescription.encode('utf-8'))

      vertices = (['({},{})'.format(vertex.x, vertex.y)
            for vertex in text.bounding_poly.vertices])

      if vertex.y < 155:
         title = title + " " +  textDescription.encode('utf-8')
         progressTitle = textDescription.encode('utf-8')
      elif vertex.x > 44 and vertex.y in range(155,250):
         if onAccount:
            account = textDescription.encode('utf-8')
            onAccount = False
         else:
            date = date + " " +  textDescription.encode('utf-8')
      #elif vertex.x in range(300,1000) and vertex.y in range(121,185):
      elif vertex.x in range(920,935) and vertex.y in range(1725,1740):
         length = textDescription.encode('utf-8')
      elif textDescription.encode('utf-8') == 'views':
         views = lastStore
      elif textDescription.encode('utf-8') == 'comments':
         comments = lastStore

      lastStore = textDescription.encode('utf-8')

   print(account + '/' + date + '/' + length + '/' + title + '/' + views + '/' + comments)

   r.lpush(account + '-dates', "/" + title + "/, was released: " + date + "           ")
   r.lpush(account + '-lengths', "/" + title + "/, length: " + length + "          ")
   r.lpush(account + '-titles', title + "         ")
   r.lpush(account + '-views',  "/" + title + "/, view count: " + views + "           ")
   r.lpush(account + '-comments', "/" + title + "/, comment count: " + comments + "           ")

def rclone_transfer():
    os.system("rclone copy gDriveIGTV:GooglePhotos gCloudIGTV:igtv-input-data")
    os.system("rclone delete gDriveIGTV:GooglePhotos")
    print('transfered!')

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

    print('Blob {} deleted.'.format(blob_name))

def make_blob_public(bucket_name, blob_name):
    """Makes a blob publicly accessible."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.make_public()
    blobURI = blob.public_url
    detect_text_uri(blobURI)
    print('Blob {} is publicly accessible at {}'.format(
        blob.name, blob.public_url))
    delete_blob(bucket_name, blob_name)

def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs()

    for blob in blobs:
        make_blob_public(bucketSet, blob.name)
    rclone_transfer()
    list_blobs(bucketSet)

list_blobs(bucketSet)
